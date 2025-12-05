"""
WebSocket endpoints for Twilio Media Streams.
Uses Deepgram for real-time streaming transcription with VAD.
"""
import json
import asyncio
import base64
import sys
import audioop
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import websockets
from src.config import settings

def log(msg):
    """Print and flush immediately."""
    print(msg, flush=True)
    sys.stdout.flush()

router = APIRouter(prefix="/streams", tags=["Streams"])

# Deepgram WebSocket URL with parameters
DEEPGRAM_WS_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?model=nova-3"
    "&language=en"
    "&encoding=mulaw"
    "&sample_rate=8000"
    "&channels=1"
    "&punctuate=true"
    "&interim_results=true"
    "&endpointing=500"  # 500ms silence = end of utterance
    "&vad_events=true"  # Get speech start/end events
    "&smart_format=true"
)


class ConversationState:
    """Track conversation state."""
    def __init__(self):
        self.transcript_buffer = ""      # Current utterance being built
        self.all_utterances = []         # List of completed utterances
        self.utterance_count = 0
        self.is_speaking = False
        

async def send_beep_to_twilio(twilio_ws: WebSocket, stream_sid: str):
    """Send a beep sound to acknowledge receipt."""
    import math
    
    # Generate beep
    num_samples = int(8000 * 0.3)  # 300ms
    samples = []
    for i in range(num_samples):
        t = i / 8000
        value = int(16000 * math.sin(2 * math.pi * 600 * t))
        value = max(-32768, min(32767, value))
        samples.append(value)
    
    pcm = b''.join(s.to_bytes(2, 'little', signed=True) for s in samples)
    mulaw = audioop.lin2ulaw(pcm, 2)
    
    # Send in chunks
    chunk_size = 160
    for i in range(0, len(mulaw), chunk_size):
        chunk = mulaw[i:i+chunk_size]
        if len(chunk) < chunk_size:
            chunk = chunk + b'\xff' * (chunk_size - len(chunk))
        
        media_message = {
            "event": "media",
            "streamSid": stream_sid,
            "media": {
                "payload": base64.b64encode(chunk).decode('utf-8')
            }
        }
        await twilio_ws.send_text(json.dumps(media_message))
        await asyncio.sleep(0.02)
    
    log(f"   🔔 Sent beep")


async def deepgram_receiver(dg_ws, state: ConversationState, twilio_ws: WebSocket, stream_sid: str):
    """Receive transcriptions from Deepgram."""
    try:
        async for message in dg_ws:
            data = json.loads(message)
            
            # Handle different message types
            msg_type = data.get("type", "")
            
            if msg_type == "SpeechStarted":
                if not state.is_speaking:
                    log(f"🎤 Speech started")
                    state.is_speaking = True
                    
            elif msg_type == "Results":
                channel = data.get("channel", {})
                alternatives = channel.get("alternatives", [])
                
                if alternatives:
                    transcript = alternatives[0].get("transcript", "")
                    is_final = data.get("is_final", False)
                    speech_final = data.get("speech_final", False)
                    
                    if transcript:
                        if is_final:
                            # Final result for this segment
                            state.transcript_buffer += transcript + " "
                            log(f"   📝 [{transcript}]")
                        else:
                            # Interim result - just for display
                            log(f"   ... {transcript}")
                    
                    # speech_final = true means endpoint detected (user stopped speaking)
                    if speech_final and state.transcript_buffer.strip():
                        state.utterance_count += 1
                        final_text = state.transcript_buffer.strip()
                        state.all_utterances.append(final_text)
                        
                        log(f"")
                        log(f"🔇 Utterance #{state.utterance_count} complete:")
                        log(f"   \"{final_text}\"")
                        
                        # Send beep to acknowledge
                        await send_beep_to_twilio(twilio_ws, stream_sid)
                        log(f"   ✅ Ready for next utterance")
                        log(f"")
                        
                        # Reset buffer
                        state.transcript_buffer = ""
                        state.is_speaking = False
                        
            elif msg_type == "Metadata":
                log(f"📊 Deepgram connected: model={data.get('model_info', {}).get('name', 'unknown')}")
                
            elif msg_type == "UtteranceEnd":
                # Alternative endpoint detection
                if state.transcript_buffer.strip():
                    state.utterance_count += 1
                    final_text = state.transcript_buffer.strip()
                    state.all_utterances.append(final_text)
                    
                    log(f"🔇 [UtteranceEnd] #{state.utterance_count}: \"{final_text}\"")
                    await send_beep_to_twilio(twilio_ws, stream_sid)
                    
                    state.transcript_buffer = ""
                    state.is_speaking = False
                    
    except websockets.exceptions.ConnectionClosed:
        log(f"🔌 Deepgram connection closed")
    except Exception as e:
        log(f"❌ Deepgram receiver error: {e}")


async def audio_forwarder(twilio_ws: WebSocket, dg_ws, state: ConversationState):
    """Forward audio from Twilio to Deepgram."""
    stream_sid = None
    call_sid = None
    media_count = 0
    
    try:
        while True:
            data = await twilio_ws.receive_text()
            message = json.loads(data)
            event = message.get('event', 'unknown')
            
            if event == 'connected':
                log(f"✅ Twilio connected")
                
            elif event == 'start':
                start_data = message.get('start', {})
                stream_sid = start_data.get('streamSid')
                call_sid = start_data.get('callSid')
                log(f"✅ Stream started: {call_sid}")
                # Return stream_sid for beep function
                return stream_sid, call_sid, "started"
                
            elif event == 'media':
                media_count += 1
                # Get raw mulaw audio
                payload = message['media']['payload']
                audio_bytes = base64.b64decode(payload)
                
                # Forward directly to Deepgram (it accepts mulaw 8kHz)
                await dg_ws.send(audio_bytes)
                
                if media_count % 200 == 0:
                    log(f"📦 Forwarded {media_count} packets to Deepgram")
                
            elif event == 'stop':
                log(f"🛑 Stream stopped")
                return stream_sid, call_sid, "stopped"
                
            elif event == 'mark':
                pass  # Ignore marks
                
    except WebSocketDisconnect:
        log(f"⚠️ Twilio disconnected")
        return stream_sid, call_sid, "disconnected"
    except Exception as e:
        log(f"❌ Forwarder error: {e}")
        return stream_sid, call_sid, "error"


@router.websocket("/twilio")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handle Twilio Media Streams with Deepgram real-time transcription.
    """
    log("=" * 60)
    log("🎙️ New call incoming...")
    await websocket.accept()
    log("✅ Twilio WebSocket accepted")
    
    state = ConversationState()
    stream_sid = None
    call_sid = None
    dg_ws = None
    
    try:
        # Connect to Deepgram
        log(f"🔌 Connecting to Deepgram...")
        
        async with websockets.connect(
            DEEPGRAM_WS_URL,
            additional_headers={
                "Authorization": f"Token {settings.deepgram_api_key}"
            }
        ) as dg_ws:
            log(f"✅ Deepgram connected")
            
            # Wait for Twilio to send 'start' event first
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                event = message.get('event', 'unknown')
                
                if event == 'connected':
                    log(f"✅ Twilio protocol: {message.get('protocol')}")
                elif event == 'start':
                    start_data = message.get('start', {})
                    stream_sid = start_data.get('streamSid')
                    call_sid = start_data.get('callSid')
                    log(f"✅ Stream started: {call_sid}")
                    log(f"   Format: mulaw 8kHz mono")
                    break
            
            # Create tasks for bidirectional communication
            receiver_task = asyncio.create_task(
                deepgram_receiver(dg_ws, state, websocket, stream_sid)
            )
            
            # Forward audio from Twilio to Deepgram
            media_count = 0
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    event = message.get('event', 'unknown')
                    
                    if event == 'media':
                        media_count += 1
                        payload = message['media']['payload']
                        audio_bytes = base64.b64decode(payload)
                        await dg_ws.send(audio_bytes)
                        
                        if media_count % 200 == 0:
                            log(f"📦 Packets: {media_count}")
                            
                    elif event == 'stop':
                        log(f"🛑 Stream stopped (packets: {media_count})")
                        break
                        
            except WebSocketDisconnect:
                log(f"⚠️ Twilio disconnected (packets: {media_count})")
            
            # Cancel receiver task
            receiver_task.cancel()
            try:
                await receiver_task
            except asyncio.CancelledError:
                pass
            
            # Close Deepgram connection gracefully
            await dg_ws.send(json.dumps({"type": "CloseStream"}))
            
    except websockets.exceptions.InvalidStatusCode as e:
        log(f"❌ Deepgram auth failed: {e}")
    except Exception as e:
        log(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Print conversation summary
        log(f"")
        log(f"📋 Conversation Summary ({state.utterance_count} utterances):")
        for i, text in enumerate(state.all_utterances, 1):
            log(f"   {i}. {text}")
        log(f"")
        log(f"🔚 Call ended")
        log("=" * 60)

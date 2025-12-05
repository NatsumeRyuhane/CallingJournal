"""
WebSocket endpoints for Twilio Media Streams.
"""
import json
import asyncio
import base64
import sys
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.config import settings

def log(msg):
    """Print and flush immediately."""
    print(msg, flush=True)
    sys.stdout.flush()

router = APIRouter(prefix="/streams", tags=["Streams"])

@router.websocket("/twilio")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handle Twilio Media Streams WebSocket connection.
    """
    log("=" * 50)
    log("DEBUG: WebSocket connection attempt received")
    await websocket.accept()
    log("DEBUG: WebSocket connection accepted")
    
    stream_sid = None
    media_count = 0
    
    try:
        while True:
            # Receive message from Twilio
            log("DEBUG: Waiting for message...")
            data = await websocket.receive_text()
            log(f"DEBUG: Received data length: {len(data)}")
            message = json.loads(data)
            event = message.get('event', 'unknown')
            log(f"DEBUG: Event type: {event}")
            
            if event == 'connected':
                log(f"✅ Twilio Connected: protocol={message.get('protocol')}")
                
            elif event == 'start':
                start_data = message.get('start', {})
                stream_sid = start_data.get('streamSid')
                call_sid = start_data.get('callSid')
                log(f"✅ Twilio Stream Started: streamSid={stream_sid}, callSid={call_sid}")
                log(f"   Media format: {start_data.get('mediaFormat', {})}")
                
            elif event == 'media':
                media_count += 1
                # Log every 100th media packet to avoid spam
                if media_count % 100 == 1:
                    log(f"📦 Receiving audio... (packet #{media_count})")
                # payload = message['media']['payload']
                # chunk = base64.b64decode(payload)
                # TODO: Process audio with STT, VAD, etc.
                pass
                
            elif event == 'stop':
                stop_data = message.get('stop', {})
                log(f"🛑 Twilio Stream Stopped: streamSid={stop_data.get('streamSid', stream_sid)}")
                log(f"   Total media packets received: {media_count}")
                break
                
            elif event == 'mark':
                log(f"📍 Mark event: {message.get('mark', {})}")
                
            else:
                log(f"❓ Unknown event: {event}, message: {message}")
                
    except WebSocketDisconnect:
        log(f"⚠️ WebSocket disconnected (received {media_count} media packets)")
    except Exception as e:
        log(f"❌ WebSocket error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        log(f"🔚 WebSocket closing... (stream_sid={stream_sid})")
        try:
            await websocket.close()
        except:
            pass

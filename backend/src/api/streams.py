"""
WebSocket endpoints for Twilio Media Streams.
Implements bidirectional conversation with real-time transcription (Deepgram),
LLM response generation, and TTS playback.
"""
import json
import asyncio
import base64
from typing import Optional, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import websockets
from sqlalchemy import select

from src.config import settings
from src.logging_config import get_logger
from src.database import AsyncSessionLocal
from src.db_models import Call, Journal, Conversation, ConversationTurn
from src.services.conversation_service import conversation_service, ConversationContext
from src.services.tts_service import tts_service

logger = get_logger(__name__)

router = APIRouter(prefix="/streams", tags=["Streams"])


def get_deepgram_ws_url() -> str:
    """Build Deepgram WebSocket URL from config settings."""
    return (
        "wss://api.deepgram.com/v1/listen"
        f"?model={settings.deepgram_model}"
        f"&language={settings.deepgram_language}"
        f"&encoding={settings.deepgram_encoding}"
        f"&sample_rate={settings.deepgram_sample_rate}"
        f"&channels={settings.deepgram_channels}"
        "&punctuate=true"
        "&interim_results=true"
        f"&endpointing={settings.deepgram_endpointing}"
        "&vad_events=true"
        "&smart_format=true"
    )


class CallState:
    """Track call state for bidirectional conversation."""

    def __init__(self):
        self.transcript_buffer = ""
        self.all_utterances = []
        self.utterance_count = 0
        self.is_speaking = False
        self.is_ai_speaking = False
        self.context: Optional[ConversationContext] = None
        self.stream_sid: Optional[str] = None
        self.call_sid: Optional[str] = None
        self.pending_response: Optional[asyncio.Task] = None


async def send_audio_to_twilio(twilio_ws: WebSocket, stream_sid: str, audio_data: bytes):
    """
    Send audio data to Twilio in chunks.

    Args:
        twilio_ws: Twilio WebSocket connection
        stream_sid: Twilio stream SID
        audio_data: Audio bytes in mulaw 8kHz format
    """
    chunk_size = 160  # 20ms of audio at 8kHz
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i + chunk_size]
        # Pad if needed
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
        await asyncio.sleep(0.02)  # 20ms pacing


async def speak_response(twilio_ws: WebSocket, state: CallState, text: str):
    """
    Log the AI response, generate TTS audio, and send to Twilio.

    Args:
        twilio_ws: Twilio WebSocket connection
        state: Call state
        text: Text to speak
    """
    state.is_ai_speaking = True
    logger.info(f"[{state.call_sid}] AI response: {text}")

    try:
        # Generate TTS audio
        audio_data = await tts_service.synthesize(text)

        # Send to Twilio
        await send_audio_to_twilio(twilio_ws, state.stream_sid, audio_data)

    except Exception as e:
        logger.error(f"[{state.call_sid}] TTS error: {e}", exc_info=True)
    finally:
        state.is_ai_speaking = False


async def process_user_utterance(twilio_ws: WebSocket, state: CallState, utterance: str):
    """
    Process a completed user utterance and generate AI response.

    Args:
        twilio_ws: Twilio WebSocket connection
        state: Call state
        utterance: User's transcribed speech
    """
    if not state.context:
        return

    logger.info(f"[{state.call_sid}] User said: {utterance}")

    # Generate AI response
    try:
        response = await conversation_service.generate_response(state.context, utterance)
        await speak_response(twilio_ws, state, response)

        # Check if conversation is ending
        if state.context.is_ending:
            logger.info(f"[{state.call_sid}] User requested to end conversation")

    except Exception as e:
        logger.error(f"[{state.call_sid}] Error generating response: {e}", exc_info=True)
        await speak_response(twilio_ws, state, "I'm sorry, I had trouble understanding. Could you please repeat that?")


async def save_diary_to_database(
    call_sid: str,
    diary_entry: Dict[str, Any],
    context: ConversationContext
) -> Optional[int]:
    """
    Save diary entry and conversation to database.

    Args:
        call_sid: Twilio call SID (external_call_id)
        diary_entry: Generated diary data
        context: Conversation context with messages

    Returns:
        Journal ID if saved successfully, None otherwise
    """
    async with AsyncSessionLocal() as db:
        try:
            # Find the call record by external_call_id
            result = await db.execute(
                select(Call).where(Call.external_call_id == call_sid)
            )
            call = result.scalar_one_or_none()

            if not call:
                logger.warning(f"[{call_sid}] Call record not found in database, cannot save diary")
                return None

            # Save conversation turns
            for i, msg in enumerate(context.messages):
                if msg.role == "system":
                    continue  # Skip system messages

                turn = ConversationTurn.USER if msg.role == "user" else ConversationTurn.ASSISTANT
                logger.debug(
                    f"SAVING TURN: role={msg.role}, enum={turn!r}, value={turn.value}"
                )
                conversation = Conversation(
                    call_id=call.id,
                    turn=turn,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    order_index=i
                )
                db.add(conversation)

            # Create journal entry
            journal = Journal(
                user_id=call.user_id,
                call_id=call.id,
                title=diary_entry.get("title", f"Diary - {context.started_at.strftime('%B %d, %Y')}"),
                summary=diary_entry.get("content", ""),
                key_points=diary_entry.get("key_points", []),
                action_items=diary_entry.get("action_items", []),
                tags=diary_entry.get("topics", []) + [diary_entry.get("mood", "")],
                full_content=context.get_transcript(),
                entities=diary_entry.get("gratitude", []),
                topics=diary_entry.get("topics", []),
                sentiment=diary_entry.get("sentiment", "neutral")
            )
            db.add(journal)

            # Update call with transcript
            call.raw_transcript = context.get_transcript()

            await db.commit()
            await db.refresh(journal)

            logger.info(f"[{call_sid}] Diary saved to database: journal_id={journal.id}")
            return journal.id

        except Exception as e:
            logger.error(f"[{call_sid}] Failed to save diary to database: {e}", exc_info=True)
            await db.rollback()
            return None


async def deepgram_receiver(dg_ws, state: CallState, twilio_ws: WebSocket):
    """Receive transcriptions from Deepgram and trigger AI responses."""
    try:
        async for message in dg_ws:
            data = json.loads(message)
            msg_type = data.get("type", "")

            if msg_type == "SpeechStarted":
                if not state.is_speaking and not state.is_ai_speaking:
                    logger.debug(f"[{state.call_sid}] User started speaking")
                    state.is_speaking = True

                    # Cancel any pending AI response if user interrupts
                    if state.pending_response and not state.pending_response.done():
                        state.pending_response.cancel()

            elif msg_type == "Results":
                channel = data.get("channel", {})
                alternatives = channel.get("alternatives", [])

                if alternatives:
                    transcript = alternatives[0].get("transcript", "")
                    is_final = data.get("is_final", False)
                    speech_final = data.get("speech_final", False)

                    if transcript:
                        if is_final:
                            state.transcript_buffer += transcript + " "
                            logger.debug(f"[{state.call_sid}] Transcript segment: {transcript}")

                    # speech_final = endpoint detected (user stopped speaking)
                    if speech_final and state.transcript_buffer.strip():
                        state.utterance_count += 1
                        final_text = state.transcript_buffer.strip()
                        state.all_utterances.append(final_text)

                        logger.debug(f"[{state.call_sid}] Utterance #{state.utterance_count} complete")

                        # Process utterance and generate response
                        state.pending_response = asyncio.create_task(
                            process_user_utterance(twilio_ws, state, final_text)
                        )

                        # Reset buffer
                        state.transcript_buffer = ""
                        state.is_speaking = False

            elif msg_type == "Metadata":
                model_name = data.get('model_info', {}).get('name', 'unknown')
                logger.info(f"[{state.call_sid}] Deepgram connected: model={model_name}")

            elif msg_type == "UtteranceEnd":
                if state.transcript_buffer.strip():
                    state.utterance_count += 1
                    final_text = state.transcript_buffer.strip()
                    state.all_utterances.append(final_text)

                    logger.debug(f"[{state.call_sid}] UtteranceEnd #{state.utterance_count}")

                    state.pending_response = asyncio.create_task(
                        process_user_utterance(twilio_ws, state, final_text)
                    )

                    state.transcript_buffer = ""
                    state.is_speaking = False

    except websockets.exceptions.ConnectionClosed:
        logger.info(f"[{state.call_sid}] Deepgram connection closed")
    except Exception as e:
        logger.error(f"[{state.call_sid}] Deepgram receiver error: {e}", exc_info=True)


@router.websocket("/twilio")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handle Twilio Media Streams with bidirectional AI conversation.

    Flow:
    1. Twilio connects and starts streaming audio
    2. Audio is forwarded to Deepgram for real-time transcription
    3. When user finishes speaking (VAD), LLM generates response
    4. Response is converted to speech (TTS) and sent back to Twilio
    5. Conversation continues until user ends or hangs up
    6. On disconnect, diary entry is generated from conversation
    """
    logger.info("New Twilio WebSocket connection incoming")
    await websocket.accept()
    logger.debug("Twilio WebSocket accepted")

    state = CallState()

    try:
        # Connect to Deepgram
        logger.debug("Connecting to Deepgram...")

        async with websockets.connect(
            get_deepgram_ws_url(),
            additional_headers={
                "Authorization": f"Token {settings.deepgram_api_key}"
            }
        ) as dg_ws:
            logger.debug("Deepgram WebSocket connected")

            # Wait for Twilio to send 'start' event
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                event = message.get('event', 'unknown')

                if event == 'connected':
                    logger.debug(f"Twilio protocol: {message.get('protocol')}")
                elif event == 'start':
                    start_data = message.get('start', {})
                    state.stream_sid = start_data.get('streamSid')
                    state.call_sid = start_data.get('callSid')
                    logger.info(f"[{state.call_sid}] Call started")

                    # Start conversation
                    state.context = conversation_service.start_conversation(
                        call_id=state.call_sid
                    )

                    # Send initial greeting
                    greeting = await conversation_service.generate_greeting(state.context)
                    await speak_response(websocket, state, greeting)

                    break

            # Create task for receiving Deepgram transcriptions
            receiver_task = asyncio.create_task(
                deepgram_receiver(dg_ws, state, websocket)
            )

            # Forward audio from Twilio to Deepgram
            media_count = 0
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    event = message.get('event', 'unknown')

                    if event == 'media':
                        # Don't forward audio while AI is speaking (echo cancellation)
                        if not state.is_ai_speaking:
                            media_count += 1
                            payload = message['media']['payload']
                            audio_bytes = base64.b64decode(payload)
                            await dg_ws.send(audio_bytes)

                            if media_count % 500 == 0:
                                logger.debug(f"[{state.call_sid}] Audio packets processed: {media_count}")

                    elif event == 'stop':
                        logger.info(f"[{state.call_sid}] Stream stopped (packets: {media_count})")
                        break

            except WebSocketDisconnect:
                logger.info(f"[{state.call_sid}] Twilio disconnected (packets: {media_count})")

            # Cancel receiver task
            receiver_task.cancel()
            try:
                await receiver_task
            except asyncio.CancelledError:
                pass

            # Close Deepgram connection
            await dg_ws.send(json.dumps({"type": "CloseStream"}))

    except websockets.exceptions.InvalidStatusCode as e:
        logger.error(f"Deepgram auth failed: {e}")
    except Exception as e:
        logger.error(f"Stream error: {type(e).__name__}: {e}", exc_info=True)
    finally:
        # End conversation and generate diary
        if state.context:
            context = conversation_service.end_conversation(state.call_sid)
            if context and context.messages:
                logger.info(f"[{state.call_sid}] Conversation ended with {state.utterance_count} utterances")

                # Log utterances at debug level
                for i, text in enumerate(state.all_utterances, 1):
                    logger.debug(f"[{state.call_sid}] Utterance {i}: {text}")

                # Generate and save diary entry
                try:
                    logger.info(f"[{state.call_sid}] Generating diary entry...")
                    diary_entry = await conversation_service.generate_diary_entry(context)
                    logger.info(
                        f"[{state.call_sid}] Diary generated: "
                        f"title='{diary_entry.get('title', 'Untitled')}', "
                        f"mood='{diary_entry.get('mood', 'unknown')}'"
                    )

                    # Save diary entry to database
                    journal_id = await save_diary_to_database(
                        call_sid=state.call_sid,
                        diary_entry=diary_entry,
                        context=context
                    )

                    if journal_id:
                        logger.info(f"[{state.call_sid}] Diary persisted: journal_id={journal_id}")

                except Exception as e:
                    logger.error(f"[{state.call_sid}] Error generating/saving diary: {e}", exc_info=True)

        logger.info(f"[{state.call_sid or 'unknown'}] Call ended")
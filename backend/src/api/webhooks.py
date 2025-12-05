"""
Webhook endpoints for phone service callbacks.
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.db_models import Call, CallStatus
from src.schemas import TwilioCallbackRequest, MessageResponse
from src.services.phone_service import phone_service
from src.services.transcription_service import transcription_service

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/twilio/call-status")
async def twilio_call_status(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Twilio call status callbacks.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        TwiML response or success message
    """
    # Parse form data from Twilio
    form_data = await request.form()
    
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")
    duration = form_data.get("Duration")
    
    # Find call in database
    result = await db.execute(
        select(Call).where(Call.external_call_id == call_sid)
    )
    call = result.scalar_one_or_none()
    
    if call:
        # Update call status
        if call_status == "completed":
            call.status = CallStatus.COMPLETED
            if duration:
                call.duration = float(duration)
        elif call_status == "failed":
            call.status = CallStatus.FAILED
        elif call_status == "busy" or call_status == "no-answer":
            call.status = CallStatus.CANCELLED
        
        await db.commit()
    
    return MessageResponse(message="Status updated")


@router.post("/twilio/recording")
async def twilio_recording(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Twilio recording callbacks.
    Downloads and transcribes the recording using local transcription service.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Success message
    """
    form_data = await request.form()
    
    call_sid = form_data.get("CallSid")
    recording_url = form_data.get("RecordingUrl")
    
    # Find call in database
    result = await db.execute(
        select(Call).where(Call.external_call_id == call_sid)
    )
    call = result.scalar_one_or_none()
    
    if call:
        call.audio_url = recording_url
        
        # Transcribe the recording
        try:
            transcription_result = await transcription_service.transcribe_from_url(recording_url)
            call.raw_transcript = transcription_result.get("text", "")
        except Exception as e:
            # Log error but don't fail the webhook
            print(f"Transcription error: {e}")
            call.raw_transcript = f"[Transcription failed: {str(e)}]"
        
        await db.commit()
    
    return MessageResponse(message="Recording saved and transcribed")


@router.post("/twilio/transcription")
async def twilio_transcription(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Twilio transcription callbacks.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Success message
    """
    form_data = await request.form()
    
    call_sid = form_data.get("CallSid")
    transcription_text = form_data.get("TranscriptionText")
    
    # Find call in database
    result = await db.execute(
        select(Call).where(Call.external_call_id == call_sid)
    )
    call = result.scalar_one_or_none()
    
    if call:
        call.raw_transcript = transcription_text
        await db.commit()
    
    return MessageResponse(message="Transcription saved")


@router.post("/twilio/voice")
async def twilio_voice_response(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate TwiML response for incoming or outgoing calls.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        TwiML XML response
    """
    form_data = await request.form()
    
    # Determine WebSocket URL from request
    host = request.headers.get("host")
    # Force wss if using ngrok (usually safer) or trust scheme
    # If running behind ngrok http, scheme is http, but we want wss for the public side usually
    # But let's just log what we have first
    # Force wss if using ngrok, cloudflare, or localtunnel
    is_secure_host = any(domain in host for domain in ["ngrok", "cloudflare", "localtunnel", "pinggy"])
    protocol = "wss" if request.url.scheme == "https" or is_secure_host else "ws"
    stream_url = f"{protocol}://{host}/streams/twilio"
    
    print(f"DEBUG: Generated Stream URL: {stream_url}")
    
    # Generate TwiML with Stream
    twiml = phone_service.generate_twiml_response(
        stream=True,
        stream_url=stream_url,
        message="Connecting to your AI assistant.",
        record=True
    )
    
    print(f"DEBUG: Generated TwiML: {twiml}")
    
    from fastapi.responses import Response
    return Response(content=twiml, media_type="application/xml")


@router.get("/twilio/voice")
async def twilio_voice_test():
    """
    Test endpoint for browser verification.
    """
    print("DEBUG: GET request received on /twilio/voice")
    return {"message": "Twilio webhook is accessible via GET"}


@router.post("/twilio/process-speech")
async def process_speech(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Process speech input from user during call.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        TwiML response
    """
    form_data = await request.form()
    
    speech_result = form_data.get("SpeechResult")
    call_sid = form_data.get("CallSid")
    
    # TODO: Process speech with LLM and generate response
    # For now, just echo back
    response_message = f"You said: {speech_result}. Is there anything else?"
    
    twiml = phone_service.generate_twiml_response(
        message=response_message,
        gather_input=True,
        action="/webhooks/twilio/process-speech",
        record=True
    )
    
    from fastapi.responses import Response
    return Response(content=twiml, media_type="application/xml")


@router.post("/vonage/events")
async def vonage_events(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Vonage event callbacks.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Success message
    """
    data = await request.json()
    
    call_uuid = data.get("uuid")
    status = data.get("status")
    
    # Find call in database
    result = await db.execute(
        select(Call).where(Call.external_call_id == call_uuid)
    )
    call = result.scalar_one_or_none()
    
    if call:
        # Update call status based on Vonage status
        if status == "completed":
            call.status = CallStatus.COMPLETED
        elif status == "failed":
            call.status = CallStatus.FAILED
        
        await db.commit()
    
    return MessageResponse(message="Event processed")

"""
Call management API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.schemas import CallCreate, CallResponse, CallUpdate, MessageResponse
from src.db_models import User, Call, CallStatus
from src.api.auth import get_current_user
from src.services.phone_service import phone_service
from src.services.journal_service import journal_service
from src.services.transcription_service import transcription_service

router = APIRouter(prefix="/calls", tags=["Calls"])


@router.post("", response_model=CallResponse, status_code=status.HTTP_201_CREATED)
async def initiate_call(
    call_data: CallCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initiate a new outbound call.
    
    Args:
        call_data: Call initiation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created call object
    """
    # Initiate call via phone service
    call_result = await phone_service.initiate_call(
        to_number=call_data.phone_number,
        callback_url=call_data.callback_url
    )
    
    # Create call record in database
    call = Call(
        user_id=current_user.id,
        external_call_id=call_result["call_id"],
        phone_number=call_data.phone_number,
        status=CallStatus.IN_PROGRESS
    )
    
    db.add(call)
    await db.commit()
    await db.refresh(call)
    
    return call


@router.get("", response_model=List[CallResponse])
async def get_calls(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's call history.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of call objects
    """
    result = await db.execute(
        select(Call)
        .where(Call.user_id == current_user.id)
        .order_by(Call.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    calls = result.scalars().all()
    return calls


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific call by ID.
    
    Args:
        call_id: Call ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Call object
    """
    result = await db.execute(
        select(Call).where(Call.id == call_id, Call.user_id == current_user.id)
    )
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    return call


@router.patch("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: int,
    call_data: CallUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update call information.
    
    Args:
        call_id: Call ID
        call_data: Call update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated call object
    """
    result = await db.execute(
        select(Call).where(Call.id == call_id, Call.user_id == current_user.id)
    )
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    # Update call fields
    for field, value in call_data.model_dump(exclude_unset=True).items():
        setattr(call, field, value)
    
    await db.commit()
    await db.refresh(call)
    
    return call


@router.post("/{call_id}/end", response_model=MessageResponse)
async def end_call(
    call_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    End an active call.
    
    Args:
        call_id: Call ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    result = await db.execute(
        select(Call).where(Call.id == call_id, Call.user_id == current_user.id)
    )
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    # End call via phone service
    if call.external_call_id:
        success = await phone_service.end_call(call.external_call_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to end call"
            )
    
    # Update call status
    call.status = CallStatus.COMPLETED
    await db.commit()
    
    return MessageResponse(message="Call ended successfully")


@router.post("/{call_id}/generate-journal", response_model=MessageResponse)
async def generate_journal(
    call_id: int,
    background_tasks: BackgroundTasks,
    focus: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate journal entry from call conversation.
    
    Args:
        call_id: Call ID
        background_tasks: FastAPI background tasks
        focus: Optional focus area for summarization
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    result = await db.execute(
        select(Call).where(Call.id == call_id, Call.user_id == current_user.id)
    )
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    # Generate journal in background
    async def _generate():
        async for session in get_db():
            await journal_service.generate_journal_from_call(
                db=session,
                call_id=call_id,
                user_id=current_user.id,
                focus=focus
            )
            await session.commit()
            break
    
    background_tasks.add_task(_generate)
    
    return MessageResponse(message="Journal generation started")


@router.post("/{call_id}/transcribe", response_model=MessageResponse)
async def transcribe_call(
    call_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger transcription for a call recording.
    
    Args:
        call_id: Call ID
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    result = await db.execute(
        select(Call).where(Call.id == call_id, Call.user_id == current_user.id)
    )
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    if not call.audio_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audio recording available for this call"
        )
    
    # Transcribe in background
    async def _transcribe():
        async for session in get_db():
            try:
                # Re-fetch call in background task session
                result = await session.execute(
                    select(Call).where(Call.id == call_id)
                )
                call = result.scalar_one_or_none()
                
                if call and call.audio_url:
                    transcription_result = await transcription_service.transcribe_from_url(
                        call.audio_url
                    )
                    call.raw_transcript = transcription_result.get("text", "")
                    await session.commit()
            except Exception as e:
                print(f"Background transcription error: {e}")
            break
    
    background_tasks.add_task(_transcribe)
    
    return MessageResponse(message="Transcription started")

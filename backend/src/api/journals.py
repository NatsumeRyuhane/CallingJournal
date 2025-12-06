"""
Journal management API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas import (
    JournalCreate, JournalResponse, JournalDetailResponse,
    JournalUpdate, JournalSearchRequest, MessageResponse
)
from src.db_models import User
from src.api.auth import get_current_user
from src.services.journal_service import journal_service

router = APIRouter(prefix="/journals", tags=["Journals"])


@router.post("", response_model=JournalResponse, status_code=status.HTTP_201_CREATED)
async def create_journal(
    journal_data: JournalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new journal entry manually.
    
    Args:
        journal_data: Journal creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created journal object
    """
    from src.db_models import Journal
    
    journal = Journal(
        user_id=current_user.id,
        call_id=journal_data.call_id,
        title=journal_data.title,
        summary=journal_data.summary,
        key_points=journal_data.key_points,
        action_items=journal_data.action_items,
        tags=journal_data.tags,
        full_content=journal_data.full_content
    )
    
    db.add(journal)
    await db.commit()
    await db.refresh(journal)
    
    return journal


@router.get("", response_model=List[JournalResponse])
async def get_journals(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's journal entries.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of journal objects
    """
    journals = await journal_service.get_user_journals(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=skip
    )
    return journals


@router.get("/{journal_id}", response_model=JournalDetailResponse)
async def get_journal(
    journal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific journal entry by ID.
    
    Args:
        journal_id: Journal ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Journal object with full details
    """
    journal = await journal_service.get_journal(db=db, journal_id=journal_id)
    
    if not journal or journal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal not found"
        )
    
    return journal


@router.patch("/{journal_id}", response_model=JournalResponse)
async def update_journal(
    journal_id: int,
    journal_data: JournalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a journal entry.
    
    Args:
        journal_id: Journal ID
        journal_data: Journal update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated journal object
    """
    journal = await journal_service.get_journal(db=db, journal_id=journal_id)
    
    if not journal or journal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal not found"
        )
    
    updates = journal_data.model_dump(exclude_unset=True)
    updated_journal = await journal_service.update_journal(
        db=db,
        journal_id=journal_id,
        updates=updates
    )
    
    await db.commit()
    return updated_journal


@router.delete("/{journal_id}", response_model=MessageResponse)
async def delete_journal(
    journal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a journal entry.
    
    Args:
        journal_id: Journal ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    journal = await journal_service.get_journal(db=db, journal_id=journal_id)
    
    if not journal or journal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal not found"
        )
    
    success = await journal_service.delete_journal(db=db, journal_id=journal_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete journal"
        )
    
    await db.commit()
    return MessageResponse(message="Journal deleted successfully")


@router.post("/search", response_model=List[JournalResponse])
async def search_journals(
    search_data: JournalSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search journal entries.
    
    Args:
        search_data: Search parameters
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of matching journal objects
    """
    journals = await journal_service.search_journals(
        db=db,
        user_id=current_user.id,
        query=search_data.query,
        tags=search_data.tags
    )
    return journals


@router.post("/{journal_id}/extract-knowledge", response_model=MessageResponse)
async def extract_knowledge(
    journal_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Extract domain knowledge from a journal entry.
    
    Args:
        journal_id: Journal ID
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    journal = await journal_service.get_journal(db=db, journal_id=journal_id)
    
    if not journal or journal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal not found"
        )
    
    # Extract knowledge in background
    async def _extract():
        async for session in get_db():
            await journal_service.extract_knowledge(
                db=session,
                journal_id=journal_id,
                user_id=current_user.id
            )
            await session.commit()
            break
    
    background_tasks.add_task(_extract)
    # 🔍 DEBUG MODE: run inline, not as background task
    await _extract()
    
    return MessageResponse(message="Knowledge extraction started")

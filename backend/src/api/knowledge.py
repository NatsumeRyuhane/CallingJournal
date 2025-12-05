"""
Knowledge base API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas import KnowledgeBaseResponse, KnowledgeSearchRequest
from src.db_models import User
from src.api.auth import get_current_user
from src.services.journal_service import journal_service

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


@router.get("", response_model=List[KnowledgeBaseResponse])
async def get_knowledge(
    topic: str = None,
    category: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get knowledge base entries for the current user.
    
    Args:
        topic: Optional topic filter
        category: Optional category filter
        limit: Maximum number of entries to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of knowledge base entries
    """
    knowledge = await journal_service.get_user_knowledge(
        db=db,
        user_id=current_user.id,
        topic=topic,
        category=category,
        limit=limit
    )
    return knowledge


@router.post("/search", response_model=List[KnowledgeBaseResponse])
async def search_knowledge(
    search_data: KnowledgeSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search knowledge base entries.
    
    Args:
        search_data: Search parameters
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of matching knowledge base entries
    """
    knowledge = await journal_service.get_user_knowledge(
        db=db,
        user_id=current_user.id,
        topic=search_data.topic,
        category=search_data.category,
        limit=search_data.limit
    )
    return knowledge

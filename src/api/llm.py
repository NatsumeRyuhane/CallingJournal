"""
LLM API endpoints for direct interaction with language models.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas import LLMChatRequest, LLMSummarizeRequest
from src.db_models import User
from src.api.auth import get_current_user
from src.services.llm_service import llm_service

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post("/chat")
async def chat(
    request: LLMChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Chat with the LLM.
    
    Args:
        request: Chat request with messages and parameters
        current_user: Current authenticated user
        
    Returns:
        LLM response (text or streaming)
    """
    if request.stream:
        # Return streaming response
        async def generate():
            async for chunk in llm_service.generate_streaming_response(
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                yield chunk
        
        return StreamingResponse(generate(), media_type="text/plain")
    else:
        # Return complete response
        response = await llm_service.generate_response(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return {"response": response}


@router.post("/summarize")
async def summarize(
    request: LLMSummarizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Summarize text using the LLM.
    
    Args:
        request: Summarization request
        current_user: Current authenticated user
        
    Returns:
        Structured summary
    """
    summary = await llm_service.summarize_conversation(
        conversation=request.text,
        focus=request.focus
    )
    return summary


@router.post("/extract-entities")
async def extract_entities(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """
    Extract named entities from text.
    
    Args:
        text: Text to analyze
        current_user: Current authenticated user
        
    Returns:
        List of extracted entities
    """
    entities = await llm_service.extract_entities(text=text)
    return {"entities": entities}


@router.post("/analyze-sentiment")
async def analyze_sentiment(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze sentiment of text.
    
    Args:
        text: Text to analyze
        current_user: Current authenticated user
        
    Returns:
        Sentiment analysis result
    """
    sentiment = await llm_service.analyze_sentiment(text=text)
    return sentiment

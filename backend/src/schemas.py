"""
Pydantic schemas for API request/response validation.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr
    phone_number: Optional[str] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str


class UserUpdate(BaseModel):
    """Schema for user update."""
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Call Schemas
class CallCreate(BaseModel):
    """Schema for initiating a call."""
    phone_number: str
    callback_url: Optional[str] = None


class CallUpdate(BaseModel):
    """Schema for updating a call."""
    status: Optional[str] = None
    ended_at: Optional[datetime] = None
    duration: Optional[float] = None
    raw_transcript: Optional[str] = None


class CallResponse(BaseModel):
    """Schema for call response."""
    id: int
    user_id: int
    external_call_id: Optional[str]
    phone_number: str
    status: str
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration: Optional[float]
    audio_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True
        orm_mode = True


# Conversation Schemas
class ConversationCreate(BaseModel):
    """Schema for creating a conversation entry."""
    turn: str  # 'user', 'assistant', 'system'
    content: str
    meta_data: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: int
    call_id: int
    turn: str
    content: str
    timestamp: datetime
    order_index: int
    meta_data: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


# Journal Schemas
class JournalCreate(BaseModel):
    """Schema for creating a journal entry."""
    call_id: Optional[int] = None
    title: str
    summary: str
    key_points: Optional[List[str]] = None
    action_items: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    full_content: Optional[str] = None


class JournalUpdate(BaseModel):
    """Schema for updating a journal entry."""
    title: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    action_items: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    full_content: Optional[str] = None


class JournalResponse(BaseModel):
    """Schema for journal response."""
    id: int
    user_id: int
    call_id: Optional[int]
    title: str
    summary: str
    key_points: Optional[List[str]]
    action_items: Optional[List[str]]
    tags: Optional[List[str]]
    entities: Optional[List[Dict[str, str]]]
    topics: Optional[List[str]]
    sentiment: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True
        orm_mode = True


class JournalDetailResponse(JournalResponse):
    """Schema for detailed journal response."""
    full_content: Optional[str]
    call: Optional[CallResponse] = None

    class Config:
        orm_mode = True
        use_enum_values = True


# Knowledge Base Schemas
class KnowledgeBaseResponse(BaseModel):
    """Schema for knowledge base response."""
    id: int
    user_id: int
    topic: str
    content: str
    category: Optional[str]
    keywords: Optional[List[str]]
    confidence_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


# LLM Request Schemas
class LLMChatRequest(BaseModel):
    """Schema for LLM chat request."""
    messages: List[Dict[str, str]]
    temperature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: Optional[int] = None
    stream: bool = False


class LLMSummarizeRequest(BaseModel):
    """Schema for LLM summarization request."""
    text: str
    focus: Optional[str] = None


# Authentication Schemas
class Token(BaseModel):
    """Schema for JWT token."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str


# Search Schemas
class JournalSearchRequest(BaseModel):
    """Schema for journal search request."""
    query: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = Field(default=50, le=100)
    offset: int = Field(default=0, ge=0)


class KnowledgeSearchRequest(BaseModel):
    """Schema for knowledge base search request."""
    topic: Optional[str] = None
    category: Optional[str] = None
    limit: int = Field(default=50, le=100)


# Webhook Schemas (for phone service callbacks)
class TwilioCallbackRequest(BaseModel):
    """Schema for Twilio webhook callback."""
    CallSid: str
    CallStatus: str
    From: Optional[str] = None
    To: Optional[str] = None
    Duration: Optional[str] = None
    RecordingUrl: Optional[str] = None
    TranscriptionText: Optional[str] = None


# Generic Response Schemas
class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: Optional[str] = None

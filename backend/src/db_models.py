"""
Database models for CallingJournal application.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Float, JSON
from sqlalchemy.orm import relationship
import enum

from src.database import Base


class CallStatus(str, enum.Enum):
    """Enum for call status."""
    # PENDING = "pending"
    # IN_PROGRESS = "in_progress"
    # COMPLETED = "completed"
    # FAILED = "failed"
    # CANCELLED = "cancelled"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ConversationTurn(str, enum.Enum):
    """Enum for conversation turn."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class User(Base):
    """User model for authentication and profile management."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    calls = relationship("Call", back_populates="user", cascade="all, delete-orphan")
    journals = relationship("Journal", back_populates="user", cascade="all, delete-orphan")


class Call(Base):
    """Call session model for tracking phone conversations."""
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Call metadata
    external_call_id = Column(String(255), unique=True, index=True)  # Twilio/Vonage call ID
    phone_number = Column(String(20), nullable=False)
    status = Column(Enum(CallStatus), default=CallStatus.PENDING)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)  # Duration in seconds
    
    # Audio
    audio_url = Column(String(500), nullable=True)
    audio_file_path = Column(String(500), nullable=True)
    
    # Transcription
    raw_transcript = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="calls")
    conversations = relationship("Conversation", back_populates="call", cascade="all, delete-orphan")
    journal = relationship("Journal", back_populates="call", uselist=False)


class Conversation(Base):
    """Conversation model for storing structured dialogue."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False)
    
    # Conversation content
    turn = Column(Enum(ConversationTurn), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    order_index = Column(Integer, nullable=False)  # Order in the conversation
    meta_data = Column(JSON, nullable=True)  # Additional data (e.g., sentiment, intent)
    
    # Relationships
    call = relationship("Call", back_populates="conversations")


class Journal(Base):
    """Journal entry model for summarized and structured logs."""
    __tablename__ = "journals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=True)
    
    # Journal content
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    key_points = Column(JSON, nullable=True)  # List of key points
    action_items = Column(JSON, nullable=True)  # List of action items
    tags = Column(JSON, nullable=True)  # List of tags
    
    # Full content
    full_content = Column(Text, nullable=True)
    
    # Knowledge extraction
    entities = Column(JSON, nullable=True)  # Named entities extracted
    topics = Column(JSON, nullable=True)  # Topic categories
    sentiment = Column(String(50), nullable=True)  # Overall sentiment
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="journals")
    call = relationship("Call", back_populates="journal")


class KnowledgeBase(Base):
    """Knowledge base model for storing domain knowledge extracted from journals."""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Knowledge content
    topic = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source_journal_ids = Column(JSON, nullable=True)  # List of journal IDs
    
    # Categorization
    category = Column(String(100), nullable=True)
    keywords = Column(JSON, nullable=True)  # List of keywords
    
    # Relevance
    confidence_score = Column(Float, nullable=True)  # 0-1 confidence score
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

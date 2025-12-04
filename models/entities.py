"""Data model entities used across the application.

Lightweight dataclasses for User, Message, Conversation, Journal, EmotionScore.
These are intentionally minimal and serialization-friendly.
"""
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Optional
from enum import Enum


class ConversationStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now()
        )


@dataclass
class EmotionScore:
    """Represents detected emotions with confidence scores."""
    anxiety: float = 0.0
    depression: float = 0.0
    stress: float = 0.0
    sadness: float = 0.0
    happiness: float = 0.0
    relief: float = 0.0
    anger: float = 0.0
    contentment: float = 0.0

    def to_dict(self) -> dict:
        return {
            "anxiety": self.anxiety,
            "depression": self.depression,
            "stress": self.stress,
            "sadness": self.sadness,
            "happiness": self.happiness,
            "relief": self.relief,
            "anger": self.anger,
            "contentment": self.contentment
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EmotionScore":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class User:
    """Represents a user in the system."""
    id: Optional[int] = None
    phone_number: str = ""
    timezone: str = "America/New_York"
    preferred_call_time: time = field(default_factory=lambda: time(20, 0))
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Conversation:
    """Represents a conversation session."""
    id: Optional[int] = None
    user_id: int = 0
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    status: ConversationStatus = ConversationStatus.IN_PROGRESS
    raw_transcript: list[Message] = field(default_factory=list)
    twilio_call_sid: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str):
        """Add a message to the conversation."""
        self.raw_transcript.append(Message(role=role, content=content))

    def end_conversation(self):
        """Mark conversation as completed."""
        self.ended_at = datetime.now()
        self.status = ConversationStatus.COMPLETED
        if self.started_at:
            self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())


@dataclass
class Journal:
    """Represents a journal entry generated from a conversation."""
    id: Optional[int] = None
    user_id: int = 0
    conversation_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    duration_seconds: Optional[int] = None
    topics: list[str] = field(default_factory=list)
    detected_emotions: EmotionScore = field(default_factory=EmotionScore)
    markdown_file_path: str = ""
    vector_embedding_id: Optional[str] = None
    summary_text: Optional[str] = None
    updated_at: datetime = field(default_factory=datetime.now)



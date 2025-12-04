# utils/mock_data.py
"""
Mock data generator for testing without database connection.
"""
from datetime import datetime, time, timedelta
from typing import Optional
from models.entities import User, Conversation, Journal, Message, EmotionScore, ConversationStatus


class MockDataGenerator:
    """Generates mock data for testing without database."""
    
    # Static mock conversations for demo
    MOCK_USER_MESSAGES = [
        "Hey, today was pretty stressful. I had a big presentation at work.",
        "It went okay, but I was really nervous beforehand. I didn't sleep well last night.",
        "Yeah, I think the anxiety about work has been building up lately.",
        "That's a good point. Maybe I should try some relaxation techniques before bed.",
        "Thanks for listening. I feel a bit better after talking about it.",
    ]
    
    @staticmethod
    def create_mock_user(user_id: int = 1) -> User:
        """Create a mock user."""
        return User(
            id=user_id,
            phone_number="+1234567890",
            timezone="America/New_York",
            preferred_call_time=time(20, 0),
            is_active=True,
            created_at=datetime.now() - timedelta(days=30),
            updated_at=datetime.now()
        )
    
    @staticmethod
    def create_mock_conversation(user_id: int = 1, conversation_id: int = 1) -> Conversation:
        """Create a mock conversation with sample messages."""
        conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            started_at=datetime.now() - timedelta(minutes=10),
            status=ConversationStatus.IN_PROGRESS
        )
        
        # Add some mock messages
        conversation.add_message("assistant", "Hi there! How was your day today?")
        conversation.add_message("user", "It was okay, a bit stressful with work deadlines.")
        conversation.add_message("assistant", "I understand. Work deadlines can be really challenging. What's been on your mind?")
        
        return conversation
    
    @staticmethod
    def create_mock_journal(user_id: int = 1, journal_id: int = 1) -> Journal:
        """Create a mock journal entry."""
        return Journal(
            id=journal_id,
            user_id=user_id,
            conversation_id=1,
            created_at=datetime.now() - timedelta(days=1),
            duration_seconds=600,
            topics=["work", "stress", "sleep", "anxiety"],
            detected_emotions=EmotionScore(
                anxiety=0.65,
                stress=0.70,
                sadness=0.30,
                relief=0.45,
                happiness=0.25
            ),
            markdown_file_path="/journals/2025-01-15/journal_user1_abc123.md",
            vector_embedding_id="vec_emb_001",
            summary_text="Had a stressful day due to work presentation. Felt anxious beforehand but it went well. Discussed the importance of sleep and relaxation techniques."
        )
    
    @staticmethod
    def get_sample_rag_context() -> str:
        """Get sample RAG context from 'past journals'."""
        return """[2025-01-14]: User discussed feeling overwhelmed with work projects. 
Mentioned difficulty sleeping due to thinking about deadlines. 
Expressed interest in finding better work-life balance.

[2025-01-12]: User had a positive day, went for a walk which helped clear their mind. 
Talked about the importance of exercise for mental health.
Mentioned wanting to make walking a daily habit."""
    
    @staticmethod
    def get_mock_emotion_analysis() -> dict:
        """Get mock emotion analysis results."""
        return {
            "anxiety": 0.45,
            "depression": 0.15,
            "stress": 0.60,
            "sadness": 0.25,
            "happiness": 0.35,
            "relief": 0.40,
            "anger": 0.10,
            "contentment": 0.30
        }
    
    @staticmethod
    def get_mock_topics() -> list[str]:
        """Get mock extracted topics."""
        return ["work", "stress", "presentation", "sleep", "anxiety", "relaxation"]


class MockUserDAO:
    """Mock UserDAO for testing without database."""
    
    def __init__(self):
        self._users = {
            1: MockDataGenerator.create_mock_user(1)
        }
        self._next_id = 2
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)
    
    def create(self, user: User) -> User:
        user.id = self._next_id
        self._users[user.id] = user
        self._next_id += 1
        return user
    
    def get_all(self, active_only: bool = False) -> list[User]:
        users = list(self._users.values())
        if active_only:
            users = [u for u in users if u.is_active]
        return users


class MockConversationDAO:
    """Mock ConversationDAO for testing without database."""
    
    def __init__(self):
        self._conversations = {}
        self._next_id = 1
    
    def create(self, conversation: Conversation) -> Conversation:
        conversation.id = self._next_id
        self._conversations[conversation.id] = conversation
        self._next_id += 1
        return conversation
    
    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        return self._conversations.get(conversation_id)
    
    def update(self, conversation: Conversation) -> Optional[Conversation]:
        if conversation.id in self._conversations:
            self._conversations[conversation.id] = conversation
            return conversation
        return None
    
    def complete_conversation(self, conversation_id: int) -> Optional[Conversation]:
        conv = self._conversations.get(conversation_id)
        if conv:
            conv.end_conversation()
            return conv
        return None


class MockJournalDAO:
    """Mock JournalDAO for testing without database."""
    
    def __init__(self):
        self._journals = {}
        self._next_id = 1
    
    def create(self, journal: Journal) -> Journal:
        journal.id = self._next_id
        self._journals[journal.id] = journal
        self._next_id += 1
        return journal
    
    def get_by_id(self, journal_id: int) -> Optional[Journal]:
        return self._journals.get(journal_id)
    
    def get_by_user_id(self, user_id: int, limit: int = 20) -> list[Journal]:
        journals = [j for j in self._journals.values() if j.user_id == user_id]
        return sorted(journals, key=lambda x: x.created_at, reverse=True)[:limit]

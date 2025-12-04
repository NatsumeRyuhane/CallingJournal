# conversation_api.py
"""
==============================================================================
CONVERSATION API - Simple Interface for Teammates
==============================================================================

Just import and call these 3 functions:

    from conversation_api import start_conversation, process_message, end_conversation

Usage:
    # 1. When call starts
    opening_message = start_conversation(phone_number="+1234567890")

    # 2. When user speaks (after STT)
    ai_response = process_message("I had a stressful day")

    # 3. When call ends
    result = end_conversation()

That's it! Everything else (LLM, RAG, database, journal generation) is handled automatically.

==============================================================================
"""

from db.connection import get_db_connection
from dao.user_dao import UserDAO
from dao.conversation_dao import ConversationDAO
from dao.journal_dao import JournalDAO
from services.llm_service import LLMService
from services.embedding_service import EmbeddingService
from services.journal_service import JournalService
from services.conversation_service import ConversationService

# ==============================================================================
# Initialize services (happens once when module is imported)
# ==============================================================================

_db = get_db_connection()
_user_dao = UserDAO(_db)
_conversation_dao = ConversationDAO(_db)
_journal_dao = JournalDAO(_db)
_llm_service = LLMService()
_embedding_service = EmbeddingService()
_journal_service = JournalService(
    journal_dao=_journal_dao,
    llm_service=_llm_service,
    embedding_service=_embedding_service
)
_conversation_service = ConversationService(
    user_dao=_user_dao,
    conversation_dao=_conversation_dao,
    llm_service=_llm_service,
    embedding_service=_embedding_service,
    journal_service=_journal_service
)


# ==============================================================================
# 3 SIMPLE FUNCTIONS FOR YOUR TEAMMATES
# ==============================================================================

def start_conversation(phone_number: str = None, user_id: int = None, twilio_call_sid: str = None) -> str:
    """
    Start a new conversation.

    Call this when: Twilio call starts / user picks up

    Args:
        phone_number: User's phone number (use this OR user_id)
        user_id: User's database ID (use this OR phone_number)
        twilio_call_sid: Optional Twilio call SID for tracking

    Returns:
        opening_message: Send this to TTS to greet the user

    Example:
        opening = start_conversation(phone_number="+1234567890")
        # opening = "Hi! How are you feeling today? Last time we talked about..."
        # → Send to TTS → Play to user
    """
    # Get user_id from phone if needed
    if phone_number and not user_id:
        user = _user_dao.get_by_phone(phone_number)
        if not user:
            raise ValueError(f"User not found with phone: {phone_number}")
        user_id = user.id

    if not user_id:
        raise ValueError("Must provide either phone_number or user_id")

    opening_message = _conversation_service.start_conversation(
        user_id=user_id,
        twilio_call_sid=twilio_call_sid
    )

    return opening_message


def process_message(text: str, stream: bool = False):
    """
    Process user's message and get AI response.

    Call this when: Speech-to-Text has transcribed user's audio

    Args:
        text: Transcribed text from user's speech
        stream: If True, returns a generator for streaming response

    Returns:
        If stream=False: AI response string
        If stream=True: Generator yielding response chunks

    Example (normal):
        response = process_message("I had a stressful day at work")
        # response = "I hear you. Work stress can be really challenging..."
        # → Send to TTS → Play to user

    Example (streaming):
        for chunk in process_message("I had a stressful day", stream=True):
            # Send each chunk to TTS immediately for faster response
            send_to_tts(chunk)
    """
    if stream:
        return _conversation_service.process_user_message_stream(text)
    else:
        return _conversation_service.process_user_message(text)


def end_conversation() -> dict:
    """
    End conversation and generate journal.

    Call this when: User hangs up / call ends

    This automatically:
        - Marks conversation as complete
        - Generates journal summary using LLM
        - Extracts topics (work, stress, family, etc.)
        - Analyzes emotions (anxiety, happiness, etc.)
        - Stores in Pinecone for future RAG
        - Saves everything to database

    Returns:
        dict with:
            - conversation_id: ID of the completed conversation
            - duration_seconds: How long the call lasted
            - journal_id: ID of generated journal
            - journal_path: Path to markdown file
            - topics: List of extracted topics
            - emotions: Dict of emotion scores

    Example:
        result = end_conversation()
        # result = {
        #     "conversation_id": 5,
        #     "duration_seconds": 480,
        #     "journal_id": 3,
        #     "journal_path": "/journals/2025-01-20/journal_user1_203045.md",
        #     "topics": ["work", "stress", "deadlines"],
        #     "emotions": {"stress": 0.7, "anxiety": 0.5, "relief": 0.3, ...}
        # }
    """
    return _conversation_service.end_conversation()


# ==============================================================================
# OPTIONAL: Helper functions your teammates might find useful
# ==============================================================================

def get_user_by_phone(phone_number: str):
    """Get user by phone number."""
    return _user_dao.get_by_phone(phone_number)


def get_user_journals(user_id: int, limit: int = 10):
    """Get user's recent journals."""
    return _journal_dao.get_by_user_id(user_id, limit)


def get_emotion_trends(user_id: int, days: int = 30):
    """Get user's average emotions over past N days."""
    return _journal_dao.get_emotion_averages(user_id, days)
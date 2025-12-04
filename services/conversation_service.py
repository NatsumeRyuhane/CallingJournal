# services/conversation_service.py
from datetime import datetime
from typing import Optional
from models.entities import User, Conversation, ConversationStatus, Message
from dao.user_dao import UserDAO
from dao.conversation_dao import ConversationDAO
from services.llm_service import LLMService
from services.embedding_service import EmbeddingService
from services.journal_service import JournalService


class ConversationService:
    """Service for managing conversation sessions."""
    
    def __init__(
        self,
        user_dao: Optional[UserDAO] = None,
        conversation_dao: Optional[ConversationDAO] = None,
        llm_service: Optional[LLMService] = None,
        embedding_service: Optional[EmbeddingService] = None,
        journal_service: Optional[JournalService] = None
    ):
        self.user_dao = user_dao or UserDAO()
        self.conversation_dao = conversation_dao or ConversationDAO()
        self.llm_service = llm_service or LLMService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.journal_service = journal_service or JournalService(
            llm_service=self.llm_service,
            embedding_service=self.embedding_service
        )
        
        self.current_conversation: Optional[Conversation] = None
        self.current_user: Optional[User] = None
    
    def start_conversation(self, user_id: int, twilio_call_sid: Optional[str] = None) -> str:
        """Start a new conversation session and return opening message."""
        # Get user
        self.current_user = self.user_dao.get_by_id(user_id)
        if not self.current_user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Clear LLM history for new conversation
        self.llm_service.clear_history()
        
        # Get RAG context from past journals
        rag_context = self.embedding_service.get_relevant_context(
            query="recent feelings and events",
            user_id=user_id,
            top_k=3
        )
        self.llm_service.set_rag_context(rag_context)
        
        # Create conversation record
        self.current_conversation = Conversation(
            user_id=user_id,
            started_at=datetime.now(),
            status=ConversationStatus.IN_PROGRESS,
            twilio_call_sid=twilio_call_sid
        )
        
        # Generate opening message
        opening_message = self.llm_service.get_opening_message(
            user_name="there",  # Could be personalized
            previous_context=rag_context if rag_context else None
        )
        
        # Add to transcript
        self.current_conversation.add_message("assistant", opening_message)
        
        # Save to database
        self.current_conversation = self.conversation_dao.create(self.current_conversation)
        
        return opening_message
    
    def process_user_message(self, message: str) -> str:
        """Process user message and return assistant response."""
        if not self.current_conversation:
            raise ValueError("No active conversation. Call start_conversation first.")
        
        # Add user message to transcript
        self.current_conversation.add_message("user", message)
        
        # Get LLM response
        response = self.llm_service.chat(message)
        
        # Add assistant response to transcript
        self.current_conversation.add_message("assistant", response)
        
        # Update conversation in database
        self.conversation_dao.update(self.current_conversation)
        
        return response
    
    def process_user_message_stream(self, message: str):
        """Process user message and stream assistant response."""
        if not self.current_conversation:
            raise ValueError("No active conversation. Call start_conversation first.")
        
        # Add user message to transcript
        self.current_conversation.add_message("user", message)
        
        # Stream LLM response
        full_response = ""
        for chunk in self.llm_service.chat_stream(message):
            full_response += chunk
            yield chunk
        
        # Add assistant response to transcript
        self.current_conversation.add_message("assistant", full_response)
        
        # Update conversation in database
        self.conversation_dao.update(self.current_conversation)
    
    def end_conversation(self) -> Optional[dict]:
        """End the current conversation and generate journal."""
        if not self.current_conversation:
            return None
        
        # Mark conversation as completed
        self.current_conversation = self.conversation_dao.complete_conversation(
            self.current_conversation.id
        )
        
        # Generate journal from conversation
        journal = None
        if len(self.current_conversation.raw_transcript) > 2:  # At least some actual conversation
            journal = self.journal_service.create_journal_from_conversation(
                self.current_conversation
            )
        
        result = {
            "conversation_id": self.current_conversation.id,
            "duration_seconds": self.current_conversation.duration_seconds,
            "journal_id": journal.id if journal else None,
            "journal_path": journal.markdown_file_path if journal else None
        }
        
        # Clear current session
        self.current_conversation = None
        self.current_user = None
        self.llm_service.clear_history()
        
        return result
    
    def get_conversation_history(self) -> list[dict]:
        """Get current conversation history."""
        if not self.current_conversation:
            return []
        return [msg.to_dict() for msg in self.current_conversation.raw_transcript]
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """Delete conversations older than specified days."""
        return self.conversation_dao.delete_expired(days)

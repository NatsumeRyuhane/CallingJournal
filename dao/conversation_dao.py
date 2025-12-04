# dao/conversation_dao.py
import json
from typing import Optional
from datetime import datetime, timedelta
from db.connection import DatabaseConnection, get_db_connection
from models.entities import Conversation, ConversationStatus, Message


class ConversationDAO:
    """Data Access Object for Conversation entity."""
    
    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or get_db_connection()
    
    # ==================== CREATE ====================
    
    def create(self, conversation: Conversation) -> Conversation:
        """Create a new conversation and return with generated ID."""
        transcript_json = json.dumps([m.to_dict() for m in conversation.raw_transcript])
        
        query = """
            INSERT INTO conversations (user_id, started_at, ended_at, duration_seconds, 
                                       status, raw_transcript, twilio_call_sid)
            VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s::jsonb, %s)
            RETURNING *
        """
        result = self.db.execute_returning(query, (
            conversation.user_id,
            conversation.ended_at,
            conversation.duration_seconds,
            conversation.status.value,
            transcript_json,
            conversation.twilio_call_sid
        ))
        return self._map_to_conversation(result)
    
    # ==================== READ ====================
    
    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID."""
        query = "SELECT * FROM conversations WHERE id = %s"
        result = self.db.execute_one(query, (conversation_id,))
        return self._map_to_conversation(result) if result else None
    
    def get_by_user_id(self, user_id: int, limit: int = 10) -> list[Conversation]:
        """Get recent conversations for a user."""
        query = """
            SELECT * FROM conversations 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        results = self.db.execute(query, (user_id, limit))
        return [self._map_to_conversation(row) for row in results]
    
    def get_by_status(self, status: ConversationStatus) -> list[Conversation]:
        """Get conversations by status."""
        query = "SELECT * FROM conversations WHERE status = %s ORDER BY created_at DESC"
        results = self.db.execute(query, (status.value,))
        return [self._map_to_conversation(row) for row in results]
    
    def get_by_twilio_sid(self, twilio_call_sid: str) -> Optional[Conversation]:
        """Get conversation by Twilio call SID."""
        query = "SELECT * FROM conversations WHERE twilio_call_sid = %s"
        result = self.db.execute_one(query, (twilio_call_sid,))
        return self._map_to_conversation(result) if result else None
    
    def get_in_progress_by_user(self, user_id: int) -> Optional[Conversation]:
        """Get current in-progress conversation for a user."""
        query = """
            SELECT * FROM conversations 
            WHERE user_id = %s AND status = 'in_progress'
            ORDER BY created_at DESC
            LIMIT 1
        """
        result = self.db.execute_one(query, (user_id,))
        return self._map_to_conversation(result) if result else None
    
    def get_expired_conversations(self, days: int = 30) -> list[Conversation]:
        """Get conversations older than specified days (for cleanup)."""
        cutoff_date = datetime.now() - timedelta(days=days)
        query = """
            SELECT * FROM conversations 
            WHERE created_at < %s 
            ORDER BY created_at ASC
        """
        results = self.db.execute(query, (cutoff_date,))
        return [self._map_to_conversation(row) for row in results]
    
    # ==================== UPDATE ====================
    
    def update(self, conversation: Conversation) -> Optional[Conversation]:
        """Update conversation details."""
        transcript_json = json.dumps([m.to_dict() for m in conversation.raw_transcript])
        
        query = """
            UPDATE conversations 
            SET ended_at = %s, duration_seconds = %s, status = %s, raw_transcript = %s::jsonb
            WHERE id = %s
            RETURNING *
        """
        result = self.db.execute_returning(query, (
            conversation.ended_at,
            conversation.duration_seconds,
            conversation.status.value,
            transcript_json,
            conversation.id
        ))
        return self._map_to_conversation(result) if result else None
    
    def update_transcript(self, conversation_id: int, messages: list[Message]) -> bool:
        """Update only the transcript of a conversation."""
        transcript_json = json.dumps([m.to_dict() for m in messages])
        
        query = """
            UPDATE conversations SET raw_transcript = %s::jsonb
            WHERE id = %s
            RETURNING id
        """
        result = self.db.execute_returning(query, (transcript_json, conversation_id))
        return result is not None
    
    def append_message(self, conversation_id: int, message: Message) -> bool:
        """Append a single message to conversation transcript."""
        message_json = json.dumps(message.to_dict())
        
        query = """
            UPDATE conversations 
            SET raw_transcript = raw_transcript || %s::jsonb
            WHERE id = %s
            RETURNING id
        """
        result = self.db.execute_returning(query, (message_json, conversation_id))
        return result is not None
    
    def complete_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Mark conversation as completed and set end time."""
        query = """
            UPDATE conversations 
            SET status = 'completed', 
                ended_at = CURRENT_TIMESTAMP,
                duration_seconds = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - started_at))::int
            WHERE id = %s
            RETURNING *
        """
        result = self.db.execute_returning(query, (conversation_id,))
        return self._map_to_conversation(result) if result else None
    
    def fail_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Mark conversation as failed."""
        query = """
            UPDATE conversations 
            SET status = 'failed', ended_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """
        result = self.db.execute_returning(query, (conversation_id,))
        return self._map_to_conversation(result) if result else None
    
    # ==================== DELETE ====================
    
    def delete(self, conversation_id: int) -> bool:
        """Delete a conversation."""
        query = "DELETE FROM conversations WHERE id = %s RETURNING id"
        result = self.db.execute_returning(query, (conversation_id,))
        return result is not None
    
    def delete_expired(self, days: int = 30) -> int:
        """Delete conversations older than specified days. Returns count deleted."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # First count how many will be deleted
        count_query = "SELECT COUNT(*) as count FROM conversations WHERE created_at < %s"
        count_result = self.db.execute_one(count_query, (cutoff_date,))
        count = count_result["count"] if count_result else 0
        
        # Then delete
        delete_query = "DELETE FROM conversations WHERE created_at < %s"
        self.db.execute(delete_query, (cutoff_date,))
        
        return count
    
    # ==================== HELPER ====================
    
    def _map_to_conversation(self, row: dict) -> Conversation:
        """Map database row to Conversation entity."""
        raw_transcript = []
        if row.get("raw_transcript"):
            transcript_data = row["raw_transcript"]
            if isinstance(transcript_data, str):
                transcript_data = json.loads(transcript_data)
            raw_transcript = [Message.from_dict(m) for m in transcript_data]
        
        return Conversation(
            id=row["id"],
            user_id=row["user_id"],
            started_at=row["started_at"],
            ended_at=row.get("ended_at"),
            duration_seconds=row.get("duration_seconds"),
            status=ConversationStatus(row["status"]),
            raw_transcript=raw_transcript,
            twilio_call_sid=row.get("twilio_call_sid"),
            created_at=row["created_at"]
        )

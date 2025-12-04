# dao/journal_dao.py
import json
from typing import Optional
from datetime import datetime, timedelta
from db.connection import DatabaseConnection, get_db_connection
from models.entities import Journal, EmotionScore


class JournalDAO:
    """Data Access Object for Journal entity."""
    
    def __init__(self, db: Optional[DatabaseConnection] = None):
        self.db = db or get_db_connection()
    
    # ==================== CREATE ====================
    
    def create(self, journal: Journal) -> Journal:
        """Create a new journal entry and return with generated ID."""
        topics_json = json.dumps(journal.topics)
        emotions_json = json.dumps(journal.detected_emotions.to_dict())
        
        query = """
            INSERT INTO journals (user_id, conversation_id, duration_seconds, topics, 
                                  detected_emotions, markdown_file_path, vector_embedding_id, summary_text)
            VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s)
            RETURNING *
        """
        result = self.db.execute_returning(query, (
            journal.user_id,
            journal.conversation_id,
            journal.duration_seconds,
            topics_json,
            emotions_json,
            journal.markdown_file_path,
            journal.vector_embedding_id,
            journal.summary_text
        ))
        return self._map_to_journal(result)
    
    # ==================== READ ====================
    
    def get_by_id(self, journal_id: int) -> Optional[Journal]:
        """Get journal by ID."""
        query = "SELECT * FROM journals WHERE id = %s"
        result = self.db.execute_one(query, (journal_id,))
        return self._map_to_journal(result) if result else None
    
    def get_by_user_id(self, user_id: int, limit: int = 20) -> list[Journal]:
        """Get recent journals for a user."""
        query = """
            SELECT * FROM journals 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        results = self.db.execute(query, (user_id, limit))
        return [self._map_to_journal(row) for row in results]
    
    def get_by_conversation_id(self, conversation_id: int) -> Optional[Journal]:
        """Get journal by associated conversation."""
        query = "SELECT * FROM journals WHERE conversation_id = %s"
        result = self.db.execute_one(query, (conversation_id,))
        return self._map_to_journal(result) if result else None
    
    def get_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime) -> list[Journal]:
        """Get journals within a date range for a user."""
        query = """
            SELECT * FROM journals 
            WHERE user_id = %s AND created_at BETWEEN %s AND %s
            ORDER BY created_at DESC
        """
        results = self.db.execute(query, (user_id, start_date, end_date))
        return [self._map_to_journal(row) for row in results]
    
    def get_by_topic(self, user_id: int, topic: str) -> list[Journal]:
        """Get journals containing a specific topic for a user."""
        query = """
            SELECT * FROM journals 
            WHERE user_id = %s AND topics ? %s
            ORDER BY created_at DESC
        """
        results = self.db.execute(query, (user_id, topic))
        return [self._map_to_journal(row) for row in results]
    
    def get_by_topics(self, user_id: int, topics: list[str]) -> list[Journal]:
        """Get journals containing any of the specified topics."""
        topics_json = json.dumps(topics)
        query = """
            SELECT * FROM journals 
            WHERE user_id = %s AND topics ?| %s::text[]
            ORDER BY created_at DESC
        """
        results = self.db.execute(query, (user_id, topics))
        return [self._map_to_journal(row) for row in results]
    
    def get_by_high_emotion(self, user_id: int, emotion: str, threshold: float = 0.5) -> list[Journal]:
        """Get journals where a specific emotion exceeds threshold."""
        query = f"""
            SELECT * FROM journals 
            WHERE user_id = %s 
            AND (detected_emotions->>%s)::float > %s
            ORDER BY created_at DESC
        """
        results = self.db.execute(query, (user_id, emotion, threshold))
        return [self._map_to_journal(row) for row in results]
    
    def get_by_vector_ids(self, vector_ids: list[str]) -> list[Journal]:
        """Get journals by their vector embedding IDs (for RAG retrieval)."""
        placeholders = ','.join(['%s'] * len(vector_ids))
        query = f"""
            SELECT * FROM journals 
            WHERE vector_embedding_id IN ({placeholders})
            ORDER BY created_at DESC
        """
        results = self.db.execute(query, tuple(vector_ids))
        return [self._map_to_journal(row) for row in results]
    
    def get_recent_summaries(self, user_id: int, days: int = 7) -> list[dict]:
        """Get recent journal summaries for RAG context."""
        cutoff_date = datetime.now() - timedelta(days=days)
        query = """
            SELECT id, created_at, topics, summary_text, vector_embedding_id
            FROM journals 
            WHERE user_id = %s AND created_at > %s
            ORDER BY created_at DESC
        """
        return self.db.execute(query, (user_id, cutoff_date))
    
    def get_all_vector_ids_for_user(self, user_id: int) -> list[str]:
        """Get all vector embedding IDs for a user (for vector DB queries)."""
        query = """
            SELECT vector_embedding_id FROM journals 
            WHERE user_id = %s AND vector_embedding_id IS NOT NULL
        """
        results = self.db.execute(query, (user_id,))
        return [row["vector_embedding_id"] for row in results]
    
    # ==================== UPDATE ====================
    
    def update(self, journal: Journal) -> Optional[Journal]:
        """Update journal details."""
        topics_json = json.dumps(journal.topics)
        emotions_json = json.dumps(journal.detected_emotions.to_dict())
        
        query = """
            UPDATE journals 
            SET topics = %s::jsonb, detected_emotions = %s::jsonb, 
                markdown_file_path = %s, vector_embedding_id = %s, 
                summary_text = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """
        result = self.db.execute_returning(query, (
            topics_json,
            emotions_json,
            journal.markdown_file_path,
            journal.vector_embedding_id,
            journal.summary_text,
            journal.id
        ))
        return self._map_to_journal(result) if result else None
    
    def update_vector_embedding_id(self, journal_id: int, vector_embedding_id: str) -> bool:
        """Update the vector embedding ID for a journal."""
        query = """
            UPDATE journals 
            SET vector_embedding_id = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id
        """
        result = self.db.execute_returning(query, (vector_embedding_id, journal_id))
        return result is not None
    
    def update_emotions(self, journal_id: int, emotions: EmotionScore) -> bool:
        """Update detected emotions for a journal."""
        emotions_json = json.dumps(emotions.to_dict())
        query = """
            UPDATE journals 
            SET detected_emotions = %s::jsonb, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id
        """
        result = self.db.execute_returning(query, (emotions_json, journal_id))
        return result is not None
    
    def add_topic(self, journal_id: int, topic: str) -> bool:
        """Add a topic to journal's topic list."""
        query = """
            UPDATE journals 
            SET topics = topics || %s::jsonb, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND NOT topics ? %s
            RETURNING id
        """
        topic_json = json.dumps([topic])
        result = self.db.execute_returning(query, (topic_json, journal_id, topic))
        return result is not None
    
    # ==================== DELETE ====================
    
    def delete(self, journal_id: int) -> bool:
        """Delete a journal entry."""
        query = "DELETE FROM journals WHERE id = %s RETURNING id"
        result = self.db.execute_returning(query, (journal_id,))
        return result is not None
    
    def delete_by_user_id(self, user_id: int) -> int:
        """Delete all journals for a user. Returns count deleted."""
        count_query = "SELECT COUNT(*) as count FROM journals WHERE user_id = %s"
        count_result = self.db.execute_one(count_query, (user_id,))
        count = count_result["count"] if count_result else 0
        
        delete_query = "DELETE FROM journals WHERE user_id = %s"
        self.db.execute(delete_query, (user_id,))
        
        return count
    
    # ==================== AGGREGATIONS ====================
    
    def get_topic_frequency(self, user_id: int, limit: int = 10) -> list[dict]:
        """Get most frequent topics for a user."""
        query = """
            SELECT topic, COUNT(*) as frequency
            FROM journals, jsonb_array_elements_text(topics) as topic
            WHERE user_id = %s
            GROUP BY topic
            ORDER BY frequency DESC
            LIMIT %s
        """
        return self.db.execute(query, (user_id, limit))
    
    def get_emotion_averages(self, user_id: int, days: int = 30) -> dict:
        """Get average emotion scores over a period."""
        cutoff_date = datetime.now() - timedelta(days=days)
        query = """
            SELECT 
                AVG((detected_emotions->>'anxiety')::float) as avg_anxiety,
                AVG((detected_emotions->>'depression')::float) as avg_depression,
                AVG((detected_emotions->>'stress')::float) as avg_stress,
                AVG((detected_emotions->>'happiness')::float) as avg_happiness,
                AVG((detected_emotions->>'sadness')::float) as avg_sadness
            FROM journals 
            WHERE user_id = %s AND created_at > %s
        """
        result = self.db.execute_one(query, (user_id, cutoff_date))
        return dict(result) if result else {}
    
    def count_journals_by_user(self, user_id: int) -> int:
        """Count total journals for a user."""
        query = "SELECT COUNT(*) as count FROM journals WHERE user_id = %s"
        result = self.db.execute_one(query, (user_id,))
        return result["count"] if result else 0
    
    # ==================== HELPER ====================
    
    def _map_to_journal(self, row: dict) -> Journal:
        """Map database row to Journal entity."""
        topics = row.get("topics", [])
        if isinstance(topics, str):
            topics = json.loads(topics)
        
        emotions_data = row.get("detected_emotions", {})
        if isinstance(emotions_data, str):
            emotions_data = json.loads(emotions_data)
        
        return Journal(
            id=row["id"],
            user_id=row["user_id"],
            conversation_id=row.get("conversation_id"),
            created_at=row["created_at"],
            duration_seconds=row.get("duration_seconds"),
            topics=topics,
            detected_emotions=EmotionScore.from_dict(emotions_data),
            markdown_file_path=row["markdown_file_path"],
            vector_embedding_id=row.get("vector_embedding_id"),
            summary_text=row.get("summary_text"),
            updated_at=row["updated_at"]
        )

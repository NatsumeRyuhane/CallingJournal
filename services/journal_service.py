# services/journal_service.py
import os
from datetime import datetime
from typing import Optional
from models.entities import Journal, Conversation, EmotionScore
from dao.journal_dao import JournalDAO
from services.llm_service import LLMService
from services.embedding_service import EmbeddingService


class JournalService:
    """Service for journal-related business logic."""
    # use absolute path for markdown file storage
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    JOURNALS_BASE_PATH = os.path.join(BASE_DIR, "journals")
    
    def __init__(
        self,
        journal_dao: Optional[JournalDAO] = None,
        llm_service: Optional[LLMService] = None,
        embedding_service: Optional[EmbeddingService] = None
    ):
        self.journal_dao = journal_dao or JournalDAO()
        self.llm_service = llm_service or LLMService()
        self.embedding_service = embedding_service or EmbeddingService()
    
    def create_journal_from_conversation(self, conversation: Conversation) -> Journal:
        """Create a complete journal entry from a finished conversation."""
        # 1. Generate transcript for LLM
        transcript = [msg.to_dict() for msg in conversation.raw_transcript]

        transcript_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in transcript
        ])
        
        # 2. Generate summary using LLM
        summary_text = self.llm_service.generate_journal_summary(transcript)
        
        # 3. Extract topics
        topics = self.llm_service.extract_topics(summary_text)
        
        # 4. Analyze emotions
        emotions_dict = self.llm_service.analyze_emotions(transcript_text)
        emotions = EmotionScore.from_dict(emotions_dict)
        
        # 5. Generate markdown file
        markdown_content = self._generate_markdown(
            summary_text=summary_text,
            topics=topics,
            emotions=emotions,
            conversation=conversation
        )
        markdown_path = self._save_markdown(
            user_id=conversation.user_id,
            content=markdown_content
        )
        
        # 6. Store embedding
        vector_id = self.embedding_service.store_embedding(
            text=summary_text,
            metadata={
                "user_id": conversation.user_id,
                "conversation_id": conversation.id,
                "topics": topics,
                "created_at": datetime.now().isoformat()
            }
        )
        
        # 7. Create journal entity
        journal = Journal(
            user_id=conversation.user_id,
            conversation_id=conversation.id,
            duration_seconds=conversation.duration_seconds,
            topics=topics,
            detected_emotions=emotions,
            markdown_file_path=markdown_path,
            vector_embedding_id=vector_id,
            summary_text=summary_text
        )
        
        # 8. Save to database
        return self.journal_dao.create(journal)
    
    def _generate_markdown(
        self,
        summary_text: str,
        topics: list[str],
        emotions: EmotionScore,
        conversation: Conversation
    ) -> str:
        """Generate markdown content for journal file."""
        date_str = datetime.now().strftime("%B %d, %Y, %I:%M %p")
        topics_str = ", ".join(topics) if topics else "General reflection"
        
        # Find top emotions
        emotions_dict = emotions.to_dict()
        top_emotions = sorted(emotions_dict.items(), key=lambda x: x[1], reverse=True)[:3]
        emotions_str = ", ".join([f"{e[0]} ({e[1]:.0%})" for e in top_emotions if e[1] > 0])
        
        markdown = f"""# Journal Entry - {date_str}

                    ## Session Summary

                    {summary_text}

                ## Topics Discussed
                
                {topics_str}
                
                ## Emotional State
                
                {emotions_str if emotions_str else "Neutral"}
                
                ---
                
                *Duration: {conversation.duration_seconds if conversation.duration_seconds else 0} seconds*
                """
        return markdown
    
    def _save_markdown(self, user_id: int, content: str) -> str:
        """Save markdown content to file and return path."""
        # Create directory structure
        date_str = datetime.now().strftime("%Y-%m-%d")
        dir_path = os.path.join(self.JOURNALS_BASE_PATH, date_str)
        os.makedirs(dir_path, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"journal_user{user_id}_{timestamp}.md"
        file_path = os.path.join(dir_path, filename)
        
        # Write file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return file_path
    
    def get_user_journals(self, user_id: int, limit: int = 20) -> list[Journal]:
        """Get recent journals for a user."""
        return self.journal_dao.get_by_user_id(user_id, limit)
    
    def get_journals_by_topic(self, user_id: int, topic: str) -> list[Journal]:
        """Get journals containing a specific topic."""
        return self.journal_dao.get_by_topic(user_id, topic)
    
    def get_emotion_trends(self, user_id: int, days: int = 30) -> dict:
        """Get emotion averages over a period."""
        return self.journal_dao.get_emotion_averages(user_id, days)
    
    def search_journals(self, user_id: int, query: str, top_k: int = 5) -> list[dict]:
        """Search journals using semantic similarity."""
        return self.embedding_service.search_similar(query, user_id, top_k)
    
    def read_journal_markdown(self, journal: Journal) -> Optional[str]:
        """Read the markdown content of a journal."""
        if os.path.exists(journal.markdown_file_path):
            with open(journal.markdown_file_path, "r", encoding="utf-8") as f:
                return f.read()
        return None

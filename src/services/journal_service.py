"""
Journal service module for managing conversation logs and journal generation.
Handles conversation storage, summarization, and knowledge extraction.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.db_models import Call, Conversation, Journal, KnowledgeBase, ConversationTurn
from src.services.llm_service import ILLMService, llm_service as default_llm_service


class JournalService:
    """Service for managing journal entries and conversation logs."""
    
    def __init__(self, llm_service: Optional[ILLMService] = None):
        """
        Initialize journal service.
        
        Args:
            llm_service: LLM service instance (uses default if not provided)
        """
        self.llm_service = llm_service or default_llm_service
    
    async def create_conversation_log(
        self,
        db: AsyncSession,
        call_id: int,
        conversations: List[Dict[str, str]]
    ) -> List[Conversation]:
        """
        Create conversation log entries from a call.
        
        Args:
            db: Database session
            call_id: Call ID
            conversations: List of conversation dicts with 'turn' and 'content'
            
        Returns:
            List of created Conversation objects
        """
        conversation_objects = []
        for idx, conv in enumerate(conversations):
            conversation = Conversation(
                call_id=call_id,
                turn=ConversationTurn(conv["turn"]),
                content=conv["content"],
                order_index=idx,
                metadata=conv.get("metadata")
            )
            db.add(conversation)
            conversation_objects.append(conversation)
        
        await db.flush()
        return conversation_objects
    
    async def get_conversation_history(
        self,
        db: AsyncSession,
        call_id: int
    ) -> List[Conversation]:
        """
        Get conversation history for a call.
        
        Args:
            db: Database session
            call_id: Call ID
            
        Returns:
            List of Conversation objects ordered by index
        """
        result = await db.execute(
            select(Conversation)
            .where(Conversation.call_id == call_id)
            .order_by(Conversation.order_index)
        )
        return result.scalars().all()
    
    async def generate_journal_from_call(
        self,
        db: AsyncSession,
        call_id: int,
        user_id: int,
        focus: Optional[str] = None
    ) -> Journal:
        """
        Generate a journal entry from a call conversation.
        
        Args:
            db: Database session
            call_id: Call ID
            user_id: User ID
            focus: Optional focus area for summarization
            
        Returns:
            Created Journal object
        """
        # Get conversation history
        conversations = await self.get_conversation_history(db, call_id)
        
        # Build full conversation text
        conversation_text = "\n".join([
            f"{conv.turn.value.upper()}: {conv.content}"
            for conv in conversations
        ])
        
        # Generate summary using LLM
        summary_data = await self.llm_service.summarize_conversation(
            conversation=conversation_text,
            focus=focus
        )
        
        # Create journal entry
        journal = Journal(
            user_id=user_id,
            call_id=call_id,
            title=summary_data.get("title", f"Call on {datetime.now(timezone.utc).date()}"),
            summary=summary_data.get("summary", ""),
            key_points=summary_data.get("key_points", []),
            action_items=summary_data.get("action_items", []),
            tags=summary_data.get("topics", []),
            full_content=conversation_text,
            entities=summary_data.get("entities", []),
            topics=summary_data.get("topics", []),
            sentiment=summary_data.get("sentiment", "neutral")
        )
        
        db.add(journal)
        await db.flush()
        
        return journal
    
    async def get_journal(
        self,
        db: AsyncSession,
        journal_id: int
    ) -> Optional[Journal]:
        """
        Get a journal entry by ID.
        
        Args:
            db: Database session
            journal_id: Journal ID
            
        Returns:
            Journal object or None
        """
        result = await db.execute(
            select(Journal).where(Journal.id == journal_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_journals(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Journal]:
        """
        Get journals for a user.
        
        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of journals to return
            offset: Offset for pagination
            
        Returns:
            List of Journal objects
        """
        result = await db.execute(
            select(Journal)
            .where(Journal.user_id == user_id)
            .order_by(Journal.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def search_journals(
        self,
        db: AsyncSession,
        user_id: int,
        query: str,
        tags: Optional[List[str]] = None
    ) -> List[Journal]:
        """
        Search journals by content or tags.
        
        Args:
            db: Database session
            user_id: User ID
            query: Search query
            tags: Optional list of tags to filter by
            
        Returns:
            List of matching Journal objects
        """
        conditions = [Journal.user_id == user_id]
        
        # Text search (simple implementation, can be enhanced with FTS)
        if query:
            conditions.append(
                Journal.summary.ilike(f"%{query}%") |
                Journal.full_content.ilike(f"%{query}%")
            )
        
        # Tag filter
        if tags:
            # This is a simplified version; proper JSON querying depends on DB
            for tag in tags:
                conditions.append(Journal.tags.contains([tag]))
        
        result = await db.execute(
            select(Journal)
            .where(and_(*conditions))
            .order_by(Journal.created_at.desc())
        )
        return result.scalars().all()
    
    async def extract_knowledge(
        self,
        db: AsyncSession,
        journal_id: int,
        user_id: int
    ) -> List[KnowledgeBase]:
        """
        Extract domain knowledge from a journal entry.
        
        Args:
            db: Database session
            journal_id: Journal ID
            user_id: User ID
            
        Returns:
            List of created KnowledgeBase objects
        """
        # Get journal
        journal = await self.get_journal(db, journal_id)
        if not journal:
            return []
        
        # Extract entities and topics (already done during journal creation)
        knowledge_items = []
        
        # Create knowledge base entries from topics and key points
        if journal.topics:
            for topic in journal.topics:
                knowledge = KnowledgeBase(
                    user_id=user_id,
                    topic=topic,
                    content=journal.summary,
                    source_journal_ids=[journal_id],
                    category="topic",
                    keywords=journal.tags or [],
                    confidence_score=0.8
                )
                db.add(knowledge)
                knowledge_items.append(knowledge)
        
        # Create knowledge from entities
        if journal.entities:
            for entity in journal.entities[:5]:  # Limit to top 5 entities
                if isinstance(entity, dict):
                    knowledge = KnowledgeBase(
                        user_id=user_id,
                        topic=entity.get("value", ""),
                        content=f"Entity: {entity.get('type', '')} - {entity.get('value', '')}",
                        source_journal_ids=[journal_id],
                        category="entity",
                        keywords=[entity.get("type", "")],
                        confidence_score=0.7
                    )
                    db.add(knowledge)
                    knowledge_items.append(knowledge)
        
        await db.flush()
        return knowledge_items
    
    async def get_user_knowledge(
        self,
        db: AsyncSession,
        user_id: int,
        topic: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[KnowledgeBase]:
        """
        Get knowledge base entries for a user.
        
        Args:
            db: Database session
            user_id: User ID
            topic: Optional topic filter
            category: Optional category filter
            limit: Maximum number of entries to return
            
        Returns:
            List of KnowledgeBase objects
        """
        conditions = [KnowledgeBase.user_id == user_id]
        
        if topic:
            conditions.append(KnowledgeBase.topic.ilike(f"%{topic}%"))
        
        if category:
            conditions.append(KnowledgeBase.category == category)
        
        result = await db.execute(
            select(KnowledgeBase)
            .where(and_(*conditions))
            .order_by(KnowledgeBase.confidence_score.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_journal(
        self,
        db: AsyncSession,
        journal_id: int,
        updates: Dict[str, Any]
    ) -> Optional[Journal]:
        """
        Update a journal entry.
        
        Args:
            db: Database session
            journal_id: Journal ID
            updates: Dictionary of fields to update
            
        Returns:
            Updated Journal object or None
        """
        journal = await self.get_journal(db, journal_id)
        if not journal:
            return None
        
        for key, value in updates.items():
            if hasattr(journal, key):
                setattr(journal, key, value)
        
        journal.updated_at = datetime.utcnow()
        await db.flush()
        
        return journal
    
    async def delete_journal(
        self,
        db: AsyncSession,
        journal_id: int
    ) -> bool:
        """
        Delete a journal entry.
        
        Args:
            db: Database session
            journal_id: Journal ID
            
        Returns:
            True if deleted successfully
        """
        journal = await self.get_journal(db, journal_id)
        if not journal:
            return False
        
        await db.delete(journal)
        await db.flush()
        
        return True


# Default journal service instance
journal_service = JournalService()

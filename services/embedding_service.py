# services/embedding_service.py
import uuid
from typing import Optional
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from config.settings import get_settings


class EmbeddingService:
    """Service for generating and managing text embeddings with Pinecone."""

    # Embedding dimension for text-embedding-3-small
    EMBEDDING_DIMENSION = 1536

    def __init__(self):
        self.settings = get_settings()

        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            model=self.settings.openai_embedding_model,
            api_key=self.settings.openai_api_key
        )

        # Initialize Pinecone
        self._pinecone_client = None
        self._index = None
        self._mock_vector_store: dict[str, dict] = {}

        if self.settings.pinecone_api_key:
            self._init_pinecone()
        else:
            print("Warning: PINECONE_API_KEY not set. Using mock vector store.")

    def _init_pinecone(self):
        """Initialize Pinecone client and index."""
        try:
            # Initialize Pinecone client
            self._pinecone_client = Pinecone(api_key=self.settings.pinecone_api_key)

            index_name = self.settings.pinecone_index_name

            # Check if index exists, create if not
            existing_indexes = [idx.name for idx in self._pinecone_client.list_indexes()]

            if index_name not in existing_indexes:
                print(f"Creating Pinecone index: {index_name}")
                self._pinecone_client.create_index(
                    name=index_name,
                    dimension=self.EMBEDDING_DIMENSION,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print(f"Index '{index_name}' created successfully.")

            # Connect to index
            self._index = self._pinecone_client.Index(index_name)
            print(f"Connected to Pinecone index: {index_name}")

        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            print("Falling back to mock vector store.")
            self._index = None

    @property
    def is_pinecone_enabled(self) -> bool:
        """Check if Pinecone is properly initialized."""
        return self._index is not None

    # ==================== EMBEDDING GENERATION ====================

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding vector for text."""
        return self.embeddings.embed_query(text)

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        return self.embeddings.embed_documents(texts)

    # ==================== VECTOR STORAGE (Pinecone) ====================

    def store_embedding(
            self,
            text: str,
            metadata: dict,
            embedding_id: Optional[str] = None
    ) -> str:
        """Store embedding in Pinecone vector database."""
        # Generate ID if not provided
        if embedding_id is None:
            embedding_id = f"vec_{uuid.uuid4().hex[:12]}"

        # Generate embedding
        vector = self.generate_embedding(text)

        # Add text to metadata for retrieval
        metadata_with_text = {
            **metadata,
            "text": text  # Store original text in metadata for retrieval
        }

        # Ensure all metadata values are compatible with Pinecone
        # Pinecone only supports str, int, float, bool, list of str
        clean_metadata = self._clean_metadata(metadata_with_text)

        if self.is_pinecone_enabled:
            # Store in Pinecone
            self._index.upsert(
                vectors=[
                    {
                        "id": embedding_id,
                        "values": vector,
                        "metadata": clean_metadata
                    }
                ]
            )
        else:
            # Fallback to mock store
            self._mock_vector_store[embedding_id] = {
                "id": embedding_id,
                "vector": vector,
                "metadata": clean_metadata
            }

        return embedding_id

    def store_embeddings_batch(
            self,
            items: list[dict]  # List of {"text": str, "metadata": dict, "id": Optional[str]}
    ) -> list[str]:
        """Store multiple embeddings in batch."""
        ids = []
        vectors_to_upsert = []

        # Generate all embeddings
        texts = [item["text"] for item in items]
        embeddings = self.generate_embeddings_batch(texts)

        for i, item in enumerate(items):
            embedding_id = item.get("id") or f"vec_{uuid.uuid4().hex[:12]}"
            ids.append(embedding_id)

            metadata_with_text = {
                **item["metadata"],
                "text": item["text"]
            }
            clean_metadata = self._clean_metadata(metadata_with_text)

            vectors_to_upsert.append({
                "id": embedding_id,
                "values": embeddings[i],
                "metadata": clean_metadata
            })

        if self.is_pinecone_enabled:
            # Batch upsert to Pinecone (max 100 at a time)
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self._index.upsert(vectors=batch)
        else:
            # Fallback to mock store
            for vec in vectors_to_upsert:
                self._mock_vector_store[vec["id"]] = {
                    "id": vec["id"],
                    "vector": vec["values"],
                    "metadata": vec["metadata"]
                }

        return ids

    # ==================== VECTOR SEARCH ====================

    def search_similar(
            self,
            query_text: str,
            user_id: int,
            top_k: int = 5
    ) -> list[dict]:
        """Search for similar embeddings filtered by user_id."""
        query_vector = self.generate_embedding(query_text)

        if self.is_pinecone_enabled:
            # Search in Pinecone with metadata filter
            results = self._index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter={"user_id": {"$eq": user_id}}
            )

            return [
                {
                    "id": match.id,
                    "text": match.metadata.get("text", ""),
                    "metadata": match.metadata,
                    "score": match.score
                }
                for match in results.matches
            ]
        else:
            # Fallback to mock implementation
            return self._mock_search_similar(query_vector, user_id, top_k)

    def search_similar_by_topics(
            self,
            query_text: str,
            user_id: int,
            topics: list[str],
            top_k: int = 5
    ) -> list[dict]:
        """Search for similar embeddings filtered by user_id and topics."""
        query_vector = self.generate_embedding(query_text)

        if self.is_pinecone_enabled:
            # Search with topic filter
            results = self._index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter={
                    "$and": [
                        {"user_id": {"$eq": user_id}},
                        {"topics": {"$in": topics}}
                    ]
                }
            )

            return [
                {
                    "id": match.id,
                    "text": match.metadata.get("text", ""),
                    "metadata": match.metadata,
                    "score": match.score
                }
                for match in results.matches
            ]
        else:
            return self._mock_search_similar(query_vector, user_id, top_k)

    # ==================== DELETE OPERATIONS ====================

    def delete_embedding(self, embedding_id: str) -> bool:
        """Delete embedding from vector store."""
        try:
            if self.is_pinecone_enabled:
                self._index.delete(ids=[embedding_id])
            else:
                if embedding_id in self._mock_vector_store:
                    del self._mock_vector_store[embedding_id]
            return True
        except Exception as e:
            print(f"Error deleting embedding {embedding_id}: {e}")
            return False

    def delete_embeddings_by_user(self, user_id: int) -> bool:
        """Delete all embeddings for a user."""
        try:
            if self.is_pinecone_enabled:
                # Pinecone requires deleting by ID, so we need to query first
                # Use a dummy vector to find all user's embeddings
                dummy_vector = [0.0] * self.EMBEDDING_DIMENSION
                results = self._index.query(
                    vector=dummy_vector,
                    top_k=10000,  # Get all
                    include_metadata=False,
                    filter={"user_id": {"$eq": user_id}}
                )

                if results.matches:
                    ids_to_delete = [match.id for match in results.matches]
                    # Delete in batches
                    batch_size = 1000
                    for i in range(0, len(ids_to_delete), batch_size):
                        batch = ids_to_delete[i:i + batch_size]
                        self._index.delete(ids=batch)
            else:
                # Mock implementation
                ids_to_delete = [
                    emb_id for emb_id, data in self._mock_vector_store.items()
                    if data["metadata"].get("user_id") == user_id
                ]
                for emb_id in ids_to_delete:
                    del self._mock_vector_store[emb_id]

            return True
        except Exception as e:
            print(f"Error deleting embeddings for user {user_id}: {e}")
            return False

    # ==================== RAG HELPER METHODS ====================

    def get_relevant_context(self, query: str, user_id: int, top_k: int = 3) -> str:
        """Get relevant context from past journals for RAG."""
        similar_docs = self.search_similar(query, user_id, top_k)

        if not similar_docs:
            return ""

        context_parts = []
        for doc in similar_docs:
            date = doc["metadata"].get("created_at", "Unknown date")
            text = doc["metadata"].get("text", doc.get("text", ""))
            topics = doc["metadata"].get("topics", [])

            if isinstance(topics, list):
                topics_str = ", ".join(topics)
            else:
                topics_str = str(topics)

            context_parts.append(f"[{date}] (Topics: {topics_str})\n{text}")

        return "\n\n---\n\n".join(context_parts)

    def get_index_stats(self) -> dict:
        """Get Pinecone index statistics."""
        if self.is_pinecone_enabled:
            stats = self._index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "namespaces": stats.namespaces
            }
        else:
            return {
                "total_vector_count": len(self._mock_vector_store),
                "dimension": self.EMBEDDING_DIMENSION,
                "namespaces": {"mock": len(self._mock_vector_store)}
            }

    # ==================== HELPER METHODS ====================

    def _clean_metadata(self, metadata: dict) -> dict:
        """Clean metadata to ensure Pinecone compatibility."""
        clean = {}
        for key, value in metadata.items():
            if value is None:
                continue
            elif isinstance(value, (str, int, float, bool)):
                clean[key] = value
            elif isinstance(value, list):
                # Pinecone supports list of strings
                clean[key] = [str(v) for v in value]
            else:
                # Convert other types to string
                clean[key] = str(value)
        return clean

    def _mock_search_similar(
            self,
            query_vector: list[float],
            user_id: int,
            top_k: int
    ) -> list[dict]:
        """Mock implementation of similarity search."""
        import math

        results = []
        for emb_id, data in self._mock_vector_store.items():
            # Filter by user_id
            if data["metadata"].get("user_id") != user_id:
                continue

            # Calculate cosine similarity
            vec1 = query_vector
            vec2 = data["vector"]

            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(b * b for b in vec2))

            if magnitude1 == 0 or magnitude2 == 0:
                similarity = 0.0
            else:
                similarity = dot_product / (magnitude1 * magnitude2)

            results.append({
                "id": emb_id,
                "text": data["metadata"].get("text", ""),
                "metadata": data["metadata"],
                "score": similarity
            })

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
from datetime import datetime

from src.services.embedding_service import EmbeddingService
from src.config import settings


def main() -> None:
    # 1) Create service
    service = EmbeddingService()

    print("=== EmbeddingService configuration summary ===")
    print(f"OpenAI embedding model : {settings.openai_embedding_model}")
    print(f"Pinecone enabled       : {service.is_pinecone_enabled}")
    print(f"Pinecone index name    : {getattr(settings, 'pinecone_index_name', 'N/A')}")
    print()

    # 2) Generate an embedding for a sample text
    sample_text = (
        "Had a call with the client about project timeline and next steps. "
        "They approved the new UI design but want more details on deployment."
    )
    vector = service.generate_embedding(sample_text)

    print("=== Single embedding test ===")
    print(f"Sample text          : {sample_text}")
    print(f"Vector dimension     : {len(vector)}")
    print(f"First 10 values      : {vector[:10]}")
    print()

    # 3) Store the embedding with example metadata
    print("=== Store embedding ===")
    user_id = 1  # example user id; adjust to your test user
    metadata = {
        "user_id": user_id,
        "journal_id": 123,                      # fake journal id for demo
        "created_at": datetime.utcnow().isoformat(),
        "topics": ["client", "project", "timeline"],
    }

    embedding_id = service.store_embedding(
        text=sample_text,
        metadata=metadata,
    )
    print(f"Stored embedding id  : {embedding_id}")
    print()

    # 4) Run a similarity search using the same query text
    print("=== Similarity search ===")
    query = "recent feelings"
    results = service.search_similar(
        query_text=query,
        user_id=user_id,
        top_k=3,
    )

    print(f"Query                : {query}")
    if not results:
        print("No results found (maybe this is the first run).")
    else:
        for i, r in enumerate(results, start=1):
            print(f"\nResult #{i}")
            print(f"  id     : {r['id']}")
            print(f"  score  : {r['score']:.4f}")
            print(f"  text   : {r['text']}")
            print(f"  topics : {r['metadata'].get('topics')}")

    print()

    # 5) Show index / store stats
    print("=== Index / store stats ===")
    stats = service.get_index_stats()
    print(stats)


if __name__ == "__main__":
    main()
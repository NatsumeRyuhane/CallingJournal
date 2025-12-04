import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
print(f"Key length: {len(api_key)}")  # Should be ~50+ characters

from pinecone import Pinecone
pc = Pinecone(api_key=api_key)
print(list(pc.list_indexes()))
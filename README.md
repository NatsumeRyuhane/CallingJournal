# CallingJournal

AI-powered calling journal system for conversation logging, summarization, and local domain knowledge extraction.


## Environment Setup
python version required: 3.12

Install dependencies in your virtual environment:
   ```bash
   pip install -r requirements.txt
   ```

## Module Responsibilities

### Config Layer
- **settings.py**: Loads environment variables, provides Settings dataclass

### Models Layer
- **entities.py**: Pure data classes representing domain objects
  - `User`: User profile with phone, timezone, schedule
  - `Conversation`: Chat session with transcript
  - `Journal`: Generated diary entry with emotions and topics
  - `Message`: Single chat message
  - `EmotionScore`: Detected emotions with confidence scores

### Database Layer
- **connection.py**: PostgreSQL connection pooling and query execution

### DAO Layer (Data Access Objects)
Each DAO provides full CRUD operations:

| DAO | Key Methods |
|-----|-------------|
| `UserDAO` | create, get_by_id, get_by_phone, update, deactivate, delete |
| `ConversationDAO` | create, get_by_user_id, update_transcript, complete_conversation, delete_expired |
| `JournalDAO` | create, get_by_topic, get_by_high_emotion, get_emotion_averages, search |

### Services Layer
- **llm_service.py**: LangChain integration with GPT-4o
  - Chat with conversation history
  - Streaming responses
  - Journal summary generation
  - Topic extraction
  - Emotion analysis

- **embedding_service.py**: Vector operations
  - Generate embeddings (text-embedding-3-small)
  - Store/search similar vectors (mock implementation)
  - RAG context retrieval

- **journal_service.py**: Journal business logic
  - Create journal from conversation
  - Generate markdown files
  - Search journals semantically

- **conversation_service.py**: Orchestrates conversation flow
  - Start/end sessions
  - Process messages
  - Trigger journal generation

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up environment
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Set up database (optional)
```bash
# Connect to PostgreSQL and run:
psql -U postgres -d calling_journal -f db_schema.sql
```

### 4. Run the demo
```bash
python main.py
```

## Demo Usage

```
🌙 AI-Powered Conversational Diary
   Mental Wellness Check-in Demo
============================================================

Type your messages and press Enter.
Type 'end' to finish the conversation and generate journal.
Type 'quit' to exit without saving.
------------------------------------------------------------

🤖 Assistant: Hi there! How was your day today?

👤 You: It was stressful, had a big meeting

🤖 Assistant: I hear you. Work meetings can be really draining...

👤 You: end

📔 Conversation Summary
============================================================
  Conversation ID: 1
  Duration: 5 minutes
  Journal ID: 1
  Journal Path: ./journals/2025-01-20/journal_demo.md
============================================================
```

## Database Schema

See `db_schema.sql` for complete DDL including:
- `users` table
- `conversations` table (temporary, 7-30 day retention)
- `journals` table (permanent)
- Indexes and mock data

## Architecture Notes

1. **Mock Mode**: Runs without OpenAI API key using pre-defined responses
2. **Real Mode**: Uses GPT-4o with streaming responses
3. **RAG Context**: Past journal summaries are retrieved for personalization
4. **Emotion Detection**: LLM-based emotion analysis (can be replaced with MentalBERT)

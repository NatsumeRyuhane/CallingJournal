

# This is the project structure made so far by Zejing Chen(DB part already)

Console-based demo for mental wellness tracking through AI conversations.

## Project Structure

```
CallingJournalTest/
│
├── config/                     # Configuration management
│   ├── __init__.py
│   └── settings.py             # Environment settings (API keys, DB config)
│
├── models/                     # Data models (entities)
│   ├── __init__.py
│   └── entities.py             # User, Conversation, Journal, Message, EmotionScore
│
├── db/                         # Database connection layer
│   ├── __init__.py
│   └── connection.py           # PostgreSQL connection manager
│
├── dao/                        # Data Access Objects (CRUD operations)
│   ├── __init__.py
│   ├── user_dao.py             # User CRUD operations
│   ├── conversation_dao.py     # Conversation CRUD operations
│   └── journal_dao.py          # Journal CRUD operations
│
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── llm_service.py          # LangChain + GPT-4o integration
│   ├── embedding_service.py    # Vector embedding operations
│   ├── journal_service.py      # Journal generation logic
│   └── conversation_service.py # Conversation flow management
│
├── utils/                      # Utilities and helpers
│   ├── __init__.py
│   └── mock_data.py            # Mock data for testing
│
├── main.py                     # Console demo entry point
├── db_schema.sql               # PostgreSQL DDL + mock data
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
└── README.md                   # This file
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

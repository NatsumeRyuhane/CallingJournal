# CallingJournal

An AI-powered conversational diary and mental wellness application that transforms daily reflection into a natural, voice-based experience.

## Overview

CallingJournal addresses the common pain points of traditional diary apps:
- **Low consistency** - Users forget to write entries when busy
- **High dropout rate** - Once skipped, motivation declines
- **Limited emotional engagement** - Writing feels like a chore

Our solution: An AI companion that calls you at your preferred time, engages in natural conversation, and automatically generates journal entries from your voice conversations.

## Features

### Current Implementation

| Feature | Status | Description |
|---------|--------|-------------|
| Phone Calls (Twilio) | Implemented | Outbound calls via Twilio API |
| Real-time Transcription | Implemented | Deepgram Nova-3 with VAD |
| AI Voice Response | Implemented | LLM responses with TTS playback |
| Bidirectional Conversation | Implemented | Full voice-to-voice dialogue |
| Diary Generation | Implemented | First-person diary from conversations |
| Batch Transcription | Implemented | Local Whisper for recordings |
| Conversation Logging | Implemented | Turn-based conversation storage |
| Entity Extraction | Implemented | Named entity recognition |
| Sentiment Analysis | Implemented | Emotional state detection |
| Knowledge Base | Implemented | Semantic search with Pinecone |
| User Authentication | Implemented | JWT-based auth |
| Multi-LLM Support | Implemented | OpenAI, Anthropic, OpenRouter |
| Multi-TTS Support | Implemented | OpenAI TTS, ElevenLabs |

### Planned Features (Not Yet Implemented)

| Feature | Priority | Description |
|---------|----------|-------------|
| Scheduled Calls | High | User-specified call times |
| Customizable AI Persona | Medium | Tone & style customization |
| Mental Health Insights | Medium | Trend analysis over time |
| Personalized Prompts | Medium | Based on previous entries |
| Mobile App | Low | Native iOS/Android apps |
| B2B Dashboard | Low | Enterprise wellness programs |

---

## Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Async web framework with automatic OpenAPI docs |
| **PostgreSQL** | Primary database with async support (asyncpg) |
| **SQLAlchemy 2.0** | Async ORM for database operations |
| **Alembic** | Database migrations |
| **Twilio** | Phone call initiation and media streams |
| **Deepgram** | Real-time streaming transcription with VAD |
| **OpenAI Whisper** | Local batch transcription |
| **OpenAI / Anthropic / OpenRouter** | LLM for conversation and summarization |
| **Pinecone** | Vector database for semantic search |
| **Redis + Celery** | Background task queue |
| **JWT (python-jose)** | Authentication tokens |

### Frontend

| Technology | Purpose |
|------------|---------|
| **React 19** | UI framework |
| **Vite** | Build tool and dev server |
| **Tailwind CSS 4** | Utility-first styling |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization (PostgreSQL, Redis) |
| **ngrok** | Local development tunneling for webhooks |

---

## Project Structure

```
CallingJournal/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment configuration template
│   ├── src/
│   │   ├── config.py          # Settings loader (from .env)
│   │   ├── database.py        # Async database connection
│   │   ├── db_models.py       # SQLAlchemy ORM models
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── auth.py            # JWT authentication
│   │   ├── api/               # API route handlers
│   │   │   ├── auth.py        # Auth endpoints
│   │   │   ├── calls.py       # Call management
│   │   │   ├── journals.py    # Journal CRUD
│   │   │   ├── knowledge.py   # Knowledge base
│   │   │   ├── llm.py         # LLM interaction
│   │   │   ├── streams.py     # Twilio WebSocket streams
│   │   │   └── webhooks.py    # Twilio/Vonage callbacks
│   │   ├── services/          # Business logic
│   │   │   ├── phone_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── journal_service.py
│   │   │   ├── transcription_service.py
│   │   │   └── embedding_service.py
│   │   └── utils/             # Helpers
│   ├── test/                  # Unit tests
│   └── docs/                  # Documentation
│       └── SETUP.md           # Development setup guide
│
├── frontend/
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite configuration
│   ├── tailwind.config.js     # Tailwind configuration
│   └── src/
│       ├── main.jsx           # React entry point
│       ├── App.jsx            # Main app with routing
│       ├── Landing.jsx        # Login/landing page
│       ├── ChatInterface.jsx  # Chat UI
│       ├── Calendar.jsx       # Journal calendar view
│       ├── AITalk.jsx         # Voice conversation UI
│       └── ProfileMenu.jsx    # User profile
│
└── PROJECT.md                 # Product Requirements Document
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- ffmpeg (for audio processing)
- ngrok (for Twilio webhooks)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (see .env.example for documentation)

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Required API Keys

| Service | Purpose | Get Key |
|---------|---------|---------|
| OpenAI / Anthropic / OpenRouter | LLM | Choose one provider |
| Twilio | Phone calls | https://console.twilio.com |
| Deepgram | Real-time transcription | https://console.deepgram.com |
| Pinecone (optional) | Vector search | https://www.pinecone.io |

See `backend/.env.example` for complete configuration documentation.

---

## API Documentation

When running in development mode, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | User registration |
| POST | `/auth/token` | Login (OAuth2) |
| POST | `/calls` | Initiate outbound call |
| GET | `/calls` | List call history |
| POST | `/journals` | Create journal entry |
| GET | `/journals` | List journals |
| POST | `/journals/search` | Search journals |
| POST | `/llm/chat` | Chat with LLM |
| WS | `/streams/twilio` | Twilio media stream |

---

## Development Status

### Completed (MVP Phase 1)

- [x] Phone call initiation via Twilio
- [x] Real-time voice transcription (Deepgram)
- [x] AI voice responses with TTS (OpenAI / ElevenLabs)
- [x] Bidirectional voice conversation
- [x] Diary-style journal generation (first-person perspective)
- [x] Batch transcription (Whisper)
- [x] Conversation storage and retrieval
- [x] LLM-powered summarization
- [x] Entity and sentiment extraction
- [x] User authentication (JWT)
- [x] Basic frontend UI (React)
- [x] Multi-provider LLM support (OpenAI, Anthropic, OpenRouter)
- [x] Multi-provider TTS support (OpenAI, ElevenLabs)

### In Progress

- [ ] Frontend-backend integration
- [ ] Call scheduling system

### Not Started

- [ ] Scheduled call initiation (user-specified times)
- [ ] Customizable AI persona (tone & style)
- [ ] Mental health trend analysis
- [ ] Personalized prompts based on history
- [ ] Push notifications
- [ ] Mobile apps (iOS/Android)
- [ ] B2B enterprise features
- [ ] Psychological wellness resources integration

---

## Architecture Notes

### Call Flow

1. User initiates call via API or scheduled trigger
2. Twilio places outbound call to user's phone
3. User answers, Twilio streams audio via WebSocket
4. Deepgram transcribes audio in real-time with VAD
5. LLM generates responses, TTS plays audio to user
6. Conversation continues bidirectionally
7. On call end, diary entry is generated (first-person perspective)
8. Knowledge extracted and indexed for future context

### LLM Provider Abstraction

The application supports multiple LLM providers through a unified interface:

```
LLM_PROVIDER=openai      # Direct OpenAI API
LLM_PROVIDER=anthropic   # Direct Anthropic API
LLM_PROVIDER=openrouter  # 100+ models via OpenRouter
```

Configure in `.env` - only the selected provider's API key is required.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Twilio](https://www.twilio.com/) - Phone call infrastructure
- [Deepgram](https://deepgram.com/) - Speech-to-text API
- [OpenAI](https://openai.com/) - GPT models and Whisper

"""
Configuration management for CallingJournal application.
Loads and validates environment variables.

DON'T WRITE ANY CREDENTIALS OR SECRETS HERE.
WRITE THEM IN A .env FILE AND PYDANTIC WILL LOAD THEM FOR YOU.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    app_name: str = "CallingJournal"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Database
    # database_url: str = "sqlite+aiosqlite:///./calling_journal.db"
    db_host: str
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str

    @property
    def database_url(self) -> str:
        """
        SQLAlchemy/PostgreSQL async URL constructed from DB_* env vars.

        Example:
        postgresql+asyncpg://user:password@host:5432/dbname
        """
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


    # JWT Authentication
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 day
    
    # LLM Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    openai_embedding_model: str = "text-embedding-3-small"  # OPENAI_EMBEDDING_MODEL

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-opus-20240229"

    # Vector Database (Pinecone)
    pinecone_api_key: str = ""  # PINECONE_API_KEY
    pinecone_index_name: str = "journal-embeddings"  # PINECONE_INDEX_NAME

    
    # Phone Service
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = "+17752547971"
    # vonage_api_key: str = ""
    # vonage_api_secret: str = ""
    # vonage_phone_number: str = ""
    
    # Transcription
    # Using local Whisper or SpeechRecognition - no API key needed
    whisper_model: str = "base"  # Options: tiny, base, small, medium, large
    
    # Deepgram (for streaming transcription)
    deepgram_api_key: str = ""
    deepgram_model: str = "nova-3"  # Options: nova-3, nova-2, whisper, etc.
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # File Storage
    audio_storage_path: str = "./data/audio"
    log_storage_path: str = "./data/logs"
    journal_storage_path: str = "./data/journals"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080","http://localhost:80"]


# Global settings instance
settings = Settings()

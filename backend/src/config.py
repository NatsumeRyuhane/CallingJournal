"""
Configuration management for CallingJournal application.

All configuration is loaded from environment variables via the .env file.
See .env.example for documentation of all available settings.

IMPORTANT: Do not add default values here. All defaults should be set in .env
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All values are loaded from .env file. No defaults are set here to ensure
    configuration is explicit and centralized in .env.
    """

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    app_name: str
    app_version: str
    environment: str
    debug: bool
    api_host: str
    api_port: int

    # -------------------------------------------------------------------------
    # Database (PostgreSQL)
    # -------------------------------------------------------------------------
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    @property
    def database_url(self) -> str:
        """Construct async PostgreSQL URL from individual DB settings."""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    # -------------------------------------------------------------------------
    # JWT Authentication
    # -------------------------------------------------------------------------
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # -------------------------------------------------------------------------
    # LLM Configuration
    # -------------------------------------------------------------------------
    llm_provider: str

    # OpenAI
    openai_api_key: str
    openai_model: str
    openai_embedding_model: str

    # Anthropic
    anthropic_api_key: str
    anthropic_model: str

    # OpenRouter
    openrouter_api_key: str
    openrouter_model: str
    openrouter_site_url: str
    openrouter_app_name: str

    # -------------------------------------------------------------------------
    # Vector Database (Pinecone)
    # -------------------------------------------------------------------------
    pinecone_api_key: str
    pinecone_index_name: str

    # -------------------------------------------------------------------------
    # Phone Service (Twilio)
    # -------------------------------------------------------------------------
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str

    # -------------------------------------------------------------------------
    # Text-to-Speech (TTS)
    # -------------------------------------------------------------------------
    tts_provider: str  # openai, elevenlabs
    tts_voice: str  # Voice ID or name
    tts_model: str  # TTS model
    elevenlabs_api_key: str

    # -------------------------------------------------------------------------
    # Transcription - Whisper (Local)
    # -------------------------------------------------------------------------
    whisper_model: str

    # -------------------------------------------------------------------------
    # Transcription - Deepgram (Streaming)
    # -------------------------------------------------------------------------
    deepgram_api_key: str
    deepgram_model: str
    deepgram_language: str
    deepgram_encoding: str
    deepgram_sample_rate: int
    deepgram_channels: int
    deepgram_endpointing: int

    # -------------------------------------------------------------------------
    # Redis
    # -------------------------------------------------------------------------
    redis_url: str

    # -------------------------------------------------------------------------
    # File Storage
    # -------------------------------------------------------------------------
    audio_storage_path: str
    log_storage_path: str
    journal_storage_path: str

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    log_level: str
    log_file: str

    # -------------------------------------------------------------------------
    # CORS
    cors_origins: list[str]


# Global settings instance
settings = Settings()
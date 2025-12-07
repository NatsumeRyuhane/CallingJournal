"""
Main FastAPI application entry point.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.logging_config import setup_logging, get_logger
from src.database import init_db, close_db
from src.api import auth, calls, journals, knowledge, llm, webhooks

# Initialize logging first
setup_logging(
    log_level=settings.log_level,
    log_file=settings.log_file
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting CallingJournal application...")
    await init_db()
    logger.info("Database initialized")
    
    # Create necessary directories
    import os
    os.makedirs(settings.audio_storage_path, exist_ok=True)
    os.makedirs(settings.log_storage_path, exist_ok=True)
    os.makedirs(settings.journal_storage_path, exist_ok=True)
    logger.info("Storage directories created")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CallingJournal application...")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered calling journal system for conversation logging and knowledge extraction",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(auth.router)
app.include_router(calls.router)
app.include_router(journals.router)
app.include_router(knowledge.router)
app.include_router(llm.router)
app.include_router(webhooks.router)
from src.api import streams
app.include_router(streams.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs" if settings.debug else "disabled in production"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )

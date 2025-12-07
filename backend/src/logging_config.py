"""
Centralized logging configuration for CallingJournal.

Usage:
    from src.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("Message")
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

# Will be initialized on first call to setup_logging()
_logging_configured = False


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    Configure application-wide logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        log_format: Custom log format string (optional)
    """
    global _logging_configured

    if _logging_configured:
        return

    # Default format with timestamp, logger name, level, and message
    if log_format is None:
        log_format = "%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s"

    # Get numeric log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler - always enabled
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)

    # File handler - only if log_file is specified
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Rotating file handler: 10MB max, keep 5 backups
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Convenience loggers for common components
def get_api_logger() -> logging.Logger:
    """Get logger for API endpoints."""
    return logging.getLogger("api")


def get_service_logger() -> logging.Logger:
    """Get logger for services."""
    return logging.getLogger("service")


def get_call_logger() -> logging.Logger:
    """Get logger for call-related operations."""
    return logging.getLogger("call")
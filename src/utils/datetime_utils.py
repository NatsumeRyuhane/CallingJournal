"""
Utility functions for date and time operations.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional


def utcnow() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Parse datetime string.
    
    Args:
        date_str: Datetime string
        format_str: Format string
        
    Returns:
        Datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None


def calculate_duration(start: datetime, end: datetime) -> float:
    """
    Calculate duration in seconds between two datetimes.
    
    Args:
        start: Start datetime
        end: End datetime
        
    Returns:
        Duration in seconds
    """
    delta = end - start
    return delta.total_seconds()


def add_days(dt: datetime, days: int) -> datetime:
    """
    Add days to a datetime.
    
    Args:
        dt: Datetime object
        days: Number of days to add (can be negative)
        
    Returns:
        New datetime
    """
    return dt + timedelta(days=days)


def is_expired(dt: datetime, expiry_minutes: int) -> bool:
    """
    Check if a datetime has expired.
    
    Args:
        dt: Datetime to check
        expiry_minutes: Expiry time in minutes
        
    Returns:
        True if expired
    """
    expiry_time = dt + timedelta(minutes=expiry_minutes)
    return utcnow() > expiry_time

"""
Utility functions for file operations.
"""
import aiofiles
import os
from typing import Optional
from datetime import datetime


async def save_audio_file(
    content: bytes,
    filename: str,
    storage_path: str
) -> str:
    """
    Save audio file to storage.
    
    Args:
        content: Audio file content
        filename: Filename to save as
        storage_path: Base storage path
        
    Returns:
        Full file path
    """
    os.makedirs(storage_path, exist_ok=True)
    
    # Add timestamp to filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{timestamp}_{filename}"
    file_path = os.path.join(storage_path, full_filename)
    
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    return file_path


async def read_file(file_path: str) -> Optional[bytes]:
    """
    Read file content.
    
    Args:
        file_path: Path to file
        
    Returns:
        File content or None if not found
    """
    if not os.path.exists(file_path):
        return None
    
    async with aiofiles.open(file_path, "rb") as f:
        content = await f.read()
    
    return content


async def delete_file(file_path: str) -> bool:
    """
    Delete a file.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if deleted successfully
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def get_file_extension(filename: str) -> str:
    """
    Get file extension.
    
    Args:
        filename: Filename
        
    Returns:
        File extension (without dot)
    """
    return os.path.splitext(filename)[1].lstrip(".")

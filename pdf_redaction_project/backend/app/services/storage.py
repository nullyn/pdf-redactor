"""
app/services/storage.py
Temporary file storage and cleanup management
"""

import os
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages temporary PDF storage and cleanup"""

    @staticmethod
    def generate_file_id() -> str:
        """Generate unique file ID"""
        return str(uuid.uuid4())

    @staticmethod
    def get_upload_path(file_id: str) -> Path:
        """Get path where uploaded PDF should be stored"""
        return settings.TEMP_DIR / f"{file_id}_original.pdf"

    @staticmethod
    def get_redacted_path(file_id: str) -> Path:
        """Get path for redacted PDF output"""
        return settings.TEMP_DIR / f"{file_id}_redacted.pdf"

    @staticmethod
    def save_upload(file_id: str, file_content: bytes) -> Path:
        """Save uploaded PDF to temp storage."""
        file_path = StorageManager.get_upload_path(file_id)

        with open(file_path, "wb") as f:
            f.write(file_content)

        logger.info(f"Saved upload {file_id} to {file_path}")
        return file_path

    @staticmethod
    def file_exists(file_id: str) -> bool:
        """Check if uploaded file exists"""
        return StorageManager.get_upload_path(file_id).exists()

    @staticmethod
    def delete_file(file_path: Path) -> bool:
        """Delete a file"""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")
            return False

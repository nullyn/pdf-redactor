"""
app/config.py
Environment configuration and settings
"""

from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "PDF Redaction Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # CORS
    ALLOWED_ORIGINS: list = ["*"]

    # File storage
    TEMP_DIR: Path = Path("/tmp/pdf_redaction")
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    FILE_RETENTION_HOURS: int = 24  # Auto-delete after 24 hours

    # NLP Model
    SPACY_MODEL: str = "en_core_web_lg"

    # Entity detection confidence thresholds
    NER_CONFIDENCE_THRESHOLD: float = 0.7

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create temp directory if it doesn't exist
try:
    settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass # Handle permissions in Docker/Cloud later

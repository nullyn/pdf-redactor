"""
app/api/routes/upload.py
File upload endpoint
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.api.models.schemas import FileUploadResponse
from app.services.storage import StorageManager
from app.services.pdf_handler import PDFHandler
from app.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["upload"])

@router.post("/upload", response_model=FileUploadResponse)
async def upload_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    """Upload a PDF file for redaction."""

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read upload: {e}")
        raise HTTPException(status_code=400, detail="Failed to read file")

    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    file_id = StorageManager.generate_file_id()

    try:
        file_path = StorageManager.save_upload(file_id, content)
    except Exception as e:
        logger.error(f"Failed to save upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")

    is_valid, error_msg = PDFHandler.validate_pdf(str(file_path))
    if not is_valid:
        StorageManager.delete_file(file_path)
        raise HTTPException(status_code=400, detail=f"Invalid PDF: {error_msg}")

    try:
        page_count = PDFHandler.get_page_count(str(file_path))
    except Exception as e:
        logger.error(f"Failed to get page count: {e}")
        StorageManager.delete_file(file_path)
        raise HTTPException(status_code=500, detail="Failed to process PDF")

    return FileUploadResponse(
        file_id=file_id,
        page_count=page_count,
        filename=file.filename,
        size_bytes=len(content),
    )

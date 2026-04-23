"""
app/api/routes/apply.py
Redaction application endpoint
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.api.models.schemas import RedactionRequest, RedactionResponse
from app.services.storage import StorageManager
from app.services.redactor import RedactionService
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["redact"])

redaction_service = RedactionService()

@router.post("/apply", response_model=RedactionResponse)
async def apply_redactions(request: RedactionRequest):
    """Apply selected redactions to PDF and generate output file."""

    file_id = request.file_id
    redactions = request.redactions

    if not StorageManager.file_exists(file_id):
        raise HTTPException(status_code=404, detail="File not found")

    input_path = str(StorageManager.get_upload_path(file_id))
    output_path = str(StorageManager.get_redacted_path(file_id))

    if not redactions:
        raise HTTPException(status_code=400, detail="No redactions specified")

    try:
        redaction_service.apply_redactions(input_path, output_path, redactions)

        logger.info(f"Applied {len(redactions)} redactions to {file_id}")

        return RedactionResponse(
            file_id=file_id,
            redaction_count=len(redactions),
            download_url=f"/api/download/{file_id}",
            message=f"Successfully applied {len(redactions)} redactions",
        )

    except Exception as e:
        logger.error(f"Redaction failed for {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Redaction failed: {str(e)}")

@router.get("/download/{file_id}")
async def download_redacted_pdf(file_id: str):
    """Download the redacted PDF."""

    redacted_path = StorageManager.get_redacted_path(file_id)

    if not redacted_path.exists():
        raise HTTPException(status_code=404, detail="Redacted file not found. Did you apply redactions?")

    return FileResponse(
        path=redacted_path,
        filename=f"redacted_{file_id[:8]}.pdf",
        media_type="application/pdf",
    )

"""
app/api/routes/detect.py
PII detection endpoint
"""

from fastapi import APIRouter, HTTPException
from app.api.models.schemas import DetectionResponse, EntityMatch
from app.services.storage import StorageManager
from app.services.redactor import RedactionService
from typing import Dict
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["detect"])

redaction_service = RedactionService()

@router.post("/detect", response_model=DetectionResponse)
async def detect_pii(file_id: str):
    """Detect PII entities in uploaded PDF."""

    if not StorageManager.file_exists(file_id):
        raise HTTPException(status_code=404, detail="File not found")

    pdf_path = str(StorageManager.get_upload_path(file_id))

    try:
        result = redaction_service.detect_pii_in_pdf(pdf_path)

        matches = [
            EntityMatch(
                page=m["page"],
                text=m["text"],
                type=m["type"],
                rect=m["rect"],
                confidence=m.get("confidence", 0.0),
                source=m.get("source", "NER"),
            )
            for m in result["matches"]
        ]

        summary: Dict[str, int] = {}
        for match in matches:
            entity_type = match.type.value
            summary[entity_type] = summary.get(entity_type, 0) + 1

        logger.info(f"Detection complete for {file_id}: {len(matches)} entities found")

        return DetectionResponse(
            file_id=file_id,
            page_count=result["page_count"],
            matches=matches,
            summary=summary,
        )

    except Exception as e:
        logger.error(f"Detection failed for {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

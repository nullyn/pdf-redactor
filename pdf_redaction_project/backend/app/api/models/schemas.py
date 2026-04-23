"""
app/api/models/schemas.py
Pydantic request/response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from app.utils.constants import EntityType

class FileUploadResponse(BaseModel):
    file_id: str
    page_count: int
    filename: str
    size_bytes: int

class EntityMatch(BaseModel):
    page: int
    text: str
    type: EntityType
    rect: List[float] = Field(description="[x0, y0, x1, y1]")
    confidence: float = 0.0
    source: str = "NER"

class DetectionResponse(BaseModel):
    file_id: str
    page_count: int
    matches: List[EntityMatch]
    summary: Dict[str, int] = Field(description="Count of each entity type")

class RedactionRequest(BaseModel):
    file_id: str
    redactions: List[Dict] = Field(description="List of {page, rect, type, text} to redact")

class RedactionResponse(BaseModel):
    file_id: str
    redaction_count: int
    download_url: str
    message: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int

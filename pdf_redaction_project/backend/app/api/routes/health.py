"""
app/api/routes/health.py
Health check endpoint
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "ok",
        "service": "pdf-redaction-api",
        "version": "1.0.0",
    }

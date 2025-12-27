"""
API route definitions.
"""
from fastapi import APIRouter

from app.utils.logger import logger

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response indicating service health status
    """
    logger.info("Health check requested")
    return {"status": "ok"}

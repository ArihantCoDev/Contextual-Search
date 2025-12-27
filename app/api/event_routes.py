"""
API routes for capturing user behavior events.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.services.event_service import get_event_service
from app.utils.logger import logger

router = APIRouter()


class EventRequest(BaseModel):
    """
    Request model for tracking events.
    """
    event_type: str = Field(..., description="Type of event (search, click, purchase, etc.)")
    session_id: str = Field(..., description="Unique session identifier for the user")
    payload: Dict[str, Any] = Field(..., description="Event details (e.g. product_id, query)")


@router.post("/event")
async def track_event(request: EventRequest):
    """
    Track a user behavior event asynchronously.
    
    This endpoint returns immediately while the event is processed 
    in the background.
    """
    try:
        service = get_event_service()
        await service.track_event(
            event_type=request.event_type,
            session_id=request.session_id,
            payload=request.payload
        )
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Failed to queue event: {e}")
        # Even if queuing fails, we might not want to 500 the client for analytics
        # But for debugging, let's return error
        raise HTTPException(status_code=500, detail="Failed to track event")

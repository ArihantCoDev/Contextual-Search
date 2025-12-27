"""
FastAPI application entry point.
"""
from fastapi import FastAPI

from app.api.routes import router
from app.api.ingestion_routes import router as ingestion_router
from app.api.search_routes import router as search_router
from app.api.event_routes import router as event_router
from app.services.event_service import get_event_service
from app.utils.logger import logger

# Create FastAPI application
app = FastAPI(
    title="Contextual Search API",
    description="AI-powered contextual search system",
    version="0.1.0"
)

# Include API routes
app.include_router(router, prefix="/api", tags=["api"])
app.include_router(ingestion_router, prefix="/ingest", tags=["ingestion"])
app.include_router(search_router, prefix="/api", tags=["search"])
app.include_router(event_router, tags=["events"])


@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns:
        Welcome message
    """
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to Contextual Search API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    logger.info("Starting Contextual Search API...")
    # Start event processing worker
    await get_event_service().start_worker()


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    logger.info("Shutting down Contextual Search API...")
    # Stop event processing worker
    await get_event_service().stop_worker()

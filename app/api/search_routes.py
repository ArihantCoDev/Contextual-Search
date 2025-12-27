"""
API routes for semantic search.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.search_service import get_search_service, SearchResult, SearchFilters
from app.utils.logger import logger

router = APIRouter()


class SearchRequest(BaseModel):
    """
    Request model for search endpoint.
    """
    query: str = Field(..., description="Natural language search query")
    filters: Optional[SearchFilters] = Field(None, description="Optional structured filters")
    limit: int = Field(10, description="Maximum number of results (default 10)")


class SearchResponse(BaseModel):
    """
    Response model for search endpoint.
    """
    count: int
    results: List[SearchResult]


@router.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """
    Perform contextual semantic search.
    
    Args:
        request: Search query and filters
        
    Returns:
        List of ranked products matching the context
    """
    logger.info(f"Search request: {request.query}")
    try:
        search_service = get_search_service()
        results = search_service.search(
            query=request.query, 
            filters=request.filters, 
            limit=request.limit
        )
        
        return {
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

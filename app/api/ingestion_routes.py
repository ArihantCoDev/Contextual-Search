"""
API routes for product ingestion.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any

from app.services.ingestion_service import get_ingestion_service
from app.utils.logger import logger

router = APIRouter()


@router.post("/products")
async def ingest_products(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Ingest products from CSV or JSON file.
    
    Args:
        file: Uploaded file (CSV or JSON format)
        
    Returns:
        Ingestion results including count of products ingested
        
    Raises:
        HTTPException: If file format is unsupported or ingestion fails
    """
    logger.info(f"Ingestion request received for file: {file.filename}")
    
    # Determine file format from extension
    if file.filename.endswith('.json'):
        data_format = 'json'
    elif file.filename.endswith('.csv'):
        data_format = 'csv'
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload CSV or JSON file."
        )
    
    try:
        # Read file contents
        contents = await file.read()
        
        # Create ingestion service instance (lazy loading of models)
        ingestion_service = get_ingestion_service()
        result = ingestion_service.ingest_products(contents, data_format)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


# Temporarily disabled to debug OpenAPI issue
# @router.get("/stats")
# async def get_ingestion_stats() -> Dict[str, Any]:
#     """
#     Get statistics about ingested products.
#     
#     Returns:
#         Dictionary with product count and vector count
#     """
#     from app.data.product_repository import get_product_repository
#     from app.data.vector_repository import get_vector_repository
#     
#     product_repo = get_product_repository()
#     vector_repo = get_vector_repository()
#     
#     return {
#         "product_count": product_repo.get_product_count(),
#         "vector_count": vector_repo.get_vector_count()
#     }

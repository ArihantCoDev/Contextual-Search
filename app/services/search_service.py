"""
Search service for handling semantic search with filters.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.services.ingestion_service import get_ingestion_service, IngestionService
from app.data.product_repository import get_product_repository
from app.data.vector_repository import get_vector_repository
from app.ai.embedding_service import get_embedding_service
from app.utils.logger import logger


class SearchFilters(BaseModel):
    """
    Structured filters for search.
    """
    max_price: Optional[float] = Field(None, description="Maximum price filter")
    category: Optional[str] = Field(None, description="Category filter (exact match)")
    min_rating: Optional[float] = Field(None, description="Minimum rating filter")


class SearchResult(BaseModel):
    """
    Product search result with similarity score.
    """
    id: str
    title: str
    price: Optional[float]
    rating: Optional[float]
    similarity_score: float
    description: Optional[str] = None
    category: Optional[str] = None


class SearchService:
    """
    Service for executing contextual semantic search.
    
    Combines:
    1. Query embedding generation
    2. Vector similarity search (FAISS)
    3. Structured data retrieval (SQLite)
    4. Post-filtering (Business logic)
    """
    
    def __init__(self):
        """Initialize search service with repositories."""
        self.product_repo = None
        self.embedding_service = None
        self.vector_repo = None

    def _ensure_initialized(self):
        """Lazy initialization of dependencies."""
        if self.product_repo is None:
            self.product_repo = get_product_repository()
        if self.embedding_service is None:
            self.embedding_service = get_embedding_service()
        if self.vector_repo is None:
            self.vector_repo = get_vector_repository(
                embedding_dimension=self.embedding_service.get_embedding_dimension()
            )

    def search(
        self, 
        query: str, 
        filters: Optional[SearchFilters] = None, 
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Perform semantic search with filters.
        
        Args:
            query: Natural language query
            filters: Optional structured filters
            limit: Maximum number of results to return
            
        Returns:
            List of ranked SearchResult objects
        """
        self._ensure_initialized()
        logger.info(f"Searching for: '{query}' with filters: {filters}")
        
        # 1. Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        
        # 2. Vector Search
        # We fetch more candidates than 'limit' to allow for post-filtering
        # Rule of thumb: fetch 5x-10x the limit if heavy filtering is expected
        candidate_multiplier = 10
        fetch_k = limit * candidate_multiplier
        
        product_ids, distances = self.vector_repo.search(query_embedding, k=fetch_k)
        
        if not product_ids:
            logger.info("No vector matches found")
            return []
            
        # 3. Retrieve Product Data & 4. Apply Filters
        results = []
        
        # We need to process in order of similarity (which FAISS returns)
        for pid, distance in zip(product_ids, distances):
            # Stop if we found enough matching results
            if len(results) >= limit:
                break
                
            product = self.product_repo.get_product_by_id(pid)
            if not product:
                continue
                
            # Apply filters
            if not self._passes_filters(product, filters):
                continue
            
            # Convert L2 distance to similarity score (approximate)
            # L2 is 0 for identical, higher for different. 
            # Simple conversion: 1 / (1 + distance) or just 1 - distance (if normalized)
            # For this demo, we'll use a simple transformation for display
            similarity = 1.0 / (1.0 + distance)
            
            results.append(SearchResult(
                id=product['id'],
                title=product['title'],
                price=product['price'],
                rating=product['rating'],
                description=product['description'],
                category=product['category'],
                similarity_score=round(similarity, 4)
            ))
            
        logger.info(f"Search returned {len(results)} results")
        return results

    def _passes_filters(self, product: Dict[str, Any], filters: Optional[SearchFilters]) -> bool:
        """
        Check if product passes all filters.
        
        Args:
            product: Product dictionary from DB
            filters: SearchFilters object
            
        Returns:
            True if fully compliant, False otherwise
        """
        if not filters:
            return True
            
        # Max Price
        if filters.max_price is not None:
            if product.get('price') is None or product['price'] > filters.max_price:
                return False
                
        # Min Rating        
        if filters.min_rating is not None:
            if product.get('rating') is None or product['rating'] < filters.min_rating:
                return False
                
        # Category (Case-insensitive match)
        if filters.category:
            prod_cat = product.get('category', '').lower()
            if filters.category.lower() not in prod_cat:
                # Using 'in' for loose matching, or '==' for strict
                # Requirements requested: "category: string" - usually implies strict or substring
                if filters.category.lower() != prod_cat: 
                    return False
                    
        return True


# Singleton pattern
_search_service_instance = None

def get_search_service() -> SearchService:
    """Get singleton search service instance."""
    global _search_service_instance
    if _search_service_instance is None:
        _search_service_instance = SearchService()
    return _search_service_instance

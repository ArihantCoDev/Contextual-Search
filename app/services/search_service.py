"""
Search service for handling semantic search with filters.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.services.ingestion_service import get_ingestion_service, IngestionService
from app.data.product_repository import get_product_repository
from app.data.vector_repository import get_vector_repository
from app.ai.embedding_service import get_embedding_service
from app.nlp.intent_extractor import extract_intent
from app.utils.logger import logger


class SearchFilters(BaseModel):
    """
    Structured filters for search.
    """
    # Price filters
    price_min: Optional[float] = Field(None, description="Minimum price filter")
    price_max: Optional[float] = Field(None, description="Maximum price filter (alias: max_price)")
    max_price: Optional[float] = Field(None, description="Maximum price filter (deprecated, use price_max)")
    
    # Rating filter
    min_rating: Optional[float] = Field(None, description="Minimum rating filter")
    
    # Category and brand
    category: Optional[str] = Field(None, description="Category filter (exact or substring match)")
    brand: Optional[str] = Field(None, description="Brand filter")
    
    # Attributes
    color: Optional[str] = Field(None, description="Color filter")
    size: Optional[str] = Field(None, description="Size filter")
    
    # Metadata flags (typically set by NLP, not UI)
    approximate_price: Optional[bool] = Field(None, description="Whether price is approximate (±15%)")
    fuzzy_price: Optional[bool] = Field(None, description="Whether to use fuzzy price matching")
    conflict: Optional[bool] = Field(None, description="Whether there's a constraint conflict")


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
    explanation: Optional[str] = None


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
            filters: Optional structured filters (from UI or API)
            limit: Maximum number of results to return
            
        Returns:
            List of ranked SearchResult objects
        """
        self._ensure_initialized()
        
        # 1. Extract intent from natural language query using NLP
        intent = extract_intent(query)
        semantic_query = intent['semantic_query']
        nlp_constraints = intent['constraints']
        
        logger.info(f"Query: '{query}'")
        logger.info(f"Semantic query: '{semantic_query}'")
        logger.info(f"NLP constraints: {nlp_constraints}")
        logger.info(f"UI filters (raw): {filters}")
        
        # 2. Merge NLP constraints with UI filters (UI takes precedence)
        merged_filters = self._merge_filters(nlp_constraints, filters)
        logger.info(f"Merged filters (final): price_min={merged_filters.price_min}, price_max={merged_filters.price_max}, "
                   f"category={merged_filters.category}, min_rating={merged_filters.min_rating}, "
                   f"brand={merged_filters.brand}")
        
        # Warn if conflict detected
        if merged_filters.conflict:
            logger.warning(f"Conflicting price constraints detected in query: '{query}'")
        
        # 3. Generate query embedding using cleaned semantic query
        query_embedding = self.embedding_service.generate_embedding(semantic_query)
        
        # 4. Vector Search
        # We fetch more candidates than 'limit' to allow for post-filtering
        # Rule of thumb: fetch 5x-10x the limit if heavy filtering is expected
        candidate_multiplier = 10
        fetch_k = limit * candidate_multiplier
        
        product_ids, distances = self.vector_repo.search(query_embedding, k=fetch_k)
        
        if not product_ids:
            logger.info("No vector matches found")
            return []
            
        # 5. Retrieve Product Data & Apply Filters
        results = []
        
        # We need to process in order of similarity (which FAISS returns)
        for pid, distance in zip(product_ids, distances):
            # Stop if we found enough matching results
            if len(results) >= limit:
                break
                
            product = self.product_repo.get_product_by_id(pid)
            if not product:
                continue
                
            # Apply merged filters
            if not self._passes_filters(product, merged_filters):
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
            
        # 6. Apply Learning-to-Rank (Re-ranking)
        if results:
            from app.services.ranking_service import get_ranking_service
            ranking_service = get_ranking_service()
            results = ranking_service.apply_ranking(results)
            
            # 7. AI Explanation (Enrichment)
            # We apply this after ranking so we only explain top results
            from app.services.explanation_orchestrator import get_explanation_orchestrator
            orchestrator = get_explanation_orchestrator()
            results = orchestrator.enrich_results(results, query)
            
        logger.info(f"Search returned {len(results)} results")
        return results
    
    def _merge_filters(
        self, 
        nlp_constraints: Dict[str, Any], 
        ui_filters: Optional[SearchFilters]
    ) -> SearchFilters:
        """
        Merge NLP-extracted constraints with UI-provided filters.
        UI filters STRICTLY override NLP constraints when provided.
        
        Args:
            nlp_constraints: Constraints extracted from NLP
            ui_filters: Filters provided from UI/API
            
        Returns:
            Merged SearchFilters object
        """
        # Helper function to check if a value is "empty" (None, empty string, or 0)
        # These values indicate "no filter" and should NOT override NLP constraints
        def is_empty(val):
            if val is None:
                return True
            if isinstance(val, str) and val.strip() == '':
                return True
            if isinstance(val, (int, float)) and val == 0:
                return True
            return False
        
        # Start with NLP constraints as base
        price_min = nlp_constraints.get('price_min')
        price_max = nlp_constraints.get('price_max')
        min_rating = nlp_constraints.get('rating_min')
        category = nlp_constraints.get('category')
        brand = nlp_constraints.get('brand')
        color = nlp_constraints.get('color')
        size = nlp_constraints.get('size')
        approximate_price = nlp_constraints.get('approximate_price', False)
        fuzzy_price = nlp_constraints.get('fuzzy_price', False)
        conflict = nlp_constraints.get('conflict', False)
        
        # UI filters STRICTLY override NLP constraints ONLY if they have meaningful values
        # Empty strings (like "All Categories") are ignored, allowing NLP to work
        if ui_filters:
            # Price Min: Override only if not empty
            if not is_empty(ui_filters.price_min):
                price_min = float(ui_filters.price_min) if ui_filters.price_min else None
                
            # Price Max: Check both price_max and legacy max_price
            if not is_empty(ui_filters.price_max):
                price_max = float(ui_filters.price_max) if ui_filters.price_max else None
            elif not is_empty(ui_filters.max_price):
                price_max = float(ui_filters.max_price) if ui_filters.max_price else None
                
            # Rating: Override only if not empty
            if not is_empty(ui_filters.min_rating):
                min_rating = float(ui_filters.min_rating) if ui_filters.min_rating else None
                
            # Category: Override only if not empty (allows "All Categories" to use NLP)
            if not is_empty(ui_filters.category):
                category = ui_filters.category
                
            # Brand: Override only if not empty
            if not is_empty(ui_filters.brand):
                brand = ui_filters.brand
                
            # Color: Override only if not empty
            if not is_empty(ui_filters.color):
                color = ui_filters.color
                
            # Size: Override only if not empty
            if not is_empty(ui_filters.size):
                size = ui_filters.size
        
        # Conflict resolution: If UI provided price filters, clear conflicting NLP constraints
        # This ensures UI precedence and prevents conflicts
        ui_has_price = ui_filters and (not is_empty(ui_filters.price_min) or 
                                       not is_empty(ui_filters.price_max) or 
                                       not is_empty(ui_filters.max_price))
        
        if ui_has_price:
            # If UI set price_max but NLP set price_min, and they conflict, clear NLP price_min
            if price_max is not None and price_min is not None and price_min > price_max:
                # Check which came from UI vs NLP
                ui_set_min = ui_filters and not is_empty(ui_filters.price_min)
                ui_set_max = ui_filters and (not is_empty(ui_filters.price_max) or not is_empty(ui_filters.max_price))
                
                # Clear the NLP-originated constraint
                if not ui_set_min:  # price_min came from NLP
                    price_min = None
                if not ui_set_max:  # price_max came from NLP
                    price_max = None
        
        # Re-check for conflicts after UI override
        if price_min is not None and price_max is not None and price_min > price_max:
            conflict = True
        else:
            conflict = False
        
        # Create merged filters
        merged = SearchFilters(
            price_min=price_min,
            price_max=price_max,
            min_rating=min_rating,
            category=category,
            brand=brand,
            color=color,
            size=size,
            approximate_price=approximate_price,
            fuzzy_price=fuzzy_price,
            conflict=conflict
        )
        
        # IMPORTANT: Mark if category came from NLP (for filtering logic)
        # NLP categories are for semantic search, not strict filtering
        merged._nlp_category = (category == nlp_constraints.get('category') and 
                               (not ui_filters or is_empty(ui_filters.category)))
        
        return merged

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
        
        # Skip filtering if conflict detected
        if filters.conflict:
            logger.warning("Skipping filters due to detected conflict")
            return True
            
        # Min Price
        if filters.price_min is not None:
            if product.get('price') is None or product['price'] < filters.price_min:
                return False
        
        # Max Price (check both price_max and legacy max_price)
        max_price = filters.price_max or filters.max_price
        if max_price is not None:
            if product.get('price') is None or product['price'] > max_price:
                return False
                
        # Min Rating        
        if filters.min_rating is not None:
            if product.get('rating') is None or product['rating'] < filters.min_rating:
                return False
                
        # Category (Case-insensitive substring match)
        # IMPORTANT: Only filter if category came from UI, not from NLP
        # NLP categories (like "headphones") are for semantic search, not strict filtering
        # UI categories (like "Electronics") are actual database categories for filtering
        if filters.category and not getattr(filters, '_nlp_category', False):
            prod_cat = product.get('category', '').lower()
            if filters.category.lower() not in prod_cat:
                return False
        
        # Brand (Case-insensitive substring match)
        if filters.brand:
            prod_brand = product.get('brand', '').lower()
            if filters.brand.lower() not in prod_brand:
                return False
        
        # Color (Case-insensitive substring match)
        if filters.color:
            # Check in title or description
            searchable_text = f"{product.get('title', '')} {product.get('description', '')}".lower()
            if filters.color.lower() not in searchable_text:
                return False
        
        # Size (Case-insensitive substring match)
        if filters.size:
            # Check in title or description
            searchable_text = f"{product.get('title', '')} {product.get('description', '')}".lower()
            if filters.size.lower() not in searchable_text:
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

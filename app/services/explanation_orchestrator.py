"""
Orchestrator for managing the explanation flow.
"""
from typing import List, Dict, Any
from app.ai.explanation_service import get_explanation_service
from app.services.search_service import SearchResult
from app.data.product_repository import get_product_repository
from app.utils.logger import logger


class ExplanationOrchestrator:
    """
    Coordination layer that enriches search results with explanations.
    
    Decouples the core search logic from the expensive/complex explanation generation.
    """
    
    def __init__(self):
        """Initialize orchestrator with required services."""
        self.explanation_service = get_explanation_service()
        self.product_repo = get_product_repository()
        
    def enrich_results(
        self, 
        results: List[SearchResult], 
        query: str
    ) -> List[SearchResult]:
        """
        Attach explanations to a list of search results.
        
        Args:
            results: List of SearchResult objects
            query: Original user query
            
        Returns:
            List of SearchResults with 'explanation' field populated
        """
        if not results:
            return results
            
        logger.info(f"Generating explanations for {len(results)} results")
        
        for result in results:
            # We already have most data in SearchResult, but let's ensure we use 
            # the full context if needed (e.g. detailed attributes not in result obj)
            
            # Construct product context dictionary
            product_context = {
                "title": result.title,
                "category": result.category,
                "description": result.description,
                # In a real app we might fetch full attributes here if not present
                "attributes": {} # Placeholder if attributes aren't in SearchResult
            }
            
            # Generate explanation
            explanation = self.explanation_service.generate_explanation(
                query=query,
                product=product_context,
                score=result.similarity_score
            )
            
            # Attach to result
            # We need to dynamically add this field or update the model
            # Since Pydantic models are strict, we added 'explanation' field to the model
            result.explanation = explanation
            
        return results


# Singleton instance
_orchestrator_instance = None


def get_explanation_orchestrator() -> ExplanationOrchestrator:
    """Get singleton orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = ExplanationOrchestrator()
    return _orchestrator_instance

"""
Service for improving search ranking based on user behavior.
"""
from typing import List
from app.data.behavior_repository import get_behavior_repository
from app.services.search_service import SearchResult
from app.utils.logger import logger


class RankingService:
    """
    Service that applies learning-to-rank heuristics using behavior data.
    
    Adjusts the semantic similarity scores using signals like click-through rate.
    """
    
    def __init__(self):
        """Initialize ranking service."""
        self.behavior_repo = get_behavior_repository()
        
        # Hyperparameters for ranking logic
        self.alpha_click = 0.05  # Boost factor for clicks (5% boost per click roughly)
        self.max_boost = 0.5     # Cap maximum boost (50%)
        
    def apply_ranking(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Re-rank search results based on user behavior signals.
        
        Args:
            results: List of initial search results (semantically ranked)
            
        Returns:
            List of re-ranked results
        """
        if not results:
            return results
            
        # 1. Fetch metrics for these candidates
        product_ids = [r.id for r in results]
        metrics = self.behavior_repo.get_product_metrics(product_ids)
        
        logger.info(f"Applying ranking adjustments to {len(results)} results")
        
        # 2. Adjust scores
        reranked_results = []
        for result in results:
            # duplicate result to avoid mutating original if needed, 
            # but Pydantic models are mutable by default so we modify in place or copy
            # Here we modify in place for efficiency
            
            product_metrics = metrics.get(result.id, {"clicks": 0})
            clicks = product_metrics.get("clicks", 0)
            
            # Simple Heuristic Ranking Formula:
            # final_score = semantic_score + (alpha * click_score)
            # We normalize click score effect to prevent popular items from
            # completely overriding semantic relevance for irrelevant queries.
            
            # Logarithmic-like boost helps prevent runaway scores for viral items
            # specific formula: boost = min(max_boost, clicks * alpha)
            boost = min(self.max_boost, clicks * self.alpha_click)
            
            old_score = result.similarity_score
            new_score = old_score + boost
            
            # Update score
            result.similarity_score = round(new_score, 4)
            
            if boost > 0:
                logger.debug(f"Boosted product {result.id}: {old_score:.4f} -> {new_score:.4f} (Clicks: {clicks})")
                
            reranked_results.append(result)
            
        # 3. Sort by new score descending
        reranked_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return reranked_results


# Singleton instance
_ranking_service_instance = None


def get_ranking_service() -> RankingService:
    """Get singleton ranking service instance."""
    global _ranking_service_instance
    if _ranking_service_instance is None:
        _ranking_service_instance = RankingService()
    return _ranking_service_instance

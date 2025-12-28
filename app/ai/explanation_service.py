"""
Service for generating AI explanations for search results.
"""
import random
from typing import List, Dict, Any, Optional
from app.utils.logger import logger


class ExplanationService:
    """
    Service that provides rationale for why specific products were returned.
    
    In a real production system, this would call an LLM (OpenAI/Gemini/Anthropic).
    For this starter kit, we simulate the LLM's reasoning logic to demonstrate
    the architecture without requiring an API key.
    """
    
    def __init__(self):
        """Initialize the explanation service."""
        # Templates for "mock" LLM generation
        self.templates = [
            "Matches '{query}' because it features {attribute}.",
            "Selected based on high relevance to '{main_keyword}' and popularity.",
            "Relevant to your search for '{query}' due to its description.",
            "This item is frequently viewed by users searching for '{query}'.",
            "A top-rated choice in the {category} category matching '{query}'.",
        ]
        
    def generate_explanation(
        self, 
        query: str, 
        product: Dict[str, Any], 
        score: float,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a human-readable explanation for a single result.
        
        DESIGN NOTE: Explanations are QUALITATIVE, not quantitative:
        - We focus on semantic relevance and visible signals
        - We avoid false precision ("95% match", "87% relevant")
        - We only mention signals that were actually used
        - Future enhancement: Use LLM API for richer natural language
        
        Args:
            query: User's search query
            product: Product details (title, attributes, etc.)
            score: Relevance/ranking score
            context: Additional context keys (filters, user history)
            
        Returns:
            String explanation
        """
        try:
            # 1. Extract key info
            title = product.get("title", "Item")
            category = product.get("category", "General")
            attributes = product.get("attributes", {})
            
            # 2. Simple keyword extraction (naive)
            keywords = query.lower().split()
            main_keyword = keywords[0] if keywords else "item"
            
            # 3. EXPLANATION STRATEGY: Check for direct matches first
            # This ensures explanations are grounded in actual matches
            
            # Direct title match (strongest signal)
            if query.lower() in title.lower():
                return f"Direct match: The title explicitly contains '{query}'."
            
            # Attribute matching (specific features)
            for key, value in attributes.items():
                if str(value).lower() in query.lower():
                    return f"Selected because it has the attribute {key}: {value}."
            
            # Category reason (categorical match)
            if query.lower() in category.lower():
                return f"This is a highly rated item in the {category} category."
            
            # 4. FALLBACK: Generic semantic relevance
            # NOTE: We use generic phrasing to avoid inventing specific reasons
            # Better than guessing at why the embedding matched
            return f"Relevant to your search for '{query}' based on semantic similarity."
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            # Safe fallback that doesn't crash
            return "Recommended based on semantic relevance."


# Singleton instance
_explanation_service_instance = None


def get_explanation_service() -> ExplanationService:
    """Get singleton explanation service instance."""
    global _explanation_service_instance
    if _explanation_service_instance is None:
        _explanation_service_instance = ExplanationService()
    return _explanation_service_instance

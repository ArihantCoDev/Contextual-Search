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
        
        Args:
            query: User's search query
            product: Product details (title, attributes, etc.)
            score: Relevance/ranking score
            context: Additional context keys (filters, user history)
            
        Returns:
            String explanation
        """
        try:
            # 1. extract key info
            title = product.get("title", "Item")
            category = product.get("category", "General")
            attributes = product.get("attributes", {})
            
            # 2. Heuristic "Reasoning" to simulate LLM 
            # In production: prompt = f"Explain why {title} matches {query}..."
            
            # Simple keyword extraction (naive)
            keywords = query.lower().split()
            main_keyword = keywords[0] if keywords else "item"
            
            # Verify if it's a "perfect match"
            if query.lower() in title.lower():
                return f"Direct match: The title explicitly contains '{query}'."
            
            # Attribute matching
            for key, value in attributes.items():
                if str(value).lower() in query.lower():
                    return f"Selected because it has the attribute {key}: {value}."
            
            # Category reason
            if query.lower() in category.lower():
                return f"This is a highly rated item in the {category} category."
                
            # Random template fallback (simulating generative variation)
            import random
            template = random.choice(self.templates)
            explanation = template.format(
                query=query,
                title=title,
                attribute=list(attributes.keys())[0] if attributes else "quality specs",
                main_keyword=main_keyword,
                category=category
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Recommended based on semantic relevance."


# Singleton instance
_explanation_service_instance = None


def get_explanation_service() -> ExplanationService:
    """Get singleton explanation service instance."""
    global _explanation_service_instance
    if _explanation_service_instance is None:
        _explanation_service_instance = ExplanationService()
    return _explanation_service_instance

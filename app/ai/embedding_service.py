"""
Embedding service for generating vector representations of text.
"""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from app.utils.logger import logger


class EmbeddingService:
    """
    Service for generating embeddings using sentence-transformers.
    
    This service provides a reusable interface for converting text into
    dense vector representations suitable for semantic search.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence-transformer model to use.
                       Default is 'all-MiniLM-L6-v2' (384-dim, fast, good quality)
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding model loaded. Dimension: {self.embedding_dimension}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Numpy array containing the embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.embedding_dimension, dtype=np.float32)
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of shape (len(texts), embedding_dimension)
        """
        if not texts:
            return np.array([], dtype=np.float32)
        
        # Replace empty strings with placeholder to avoid errors
        processed_texts = [text if text and text.strip() else " " for text in texts]
        
        embeddings = self.model.encode(
            processed_texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 100
        )
        return embeddings.astype(np.float32)
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this service.
        
        Returns:
            Integer dimension of embedding vectors
        """
        return self.embedding_dimension


# Singleton instance - lazy initialization
_embedding_service_instance = None


def get_embedding_service(load_model: bool = True) -> EmbeddingService:
    """
    Get or create the singleton embedding service instance.
    
    Args:
        load_model: If False, returns a placeholder without loading the model
    
    Returns:
        Shared EmbeddingService instance
    """
    global _embedding_service_instance
    if _embedding_service_instance is None and load_model:
        _embedding_service_instance = EmbeddingService()
    return _embedding_service_instance


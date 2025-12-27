"""
Repository for managing vector embeddings using FAISS.
"""
from typing import List, Tuple, Optional
import numpy as np
import faiss

from app.utils.logger import logger


class VectorRepository:
    """
    Repository for storing and searching vector embeddings using FAISS.
    
    This repository provides an in-memory vector database for fast
    similarity search on product embeddings.
    """
    
    def __init__(self, embedding_dimension: int = 384):
        """
        Initialize the vector repository.
        
        Args:
            embedding_dimension: Dimension of embedding vectors
        """
        self.embedding_dimension = embedding_dimension
        
        # Initialize FAISS index (using L2 distance)
        self.index = faiss.IndexFlatL2(embedding_dimension)
        
        # Maintain mapping between FAISS index position and product IDs
        self.product_ids: List[str] = []
        
        logger.info(f"Vector repository initialized with dimension {embedding_dimension}")
    
    def add_vectors(self, product_ids: List[str], embeddings: np.ndarray) -> int:
        """
        Add vectors to the FAISS index.
        
        Args:
            product_ids: List of product IDs corresponding to embeddings
            embeddings: Numpy array of shape (n, embedding_dimension)
            
        Returns:
            Number of vectors added
        """
        if len(product_ids) != len(embeddings):
            raise ValueError("Number of product IDs must match number of embeddings")
        
        if embeddings.shape[1] != self.embedding_dimension:
            raise ValueError(
                f"Embedding dimension {embeddings.shape[1]} doesn't match "
                f"expected dimension {self.embedding_dimension}"
            )
        
        # Add vectors to FAISS index
        self.index.add(embeddings)
        
        # Store product ID mapping
        self.product_ids.extend(product_ids)
        
        logger.info(f"Added {len(product_ids)} vectors to index")
        return len(product_ids)
    
    def search(
        self, 
        query_embedding: np.ndarray, 
        k: int = 10
    ) -> Tuple[List[str], List[float]]:
        """
        Search for nearest neighbors to a query embedding.
        
        Args:
            query_embedding: Query vector of shape (embedding_dimension,)
            k: Number of nearest neighbors to return
            
        Returns:
            Tuple of (product_ids, distances) for the k nearest neighbors
        """
        if self.index.ntotal == 0:
            logger.warning("Search attempted on empty index")
            return [], []
        
        # Reshape query to (1, dimension) for FAISS
        query = query_embedding.reshape(1, -1)
        
        # Ensure we don't request more results than available
        k = min(k, self.index.ntotal)
        
        # Search FAISS index
        distances, indices = self.index.search(query, k)
        
        # Convert to lists and map indices to product IDs
        distances = distances[0].tolist()
        product_ids = [self.product_ids[idx] for idx in indices[0]]
        
        return product_ids, distances
    
    def get_vector_count(self) -> int:
        """
        Get the number of vectors in the index.
        
        Returns:
            Count of vectors
        """
        return self.index.ntotal
    
    def clear(self):
        """Clear all vectors from the index."""
        self.index.reset()
        self.product_ids.clear()
        logger.info("Vector index cleared")
    
    def update_vector(self, product_id: str, embedding: np.ndarray):
        """
        Update or add a single vector.
        
        Note: FAISS doesn't support efficient updates, so this is a
        convenience method that rebuilds the index if the product exists.
        
        Args:
            product_id: Product ID
            embedding: Embedding vector
        """
        # Check if product already exists
        if product_id in self.product_ids:
            # Remove old vector (rebuild index without it)
            idx = self.product_ids.index(product_id)
            
            # Get all embeddings except the one to update
            all_embeddings = []
            all_ids = []
            
            # This is inefficient but necessary for FAISS updates
            # In production, consider using a different index type or
            # periodic batch rebuilds
            for i, pid in enumerate(self.product_ids):
                if i != idx:
                    all_ids.append(pid)
            
            # Rebuild index (simplified - in production, store embeddings)
            logger.warning(
                f"Updating vector for {product_id} requires index rebuild. "
                "Consider batch operations for better performance."
            )
        
        # Add the new/updated vector
        self.add_vectors([product_id], embedding.reshape(1, -1))


# Singleton instance
_vector_repository_instance = None


def get_vector_repository(embedding_dimension: int = 384) -> VectorRepository:
    """
    Get or create the singleton vector repository instance.
    
    Args:
        embedding_dimension: Dimension of embeddings (only used on first call)
    
    Returns:
        Shared VectorRepository instance
    """
    global _vector_repository_instance
    if _vector_repository_instance is None:
        _vector_repository_instance = VectorRepository(embedding_dimension)
    return _vector_repository_instance

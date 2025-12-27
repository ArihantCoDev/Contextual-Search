"""
Ingestion service for processing and storing product data.
"""
from typing import List, Dict, Any, Union
import pandas as pd
import json
from io import StringIO

from app.data.product_repository import get_product_repository
from app.data.vector_repository import get_vector_repository
from app.ai.embedding_service import get_embedding_service
from app.utils.logger import logger


class IngestionService:
    """
    Service for ingesting product data into the search system.
    
    This service orchestrates the complete ingestion pipeline:
    1. Parse input data (CSV or JSON)
    2. Normalize product fields
    3. Generate vector embeddings
    4. Store in SQLite and FAISS
    """
    
    def __init__(self):
        """Initialize the ingestion service with required dependencies."""
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
    
    def ingest_products(
        self, 
        data: Union[str, bytes], 
        data_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Ingest products from CSV or JSON data.
        
        Args:
            data: Raw data as string or bytes
            data_format: Format of data - 'json' or 'csv'
            
        Returns:
            Dictionary with ingestion statistics
        """
        logger.info(f"Starting ingestion pipeline for {data_format} data")
        
        # Lazy initialization of dependencies
        self._ensure_initialized()
        
        try:
            # Step 1: Parse data
            products = self._parse_data(data, data_format)
            
            if not products:
                logger.warning("No products found in input data")
                return {
                    "status": "success",
                    "products_ingested": 0,
                    "message": "No products found in input data"
                }
            
            # Step 2: Normalize products
            normalized_products = self._normalize_products(products)
            
            # Step 3: Generate embeddings
            embeddings = self._generate_embeddings(normalized_products)
            
            # Step 4: Store in databases
            self._store_products(normalized_products, embeddings)
            
            logger.info(f"Successfully ingested {len(normalized_products)} products")
            
            return {
                "status": "success",
                "products_ingested": len(normalized_products),
                "message": f"Successfully ingested {len(normalized_products)} products"
            }
            
        except Exception as e:
            logger.error(f"Error during ingestion: {e}")
            return {
                "status": "error",
                "products_ingested": 0,
                "message": str(e)
            }
    
    def _parse_data(
        self, 
        data: Union[str, bytes], 
        data_format: str
    ) -> List[Dict[str, Any]]:
        """
        Parse raw data into list of product dictionaries.
        
        Args:
            data: Raw input data
            data_format: 'json' or 'csv'
            
        Returns:
            List of product dictionaries
        """
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        if data_format.lower() == "json":
            return self._parse_json(data)
        elif data_format.lower() == "csv":
            return self._parse_csv(data)
        else:
            raise ValueError(f"Unsupported data format: {data_format}")
    
    def _parse_json(self, data: str) -> List[Dict[str, Any]]:
        """
        Parse JSON data.
        
        Args:
            data: JSON string
            
        Returns:
            List of product dictionaries
        """
        parsed = json.loads(data)
        
        # Handle both single object and array
        if isinstance(parsed, dict):
            return [parsed]
        elif isinstance(parsed, list):
            return parsed
        else:
            raise ValueError("JSON must be an object or array")
    
    def _parse_csv(self, data: str) -> List[Dict[str, Any]]:
        """
        Parse CSV data.
        
        Args:
            data: CSV string
            
        Returns:
            List of product dictionaries
        """
        df = pd.read_csv(StringIO(data))
        return df.to_dict('records')
    
    def _normalize_products(
        self, 
        products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Normalize product fields to expected schema.
        
        Expected fields: id, title, description, category, attributes, price, rating
        
        Args:
            products: List of raw product dictionaries
            
        Returns:
            List of normalized product dictionaries
        """
        normalized = []
        
        for idx, product in enumerate(products):
            try:
                # Handle missing ID
                product_id = str(product.get("id", f"product_{idx}"))
                
                # Handle attributes - can be dict or JSON string
                attributes = product.get("attributes", {})
                if isinstance(attributes, str):
                    try:
                        attributes = json.loads(attributes)
                    except json.JSONDecodeError:
                        attributes = {}
                
                normalized_product = {
                    "id": product_id,
                    "title": str(product.get("title", "")),
                    "description": str(product.get("description", "")),
                    "category": str(product.get("category", "")),
                    "attributes": attributes if isinstance(attributes, dict) else {},
                    "price": self._safe_float(product.get("price")),
                    "rating": self._safe_float(product.get("rating"))
                }
                
                normalized.append(normalized_product)
                
            except Exception as e:
                logger.error(f"Error normalizing product at index {idx}: {e}")
        
        logger.info(f"Normalized {len(normalized)} products")
        return normalized
    
    def _generate_embeddings(
        self, 
        products: List[Dict[str, Any]]
    ) -> List[Any]:
        """
        Generate embeddings for products.
        
        Combines title + description for each product.
        
        Args:
            products: List of normalized product dictionaries
            
        Returns:
            Numpy array of embeddings
        """
        # Combine title and description for embedding
        texts = [
            f"{product['title']} {product['description']}"
            for product in products
        ]
        
        logger.info(f"Generating embeddings for {len(texts)} products")
        embeddings = self.embedding_service.generate_embeddings(texts)
        
        return embeddings
    
    def _store_products(
        self, 
        products: List[Dict[str, Any]], 
        embeddings: Any
    ):
        """
        Store products in SQLite and vectors in FAISS.
        
        Args:
            products: List of normalized product dictionaries
            embeddings: Numpy array of embeddings
        """
        # Store in SQLite
        self.product_repo.insert_products(products)
        
        # Store in FAISS
        product_ids = [product["id"] for product in products]
        self.vector_repo.add_vectors(product_ids, embeddings)
        
        logger.info("Products and embeddings stored successfully")
    
    @staticmethod
    def _safe_float(value: Any) -> float:
        """
        Safely convert value to float.
        
        Args:
            value: Value to convert
            
        Returns:
            Float value or None
        """
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


# Singleton instance
_ingestion_service_instance = None


def get_ingestion_service() -> IngestionService:
    """
    Get or create the singleton ingestion service instance.
    
    Returns:
        Shared IngestionService instance
    """
    global _ingestion_service_instance
    if _ingestion_service_instance is None:
        _ingestion_service_instance = IngestionService()
    return _ingestion_service_instance

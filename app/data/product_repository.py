"""
Repository for managing product data in SQLite database.
"""
import sqlite3
from typing import List, Dict, Optional, Any
import json
from pathlib import Path

from app.utils.logger import logger


class ProductRepository:
    """
    Repository for storing and retrieving product data using SQLite.
    
    This repository handles all product-related database operations,
    providing a clean abstraction over SQL queries.
    """
    
    def __init__(self, db_path: str = "data/products.db"):
        """
        Initialize the product repository.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_database()
        logger.info(f"Product repository initialized at {db_path}")
    
    def _init_database(self):
        """Create the products table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    attributes TEXT,
                    price REAL,
                    rating REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for common queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_category 
                ON products(category)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_price 
                ON products(price)
            """)
            conn.commit()
    
    def insert_products(self, products: List[Dict[str, Any]]) -> int:
        """
        Insert multiple products into the database.
        
        Args:
            products: List of product dictionaries with normalized fields
            
        Returns:
            Number of products successfully inserted
        """
        if not products:
            return 0
        
        inserted_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            for product in products:
                try:
                    # Convert attributes dict to JSON string if present
                    attributes_json = None
                    if product.get("attributes"):
                        attributes_json = json.dumps(product["attributes"])
                    
                    conn.execute("""
                        INSERT OR REPLACE INTO products 
                        (id, title, description, category, attributes, price, rating)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        product["id"],
                        product["title"],
                        product.get("description", ""),
                        product.get("category", ""),
                        attributes_json,
                        product.get("price"),
                        product.get("rating")
                    ))
                    inserted_count += 1
                except Exception as e:
                    logger.error(f"Error inserting product {product.get('id')}: {e}")
            
            conn.commit()
        
        logger.info(f"Inserted {inserted_count} products into database")
        return inserted_count
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a product by its ID.
        
        Args:
            product_id: Product identifier
            
        Returns:
            Product dictionary or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM products WHERE id = ?",
                (product_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return self._row_to_dict(row)
            return None
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Retrieve all products from the database.
        
        Returns:
            List of product dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM products")
            rows = cursor.fetchall()
            
            return [self._row_to_dict(row) for row in rows]
    
    def get_product_count(self) -> int:
        """
        Get total number of products in the database.
        
        Returns:
            Count of products
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM products")
            return cursor.fetchone()[0]
    
    def delete_all_products(self):
        """Delete all products from the database (for testing/reset)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM products")
            conn.commit()
        logger.info("All products deleted from database")
    
    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """
        Convert SQLite row to dictionary.
        
        Args:
            row: SQLite row object
            
        Returns:
            Dictionary representation of the row
        """
        product = dict(row)
        
        # Parse JSON attributes back to dict
        if product.get("attributes"):
            try:
                product["attributes"] = json.loads(product["attributes"])
            except json.JSONDecodeError:
                product["attributes"] = {}
        
        return product


# Singleton instance
_product_repository_instance = None


def get_product_repository() -> ProductRepository:
    """
    Get or create the singleton product repository instance.
    
    Returns:
        Shared ProductRepository instance
    """
    global _product_repository_instance
    if _product_repository_instance is None:
        _product_repository_instance = ProductRepository()
    return _product_repository_instance

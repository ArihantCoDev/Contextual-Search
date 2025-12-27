"""
Quick test script to verify ingestion works directly.
"""
import sys
sys.path.insert(0, 'D:/contextual-search')

from app.services.ingestion_service import get_ingestion_service

# Read the CSV file
with open('sample_products.csv', 'r', encoding='utf-8') as f:
    csv_data = f.read()

# Test ingestion
print("Testing ingestion pipeline...")
ingestion_service = get_ingestion_service()
result = ingestion_service.ingest_products(csv_data, data_format='csv')

print("\nResult:")
print(f"Status: {result['status']}")
print(f"Products ingested: {result['products_ingested']}")
print(f"Message: {result['message']}")

# Check stats
from app.data.product_repository import get_product_repository
from app.data.vector_repository import get_vector_repository

product_repo = get_product_repository()
vector_repo = get_vector_repository()

print(f"\nVerification:")
print(f"Products in database: {product_repo.get_product_count()}")
print(f"Vectors in index: {vector_repo.get_vector_count()}")

print("\nSample product:")
products = product_repo.get_all_products()
if products:
    print(f"ID: {products[0]['id']}")
    print(f"Title: {products[0]['title']}")
    print(f"Category: {products[0]['category']}")

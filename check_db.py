"""
Quick check if products exist in the database.
"""
import sys
sys.path.insert(0, 'D:/contextual-search')

from app.data.product_repository import get_product_repository
from app.data.vector_repository import get_vector_repository

product_repo = get_product_repository()
vector_repo = get_vector_repository()

print(f"\n=== Database Status ===")
print(f"Products in database: {product_repo.get_product_count()}")
print(f"Vectors in FAISS: {vector_repo.get_vector_count()}")

# Get sample products
products = product_repo.get_all_products()
if products:
    print(f"\nSample products:")
    for p in products[:5]:
        print(f"  - {p['title']}")
        print(f"    Category: {p.get('category', 'N/A')}, Price: ${p.get('price', 'N/A')}")
else:
    print("\n❗ No products found! Please run: python ingest_data.py")

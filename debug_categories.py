"""
Debug script to check what's happening with headphones search.
"""
import sys
sys.path.insert(0, 'D:/contextual-search')

# Test the intent extractor first
from app.nlp.intent_extractor import extract_intent

query = "headphones"
intent = extract_intent(query)

print("=== NLP Intent Extraction ===")
print(f"Query: '{query}'")
print(f"Semantic Query: '{intent['semantic_query']}'")
print(f"Constraints: {intent['constraints']}")
print(f"Category extracted: {intent['constraints'].get('category')}")

# Now test with search service
from app.services.search_service import SearchFilters

filters = SearchFilters()  # Empty filters (All Categories)
print(f"\n=== UI Filters ===")
print(f"Category: '{filters.category}'")
print(f"Is None: {filters.category is None}")
print(f"Is empty string: {filters.category == ''}")

# Check products in database
from app.data.product_repository import get_product_repository
repo = get_product_repository()
products = repo.get_all_products()

print(f"\n=== Database Products ===")
print(f"Total products: {len(products)}")

# Check for headphones category
headphones_products = [p for p in products if p.get('category') and 'headphone' in p['category'].lower()]
print(f"Products with 'headphone' in category: {len(headphones_products)}")

if headphones_products:
    print("\nSample headphones products:")
    for p in headphones_products[:3]:
        print(f"  - {p['title']}")
        print(f"    Category: {p.get('category')}")

# Check all unique categories
categories = set(p.get('category', 'None') for p in products)
print(f"\n=== Unique Categories in Database ===")
for cat in sorted(categories):
    count = len([p for p in products if p.get('category') == cat])
    print(f"  {cat}: {count} products")

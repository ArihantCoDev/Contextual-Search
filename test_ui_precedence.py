"""
Quick verification that NLP filtering works correctly.
Tests the specific case mentioned by the user: "Headphones under 2000"
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'D:/contextual-search')

from app.nlp.intent_extractor import extract_intent
from app.services.search_service import SearchFilters, SearchService

print("="*70)
print("VERIFYING NLP FILTER BUG FIX")
print("="*70)

service = SearchService()

# The exact case the user reported
print("\n🔍 Test: 'Headphones under 2000'")
print("-" * 70)

query = "Headphones under 2000"
intent = extract_intent(query)

print(f"Query: '{query}'")
print(f"NLP extracted: price_max = {intent['constraints']['price_max']}")
print(f"NLP extracted: category = {intent['constraints']['category']}")

# Simulate what frontend sends: empty filter object
empty_ui_filters = SearchFilters(
    category=None,
    price_min=None,
    price_max=None,
    min_rating=None
)

print(f"\nFrontend sends: Empty filter object (all None)")
merged = service._merge_filters(intent['constraints'], empty_ui_filters)

print(f"\n✅ RESULT after merge:")
print(f"   price_max = {merged.price_max}")
print(f"   category = {merged.category}")

# Verify the fix worked
if merged.price_max == 2000.0:
    print(f"\n✅ SUCCESS! NLP filter is being applied correctly!")
    print(f"   Products will be filtered to under ₹2000")
else:
    print(f"\n❌ FAILED! price_max should be 2000 but is {merged.price_max}")
    
if merged.category == "headphones":
    print(f"✅ Category filter also working correctly!")
else:
    print(f"❌ Category should be 'headphones' but is {merged.category}")

print("\n" + "="*70)

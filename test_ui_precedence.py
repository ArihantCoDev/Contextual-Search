"""
Test script to verify UI filter precedence over NLP extraction.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'D:/contextual-search')

from app.nlp.intent_extractor import extract_intent
from app.services.search_service import SearchFilters, SearchService

# Create a mock search service instance
service = SearchService()

print("="*70)
print("TESTING UI FILTER PRECEDENCE")
print("="*70)

# Test 1: NLP says "under 5000", UI says "under 10000" -> UI wins
print("\n--- Test 1: UI overrides NLP price ---")
query = "laptop under 5000"
intent = extract_intent(query)
print(f"Query: '{query}'")
print(f"NLP extracted: price_max = {intent['constraints']['price_max']}")

ui_filters = SearchFilters(price_max=10000)
merged = service._merge_filters(intent['constraints'], ui_filters)
print(f"UI filter: price_max = 10000")
print(f"Merged result: price_max = {merged.price_max}")
assert merged.price_max == 10000, "UI should override NLP!"
print("✓ PASS: UI filter overrode NLP")

# Test 2: NLP says "shoes", UI says "Electronics" -> UI wins
print("\n--- Test 2: UI overrides NLP category ---")
query = "Nike shoes"
intent = extract_intent(query)
print(f"Query: '{query}'")
print(f"NLP extracted: category = {intent['constraints']['category']}")

ui_filters = SearchFilters(category="Electronics")
merged = service._merge_filters(intent['constraints'], ui_filters)
print(f"UI filter: category = Electronics")
print(f"Merged result: category = {merged.category}")
assert merged.category == "Electronics", "UI should override NLP!"
print("✓ PASS: UI filter overrode NLP")

# Test 3: NLP says "rated above 4", UI says "no rating filter" -> UI wins (None)
print("\n--- Test 3: UI clears NLP rating filter ---")
query = "headphones rated above 4"
intent = extract_intent(query)
print(f"Query: '{query}'")
print(f"NLP extracted: rating_min = {intent['constraints']['rating_min']}")

ui_filters = SearchFilters(min_rating=None)  # UI explicitly says no rating filter
merged = service._merge_filters(intent['constraints'], ui_filters)
print(f"UI filter: min_rating = None")
print(f"Merged result: rating_min = {merged.min_rating}")
assert merged.min_rating is None, "UI should be able to clear NLP filter!"
print("✓ PASS: UI cleared NLP rating filter")

# Test 4: No UI filters at all -> NLP is used
print("\n--- Test 4: No UI filters, NLP is used ---")
query = "laptop under 5000 rated above 4"
intent = extract_intent(query)
print(f"Query: '{query}'")
print(f"NLP extracted: price_max={intent['constraints']['price_max']}, rating_min={intent['constraints']['rating_min']}")

merged = service._merge_filters(intent['constraints'], None)
print(f"UI filters: None")
print(f"Merged result: price_max={merged.price_max}, rating_min={merged.min_rating}")
assert merged.price_max == 5000 and merged.min_rating == 4.0, "NLP should be used when no UI filters!"
print("✓ PASS: NLP filters used when no UI filters provided")

# Test 5: Combined - UI overrides some, NLP fills others
print("\n--- Test 5: UI overrides price, NLP provides brand ---")
query = "Nike shoes under 3000"
intent = extract_intent(query)
print(f"Query: '{query}'")
print(f"NLP extracted: brand={intent['constraints']['brand']}, price_max={intent['constraints']['price_max']}")

ui_filters = SearchFilters(price_max=5000)  # UI changes price but doesn't set brand
merged = service._merge_filters(intent['constraints'], ui_filters)
print(f"UI filter: price_max=5000, brand=None")
print(f"Merged result: price_max={merged.price_max}, brand={merged.brand}")
assert merged.price_max == 5000 and merged.brand == "Nike", "UI should override price, NLP should provide brand!"
print("✓ PASS: Correct hybrid of UI and NLP")

print("\n" + "="*70)
print("ALL TESTS PASSED! ✓")
print("UI filters now strictly override NLP for category, price, and rating")
print("="*70)

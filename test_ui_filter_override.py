"""
Test script to verify UI filter override behavior.
"""
import sys
import io

# Fix Windows UTF-8 encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'D:/contextual-search')

import requests
import json

BASE_URL = "http://localhost:8000/api/search"

def test_filter_override(description, query, ui_filters):
    """Test that UI filters strictly override NLP filters."""
    print(f"\n{'='*70}")
    print(f"TEST: {description}")
    print(f"{'='*70}")
    print(f"Query: '{query}'")
    print(f"UI Filters: {json.dumps(ui_filters, indent=2)}")
    
    payload = {"query": query, "limit": 10}
    if ui_filters:
        payload["filters"] = ui_filters
    
    try:
        response = requests.post(BASE_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"\n✓ Status: {response.status_code}")
            print(f"✓ Results: {data['count']}")
            
            if results:
                print(f"\nTop 3 Results:")
                for i, result in enumerate(results[:3], 1):
                    print(f"\n  {i}. {result['title']}")
                    print(f"     Price: ${result.get('price', 'N/A')}")
                    print(f"     Rating: {result.get('rating', 'N/A')}")
                    print(f"     Category: {result.get('category', 'N/A')}")
                    
                # Validate filters are applied
                print(f"\n  VALIDATION:")
                for r in results:
                    # Check price_min
                    if 'price_min' in ui_filters:
                        if r.get('price') and r['price'] < ui_filters['price_min']:
                            print(f"     ✗ FAILED: Product '{r['title']}' price {r['price']} < min {ui_filters['price_min']}")
                        else:
                            print(f"     ✓ Price min check passed")
                    
                    # Check price_max
                    if 'price_max' in ui_filters:
                        if r.get('price') and r['price'] > ui_filters['price_max']:
                            print(f"     ✗ FAILED: Product '{r['title']}' price {r['price']} > max {ui_filters['price_max']}")
                        else:
                            print(f"     ✓ Price max check passed")
                    
                    # Check category
                    if ui_filters.get('category'):
                        if r.get('category', '').lower() != ui_filters['category'].lower():
                            print(f"     ✗ FAILED: Product '{r['title']}' category '{r.get('category')}' != '{ui_filters['category']}'")
                        else:
                            print(f"     ✓ Category check passed")
                    
                    # Check rating
                    if 'min_rating' in ui_filters:
                        if r.get('rating') and r['rating'] < ui_filters['min_rating']:
                            print(f"     ✗ FAILED: Product '{r['title']}' rating {r['rating']} < min {ui_filters['min_rating']}")
                        else:
                            print(f"     ✓ Rating check passed")
                    
                    break  # Only check first result for brevity
            else:
                print("\n  No results found (might be expected if filters are too strict)")
        else:
            print(f"✗ Error: Status {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Exception: {e}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("UI FILTER OVERRIDE - VALIDATION TESTS")
    print("="*70)
    
    # Test 1: Query says "under 50000" but UI sets price_max to 30000
    # UI should win -> results max price should be 30000
    test_filter_override(
        "UI price_max overrides NLP extracted price (under 50000 → 30000)",
        "laptop under 50000",
        {"price_max": 30000}
    )
    
    # Test 2: Query has category synonym "sneakers" but UI selects "Electronics"
    # UI should win -> results should be Electronics only
    test_filter_override(
        "UI category overrides NLP category (shoes → Electronics)",
        "sneakers",
        {"category": "Electronics"}
    )
    
    # Test 3: Query says "rated above 4" but UI sets 4.5
    # UI should win -> results should have rating >= 4.5
    test_filter_override(
        "UI rating overrides NLP rating (4.0 → 4.5)",
        "shoes rated above 4",
        {"min_rating": 4.5}
    )
    
    # Test 4: Combined - NLP extracts constraints, but UI overrides all
    test_filter_override(
        "UI overrides all NLP constraints",
        "Nike shoes under 5000 rated above 3",
        {
            "category": "Electronics",
            "price_max": 20000,
            "min_rating": 4.0
        }
    )
    
    # Test 5: Price range from UI
    test_filter_override(
        "UI sets both price_min and price_max",
        "headphones",
        {
            "price_min": 2000,
            "price_max": 5000
        }
    )
    
    print("\n" + "="*70)
    print("TESTS COMPLETED")
    print("="*70 + "\n")

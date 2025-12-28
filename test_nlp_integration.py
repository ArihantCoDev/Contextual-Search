"""
Integration test for NLP intent extractor with live search API.
"""
import sys
import io

# Fix Windows UTF-8 encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'D:/contextual-search')

import requests
import json

# Base URL - FIXED: endpoint is /api/search not /search
BASE_URL = "http://localhost:8000/api/search"

def test_search_query(query, description=""):
    """Test a search query and display results."""
    print(f"\n{'='*70}")
    if description:
        print(f"Test: {description}")
    print(f"Query: '{query}'")
    print(f"{'='*70}")
    
    try:
        response = requests.post(BASE_URL, json={"query": query, "limit": 5})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Results count: {data['count']}")
            
            if data['results']:
                print(f"\nTop {min(3, len(data['results']))} results:")
                for i, result in enumerate(data['results'][:3], 1):
                    print(f"\n  {i}. {result['title']}")
                    print(f"     Price: ${result.get('price', 'N/A')}")
                    print(f"     Rating: {result.get('rating', 'N/A')}")
                    print(f"     Category: {result.get('category', 'N/A')}")
                    print(f"     Similarity: {result['similarity_score']}")
                    if result.get('explanation'):
                        print(f"     Explanation: {result['explanation'][:100]}...")
            else:
                print("\n  No results found")
        else:
            print(f"✗ Error: Status {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Exception: {e}")


def run_integration_tests():
    """Run integration tests with various query patterns."""
    print("\n" + "="*70)
    print("NLP INTENT EXTRACTOR - INTEGRATION TESTS")
    print("="*70)
    
    # Test 1: Price upper bound
    test_search_query(
        "laptop under 50000",
        "Price upper bound filtering"
    )
    
    # Test 2: Price range
    test_search_query(
        "headphones between 2000 and 5000",
        "Price range filtering"
    )
    
    # Test 3: Rating filter
    test_search_query(
        "shoes rated above 4",
        "Rating filtering"
    )
    
    # Test 4: Approximate price
    test_search_query(
        "around 3000",
        "Approximate price (±15%)"
    )
    
    # Test 5: Brand filter
    test_search_query(
        "Nike shoes",
        "Brand filtering"
    )
    
    # Test 6: Combined constraints
    test_search_query(
        "Nike shoes under 3000 rated above 4",
        "Combined filters (brand + price + rating)"
    )
    
    # Test 7: Fuzzy keyword
    test_search_query(
        "cheap smartphones",
        "Fuzzy price intent (no hard filter)"
    )
    
    # Test 8: Category synonym
    test_search_query(
        "sneakers",
        "Category synonym (sneakers → shoes)"
    )
    
    print("\n" + "="*70)
    print("INTEGRATION TESTS COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_integration_tests()

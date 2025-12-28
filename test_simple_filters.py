"""
Simple test to check product data and verify basic filtering.
"""
import sys
import io

# Fix Windows UTF-8 encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'D:/contextual-search')

import requests

BASE_URL = "http://localhost:8000/api/search"

print("\n=== Testing Basic Search Without Filters ===")
response = requests.post(BASE_URL, json={"query": "laptop", "limit": 5})
if response.status_code == 200:
    data = response.json()
    print(f"Results: {data['count']}")
    
    if data['count'] > 0:
        print("\nSample products:")
        for r in data['results'][:5]:
            print(f"  - {r['title']}")
            print(f"    Price: ${r.get('price', 'N/A')}, Rating: {r.get('rating', 'N/A')}, Category: {r.get('category', 'N/A')}")
    
    # Now test with UI filter that should override NLP
    print("\n\n=== Testing With UI Category Filter (should override NLP category) ===")
    print("Query: 'sneakers' (NLP should extract category='shoes')")
    print("UI Filter: category='Footwear'")
    
    response2 = requests.post(BASE_URL, json={
        "query": "sneakers",
        "filters": {"category": "Footwear"},
        "limit": 5
    })
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"Results: {data2['count']}")
        
        if data2['count'] > 0:
            print("\nResults (should all be Footwear category):")
            for r in data2['results'][:5]:
                print(f"  - {r['title']}")
                print(f"    Category: {r.get('category', 'N/A')}")
                
                # Validation
                if r.get('category') != 'Footwear':
                    print(f"    ✗ FAILED: Category is '{r.get('category')}', expected 'Footwear'")
                else:
                    print(f"    ✓ PASSED: Category is correct")
        else:
            print("No results (check if Footwear category exists in data)")
    
    # Test price filter override
    print("\n\n=== Testing With UI Price Filter (should override NLP price) ===")
    print("Query: 'laptop under 100000' (NLP should extract price_max=100000)")
    print("UI Filter: price_max=50000 (should override to 50000)")
    
    response3 = requests.post(BASE_URL, json={
        "query": "laptop under 100000",
        "filters": {"price_max": 50000},
        "limit": 5
    })
    
    if response3.status_code == 200:
        data3 = response3.json()
        print(f"Results: {data3['count']}")
        
        if data3['count'] > 0:
            print("\nResults (should all be price <= 50000):")
            for r in data3['results'][:5]:
                print(f"  - {r['title']}")
                print(f"    Price: ${r.get('price', 'N/A')}")
                
                # Validation
                if r.get('price') and r['price'] > 50000:
                    print(f"    ✗ FAILED: Price {r['price']} > 50000")
                else:
                    print(f"    ✓ PASSED: Price is <= 50000")
else:
    print(f"Error: {response.status_code} - {response.text}")

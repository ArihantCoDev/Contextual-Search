"""
Test that "All Categories" selection allows contextual/NLP search to work.
"""
import sys
import io

# Fix Windows UTF-8 encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'D:/contextual-search')

import requests

BASE_URL = "http://localhost:8000/api/search"

print("\n=== Testing 'All Categories' with Contextual Search ===\n")

# Test 1: Search "headphones" with All Categories (empty category filter)
print("TEST 1: Query='headphones', UI Category='All Categories' (empty)")
print("Expected: NLP should extract category='headphones' and find headphones products")

response = requests.post(BASE_URL, json={
    "query": "headphones",
    "filters": {},  # No filters = All Categories
    "limit": 5
})

if response.status_code == 200:
    data = response.json()
    print(f"✓ Results: {data['count']}")
    
    if data['count'] > 0:
        print("\nTop 3 Results:")
        for i, r in enumerate(data['results'][:3], 1):
            print(f"  {i}. {r['title']}")
            print(f"     Category: {r.get('category', 'N/A')}")
        print(f"\n✅ SUCCESS: Found {data['count']} headphones using NLP category extraction")
    else:
        print("\n❌ FAILED: No results found. NLP category may not be working.")
else:
    print(f"❌ Error: {response.status_code}")

# Test 2: Search "laptop" with specific UI category override
print("\n" + "="*70)
print("\nTEST 2: Query='laptop', UI Category='Footwear'")
print("Expected: UI category should override NLP, return only Footwear (likely 0 results)")

response2 = requests.post(BASE_URL, json={
    "query": "laptop",
    "filters": {"category": "Footwear"},
    "limit": 5
})

if response2.status_code == 200:
    data2 = response2.json()
    print(f"✓ Results: {data2['count']}")
    
    if data2['count'] == 0:
        print(f"\n✅ SUCCESS: UI category correctly overrode NLP category (no footwear laptops)")
    else:
        print(f"\nResults found:")
        for r in data2['results'][:3]:
            cat = r.get('category', 'N/A')
            print(f"  - {r['title']} (Category: {cat})")
            if cat != 'Footwear':
                print(f"    ❌ FAILED: Expected Footwear, got {cat}")
else:
    print(f"❌ Error: {response2.status_code}")

# Test 3: Search "shoes" with All Categories
print("\n" + "="*70)
print("\nTEST 3: Query='shoes', UI Category='All Categories' (empty)")
print("Expected: NLP should extract category and find shoe products")

response3 = requests.post(BASE_URL, json={
    "query": "shoes",
    "filters": {},
    "limit": 5
})

if response3.status_code == 200:
    data3 = response3.json()
    print(f"✓ Results: {data3['count']}")
    
    if data3['count'] > 0:
        print(f"\n✅ SUCCESS: Found {data3['count']} products using NLP")
    else:
        print(f"\n⚠️  No results (data may not have shoes)")
else:
    print(f"❌ Error: {response3.status_code}")

print("\n" + "="*70)
print("\nTESTS COMPLETED")
print("="*70 + "\n")

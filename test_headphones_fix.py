"""
Quick test that headphones search works now.
"""
import requests

BASE_URL = "http://localhost:8000/api/search"

print("\n=== Testing Headphones Search with All Categories ===\n")

# Test with empty filters (All Categories)
response = requests.post(BASE_URL, json={
    "query": "headphones",
    "filters": {},
    "limit": 5
})

if response.status_code == 200:
    data = response.json()
    print(f"✓ Results: {data['count']}")
    
    if data['count'] > 0:
        print("\n✅ SUCCESS! Headphones found:")
        for i, r in enumerate(data['results'][:5], 1):
            print(f"  {i}. {r['title']}")
            print(f"     Category: {r.get('category', 'N/A')}, Price: ${r.get('price', 'N/A')}")
    else:
        print("\n❌ FAILED: Still no results")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")

# Test with specific category
print("\n\n=== Testing with UI Category=Electronics ===\n")
response2 = requests.post(BASE_URL, json={
    "query": "headphones",
    "filters": {"category": "Electronics"},
    "limit": 5
})

if response2.status_code == 200:
    data2 = response2.json()
    print(f"✓ Results: {data2['count']}")
    
    if data2['count'] > 0:
        print(f"\n✅ UI category filter working:")
        for i, r in enumerate(data2['results'][:3], 1):
            print(f"  {i}. {r['title']} (Category: {r.get('category')})")
else:
    print(f"❌ Error: {response2.status_code}")

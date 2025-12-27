"""
Direct test of the ingestion API endpoint.
"""
import requests

# Test the ingestion endpoint directly
print("Testing ingestion endpoint...")

url = "http://localhost:8000/ingest/products"

# Upload the sample CSV file
with open('sample_products.csv', 'rb') as f:
    files = {'file': ('sample_products.csv', f, 'text/csv')}
    response = requests.post(url, files=files)

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    result = response.json()
    print(f"\n✅ SUCCESS!")
    print(f"Products ingested: {result['products_ingested']}")
    print(f"Message: {result['message']}")
else:
    print(f"\n❌ FAILED!")
    print(f"Error: {response.text}")

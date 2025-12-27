import requests
import sys
import os

API_URL = "http://localhost:8000/ingest/products"
DEFAULT_FILE = "sample_products_500.csv"

def ingest_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return

    print(f"Ingesting {filepath}...")
    try:
        with open(filepath, "rb") as f:
            files = {"file": (os.path.basename(filepath), f, "text/csv")}
            response = requests.post(API_URL, files=files)
            
        if response.status_code == 200:
            print("Success!")
            print(response.json())
        else:
            print(f"Failed with status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    file_to_ingest = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE
    ingest_file(file_to_ingest)

import requests

QUERIES = ['Apollo Hospital', 'Hospital', 'Restaurant', 'ATM', 'Fuel Station', 'VIT', 'Velachery', 'Tambaram', '600042']

def run():
    print(f"{'*'*80}\\nDIAGNOSTIC TRACE SCRIPT STARTING\\n{'*'*80}")
    for q in QUERIES:
        print(f"\\n{'='*80}\\nExecuting Query: '{q}'\\n{'='*80}")
        try:
            response = requests.get(f"http://localhost:8000/search?q={q}&lat=13.0827&lon=80.2707", timeout=10)
            if response.status_code == 200:
                res_json = response.json()
                print(f"\\nAPI RESPONSE: Returned {len(res_json)} items.")
                print(f"First 10 IDs: {[r.get('id') for r in res_json[:10]]}")
                print(f"First 10 Names: {[r.get('name') for r in res_json[:10]]}")
            else:
                print(f"API ERROR: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    run()

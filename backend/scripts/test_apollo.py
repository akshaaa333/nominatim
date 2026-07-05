import requests
import json

response = requests.get("http://localhost:8000/search?q=Apollo&lat=13.0827&lon=80.2707", timeout=10)
if response.status_code == 200:
    res_json = response.json()
    print(f"API RESPONSE: Returned {len(res_json)} items.")
    for i, r in enumerate(res_json[:20]):
        print(f"{i+1}. {r.get('name')} (ID: {r.get('id')}) | {r.get('provider')} | Score: {r.get('final_score')} | Dist: {r.get('distance_meters')} | Match: {r.get('matched_by')}")
else:
    print(f"API ERROR: {response.status_code} - {response.text}")

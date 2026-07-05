import requests
res = requests.get('http://127.0.0.1:8000/search?q=hospital&lat=12.9910579&lon=80.2195223').json()
for idx, r in enumerate(res[:5]):
    print(f"{idx}. {r.get('name')} | dist: {r.get('distance_meters')} | bonus: {r.get('distance_bonus')} | final: {r.get('final_score')} | prov: {r.get('provider')} | match: {r.get('matched_by')}")

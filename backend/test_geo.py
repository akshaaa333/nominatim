import re

def generate_fallback_queries(address: str):
    queries = []
    queries.append(address)
    
    parts = [p.strip() for p in address.split(',')]
    
    if len(parts) > 1:
        # Attempt 2: Remove place/building name
        queries.append(", ".join(parts[1:]))
        
        # Attempt 3: Area + City + Pincode
        if len(parts) >= 3:
            queries.append(", ".join(parts[-2:]))
        else:
            queries.append(parts[-1])
            
        # Attempt 4: Area + City
        area_city_pin = queries[-1]
        area_city = re.sub(r'\b\d{6}\b', '', area_city_pin).strip().strip(',')
        area_city = re.sub(r'\s+', ' ', area_city).strip(',')
        if area_city:
            queries.append(area_city)
            
    # Attempt 5: Pincode only
    pincode_match = re.search(r'\b(\d{6})\b', address)
    if pincode_match:
        queries.append(pincode_match.group(1))
        
    unique = []
    seen = set()
    for q in queries:
        q = q.strip().strip(',')
        if q and q.lower() not in seen:
            unique.append(q)
            seen.add(q.lower())
    return unique

print(generate_fallback_queries('Altis Ashraya, Shriram City Road, Mangadu, Chennai 600122'))
print(generate_fallback_queries('SRM University, Kattankulathur'))
print(generate_fallback_queries('Phoenix MarketCity Chennai'))

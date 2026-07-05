import httpx
import re
from typing import Dict, Any, Optional, List
from app.core.config import settings

class GeocoderService:
    def __init__(self):
        self.base_url = settings.NOMINATIM_URL

    def _generate_fallback_queries(self, address: str) -> List[str]:
        queries = []
        # Attempt 1: Full address
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

    def _rank_candidates(self, results: List[Dict[str, Any]], address: str) -> Dict[str, Any]:
        has_chennai = 'chennai' in address.lower()
        pincode_match = re.search(r'\b(\d{6})\b', address)
        target_pincode = pincode_match.group(1) if pincode_match else None
        
        def get_score(res):
            score = float(res.get("importance", 0.0))
            addr = res.get("address", {})
            # Prefer exact postcode
            if target_pincode and addr.get("postcode") == target_pincode:
                score += 10.0
            # Prefer Chennai when address contains Chennai
            if has_chennai:
                dn = res.get("display_name", "").lower()
                if "chennai" in dn:
                    score += 5.0
            return score
            
        return sorted(results, key=get_score, reverse=True)[0]

    async def geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """Queries local Nominatim for the given address to get lat, lon, and address details."""
        queries = self._generate_fallback_queries(address)
        
        async with httpx.AsyncClient() as client:
            for q in queries:
                try:
                    url = f"{self.base_url}/search"
                    params = {
                        "q": q,
                        "format": "json",
                        "addressdetails": 1,
                        "limit": 5
                    }
                    response = await client.get(url, params=params)
                    
                    print(f"Request URL: {url}")
                    print(f"Query string: {q}")
                    print(f"HTTP status: {response.status_code}")
                    print(f"Response body: {response.text}")
                    
                    response.raise_for_status()
                    data = response.json()
                    if not data:
                        continue
                    
                    best_result = self._rank_candidates(data, address)
                    addr_details = best_result.get("address", {})
                    
                    return {
                        "latitude": float(best_result.get("lat")),
                        "longitude": float(best_result.get("lon")),
                        "district": addr_details.get("county") or addr_details.get("state_district"),
                        "state": addr_details.get("state"),
                        "pincode": addr_details.get("postcode"),
                        "country": addr_details.get("country"),
                        "display_name": best_result.get("display_name"),
                        "exact_match": q == queries[0]
                    }
                except Exception as e:
                    print(f"GeocoderService error: {e}")
                    continue
        return None

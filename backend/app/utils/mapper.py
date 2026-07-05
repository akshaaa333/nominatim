from typing import Dict, Any
from app.schemas.place import SearchResultResponse

def map_nominatim_to_place_response(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map a raw Nominatim result to a unified SearchResultResponse format.
    """
    # Extract location hierarchy if available from address
    address = item.get("address", {})
    district = address.get("state_district") or address.get("county") or address.get("city_district")
    state = address.get("state")
    country = address.get("country")
    
    # Safe float conversion
    try:
        lat = float(item.get("lat", 0.0))
        lon = float(item.get("lon", 0.0))
    except (ValueError, TypeError):
        lat = 0.0
        lon = 0.0

    place_id = item.get("place_id")
    
    # Construct dict matching SearchResultResponse
    response_data = {
        "id": None,
        "name": item.get("name") or item.get("display_name", "").split(",")[0],
        "display_name": item.get("display_name"),
        "latitude": lat,
        "longitude": lon,
        "category": item.get("type") or item.get("class"),
        "district": district,
        "state": state,
        "country": country,
        "search_key": None,
        "source": "nominatim",
        "place_id": str(place_id) if place_id else None,
        "search_count": 0,
        "match_type": "nominatim",
        "importance_score": float(item.get("importance", 0.0)),
        "place_rank": int(item.get("place_rank", 0))
    }
    
    # Validate and return as dict
    return SearchResultResponse.model_validate(response_data).model_dump(mode='json')

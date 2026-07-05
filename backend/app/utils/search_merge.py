from typing import List
from app.schemas.place import SearchResultResponse
from app.utils.geo import haversine_distance

def deduplicate_results(results: List[SearchResultResponse]) -> List[SearchResultResponse]:
    """
    Remove duplicates from a merged list of search results.
    Prefers 'goride' provider when duplicates exist.
    """
    unique_places = {}
    
    for place in results:
        is_duplicate = False
        duplicate_key = None
        
        # 1. Match by place_id if present
        if place.place_id:
            duplicate_key = f"id_{place.place_id}"
        
        # 2. Match by normalized name and coordinate distance
        norm_name = place.name.lower().strip() if place.name else ""
        
        if duplicate_key in unique_places:
            is_duplicate = True
        else:
            # Check by distance & name
            for existing_key, existing_place in unique_places.items():
                existing_norm = existing_place.name.lower().strip() if existing_place.name else ""
                # Fuzzier matching: substring match
                name_match = (norm_name and existing_norm) and (
                    norm_name in existing_norm or existing_norm in norm_name
                )
                if name_match:
                    dist = haversine_distance(
                        place.latitude, place.longitude,
                        existing_place.latitude, existing_place.longitude
                    )
                    if dist < 50.0:
                        is_duplicate = True
                        duplicate_key = existing_key
                        break
        
        if is_duplicate and duplicate_key:
            existing = unique_places[duplicate_key]
            # Replace if new one is from 'goride' and existing is not
            if place.provider == 'goride' and existing.provider != 'goride':
                unique_places[duplicate_key] = place
        else:
            # Generate a key if it didn't have one
            key = duplicate_key or f"name_{norm_name}_{place.latitude}_{place.longitude}"
            unique_places[key] = place
            
    return list(unique_places.values())

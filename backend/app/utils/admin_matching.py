from app.schemas.place import SearchResultResponse
from app.utils.query_intent import IntentContext

def matches_admin_area(place: SearchResultResponse, context: IntentContext) -> bool:
    """
    Check if a place belongs to the admin area specified in the intent context.
    """
    if not context.admin_area:
        return False
        
    target = context.admin_area.lower()
    
    if place.district and target in place.district.lower():
        return True
        
    if place.state and target in place.state.lower():
        return True
        
    if place.name and target in place.name.lower():
        return True
        
    # In future, expand to city, suburb, municipality, etc.
    return False

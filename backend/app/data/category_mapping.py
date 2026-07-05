from typing import Dict, Tuple

# Mapping from OSM tags (key, value) to normalized category names
CATEGORY_MAP: Dict[Tuple[str, str], str] = {
    # Healthcare
    ("amenity", "hospital"): "Hospitals",
    ("amenity", "general_hospital"): "Hospitals",
    ("healthcare", "hospital"): "Hospitals",
    ("amenity", "clinic"): "Clinics",
    ("amenity", "doctors"): "Clinics",
    ("healthcare", "clinic"): "Clinics",
    ("amenity", "pharmacy"): "Pharmacies",
    ("shop", "chemist"): "Pharmacies",
    ("healthcare", "pharmacy"): "Pharmacies",
    ("amenity", "dentist"): "Clinics",
    ("amenity", "veterinary"): "Clinics",

    # Food & Dining
    ("amenity", "restaurant"): "Restaurants",
    ("amenity", "cafe"): "Cafes",
    ("amenity", "food_court"): "Restaurants",
    ("amenity", "fast_food"): "Restaurants",
    ("amenity", "bar"): "Bars",
    ("amenity", "pub"): "Bars",
    ("amenity", "ice_cream"): "Restaurants",

    # Shopping
    ("shop", "mall"): "Malls",
    ("shop", "shopping_mall"): "Malls",
    ("shop", "supermarket"): "Supermarkets",
    ("shop", "convenience"): "Convenience Stores",
    ("shop", "department_store"): "Department Stores",
    ("shop", "clothes"): "Shopping",
    ("shop", "bakery"): "Bakeries",
    ("shop", "electronics"): "Shopping",
    ("shop", "mobile_phone"): "Shopping",

    # Education
    ("amenity", "school"): "Schools",
    ("amenity", "college"): "Colleges",
    ("amenity", "university"): "Universities",
    ("amenity", "library"): "Libraries",

    # Transport
    ("railway", "station"): "Railway Stations",
    ("railway", "halt"): "Railway Stations",
    ("railway", "subway_entrance"): "Metro Stations",
    ("public_transport", "station"): "Bus Stations",
    ("public_transport", "platform"): "Bus Stops",
    ("highway", "bus_stop"): "Bus Stops",
    ("amenity", "bus_station"): "Bus Stations",
    ("aeroway", "aerodrome"): "Airports",

    # Government
    ("amenity", "police"): "Police Stations",
    ("amenity", "fire_station"): "Fire Stations",
    ("amenity", "post_office"): "Post Offices",
    ("amenity", "townhall"): "Government",
    ("amenity", "courthouse"): "Courts",

    # Finance
    ("amenity", "bank"): "Banks",
    ("amenity", "atm"): "ATMs",

    # Fuel
    ("amenity", "fuel"): "Fuel Stations",
    ("amenity", "charging_station"): "EV Charging Stations",

    # Tourism
    ("tourism", "attraction"): "Tourist Attractions",
    ("tourism", "museum"): "Museums",
    ("tourism", "gallery"): "Museums",
    ("tourism", "viewpoint"): "Tourist Attractions",
    ("tourism", "hotel"): "Hotels",
    ("tourism", "guest_house"): "Hotels",
    ("natural", "beach"): "Beaches",
    ("water", "lake"): "Lakes",
    ("natural", "water"): "Lakes",

    # Religion
    ("amenity", "place_of_worship"): "Places of Worship", # Will be further split by religion tag later if needed

    # Leisure
    ("leisure", "park"): "Parks",
    ("leisure", "stadium"): "Stadiums",
    ("leisure", "sports_centre"): "Sports Centres",
    ("leisure", "playground"): "Parks",

    # Business
    ("building", "commercial"): "Commercial Buildings",
    ("building", "retail"): "Commercial Buildings"
}

# Any special generic rules like office=* -> Offices
def get_normalized_category(tags: Dict[str, str]) -> str | None:
    """
    Returns the normalized category string for a given set of OSM tags.
    If it doesn't match any POI criteria, returns None.
    """
    # 1. Check exact map
    for (k, v), category in CATEGORY_MAP.items():
        if tags.get(k) == v:
            if category == "Places of Worship":
                rel = tags.get("religion")
                if rel == "hindu": return "Temples"
                if rel == "christian": return "Churches"
                if rel == "muslim": return "Mosques"
                if rel == "buddhist": return "Shrines"
                if rel == "jain": return "Temples"
                return category
            return category
            
    # 2. Check wildcard business rule (office=*)
    if "office" in tags:
        return "Offices"
        
    return None

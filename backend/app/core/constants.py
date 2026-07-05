SEARCH_WEIGHTS = {
    "exact": 100,
    "prefix": 80,
    "partial": 60,
    "fuzzy": 40,
    "category": 10,
    "district": 10,
    "pincode": 10,
    "popularity": 5,
}

# Candidate search limits for the GoRide repository
EXACT_PLACE_CANDIDATE_LIMIT = 50
CATEGORY_CANDIDATE_LIMIT = 100
PINCODE_CANDIDATE_LIMIT = 100
GENERIC_CANDIDATE_LIMIT = 50
ADMIN_AREA_CANDIDATE_LIMIT = 100

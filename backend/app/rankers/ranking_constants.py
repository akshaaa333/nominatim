# Token match scoring
EXACT_MATCH_BONUS = 100.0
WHOLE_TOKEN_MATCH_BONUS = 90.0
PREFIX_MATCH_BONUS = 70.0
PARTIAL_MATCH_BONUS = 50.0

# Context specific scoring
CATEGORY_MATCH_BONUS = 50.0
ADMIN_MATCH_BONUS = 50.0
PINCODE_MATCH_BONUS = 100.0

# Global multipliers / additions
GORIDE_PROVIDER_BONUS = 15.0
POPULARITY_WEIGHT = 1.0

# Importance logic
# Importance from Nominatim is usually between 0.0 and 1.0
IMPORTANCE_WEIGHT = 50.0

# Proximity logic (Continuous Decay)
MAX_DISTANCE_BONUS = 100.0
DISTANCE_DECAY_FACTOR = 10000.0

from app.utils.geo import haversine_distance
from app.rankers.ranking_constants import MAX_DISTANCE_BONUS, DISTANCE_DECAY_FACTOR

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates distance in meters between two points.
    Wraps the existing haversine_distance function.
    """
    return haversine_distance(lat1, lon1, lat2, lon2)

def calculate_distance_bonus(distance_meters: float) -> float:
    """
    Calculates a proximity bonus using a continuous decay function.
    Closer distances approach MAX_DISTANCE_BONUS.
    Further distances gracefully approach 0.
    """
    bonus = MAX_DISTANCE_BONUS / (1 + (distance_meters / DISTANCE_DECAY_FACTOR))
    return round(bonus, 2)

def is_nearby(distance_meters: float, threshold: float = 5000.0) -> bool:
    """
    Determines if a place is 'nearby' based on a threshold.
    """
    return distance_meters <= threshold

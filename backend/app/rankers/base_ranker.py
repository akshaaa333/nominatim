from abc import ABC, abstractmethod
from typing import List
from app.schemas.place import SearchResultResponse
from app.utils.query_intent import IntentContext, IntentType
from app.utils.proximity import calculate_distance, calculate_distance_bonus
from app.rankers.ranking_constants import (
    GORIDE_PROVIDER_BONUS,
    IMPORTANCE_WEIGHT,
    POPULARITY_WEIGHT
)

class BaseRanker(ABC):
    """
    Abstract base ranker that handles generic shared scoring like 
    popularity, provider bonus, distance, and final tallying.
    """
    
    @abstractmethod
    def calculate_intent_bonus(self, place: SearchResultResponse, context: IntentContext) -> None:
        """
        Subclasses must implement this to assign context-specific bonuses.
        """
        pass

    def rank(self, results: List[SearchResultResponse], context: IntentContext, profiler=None) -> List[SearchResultResponse]:
        import time
        if profiler:
            t_sem_start = time.perf_counter()
            
        for place in results:
            # Clear old values just in case
            place.token_bonus = 0.0
            place.category_bonus = 0.0
            place.admin_bonus = 0.0
            place.pincode_bonus = 0.0
            place.distance_bonus = 0.0
            place.distance_meters = None
            
            # 1. Apply Subclass Intent Bonuses
            self.calculate_intent_bonus(place, context)
            
            # 2. Shared Bonuses
            place.provider_bonus = GORIDE_PROVIDER_BONUS if place.provider == 'goride' else 0.0
            place.popularity_bonus = float(place.search_count or 0) * POPULARITY_WEIGHT
            place.importance_bonus = (place.importance_score or 0.0) * IMPORTANCE_WEIGHT
            
            # 3. Distance
            if context.latitude and context.longitude and place.latitude and place.longitude:
                if profiler:
                    t_dist = time.perf_counter()
                
                dist = calculate_distance(context.latitude, context.longitude, place.latitude, place.longitude)
                place.distance_meters = round(dist)
                # Do not apply distance bonus to PINCODE or ADMIN_AREA
                if context.intent not in [IntentType.PINCODE, IntentType.ADMIN_AREA]:
                    place.distance_bonus = calculate_distance_bonus(dist)
                    
                if profiler:
                    elapsed = (time.perf_counter() - t_dist) * 1000.0
                    profiler.timings["distance_ranking_ms"] = profiler.timings.get("distance_ranking_ms", 0.0) + elapsed
            
            # 4. Final Tally
            place.semantic_score = (
                (place.base_score or 0.0) +
                place.token_bonus +
                place.category_bonus +
                place.admin_bonus +
                place.pincode_bonus +
                place.provider_bonus +
                place.importance_bonus +
                place.popularity_bonus
            )
            
            place.final_score = place.semantic_score + place.distance_bonus
            
            # Frontend compat
            place.score = place.final_score
            
        if profiler:
            # Semantic ranking is total loop time MINUS distance time
            elapsed_total = (time.perf_counter() - t_sem_start) * 1000.0
            dist_time = profiler.timings.get("distance_ranking_ms", 0.0)
            profiler.timings["semantic_ranking_ms"] = elapsed_total - dist_time
            
        if profiler:
            with profiler.profile("sorting_ms"):
                results = self.sort_results(results, context)
        else:
            results = self.sort_results(results, context)
            
        return results

    def sort_results(self, results: List[SearchResultResponse], context: IntentContext) -> List[SearchResultResponse]:
        """
        Default sorting strategy. Subclasses should override if they need custom sorting.
        """
        results.sort(key=lambda x: (
            -x.final_score,
            x.distance_meters if (x.distance_meters is not None and context.latitude and context.longitude) else float('inf'),
            x.place_id or ""
        ))
        return results

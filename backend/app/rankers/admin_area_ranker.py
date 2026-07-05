from app.rankers.base_ranker import BaseRanker
from app.schemas.place import SearchResultResponse
from app.utils.query_intent import IntentContext
from app.utils.admin_matching import matches_admin_area
from app.rankers.ranking_constants import ADMIN_MATCH_BONUS

class AdminAreaRanker(BaseRanker):
    """
    Optimized for administrative area searches.
    Boosts places that fall inside the requested admin area.
    """
    def calculate_intent_bonus(self, place: SearchResultResponse, context: IntentContext) -> None:
        if matches_admin_area(place, context):
            place.admin_bonus = ADMIN_MATCH_BONUS
            place.matched_by = "admin_area"

    def sort_results(self, results: list[SearchResultResponse], context: IntentContext) -> list[SearchResultResponse]:
        # Restrict results to the requested area
        filtered_results = [r for r in results if getattr(r, 'matched_by', None) == "admin_area"]
        
        if context.latitude and context.longitude:
            filtered_results.sort(key=lambda x: (
                -x.final_score,
                x.distance_meters if x.distance_meters is not None else float('inf'),
                x.place_id or ""
            ))
        else:
            filtered_results.sort(key=lambda x: (
                -x.final_score,
                x.place_id or ""
            ))
            
        return filtered_results

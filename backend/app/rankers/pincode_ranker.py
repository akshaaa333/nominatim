from app.rankers.base_ranker import BaseRanker
from app.schemas.place import SearchResultResponse
from app.utils.query_intent import IntentContext
from app.rankers.ranking_constants import PINCODE_MATCH_BONUS

class PincodeRanker(BaseRanker):
    """
    Optimized for pincode searches.
    """
    def calculate_intent_bonus(self, place: SearchResultResponse, context: IntentContext) -> None:
        if context.pincode and place.pincode == context.pincode:
            place.pincode_bonus = PINCODE_MATCH_BONUS
            place.matched_by = "pincode"

    def sort_results(self, results: list[SearchResultResponse], context: IntentContext) -> list[SearchResultResponse]:
        # Restrict results to the requested pincode
        filtered_results = [r for r in results if getattr(r, 'matched_by', None) == "pincode"]
        
        if context.latitude and context.longitude:
            filtered_results.sort(key=lambda x: (
                x.distance_meters if x.distance_meters is not None else float('inf'),
                -x.final_score,
                x.place_id or ""
            ))
        else:
            filtered_results.sort(key=lambda x: (
                -x.final_score,
                x.place_id or ""
            ))
            
        return filtered_results

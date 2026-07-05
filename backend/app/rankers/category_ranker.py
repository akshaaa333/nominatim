from app.rankers.base_ranker import BaseRanker
from app.schemas.place import SearchResultResponse
from app.utils.query_intent import IntentContext
from app.rankers.ranking_constants import CATEGORY_MATCH_BONUS

class CategoryRanker(BaseRanker):
    """
    Optimized for category searches. 
    Does not score based on name string matches. Only boosts items whose 
    actual category exactly matches the detected canonical category.
    """
    def calculate_intent_bonus(self, place: SearchResultResponse, context: IntentContext) -> None:
        if not context.category or not place.category:
            return
            
        # The user requested that CategoryRanker should not understand aliases.
        # It simply compares place.category against context.category.
        # However, place.category might be "Hospitals" or "hospital". We'll do a simple lowercase check.
        if context.category.lower() in place.category.lower():
            place.category_bonus = CATEGORY_MATCH_BONUS
            place.matched_by = "category"

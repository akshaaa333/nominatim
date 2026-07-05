from app.utils.query_intent import IntentType, IntentContext
from app.rankers.base_ranker import BaseRanker
from app.rankers.place_ranker import PlaceRanker
from app.rankers.category_ranker import CategoryRanker
from app.rankers.admin_area_ranker import AdminAreaRanker
from app.rankers.pincode_ranker import PincodeRanker

class FallbackRanker(BaseRanker):
    """
    Default ranker when intent is UNKNOWN. Applies no specific intent bonus.
    """
    def calculate_intent_bonus(self, place, context):
        place.matched_by = "unknown"

class RankerFactory:
    """
    Selects the appropriate ranking strategy based on the query intent.
    """
    @staticmethod
    def get_ranker(context: IntentContext) -> BaseRanker:
        if context.intent == IntentType.EXACT_PLACE:
            return PlaceRanker()
        elif context.intent == IntentType.CATEGORY:
            return CategoryRanker()
        elif context.intent == IntentType.ADMIN_AREA:
            return AdminAreaRanker()
        elif context.intent == IntentType.PINCODE:
            return PincodeRanker()
        else:
            # For UNKNOWN, we default to string token matching
            return FallbackRanker()

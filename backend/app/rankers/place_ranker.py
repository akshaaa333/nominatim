import re
from app.rankers.base_ranker import BaseRanker
from app.schemas.place import SearchResultResponse
from app.utils.query_intent import IntentContext
from app.utils.normalization import normalize_search_key
from app.rankers.ranking_constants import (
    EXACT_MATCH_BONUS,
    WHOLE_TOKEN_MATCH_BONUS,
    PREFIX_MATCH_BONUS,
    PARTIAL_MATCH_BONUS
)

class PlaceRanker(BaseRanker):
    """
    Optimized for exact place queries. Heavily favors string token matches.
    """
    def rank(self, results, context, profiler=None):
        # We can pre-compile regexes before looping
        self.exact_token_pattern = re.compile(rf"\b{re.escape(context.normalized_query)}\b")
        self.prefix_token_pattern = re.compile(rf"\b{re.escape(context.normalized_query)}")
        return super().rank(results, context, profiler)

    def calculate_intent_bonus(self, place: SearchResultResponse, context: IntentContext) -> None:
        token_bonus = 0.0
        norm_name = normalize_search_key(place.name) if place.name else ""
        
        if norm_name == context.normalized_query:
            token_bonus = max(token_bonus, EXACT_MATCH_BONUS)
            place.matched_by = "exact_name"
        elif self.exact_token_pattern.search(norm_name):
            token_bonus = max(token_bonus, WHOLE_TOKEN_MATCH_BONUS)
            place.matched_by = "whole_token"
        elif self.prefix_token_pattern.search(norm_name):
            token_bonus = max(token_bonus, PREFIX_MATCH_BONUS)
            place.matched_by = "prefix_token"
        elif context.normalized_query in norm_name:
            token_bonus = max(token_bonus, PARTIAL_MATCH_BONUS)
            place.matched_by = "partial_token"
            
        place.token_bonus = token_bonus


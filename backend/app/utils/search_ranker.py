from typing import List
from app.schemas.place import SearchResultResponse
from app.utils.query_intent import IntentContext
from app.rankers.ranker_factory import RankerFactory

def rank_results(results: List[SearchResultResponse], context: IntentContext, profiler = None) -> List[SearchResultResponse]:
    """
    Facade for the strategy-based ranking engine.
    """
    ranker = RankerFactory.get_ranker(context)
    return ranker.rank(results, context, profiler)

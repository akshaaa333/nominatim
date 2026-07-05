import asyncio
import logging
from typing import List, Optional
from app.providers.search_provider import SearchProvider
from app.schemas.place import SearchResultResponse
from app.utils.search_merge import deduplicate_results
from app.utils.search_ranker import rank_results
from app.utils.query_intent import detect_intent

logger = logging.getLogger(__name__)

async def run_search_pipeline(
    query: str, 
    providers: List[SearchProvider], 
    lat: Optional[float] = None, 
    lon: Optional[float] = None,
    profiler = None
) -> List[SearchResultResponse]:
    """
    Orchestrates the complete search pipeline concurrently.
    """
    # 1. Intent Detection
    if profiler:
        profiler.record_metadata("query", query)
        with profiler.profile("intent_ms"):
            intent_context = detect_intent(query, lat, lon)
        profiler.record_metadata("intent", intent_context.intent)
    else:
        intent_context = detect_intent(query, lat, lon)
    
    logger.info(f"Query: {query}")
    logger.info(f"Detected Intent: {intent_context.intent}")
    
    if len(intent_context.normalized_query) < 2:
        return []
        
    # 2. Execute all providers concurrently
    if profiler:
        tasks = [provider.search(query, intent_context, profiler=profiler) for provider in providers]
    else:
        tasks = [provider.search(query, intent_context) for provider in providers]
        
    provider_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 3. Flatten the results
    all_results = []
    if profiler:
        with profiler.profile("merge_ms"):
            for res_list in provider_results:
                if isinstance(res_list, list):
                    all_results.extend(res_list)
                elif isinstance(res_list, Exception):
                    print(f"PROVIDER EXCEPTION: {res_list}")
                    profiler.record_metadata("provider_exception", str(res_list))
    else:
        for res_list in provider_results:
            if isinstance(res_list, list):
                all_results.extend(res_list)
            
    # 4. Deduplicate
    if profiler:
        with profiler.profile("deduplication_ms"):
            unique_results = deduplicate_results(all_results)
        profiler.record_count("merged", len(all_results))
        profiler.record_count("deduplicated", len(unique_results))
    else:
        unique_results = deduplicate_results(all_results)
    
    # 5. Rank & Limit
    if profiler:
        final_results = rank_results(unique_results, intent_context, profiler=profiler)
        profiler.record_count("ranked", len(final_results))
    else:
        final_results = rank_results(unique_results, intent_context)
    


    return final_results


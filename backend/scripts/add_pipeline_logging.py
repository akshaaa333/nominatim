import os

with open("app/utils/search_pipeline.py", "r", encoding="utf-8") as f:
    code = f.read()

logging_code = """
    # --- TEMPORARY DEBUG LOGGING ---
    if profiler:
        req_id = profiler.request_id
        intent = intent_context.intent
        repo_method = profiler.metadata.get("repository_method", "UNKNOWN")
        repo_count = profiler.counts.get("goride_raw", 0)
        provider_count = profiler.counts.get("nominatim_raw", 0)
        merged_count = profiler.counts.get("merged", 0)
        ranked_count = profiler.counts.get("ranked", 0)
        final_count = len(final_results)
        
        # Get first 10 candidate IDs from the GoRide provider if available
        # since we want to see what the repository returned.
        # Actually all_results has everything.
        first_10_ids = [res.id for res in all_results if getattr(res, "provider", "") == "goride"][:10]
        if not first_10_ids:
            # Fallback to all
            first_10_ids = [res.id for res in all_results][:10]

        logger.info(f"--- DEBUG PIPELINE [{req_id}] ---")
        logger.info(f"Intent: {intent}")
        logger.info(f"Repository Method: {repo_method}")
        logger.info(f"Repository Candidate Count: {repo_count}")
        logger.info(f"Candidate IDs (first 10): {first_10_ids}")
        logger.info(f"Provider Candidate Count (Nominatim): {provider_count}")
        logger.info(f"Merged Count: {merged_count}")
        logger.info(f"Ranked Count: {ranked_count}")
        logger.info(f"Final Returned Count: {final_count}")
        logger.info(f"-----------------------------------")
    # --- END DEBUG LOGGING ---

    return final_results
"""

code = code.replace("    return final_results", logging_code)

with open("app/utils/search_pipeline.py", "w", encoding="utf-8") as f:
    f.write(code)

import os
import re

def modify_file(filepath, callback):
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
    new_code = callback(code)
    if new_code != code:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_code)
        print(f"Instrumented {filepath}")

def inst_pipeline(code):
    # Remove previous logging if any
    code = re.sub(r'# --- PIPELINE DIAGNOSTICS ---.*?# --- END PIPELINE DIAGNOSTICS ---', '', code, flags=re.DOTALL)
    
    new_log = """
    # --- PIPELINE DIAGNOSTICS ---
    print(f"\\n{'='*80}")
    print(f"PIPELINE DIAGNOSTICS [Query: '{query}']")
    print(f"Request ID: {getattr(profiler, 'request_id', 'NO_ID') if profiler else 'NO_ID'}")
    print(f"Detected Intent: {intent_context.intent}")
    
    # We don't have Repository Selected here, it's inside GoRideProvider
    
    goride_results = [r for r in all_results if getattr(r, 'provider', '') == 'goride']
    nominatim_results = [r for r in all_results if getattr(r, 'provider', '') == 'nominatim']
    
    print(f"GoRide Candidate Count: {len(goride_results)}")
    print(f"GoRide First 10 IDs: {[getattr(r, 'id', None) for r in goride_results[:10]]}")
    print(f"GoRide First 10 Names: {[getattr(r, 'name', None) for r in goride_results[:10]]}")
    
    print(f"Nominatim Candidate Count: {len(nominatim_results)}")
    
    print(f"Merged Count: {len(all_results)}")
    print(f"Merged First 10 IDs: {[getattr(r, 'id', None) for r in all_results[:10]]}")
    
    print(f"Deduplicated Count: {len(unique_results)}")
    print(f"Deduplicated First 10 IDs: {[getattr(r, 'id', None) for r in unique_results[:10]]}")
    
    print(f"Candidate Count Entering Ranker: {len(unique_results)}")
    print(f"Candidate Count Leaving Ranker: {len(final_results)}")
    print(f"Final API Response Count: {len(final_results)}")
    print(f"{'='*80}\\n")
    # --- END PIPELINE DIAGNOSTICS ---
    return final_results"""
    
    return code.replace("    return final_results", new_log)

def inst_goride_provider(code):
    new_log = """
        # --- GORIDE PROVIDER DIAGNOSTICS ---
        print(f"GoRideProvider: Repository Rows Received: {len(local_results)}")
        print(f"GoRideProvider: Rows Converted: {len(responses)}")
        print(f"GoRideProvider: Rows Returned: {len(responses)}")
        # --- END GORIDE PROVIDER DIAGNOSTICS ---
        return responses"""
    return code.replace("        return responses", new_log)

def inst_category_ranker(code):
    new_log = """
        if context.latitude and context.longitude:
            print(f"RANKER: Distance calculation executed? YES")
            print(f"RANKER: Sorting field: Distance, Score, ID")
            print(f"RANKER: First 10 results BEFORE sorting:")
            for r in results[:10]:
                print(f"  - {r.name} (ID: {r.id}) - Dist: {getattr(r, 'distance_meters', None)} - Score: {getattr(r, 'final_score', None)}")
            
            results.sort(key=lambda x: (
                x.distance_meters if x.distance_meters is not None else float('inf'),
                -x.final_score,
                x.place_id or ""
            ))
            
            print(f"RANKER: First 10 results AFTER sorting:")
            for r in results[:10]:
                print(f"  - {r.name} (ID: {r.id}) - Dist: {getattr(r, 'distance_meters', None)} - Score: {getattr(r, 'final_score', None)}")
        else:
            print(f"RANKER: Distance calculation executed? NO")
            print(f"RANKER: Sorting field: Score, ID")
            results.sort(key=lambda x: (
                -x.final_score,
                x.place_id or ""
            ))
        return results"""
    
    # We replace the entire sort_results body
    # Using regex to replace the function body
    pattern = r'    def sort_results\(self, results: list\[SearchResultResponse\], context: IntentContext\) -> list\[SearchResultResponse\]:.*'
    replacement = '    def sort_results(self, results: list[SearchResultResponse], context: IntentContext) -> list[SearchResultResponse]:' + new_log
    return re.sub(pattern, replacement, code, flags=re.DOTALL)


def inst_place_repo(code):
    # Add logs at the beginning of methods
    methods = [
        ("search_exact_place", "Repository Method: search_exact_place"),
        ("search_category", "Repository Method: search_category"),
        ("search_pincode", "Repository Method: search_pincode"),
        ("generic_search", "Repository Method: generic_search"),
    ]
    for method, log in methods:
        pattern = f'    async def {method}\\(self, raw_query: str, (.*?)\\) -> List\\[Tuple\\[Place, str, float\\]\\]:\n'
        replacement = f'    async def {method}(self, raw_query: str, \\1) -> List[Tuple[Place, str, float]]:\n        print("{log} [Query: {{raw_query}}]")\n'
        code = re.sub(pattern, replacement, code)
        
    # Log SQL and rows inside execute_stage
    # For search_exact_place: execute_stage(stage_name, stmt, stage_limit, score_label)
    exact_stage_pattern = r'        async def execute_stage\(stage_name, stmt, stage_limit, score_label\):'
    exact_stage_repl = """        async def execute_stage(stage_name, stmt, stage_limit, score_label):
              print(f"REPOSITORY SQL: {stmt}")
"""
    code = re.sub(exact_stage_pattern, exact_stage_repl, code)
    
    generic_stage_pattern = r'        async def execute_stage\(stage_name, stmt, stage_limit\):'
    generic_stage_repl = """        async def execute_stage(stage_name, stmt, stage_limit):
              print(f"REPOSITORY SQL: {stmt}")
"""
    code = re.sub(generic_stage_pattern, generic_stage_repl, code)
    
    # Also log accumulated candidates
    accum_pattern = r'seen_ids.add\(row\[0\].id\)\n                      all_results.append\(row\)\n              if profiler:'
    accum_repl = """seen_ids.add(row[0].id)
                      all_results.append(row)
              print(f"Stage '{stage_name}': Retrieved {len(res.all() if hasattr(res, 'all') else [])} rows, Accumulated total: {len(all_results)}")
              if profiler:"""
    code = re.sub(accum_pattern, accum_repl, code)

    # Note: `res.all()` exhausts the cursor, so `len(res.all())` would break the `for row in res.all():`. 
    # Wait, the original code already iterates over `res.all()`. We can just keep track of how many rows we added in this stage.
    
    accum_pattern2 = r'              for row in res.all\(\):'
    accum_repl2 = """              rows = res.all()
              for row in rows:"""
    code = code.replace(accum_pattern2, accum_repl2)
    
    accum_pattern3 = r'seen_ids.add\(row\[0\].id\)\n                      all_results.append\(row\)\n              if profiler:'
    accum_repl3 = """seen_ids.add(row[0].id)
                      all_results.append(row)
              print(f"Stage '{stage_name}': Retrieved {len(rows)} rows, Accumulated total: {len(all_results)}")
              if profiler:"""
    code = re.sub(r'seen_ids\.add\(row\[0\]\.id\)\n\s+all_results\.append\(row\)\n\s+if profiler:', accum_repl3, code)

    return code

if __name__ == "__main__":
    modify_file("app/utils/search_pipeline.py", inst_pipeline)
    modify_file("app/providers/goride_provider.py", inst_goride_provider)
    modify_file("app/rankers/category_ranker.py", inst_category_ranker)
    modify_file("app/repositories/place_repository.py", inst_place_repo)

import requests
import statistics
import time

BASE_URL = "http://localhost:8000"
QUERIES = [
    "Apollo", "Apollo Hospital", "Hospital", "Restaurant", "ATM", 
    "Fuel Station", "Phoenix", "Marina Beach", "Anna University", 
    "VIT", "Chennai Airport", "Velachery", "Tambaram", "600042", 
    "641001", "Random Query"
]
LAT, LON = 13.0827, 80.2707
ITERATIONS = 10

def run_benchmark():
    results_summary = []
    
    # Track overall timings to find bottlenecks
    overall_timings = {
        "intent_ms": [],
        "goride_repo_dispatch_ms": [],
        "goride_sql_construct_ms": [],
        "goride_db_execute_ms": [],
        "goride_orm_map_ms": [],
        "goride_provider_total_ms": [],
        "goride_mapping_ms": [],
        "nominatim_request_ms": [],
        "nominatim_mapping_ms": [],
        "merge_ms": [],
        "deduplication_ms": [],
        "semantic_ranking_ms": [],
        "distance_ranking_ms": [],
        "sorting_ms": [],
        "serialization_ms": [],
        "total_ms": []
    }
    
    for query in QUERIES:
        print(f"Benchmarking: {query}...")
        timings = []
        
        for _ in range(ITERATIONS):
            try:
                resp = requests.get(f"{BASE_URL}/debug/search", params={"q": query, "lat": LAT, "lon": LON})
                data = resp.json()
                profile = data.get("profile", {}).get("timings", {})
                timings.append(profile.get("total_ms", 0))
                
                # Collect sub-timings
                for k, v in profile.items():
                    overall_timings[k].append(v)
            except Exception as e:
                print(f"Error for {query}: {e}")
        
        if timings:
            results_summary.append([
                query,
                round(min(timings), 2),
                round(max(timings), 2),
                round(statistics.mean(timings), 2),
                round(statistics.median(timings), 2)
            ])
            
    print("\n" + "="*80)
    print("BENCHMARK RESULTS")
    print("="*80)
    print(f"{'Query':<20} | {'Min (ms)':<10} | {'Max (ms)':<10} | {'Avg (ms)':<10} | {'Median (ms)':<10}")
    print("-" * 80)
    for row in results_summary:
        print(f"{row[0]:<20} | {row[1]:<10.2f} | {row[2]:<10.2f} | {row[3]:<10.2f} | {row[4]:<10.2f}")
    
    print("\n" + "="*80)
    print("PERFORMANCE REPORT & BOTTLENECK ANALYSIS")
    print("="*80)
    
    avg_timings = {k: statistics.mean(v) for k, v in overall_timings.items() if v}
    total_avg = avg_timings.get("total_ms", 1)
    
    # Calculate percentages
    percentages = {k: (v / total_avg) * 100 for k, v in avg_timings.items() if k != "total_ms"}
    
    # Sort bottlenecks
    sorted_bottlenecks = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
    
    print("\nAverage Timings Across All Queries:")
    for k, v in avg_timings.items():
        print(f"  {k}: {v:.2f} ms")
        
    print("\nBottleneck Ranking:")
    for i, (stage, perc) in enumerate(sorted_bottlenecks, 1):
        print(f"  {i}. {stage}: {perc:.1f}%")
        
if __name__ == "__main__":
    # Wait for server to be fully ready
    time.sleep(2)
    run_benchmark()

import requests
import json
import sys
import io

# Force UTF-8 output to prevent charmap encoding errors on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

QUERIES = [
    # Exact Place
    "Apollo", "Apollo Hospital", "Apollo Pharmacy", "VIT", "SRM", "Anna University", 
    "Phoenix", "Marina Beach", "Chennai Airport", "Coimbatore Airport",
    # Category
    "Hospital", "Restaurant", "ATM", "Fuel Station", "College", "School", "Temple", "Mall",
    # Pincode
    "600042", "600001", "641001",
    # Admin Area
    "Velachery", "Tambaram", "Adyar", "T Nagar", "Chennai", "Coimbatore", "Madurai",
    # Random
    "Coffee", "Medical", "XYZ", "asdfghjkl"
]

def check_final_score_ordering(results):
    """Verify results are sorted by descending final_score, then ascending distance."""
    prev_score = float('inf')
    for i, r in enumerate(results):
        score = r.get("final_score", 0) or 0
        if score > prev_score + 0.01:  # allow tiny float rounding
            return False, i, f"final_score {score:.2f} > prev {prev_score:.2f}"
        prev_score = score
    return True, -1, ""

def run_audit():
    print("Starting Search API Audit (RC1 Post-Fix)...")
    print(f"{'Query':<22} {'Count':>5}  {'Match':^15}  {'Provider':^10}  {'Score OK':^10}  {'Status'}")
    print("-" * 85)
    
    errors = []
    
    for q in QUERIES:
        try:
            resp = requests.get(f"http://localhost:8000/search?q={q}&lat=13.0827&lon=80.2707", timeout=15)
            if resp.status_code != 200:
                print(f"{q:<22} {'--':>5}  {'--':^15}  {'--':^10}  {'--':^10}  HTTP {resp.status_code}")
                errors.append(f"{q}: HTTP {resp.status_code}")
                continue
                
            results = resp.json()
            count = len(results)
            if count == 0:
                print(f"{q:<22} {count:>5}  {'--':^15}  {'--':^10}  {'--':^10}  EMPTY")
                errors.append(f"{q}: 0 results")
                continue
                
            score_ok, fail_idx, fail_msg = check_final_score_ordering(results)
            score_str = "OK" if score_ok else f"FAIL@{fail_idx}"
            
            first = results[0]
            match = first.get("matched_by") or "unknown"
            prov = first.get("provider") or "unknown"
            
            status = "OK"
            if not score_ok:
                status = f"SCORE: {fail_msg}"
                errors.append(f"{q}: {status}")
            
            print(f"{q:<22} {count:>5}  {match:^15}  {prov:^10}  {score_str:^10}  {status}")
            
            # Print top 3 results with details
            for r in results[:3]:
                name = (r.get("name") or "?")[:35]
                dist = r.get("distance_meters")
                dist_str = f"{dist/1000:.1f}km" if dist is not None else "N/A"
                fscore = r.get("final_score", 0) or 0
                sscore = r.get("semantic_score", 0) or 0
                rprov = r.get("provider", "?")
                print(f"  -> {name:<35} {dist_str:>8}  F:{fscore:.1f}  S:{sscore:.1f}  [{rprov}]")
                
        except Exception as e:
            print(f"{q:<22} {'--':>5}  {'--':^15}  {'--':^10}  {'--':^10}  ERROR: {e}")
            errors.append(f"{q}: {e}")
    
    print(f"\n{'='*85}")
    if errors:
        print(f"TOTAL ERRORS: {len(errors)}")
        for e in errors:
            print(f"  - {e}")
    else:
        print("ALL QUERIES PASSED!")
    print(f"{'='*85}")

if __name__ == "__main__":
    run_audit()

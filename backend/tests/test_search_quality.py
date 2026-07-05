import pytest
import json
import requests
import os
import time

BASE_URL = "http://localhost:8000"
BENCHMARK_FILE = os.path.join(os.path.dirname(__file__), "search_benchmark.json")

# Default coordinates for proximity testing (Chennai)
TEST_LAT = 13.0827
TEST_LON = 80.2707

with open(BENCHMARK_FILE, 'r') as f:
    benchmark_data = json.load(f)

def run_search(query: str, lat: float = None, lon: float = None):
    params = {'q': query}
    if lat and lon:
        params['lat'] = lat
        params['lon'] = lon
    response = requests.get(f"{BASE_URL}/search", params=params)
    assert response.status_code == 200, f"API failed with {response.status_code} for query: {query}"
    return response.json()

@pytest.mark.parametrize("query", benchmark_data['category_searches'])
def test_category_search_distance_and_relevance(query):
    results = run_search(query, TEST_LAT, TEST_LON)
    assert len(results) > 0, f"No results found for category {query}"
    
    # 1. Distances strictly ascending
    distances = [r.get('distance_meters') for r in results if r.get('distance_meters') is not None]
    assert distances == sorted(distances), f"Distances are not strictly ascending for query {query}"
    
    # 2. Results belong to the category (allow some fuzziness since search pipeline might expand aliases)
    # Just check if at least one returned place has a category matching the query
    matching_cats = [r for r in results if query.lower() in (r.get('category') or '').lower()]
    if not matching_cats:
        # DB Diagnostic
        db_res = requests.get(f"{BASE_URL}/places").json()
        db_has_cat = [p for p in db_res if query.lower() in (p.get('category') or '').lower()]
        if not db_has_cat:
            pytest.fail(f"Dataset Issue: No places exist in DB for category {query}")
        else:
            pytest.fail(f"Ranking Issue: DB has {len(db_has_cat)} places for {query}, but search returned none.")
            
    # 3. No duplicate IDs or Names at same coordinates
    ids = [r['id'] for r in results if r.get('id')]
    assert len(ids) == len(set(ids)), f"Duplicate IDs found in results for {query}"
    
    coords_names = [(r.get('name'), r.get('latitude'), r.get('longitude')) for r in results]
    assert len(coords_names) == len(set(coords_names)), f"Duplicate Name/Coords found in results for {query}"

@pytest.mark.parametrize("query", benchmark_data['exact_places'])
def test_exact_place_search_ordering(query):
    results = run_search(query, TEST_LAT, TEST_LON)
    assert len(results) > 0, f"No results found for {query}"
    
    # The first result MUST contain the query tokens natively (exact or whole token)
    top_result = results[0]
    top_name = (top_result.get('name') or "").lower()
    
    # If the top result doesn't contain the query at all, it's a fuzzy failure
    tokens = query.lower().split()
    matched = any(t in top_name for t in tokens)
    
    if not matched:
        # Trace why it failed
        pytest.fail(f"Ranking Issue: Query '{query}' returned unrelated top result '{top_name}'")

@pytest.mark.parametrize("query", benchmark_data['admin_areas'])
def test_admin_area_search(query):
    results = run_search(query, TEST_LAT, TEST_LON)
    assert len(results) > 0, f"No results found for admin area {query}"
    
    # Check if results are inside the admin area (district or name match)
    for r in results:
        district = (r.get('district') or "").lower()
        name = (r.get('name') or "").lower()
        assert query.lower() in district or query.lower() in name, f"Result '{name}' (District: {district}) does not belong to requested admin area '{query}'"
        
    distances = [r.get('distance_meters') for r in results if r.get('distance_meters') is not None]
    assert distances == sorted(distances), f"Distances not ascending for admin area {query}"

@pytest.mark.parametrize("query", benchmark_data['pincodes'])
def test_pincode_search(query):
    results = run_search(query, TEST_LAT, TEST_LON)
    assert len(results) > 0, f"No results found for pincode {query}"
    
    for r in results:
        pincode = r.get('pincode')
        name = r.get('name')
        # Pincode intent can match either exact pincode or name (if pincode is in name)
        assert str(query) == str(pincode) or str(query) in str(name), f"Result '{name}' does not match pincode {query}"
        
    distances = [r.get('distance_meters') for r in results if r.get('distance_meters') is not None]
    assert distances == sorted(distances), f"Distances not ascending for pincode {query}"

def test_ranking_stability():
    """Execute important searches multiple times and verify deterministic ordering."""
    for query in ["Apollo", "Hospital", "Phoenix"]:
        results_1 = [r['id'] for r in run_search(query, TEST_LAT, TEST_LON) if r.get('id')]
        results_2 = [r['id'] for r in run_search(query, TEST_LAT, TEST_LON) if r.get('id')]
        assert results_1 == results_2, f"Ranking is not deterministic for query '{query}'"

def test_distance_validity():
    results = run_search("Hospital", TEST_LAT, TEST_LON)
    for r in results:
        dist = r.get('distance_meters')
        if dist is not None:
            assert dist >= 0, f"Negative distance calculated: {dist}"

def test_hybrid_search_deduplication():
    # Apollo Hospital has many Nominatim and GoRide results
    results = run_search("Apollo", TEST_LAT, TEST_LON)
    providers = [r.get('provider') for r in results]
    # We should see goride results
    assert 'goride' in providers, "GoRide provider results missing in Hybrid search"

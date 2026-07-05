"""
GoRide Search Engine Regression Test Suite
Run with: python -m pytest tests/test_regression.py -v
"""
import pytest
import requests

BASE_URL = "http://localhost:8001"
DEFAULT_LAT = 13.0827  # Chennai
DEFAULT_LON = 80.2707

def search(query, lat=DEFAULT_LAT, lon=DEFAULT_LON):
    resp = requests.get(f"{BASE_URL}/search", params={"q": query, "lat": lat, "lon": lon}, timeout=15)
    assert resp.status_code == 200, f"HTTP {resp.status_code} for query '{query}'"
    return resp.json()


class TestNoHTTP500:
    """Every query must return HTTP 200, never 500."""

    @pytest.mark.parametrize("query", [
        "Apollo", "Apollo Hospital", "Apollo Pharmacy", "VIT", "SRM",
        "Anna University", "Phoenix", "Marina Beach", "Chennai Airport",
        "Coimbatore Airport", "Hospital", "Restaurant", "ATM", "Fuel Station",
        "College", "School", "Temple", "Mall", "600042", "600001", "641001",
        "Velachery", "Tambaram", "Adyar", "T Nagar", "Chennai", "Coimbatore",
        "Madurai", "Coffee", "Medical", "XYZ", "asdfghjkl",
    ])
    def test_no_500(self, query):
        resp = requests.get(f"{BASE_URL}/search", params={"q": query, "lat": DEFAULT_LAT, "lon": DEFAULT_LON}, timeout=15)
        assert resp.status_code != 500, f"HTTP 500 for query '{query}'"


class TestResultCounts:
    """Critical queries must return a minimum number of results."""

    def test_apollo_hospital_returns_results(self):
        results = search("Apollo Hospital")
        assert len(results) >= 10, f"Expected >=10 results, got {len(results)}"

    def test_hospital_category_returns_many(self):
        results = search("Hospital")
        assert len(results) >= 50, f"Expected >=50 hospitals, got {len(results)}"

    def test_restaurant_category_returns_many(self):
        results = search("Restaurant")
        assert len(results) >= 50, f"Expected >=50 restaurants, got {len(results)}"

    def test_pincode_600042_returns_58(self):
        results = search("600042")
        assert len(results) >= 55, f"Expected >=55 results for 600042, got {len(results)}"

    def test_empty_for_gibberish(self):
        results = search("asdfghjkl")
        assert len(results) == 0, f"Expected 0 results for gibberish, got {len(results)}"


class TestDistanceOrdering:
    """Nearby results must appear before distant ones when scores are similar."""

    def test_apollo_pharmacy_nearby_before_distant(self):
        results = search("Apollo Pharmacy")
        # Find the nearest and farthest results
        nearby = [r for r in results if r.get("distance_meters") and r["distance_meters"] < 50000]
        distant = [r for r in results if r.get("distance_meters") and r["distance_meters"] > 200000]
        
        if nearby and distant:
            first_nearby_idx = next(i for i, r in enumerate(results) if r.get("distance_meters") and r["distance_meters"] < 50000)
            first_distant_idx = next(i for i, r in enumerate(results) if r.get("distance_meters") and r["distance_meters"] > 200000)
            assert first_nearby_idx < first_distant_idx, \
                f"Nearby result at index {first_nearby_idx} should appear before distant at {first_distant_idx}"

    def test_final_score_is_descending(self):
        results = search("Hospital")
        scores = [r.get("final_score", 0) or 0 for r in results]
        for i in range(1, len(scores)):
            assert scores[i] <= scores[i-1] + 0.01, \
                f"final_score not descending at index {i}: {scores[i]} > {scores[i-1]}"


class TestIntentDetection:
    """Queries must be routed to the correct intent."""

    def test_pincode_intent(self):
        results = search("600042")
        assert len(results) > 0
        assert results[0].get("matched_by") == "pincode"

    def test_category_intent_hospital(self):
        results = search("Hospital")
        assert len(results) > 0
        assert results[0].get("matched_by") == "category"

    def test_exact_place_intent(self):
        results = search("Apollo Hospital")
        assert len(results) > 0
        assert results[0].get("matched_by") in ("exact_name", "whole_token", "prefix_token")


class TestProviderMerge:
    """Results from both providers must be merged correctly."""

    def test_goride_provider_present(self):
        results = search("Apollo")
        providers = {r.get("provider") for r in results}
        assert "goride" in providers, f"GoRide provider missing, got: {providers}"

    def test_no_duplicate_ids(self):
        results = search("Apollo Hospital")
        ids = [r.get("id") for r in results if r.get("id") is not None]
        assert len(ids) == len(set(ids)), f"Duplicate IDs found: {len(ids)} total, {len(set(ids))} unique"


class TestMissingPlaces:
    """Previously missing places must now be searchable."""

    def test_vit_vellore(self):
        results = search("VIT Vellore")
        names = [r.get("name", "").lower() for r in results]
        assert any("vit" in n for n in names), f"VIT not found in results"

    def test_phoenix_marketcity(self):
        results = search("Phoenix Marketcity")
        names = [r.get("name", "").lower() for r in results]
        assert any("phoenix" in n for n in names), f"Phoenix not found in results"

    def test_coimbatore_airport(self):
        results = search("Coimbatore Airport")
        names = [r.get("name", "").lower() for r in results]
        assert any("coimbatore" in n and "airport" in n for n in names), f"Coimbatore Airport not found"

    def test_srm_kattankulathur(self):
        results = search("SRM")
        names = [r.get("name", "").lower() for r in results]
        assert any("srm" in n for n in names), f"SRM not found in results"

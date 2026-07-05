import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.schemas.place import SearchResultResponse

from app.core.database import AsyncSessionLocal
from app.models.place import Place

# Chennai Guindy coordinates
TEST_LAT = 13.009267
TEST_LON = 80.213084

@pytest.mark.asyncio
async def test_category_distance_sorting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # hospital
        response = await client.get("/search", params={"q": "hospital", "lat": TEST_LAT, "lon": TEST_LON})
        assert response.status_code == 200
        results = response.json()
        assert len(results) > 0
        
        # Verify distance is present and sorted correctly (primarily by distance)
        prev_dist = -1
        for res in results:
            dist = res.get('distance_meters')
            assert dist is not None
            # If distance increases, it's fine. If it decreases, something is wrong
            # Note: since it's a category ranker, we expect results to be sorted strictly by distance
            assert dist >= prev_dist
            prev_dist = dist

@pytest.mark.asyncio
async def test_restaurant_distance_sorting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # restaurant
        response = await client.get("/search", params={"q": "restaurant", "lat": TEST_LAT, "lon": TEST_LON})
        assert response.status_code == 200
        results = response.json()
        assert len(results) > 0
        
        prev_dist = -1
        for res in results:
            dist = res.get('distance_meters')
            assert dist is not None
            assert dist >= prev_dist
            prev_dist = dist

@pytest.mark.asyncio
async def test_atm_distance_sorting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # ATM
        response = await client.get("/search", params={"q": "ATM", "lat": TEST_LAT, "lon": TEST_LON})
        assert response.status_code == 200
        results = response.json()
        assert len(results) > 0
        
        prev_dist = -1
        for res in results:
            dist = res.get('distance_meters')
            assert dist is not None
            assert dist >= prev_dist
            prev_dist = dist

@pytest.mark.asyncio
async def test_exact_place_semantic_sorting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Apollo Hospital
        response = await client.get("/search", params={"q": "Apollo Hospital", "lat": TEST_LAT, "lon": TEST_LON})
        assert response.status_code == 200
        results = response.json()
        assert len(results) > 0
        
        # It should still return "Apollo Hospital" as top result, not just any nearest hospital
        assert "apollo" in results[0]["name"].lower()
        
        # VIT
        response = await client.get("/search", params={"q": "VIT", "lat": TEST_LAT, "lon": TEST_LON})
        assert response.status_code == 200
        results = response.json()
        assert len(results) > 0
        assert "vit" in results[0]["name"].lower()

@pytest.mark.asyncio
async def test_admin_area_filtering_and_sorting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Velachery
        response = await client.get("/search", params={"q": "Velachery", "lat": TEST_LAT, "lon": TEST_LON})
        assert response.status_code == 200
        results = response.json()
        assert len(results) > 0
        
        for res in results:
            assert res.get('distance_meters') is not None

@pytest.mark.asyncio
async def test_pincode_filtering_and_sorting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 600042
        response = await client.get("/search", params={"q": "600042", "lat": TEST_LAT, "lon": TEST_LON})
        assert response.status_code == 200
        results = response.json()
        assert len(results) > 0
        
        # All results should be restricted to the pincode
        for res in results:
            assert res.get('pincode') == '600042'
            assert res.get('distance_meters') is not None

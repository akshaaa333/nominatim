from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional

from app.core.database import get_db_session
from app.repositories.place_repository import PlaceRepository
from app.clients.nominatim_client import NominatimClient
from app.services.search_service import SearchService
from app.schemas.place import PlaceResponse
from app.models.place import Place

router = APIRouter()

def get_search_service(session: AsyncSession = Depends(get_db_session)) -> SearchService:
    """Dependency injector for SearchService"""
    place_repo = PlaceRepository(session)
    nominatim_client = NominatimClient()
    return SearchService(place_repo, nominatim_client)

from app.utils.search_profiler import SearchProfiler

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_places(
    q: str, 
    lat: Optional[float] = None, 
    lon: Optional[float] = None,
    service: SearchService = Depends(get_search_service)
):
    """Search API calling ONLY the SearchService."""
    profiler = SearchProfiler()
    results = await service.search(q, lat, lon, profiler=profiler)
    profiler.finish()
    return results

@router.get("/debug/search")
async def debug_search_places(
    q: str, 
    lat: Optional[float] = None, 
    lon: Optional[float] = None,
    service: SearchService = Depends(get_search_service)
):
    """Debug Search API returning both results and profiler telemetry."""
    profiler = SearchProfiler()
    results = await service.search(q, lat, lon, profiler=profiler)
    profiler.finish()
    return {
        "results": results,
        "profile": profiler.to_dict()
    }

@router.get("/places", response_model=List[PlaceResponse])
async def get_all_places(limit: int = 100, session: AsyncSession = Depends(get_db_session)):
    """Returns all records from goride.places."""
    result = await session.execute(select(Place).limit(limit))
    return list(result.scalars().all())

@router.post("/places/{place_id}/select")
async def select_place(place_id: int, session: AsyncSession = Depends(get_db_session)):
    """Increment the search_count when a user selects a place."""
    place_repo = PlaceRepository(session)
    await place_repo.increment_search_count(place_id)
    return {"status": "success", "message": "Search count incremented"}

import logging
from typing import List, Dict, Any, Optional
from app.repositories.place_repository import PlaceRepository
from app.clients.nominatim_client import NominatimClient
from app.providers.goride_provider import GoRideProvider
from app.providers.nominatim_provider import NominatimProvider
from app.utils.search_pipeline import run_search_pipeline

logger = logging.getLogger(__name__)

class SearchService:
    """Business logic for search orchestration."""
    def __init__(self, place_repo: PlaceRepository, nominatim_client: NominatimClient):
        self.place_repo = place_repo
        self.nominatim_client = nominatim_client
        
        # Initialize providers
        self.providers = [
            GoRideProvider(self.place_repo),
            NominatimProvider(self.nominatim_client)
        ]

    async def search(self, query: str, lat: Optional[float] = None, lon: Optional[float] = None, profiler=None) -> List[Dict[str, Any]]:
        """
        Executes a hybrid search across local and remote providers concurrently.
        """
        # Orchestrate via pipeline
        results = await run_search_pipeline(query, self.providers, lat, lon, profiler=profiler)
        
        # Convert pydantic models back to dict for the API response
        if profiler:
            with profiler.profile("serialization_ms"):
                serialized = [r.model_dump(mode='json') for r in results]
            profiler.record_count("returned", len(serialized))
            return serialized
        else:
            return [r.model_dump(mode='json') for r in results]

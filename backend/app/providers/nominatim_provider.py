from typing import List
from app.providers.search_provider import SearchProvider
from app.schemas.place import SearchResultResponse
from app.clients.nominatim_client import NominatimClient
from app.utils.mapper import map_nominatim_to_place_response

class NominatimProvider(SearchProvider):
    def __init__(self, nominatim_client: NominatimClient):
        self.nominatim_client = nominatim_client
        
    @property
    def name(self) -> str:
        return "nominatim"
        
    async def search(self, query: str, intent_context = None, profiler = None) -> List[SearchResultResponse]:
        if profiler:
            with profiler.profile("nominatim_request_ms"):
                raw_results = await self.nominatim_client.search(query)
            profiler.record_metadata("providers_used", {"nominatim": True})
            profiler.record_count("nominatim_raw", len(raw_results))
        else:
            raw_results = await self.nominatim_client.search(query)
        
        responses = []
        if profiler:
            with profiler.profile("nominatim_mapping_ms"):
                for res in raw_results:
                    mapped_dict = map_nominatim_to_place_response(res)
                    mapped_dict['base_score'] = 10.0
                    mapped_dict['provider'] = self.name
                    mapped_dict['matched_by'] = "fallback"
                    responses.append(SearchResultResponse.model_validate(mapped_dict))
        else:
            for res in raw_results:
                mapped_dict = map_nominatim_to_place_response(res)
                mapped_dict['base_score'] = 10.0
                mapped_dict['provider'] = self.name
                mapped_dict['matched_by'] = "fallback"
                responses.append(SearchResultResponse.model_validate(mapped_dict))
            
        return responses

from typing import List
from app.providers.search_provider import SearchProvider
from app.schemas.place import SearchResultResponse
from app.repositories.place_repository import PlaceRepository

class GoRideProvider(SearchProvider):
    def __init__(self, place_repository: PlaceRepository):
        self.place_repository = place_repository
        
    @property
    def name(self) -> str:
        return "goride"
        
    async def search(self, query: str, intent_context = None, profiler = None) -> List[SearchResultResponse]:
        if profiler:
            with profiler.profile("goride_provider_total_ms"):
                local_results = await self.place_repository.search_places(
                    query, 
                    limit=30, 
                    intent=intent_context.intent if intent_context else None,
                    category=intent_context.category if intent_context else None,
                    profiler=profiler
                )
            profiler.record_metadata("providers_used", {"goride": True})
            profiler.record_count("goride_raw", len(local_results))
        else:
            local_results = await self.place_repository.search_places(
                query, 
                limit=30, 
                intent=intent_context.intent if intent_context else None,
                category=intent_context.category if intent_context else None
            )

        responses = []
        
        if profiler:
            with profiler.profile("goride_mapping_ms"):
                for place, match_type, score in local_results:
                    place_dict = SearchResultResponse.model_validate(place).model_dump(mode='json')
                    place_dict['match_type'] = match_type
                    place_dict['base_score'] = score
                    place_dict['provider'] = self.name
                    responses.append(SearchResultResponse.model_validate(place_dict))
            profiler.record_count("goride_filtered", len(responses))
        else:
            for place, match_type, score in local_results:
                place_dict = SearchResultResponse.model_validate(place).model_dump(mode='json')
                place_dict['match_type'] = match_type
                place_dict['base_score'] = score
                place_dict['provider'] = self.name
                responses.append(SearchResultResponse.model_validate(place_dict))
            

        return responses

from abc import ABC, abstractmethod
from typing import List
from app.schemas.place import SearchResultResponse

class SearchProvider(ABC):
    """Abstract base class for search providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g., 'goride', 'nominatim')."""
        pass
        
    @abstractmethod
    async def search(self, query: str, intent_context: 'IntentContext' = None) -> List[SearchResultResponse]:
        """Execute search and return canonical SearchResultResponse list."""
        pass

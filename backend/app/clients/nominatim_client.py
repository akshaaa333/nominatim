import httpx
from typing import Any, Dict, List
from app.core.config import settings

class NominatimClient:
    """Client for handling HTTP communication with Nominatim. No business logic."""
    def __init__(self):
        self.base_url = settings.NOMINATIM_URL

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Calls local Nominatim API for search"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search",
                params={"q": query, "format": "json"}
            )
            response.raise_for_status()
            return response.json()

from typing import Dict, Any, Optional
from app.repositories.place_repository import PlaceRepository
from app.services.csv_append_service import CSVAppendService

class MissingPlaceService:
    def __init__(self, place_repo: PlaceRepository):
        self.place_repo = place_repo
        self.csv_service = CSVAppendService()

    async def check_duplicate(self, lat: float, lon: float, name: str) -> bool:
        return await self.place_repo.find_duplicate(lat, lon, name)

    async def add_missing_place(self, place_data: Dict[str, Any]) -> Dict[str, Any]:
        is_duplicate = await self.check_duplicate(
            place_data.get("latitude"),
            place_data.get("longitude"),
            place_data.get("name")
        )
        if is_duplicate:
            return {"status": "error", "message": "Place already exists"}

        # Write to DB
        new_place = await self.place_repo.insert_manual_place(place_data)

        # Append to CSV
        place_data["source"] = "goride_manual"
        self.csv_service.append_place(place_data)

        return {"status": "success", "place_id": new_place.id}

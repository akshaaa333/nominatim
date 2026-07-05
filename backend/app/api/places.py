from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.core.database import get_db_session
from app.repositories.place_repository import PlaceRepository
from app.services.geocoder_service import GeocoderService
from app.services.missing_place_service import MissingPlaceService

router = APIRouter()

class GeocodeRequest(BaseModel):
    address: str

class DuplicateCheckRequest(BaseModel):
    latitude: float
    longitude: float
    name: str

class ManualPlaceRequest(BaseModel):
    name: str
    display_name: Optional[str] = None
    latitude: float
    longitude: float
    category: Optional[str] = None
    district: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

def get_missing_place_service(session: AsyncSession = Depends(get_db_session)) -> MissingPlaceService:
    place_repo = PlaceRepository(session)
    return MissingPlaceService(place_repo)

def get_geocoder_service() -> GeocoderService:
    return GeocoderService()

@router.post("/places/geocode")
async def geocode_address(request: GeocodeRequest, geocoder: GeocoderService = Depends(get_geocoder_service)):
    result = await geocoder.geocode(request.address)
    if not result:
        raise HTTPException(status_code=404, detail="Address not found")
    return result

@router.post("/places/check-duplicate")
async def check_duplicate(request: DuplicateCheckRequest, service: MissingPlaceService = Depends(get_missing_place_service)):
    is_duplicate = await service.check_duplicate(request.latitude, request.longitude, request.name)
    return {"is_duplicate": is_duplicate}

@router.post("/places/manual")
async def add_manual_place(request: ManualPlaceRequest, service: MissingPlaceService = Depends(get_missing_place_service)):
    result = await service.add_missing_place(request.model_dump())
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

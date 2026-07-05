from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PlaceBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    district: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    search_key: Optional[str] = None
    source: Optional[str] = None
    place_id: Optional[str] = None

class PlaceCreate(PlaceBase):
    pass

class SearchResultResponse(PlaceBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    match_type: Optional[str] = None
    provider: Optional[str] = None
    
    # Granular scoring
    matched_by: Optional[str] = None
    base_score: Optional[float] = 0.0
    token_bonus: Optional[float] = 0.0
    category_bonus: Optional[float] = 0.0
    admin_bonus: Optional[float] = 0.0
    pincode_bonus: Optional[float] = 0.0
    provider_bonus: Optional[float] = 0.0
    importance_bonus: Optional[float] = 0.0
    popularity_bonus: Optional[float] = 0.0
    distance_bonus: Optional[float] = 0.0
    semantic_score: Optional[float] = 0.0
    final_score: Optional[float] = 0.0
    
    # Optional Nominatim metrics
    importance_score: Optional[float] = 0.0
    place_rank: Optional[int] = 0
    
    # Distance metrics
    distance_meters: Optional[float] = None
    
    # Keep score for frontend compatibility
    score: Optional[float] = 0.0
    
    search_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class PlaceResponse(SearchResultResponse):
    id: int

    model_config = ConfigDict(from_attributes=True)

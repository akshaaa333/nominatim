from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Index, String, Float, Integer, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from app.models.base import Base

class Place(Base):
    __tablename__ = "places"
    __table_args__ = (
        Index('ix_places_category', 'category'),
        Index('ix_places_district', 'district'),
        Index('ix_places_pincode', 'pincode'),
        Index('ix_places_search_key_trgm', 'search_key', postgresql_ops={'search_key': 'gin_trgm_ops'}, postgresql_using='gin'),
        {'schema': 'goride'}
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=True)
    district: Mapped[str] = mapped_column(String, nullable=True)
    pincode: Mapped[str] = mapped_column(String, nullable=True)
    state: Mapped[str] = mapped_column(String, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=True)
    search_key: Mapped[str] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=True)
    place_id: Mapped[str] = mapped_column(String, nullable=True)
    search_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

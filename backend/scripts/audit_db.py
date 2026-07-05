import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://nominatim:password@localhost:5433/nominatim"
engine = create_async_engine(DATABASE_URL)

PLACES_TO_CHECK = [
    "Apollo Hospital", "Apollo Pharmacy", "SRM Institute of Science and Technology, Kattankulathur",
    "VIT Vellore", "Anna University", "IIT Madras", "Marina Beach", "Phoenix Marketcity",
    "Chennai International Airport", "Coimbatore Airport", "Velachery", "Tambaram", "T Nagar",
    "Koyambedu", "Chennai Central", "600042", "600001", "641001", "Hospitals", "Restaurants",
    "ATM", "Fuel Station", "Mall", "College", "School", "Temple", "Bus Stand", "Railway Station", "Airport"
]

async def check_db():
    async with engine.connect() as conn:
        for place in PLACES_TO_CHECK:
            query = text(f"SELECT search_key, category, latitude, longitude, district, pincode FROM goride.places WHERE search_key ILIKE '%{place}%' OR pincode = '{place}' LIMIT 1")
            result = await conn.execute(query)
            row = result.fetchone()
            if row:
                print(f"[OK] {place:30} -> {row[0]:30} | Cat: {row[1]:15} | Lat: {row[2]:.4f} | Lon: {row[3]:.4f} | Dist: {row[4]} | Pin: {row[5]}")
            else:
                print(f"[MISSING] {place:30}")

if __name__ == "__main__":
    asyncio.run(check_db())

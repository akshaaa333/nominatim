import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://nominatim:password@localhost:5433/nominatim"
engine = create_async_engine(DATABASE_URL)

MISSING_PLACES = [
    {
        "search_key": "srm institute of science and technology kattankulathur",
        "name": "SRM Institute of Science and Technology, Kattankulathur",
        "category": "Universities",
        "latitude": 12.8236,
        "longitude": 80.0438,
        "district": "Chengalpattu",
        "pincode": "603203",
        "popularity": 1000
    },
    {
        "search_key": "vit vellore",
        "name": "VIT Vellore",
        "category": "Universities",
        "latitude": 12.9692,
        "longitude": 79.1559,
        "district": "Vellore",
        "pincode": "632014",
        "popularity": 1000
    },
    {
        "search_key": "phoenix marketcity",
        "name": "Phoenix Marketcity",
        "category": "Malls",
        "latitude": 12.9915,
        "longitude": 80.2166,
        "district": "Chennai",
        "pincode": "600042",
        "popularity": 1000
    },
    {
        "search_key": "coimbatore airport",
        "name": "Coimbatore Airport",
        "category": "Airports",
        "latitude": 11.0298,
        "longitude": 77.0425,
        "district": "Coimbatore",
        "pincode": "641014",
        "popularity": 1000
    }
]

async def insert_places():
    async with engine.begin() as conn:
        for p in MISSING_PLACES:
            query = text("""
                INSERT INTO goride.places (
                    search_key, name, display_name, category, 
                    latitude, longitude, district, pincode, state, country, search_count
                ) VALUES (
                    :search_key, :name, :name, :category,
                    :lat, :lon, :district, :pincode, 'Tamil Nadu', 'India', :pop
                ) ON CONFLICT DO NOTHING
            """)
            await conn.execute(query, {
                "search_key": p["search_key"],
                "name": p["name"],
                "category": p["category"],
                "lat": p["latitude"],
                "lon": p["longitude"],
                "district": p["district"],
                "pincode": p["pincode"],
                "pop": p["popularity"]
            })
            print(f"Inserted: {p['name']}")
    print("Insertion complete.")

if __name__ == "__main__":
    asyncio.run(insert_places())

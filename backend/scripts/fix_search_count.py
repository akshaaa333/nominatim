import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://nominatim:password@localhost:5433/nominatim"
engine = create_async_engine(DATABASE_URL)

async def fix():
    async with engine.begin() as conn:
        # Fix all 4 inserted places to have search_count=0 like normal entries
        await conn.execute(text("""
            UPDATE goride.places 
            SET search_count = 0 
            WHERE name IN (
                'SRM Institute of Science and Technology, Kattankulathur',
                'VIT Vellore',
                'Phoenix Marketcity',
                'Coimbatore Airport'
            )
        """))
        print("Fixed search_count for all 4 inserted places")

if __name__ == "__main__":
    asyncio.run(fix())

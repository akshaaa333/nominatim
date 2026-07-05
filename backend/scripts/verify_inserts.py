import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://nominatim:password@localhost:5433/nominatim"
engine = create_async_engine(DATABASE_URL)

async def check():
    async with engine.connect() as conn:
        # Check SRM by partial match
        result = await conn.execute(text("SELECT search_key, name, category FROM goride.places WHERE search_key ILIKE '%srm%' LIMIT 5"))
        rows = result.fetchall()
        print("SRM matches:")
        for r in rows:
            print(f"  {r[0]} | {r[1]} | {r[2]}")
        
        # Check Phoenix
        result = await conn.execute(text("SELECT search_key, name, category FROM goride.places WHERE search_key ILIKE '%phoenix%' LIMIT 5"))
        rows = result.fetchall()
        print("\nPhoenix matches:")
        for r in rows:
            print(f"  {r[0]} | {r[1]} | {r[2]}")

        # Check VIT
        result = await conn.execute(text("SELECT search_key, name, category FROM goride.places WHERE search_key ILIKE '%vit%' LIMIT 5"))
        rows = result.fetchall()
        print("\nVIT matches:")
        for r in rows:
            print(f"  {r[0]} | {r[1]} | {r[2]}")

        # Check Coimbatore Airport
        result = await conn.execute(text("SELECT search_key, name, category FROM goride.places WHERE search_key ILIKE '%coimbatore airport%' LIMIT 5"))
        rows = result.fetchall()
        print("\nCoimbatore Airport matches:")
        for r in rows:
            print(f"  {r[0]} | {r[1]} | {r[2]}")

if __name__ == "__main__":
    asyncio.run(check())

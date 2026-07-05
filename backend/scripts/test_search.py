import sys, os, asyncio
os.environ['POSTGRES_PASSWORD'] = 'password'
sys.path.insert(0, ".")

from app.core.database import AsyncSessionLocal
from app.repositories.place_repository import PlaceRepository

async def main():
    async with AsyncSessionLocal() as session:
        repo = PlaceRepository(session)
        res = await repo.search_exact_place("Apollo", limit=50)
        print(f"Apollo results: {len(res)}")
        if res:
            print(res[0])

if __name__ == "__main__":
    asyncio.run(main())

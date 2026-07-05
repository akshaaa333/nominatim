import asyncio
import sys
sys.path.insert(0, ".")
from app.core.database import AsyncSessionLocal
from app.repositories.place_repository import PlaceRepository

async def main():
    async with AsyncSessionLocal() as session:
        repo = PlaceRepository(session)
        res = await repo.search_exact_place("Apollo", limit=50)
        print(f"Apollo results exact: {len(res)}")
        
        res_cat = await repo.search_category("Hospital", "hospital", limit=100)
        print(f"Hospital results category: {len(res_cat)}")

if __name__ == "__main__":
    asyncio.run(main())

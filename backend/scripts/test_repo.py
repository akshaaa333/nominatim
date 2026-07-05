import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.database import AsyncSessionLocal
from app.repositories.place_repository import PlaceRepository

async def test_repo():
    async with AsyncSessionLocal() as session:
        repo = PlaceRepository(session)
        results = await repo.search_places("Mall", limit=20)
        print(f"GoRide returned {len(results)} results for 'Mall'")
        for place, match_type, score in results:
            print(f"- {place.name} | Category: {place.category} | Match: {match_type} | Score: {score}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_repo())

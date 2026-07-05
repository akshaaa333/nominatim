import asyncio
import time
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.repositories.place_repository import PlaceRepository
import json

queries = [
    {"query": "Apollo", "intent": "EXACT_PLACE", "category": None},
    {"query": "Apollo Hospital", "intent": "EXACT_PLACE", "category": None},
    {"query": "Hospital", "intent": "CATEGORY", "category": "hospital"},
    {"query": "Restaurant", "intent": "CATEGORY", "category": "restaurant"},
    {"query": "ATM", "intent": "CATEGORY", "category": "atm"},
    {"query": "600042", "intent": "PINCODE", "category": None},
    {"query": "641001", "intent": "PINCODE", "category": None},
    {"query": "Velachery", "intent": "ADMIN_AREA", "category": None},
    {"query": "Tambaram", "intent": "ADMIN_AREA", "category": None},
    {"query": "Chennai", "intent": "ADMIN_AREA", "category": None},
    {"query": "Phoenix", "intent": "EXACT_PLACE", "category": None},
    {"query": "Anna University", "intent": "EXACT_PLACE", "category": None},
    {"query": "Marina Beach", "intent": "EXACT_PLACE", "category": None},
    {"query": "Random query", "intent": "UNKNOWN", "category": None},
]

async def profile_query(session, repo: PlaceRepository, q_info):
    start_time = time.perf_counter()
    results = await repo.search_places(q_info["query"], limit=50, intent=q_info["intent"], category=q_info["category"])
    end_time = time.perf_counter()
    latency = (end_time - start_time) * 1000
    rows = len(results)
    
    print(f"--- Query: {q_info['query']} | Intent: {q_info['intent']} ---")
    print(f"Latency: {latency:.2f}ms | Rows returned: {rows}")
    
async def main():
    async with AsyncSessionLocal() as session:
        repo = PlaceRepository(session)
        print("Warming up...")
        await repo.search_places("Apollo", limit=5)
        print("Starting Benchmark...")
        for q in queries:
            await profile_query(session, repo, q)

if __name__ == "__main__":
    asyncio.run(main())

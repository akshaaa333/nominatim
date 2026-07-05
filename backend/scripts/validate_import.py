import asyncio
import time
import sys
import os
import requests
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.database import AsyncSessionLocal
from app.models.place import Place

async def validate_import():
    print("========================================")
    print("STEP 6 - POST IMPORT VALIDATION")
    print("========================================")
    async with AsyncSessionLocal() as session:
        # 1. Total imported rows
        result = await session.execute(text("SELECT COUNT(*) FROM goride.places;"))
        total = result.scalar()
        print(f"Total rows in goride.places: {total}")
        
        # 2. Category counts
        for cat in ['Hospitals', 'Restaurants', 'Malls']:
            res = await session.execute(text(f"SELECT COUNT(*) FROM goride.places WHERE category='{cat}';"))
            print(f"Total {cat}: {res.scalar()}")

        print("\n========================================")
        print("STEP 7 - LANDMARK VALIDATION")
        print("========================================")
        landmarks = ['Apollo', 'Phoenix', 'Marina Beach', 'Anna University', 'VIT', 'Chennai International Airport']
        categories = ['Hospitals', 'Restaurants', 'Fuel Stations']
        
        for name in landmarks:
            res = await session.execute(text(f"SELECT COUNT(*) FROM goride.places WHERE name ILIKE '%{name}%';"))
            count = res.scalar()
            if count > 0:
                print(f"{name}: [PASS] ({count} results)")
            else:
                print(f"{name}: [FAIL] (No results found)")
                
        for cat in categories:
            res = await session.execute(text(f"SELECT COUNT(*) FROM goride.places WHERE category='{cat}';"))
            count = res.scalar()
            if count > 0:
                print(f"Category {cat}: [PASS] ({count} results)")
            else:
                print(f"Category {cat}: [FAIL] (No results found)")

    print("\n========================================")
    print("STEP 8 & 9 - SEARCH VALIDATION & PERFORMANCE")
    print("========================================")
    queries = ['Apollo', 'hospital', 'restaurant', 'Phoenix', 'Marina Beach', '600042', 'Velachery']
    base_url = "http://localhost:8000/search"
    
    total_time = 0
    for q in queries:
        start_time = time.time()
        try:
            resp = requests.get(base_url, params={'q': q})
            elapsed = time.time() - start_time
            total_time += elapsed
            
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    results = len(data)
                else:
                    results = len(data.get('results', []))
                print(f"Search '{q}': [PASS] ({results} results in {elapsed*1000:.1f}ms)")
            else:
                print(f"Search '{q}': [FAIL] HTTP {resp.status_code} in {elapsed*1000:.1f}ms")
        except Exception as e:
             print(f"Search '{q}': [FAIL] Error connecting to API: {e}")

    avg_latency = total_time / len(queries) * 1000
    print(f"\nAverage Search Latency: {avg_latency:.1f}ms")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(validate_import())

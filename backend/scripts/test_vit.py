import httpx
import asyncio

async def fetch():
    async with httpx.AsyncClient() as client:
        r = await client.get('http://localhost:8000/search?q=VIT&lat=13.0827&lon=80.2707')
        print(f"VIT: {len(r.json()['results'])} results")

asyncio.run(fetch())

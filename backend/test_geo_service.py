import asyncio
from app.services.geocoder_service import GeocoderService

async def main():
    svc = GeocoderService()
    for addr in ['Altis Ashraya, Shriram City Road, Mangadu, Chennai 600122', 'SRM University, Kattankulathur', 'VIT Chennai', 'Phoenix MarketCity Chennai']:
        print(f"Address: {addr}")
        r = await svc.geocode(addr)
        print(f"Result: {r}")
        print("-" * 20)

asyncio.run(main())

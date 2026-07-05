import asyncio
import csv
import sys
import os
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.database import AsyncSessionLocal
from app.models.place import Place

async def backup_and_clear():
    backup_file = "data/goride_places_backup.csv"
    
    print("STEP 2: Backing up existing data...")
    async with AsyncSessionLocal() as session:
        # Fetch all
        result = await session.execute(select(Place))
        places = result.scalars().all()
        
        if places:
            with open(backup_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["id", "place_id", "name", "display_name", "latitude", "longitude", "category", "district", "pincode", "state", "country", "source", "search_key"])
                
                for p in places:
                    writer.writerow([p.id, p.place_id, p.name, p.display_name, p.latitude, p.longitude, p.category, p.district, p.pincode, p.state, p.country, p.source, p.search_key])
            
            print(f"Backed up {len(places)} rows to {backup_file}")
        else:
            print("Table is currently empty, nothing to backup.")

        print("STEP 4: Clearing existing data...")
        await session.execute(text("DELETE FROM goride.places;"))
        await session.commit()
        print("Cleared goride.places.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(backup_and_clear())

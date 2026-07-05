import asyncio
import csv
import re
import sys
import os
import argparse
import time
from typing import List, Dict, Any, Set
from tqdm import tqdm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add backend directory to sys.path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models.place import Place
from app.utils.normalization import normalize_string, normalize_search_key

async def process_batch(session: AsyncSession, batch: List[Dict[str, Any]], csv_seen_ids: Set[str]) -> tuple[int, int, int]:
    """
    Inserts a batch into the database, skipping duplicates.
    Returns a tuple of (imported_count, skipped_count, failed_count).
    """
    if not batch:
        return 0, 0, 0

    imported = 0
    skipped = 0
    failed = 0

    # 1. Filter out internal CSV duplicates
    unique_batch = []
    for row in batch:
        place_id = row['place_id']
        if not place_id:
            continue
            
        if place_id in csv_seen_ids:
            skipped += 1
            continue
            
        csv_seen_ids.add(place_id)
        unique_batch.append(row)

    if not unique_batch:
        return 0, skipped, 0

    # 2. Check Database for existing place_ids
    batch_place_ids = [row['place_id'] for row in unique_batch]
    
    try:
        # Fetch existing IDs in one quick query
        result = await session.execute(
            select(Place.place_id).where(Place.place_id.in_(batch_place_ids))
        )
        existing_db_ids = set(result.scalars().all())

        # Filter out rows that are already in the DB
        to_insert = []
        for row in unique_batch:
            if row['place_id'] in existing_db_ids:
                skipped += 1
            else:
                to_insert.append(row)

        if not to_insert:
            return 0, skipped, 0

        # 3. Batch Insert
        places_to_add = [Place(**data) for data in to_insert]
        session.add_all(places_to_add)
        await session.commit()
        imported = len(places_to_add)

    except Exception as e:
        await session.rollback()
        print(f"\n[Error] Batch insertion failed: {e}")
        failed += len(unique_batch)

    return imported, skipped, failed

async def run_import(file_path: str):
    print(f"Starting import from: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"[Error] File not found: {file_path}")
        return

    # Count rows to feed tqdm properly
    with open(file_path, 'r', encoding='utf-8') as f:
        total_rows = sum(1 for _ in f) - 1 # exclude header

    batch_size = 1000
    batch = []
    
    total_imported = 0
    total_skipped = 0
    total_failed = 0
    
    csv_seen_ids = set()
    start_time = time.time()

    async with AsyncSessionLocal() as session:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            with tqdm(total=total_rows, desc="Importing", unit="row") as pbar:
                for row_num, row in enumerate(reader, start=1):
                    try:
                        csv_id = row.get('id', '')
                        if not csv_id:
                            continue
                            
                        name = normalize_string(row.get('name', ''))
                        
                        # Graceful handling for bad geometry data
                        try:
                            lat = float(row.get('latitude', 0)) if row.get('latitude') else None
                            lon = float(row.get('longitude', 0)) if row.get('longitude') else None
                        except ValueError:
                            print(f"\n[Error] Malformed lat/lon at row {row_num}")
                            total_failed += 1
                            pbar.update(1)
                            continue

                        place_data = {
                            "place_id": normalize_string(csv_id),
                            "name": name,
                            "display_name": name,
                            "latitude": lat,
                            "longitude": lon,
                            "category": normalize_string(row.get('category', '')),
                            "district": normalize_string(row.get('district', '')),
                            "pincode": normalize_string(row.get('pincode', '')),
                            "state": "Tamil Nadu",
                            "country": "India",
                            "source": "osm",
                            "search_key": normalize_search_key(name)
                        }
                        
                        batch.append(place_data)
                        
                        if len(batch) >= batch_size:
                            imp, skip, fail = await process_batch(session, batch, csv_seen_ids)
                            total_imported += imp
                            total_skipped += skip
                            total_failed += fail
                            batch = []
                            
                    except Exception as e:
                        print(f"\n[Error] Failed to process row {row_num}: {e}")
                        total_failed += 1
                        
                    pbar.update(1)

                # Process the final remaining batch
                if batch:
                    imp, skip, fail = await process_batch(session, batch, csv_seen_ids)
                    total_imported += imp
                    total_skipped += skip
                    total_failed += fail

    elapsed = time.time() - start_time
    print("\n========================================")
    print("SUMMARY")
    print("========================================")
    print(f"Total Rows   : {total_rows}")
    print(f"Imported     : {total_imported}")
    print(f"Skipped      : {total_skipped}")
    print(f"Failed       : {total_failed}")
    print(f"Elapsed Time : {elapsed:.2f} seconds")
    print("========================================")
    print("Import completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import OSM places from CSV into GoRide backend")
    parser.add_argument("file_path", nargs="?", default="data/hubs_v4.csv", help="Path to the CSV file")
    args = parser.parse_args()
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(run_import(args.file_path))

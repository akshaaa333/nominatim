import asyncio
import asyncpg
import json

QUERIES = [
    ("Apollo", "EXPLAIN (ANALYZE, FORMAT JSON) SELECT *, similarity(search_key, 'apollo') as sim FROM goride.places WHERE search_key = 'apollo' OR search_key LIKE 'apollo%' OR search_key % 'apollo' ORDER BY sim DESC LIMIT 50;"),
    ("Apollo Hospital", "EXPLAIN (ANALYZE, FORMAT JSON) SELECT *, similarity(search_key, 'apollo hospital') as sim FROM goride.places WHERE search_key = 'apollo hospital' OR search_key LIKE 'apollo hospital%' OR search_key % 'apollo hospital' ORDER BY sim DESC LIMIT 50;"),
    ("Hospital", "EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM goride.places WHERE category = 'Hospital' LIMIT 100;"),
    ("Restaurant", "EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM goride.places WHERE category = 'Restaurant' LIMIT 100;"),
    ("Phoenix", "EXPLAIN (ANALYZE, FORMAT JSON) SELECT *, similarity(search_key, 'phoenix') as sim FROM goride.places WHERE search_key = 'phoenix' OR search_key LIKE 'phoenix%' OR search_key % 'phoenix' ORDER BY sim DESC LIMIT 50;"),
    ("Anna University", "EXPLAIN (ANALYZE, FORMAT JSON) SELECT *, similarity(search_key, 'anna university') as sim FROM goride.places WHERE search_key = 'anna university' OR search_key LIKE 'anna university%' OR search_key % 'anna university' ORDER BY sim DESC LIMIT 50;"),
    ("Marina Beach", "EXPLAIN (ANALYZE, FORMAT JSON) SELECT *, similarity(search_key, 'marina beach') as sim FROM goride.places WHERE search_key = 'marina beach' OR search_key LIKE 'marina beach%' OR search_key % 'marina beach' ORDER BY sim DESC LIMIT 50;"),
    ("Velachery", "EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM goride.places WHERE district ILIKE '%Velachery%' OR state ILIKE '%Velachery%' LIMIT 100;"),
    ("Tambaram", "EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM goride.places WHERE district ILIKE '%Tambaram%' OR state ILIKE '%Tambaram%' LIMIT 100;"),
    ("600042", "EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM goride.places WHERE pincode = '600042' LIMIT 100;"),
    ("641001", "EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM goride.places WHERE pincode = '641001' LIMIT 100;")
]

async def main():
    try:
        conn = await asyncpg.connect('postgresql://nominatim:nominatim@127.0.0.1:5433/nominatim')
        print("SUCCESS! Connected to PostgreSQL.")
        
        for name, sql in QUERIES:
            print(f"\n======================\nQuery: {name}\n======================")
            result = await conn.fetchval(sql)
            print(result)
            
        await conn.close()
    except Exception as e:
        print(f"FAILED: {e}")

asyncio.run(main())

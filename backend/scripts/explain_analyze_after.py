import subprocess

queries = {
    "Apollo": [
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key = 'apollo';",
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key LIKE 'apollo%';",
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key ILIKE '%apollo%';"
    ],
    "Apollo Hospital": [
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key = 'apollo hospital';",
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key LIKE 'apollo hospital%';",
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key ILIKE '%apollo%' AND search_key ILIKE '%hospital%';"
    ],
    "Hospital": [
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE category = 'Hospital';"
    ],
    "Restaurant": [
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE category = 'Restaurant';"
    ],
    "Phoenix": [
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key = 'phoenix';",
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key LIKE 'phoenix%';",
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key ILIKE '%phoenix%';"
    ],
    "Marina Beach": [
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key = 'marina beach';",
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key LIKE 'marina beach%';",
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key ILIKE '%marina%' AND search_key ILIKE '%beach%';"
    ],
    "Anna University": [
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key = 'anna university';",
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key LIKE 'anna university%';",
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE search_key ILIKE '%anna%' AND search_key ILIKE '%university%';"
    ],
    "Velachery": [
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE district = 'Velachery' OR district = 'Velachery' OR state = 'Velachery' OR state = 'Velachery';"
    ],
    "Tambaram": [
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE district = 'Tambaram' OR district = 'Tambaram' OR state = 'Tambaram' OR state = 'Tambaram';"
    ],
    "600042": [
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE pincode = '600042';"
    ],
    "641001": [
        "EXPLAIN ANALYZE SELECT * FROM goride.places WHERE pincode = '641001';"
    ]
}

with open("explain_analyze_after.txt", "w") as f:
    for q_name, stmts in queries.items():
        f.write(f"=======================================================\n")
        f.write(f"Query: {q_name}\n")
        f.write(f"=======================================================\n")
        for stmt in stmts:
            f.write(f"STAGE SQL: {stmt}\n")
            cmd = f'docker exec nominatim su postgres -c "psql -d nominatim -c \\"{stmt}\\""'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                f.write(result.stdout)
            if result.stderr:
                f.write("ERROR: " + result.stderr)
        f.write("\n\n")

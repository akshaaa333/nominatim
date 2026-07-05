import subprocess

result = subprocess.run(
    ["docker", "exec", "nominatim", "su", "postgres", "-c", "psql -d nominatim -t -c \"SELECT count(*) FROM goride.places WHERE search_key % 'vit';\""],
    capture_output=True,
    text=True
)
print("Count for % 'vit':")
print(result.stdout)

result = subprocess.run(
    ["docker", "exec", "nominatim", "su", "postgres", "-c", "psql -d nominatim -t -c \"SELECT name, search_key, category FROM goride.places WHERE search_key % 'vit' LIMIT 5;\""],
    capture_output=True,
    text=True
)
print("Samples:")
print(result.stdout)

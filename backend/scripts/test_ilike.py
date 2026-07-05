import subprocess

cmd = 'docker exec nominatim su postgres -c "psql -d nominatim -c \\"EXPLAIN ANALYZE SELECT * FROM goride.places WHERE district = \'Velachery\';\\""'
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("ERROR:", result.stderr)

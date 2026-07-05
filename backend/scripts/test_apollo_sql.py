import subprocess
cmd = "docker exec -i nominatim su postgres -c \"psql -d nominatim -c 'SELECT search_key, count(*) FROM goride.places WHERE search_key = ''apollo'' GROUP BY search_key;'\""
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(res.stdout)

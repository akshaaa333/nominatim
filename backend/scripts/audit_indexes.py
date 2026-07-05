import subprocess

cmd = 'docker exec nominatim su postgres -c "psql -d nominatim -c \\"SELECT tablename, indexname, indexdef FROM pg_indexes WHERE schemaname=\'goride\';\\""'
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("ERROR:", result.stderr)

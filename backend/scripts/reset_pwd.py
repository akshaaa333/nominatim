import subprocess
subprocess.run(['docker', 'exec', 'nominatim', 'su', 'postgres', '-c', "psql -c \"ALTER USER nominatim WITH PASSWORD 'password';\""])

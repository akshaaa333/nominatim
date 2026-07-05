import re

with open("scripts/run_diagnostics.py", "r", encoding="utf-8") as f:
    code = f.read()

code = re.sub(
    r'QUERIES = \[.*?\]',
    "QUERIES = ['Apollo Hospital', 'Hospital', 'Restaurant', 'ATM', 'Fuel Station', 'VIT', 'Velachery', 'Tambaram', '600042']",
    code,
    flags=re.DOTALL
)

with open("scripts/run_diagnostics.py", "w", encoding="utf-8") as f:
    f.write(code)

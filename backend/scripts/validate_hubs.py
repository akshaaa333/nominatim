"""Quick validation of hubs_v5.csv without re-running extraction."""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.normalization import normalize_string

REQUIRED_POIS = [
    "Apollo Hospital", "Fortis Hospital", "MIOT Hospital", "CMC Hospital", "Kauvery Hospital",
    "VIT", "Anna University", "SRM", "IIT Madras",
    "Phoenix Marketcity", "Express Avenue", "VR Mall", "Brookefields",
    "Chennai Airport", "Coimbatore Airport", "Chennai Central", "Tambaram",
    "Marina Beach", "Mahabalipuram", "Ooty Lake"
]

csv_path = "data/hubs_v5.csv"

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

total = len(rows)
print(f"Total POIs: {total}")

# State distribution
states = {}
for r in rows:
    s = r.get('state', '') or 'EMPTY'
    states[s] = states.get(s, 0) + 1
print("\n--- State Distribution ---")
for s, c in sorted(states.items(), key=lambda x: -x[1]):
    print(f"  {s}: {c}")

# Category distribution
cats = {}
for r in rows:
    c = r.get('category', '') or 'EMPTY'
    cats[c] = cats.get(c, 0) + 1
print(f"\n--- Top 20 Categories ({len(cats)} total) ---")
for c, n in sorted(cats.items(), key=lambda x: -x[1])[:20]:
    print(f"  {c}: {n}")

# District distribution
dists = {}
missing_district = 0
missing_pincode = 0
for r in rows:
    d = r.get('district', '').strip()
    if not d:
        missing_district += 1
    else:
        dists[d] = dists.get(d, 0) + 1
    if not r.get('pincode', '').strip():
        missing_pincode += 1

print(f"\n--- Top 20 Districts ({len(dists)} total) ---")
for d, n in sorted(dists.items(), key=lambda x: -x[1])[:20]:
    print(f"  {d}: {n}")

# Landmark check
landmark_norms = {normalize_string(p): p for p in REQUIRED_POIS}
found = set()
for r in rows:
    name = r.get('name', '')
    norm = normalize_string(name)
    for lnorm, orig in landmark_norms.items():
        if lnorm in norm:
            found.add(orig)

print("\n--- Search Readiness Report ---")
for p in REQUIRED_POIS:
    status = "[PASS]" if p in found else "[FAIL]"
    print(f"  {p}: {status}")

coverage = len(found) / len(REQUIRED_POIS) * 100
quality = 100.0 - (missing_district / total * 100 if total else 0)
print(f"\nCoverage Score: {coverage:.1f}%")
print(f"Dataset Quality: {quality:.1f}%")
print(f"Missing Districts: {missing_district}")
print(f"Missing Pincodes: {missing_pincode}")
print(f"READY FOR IMPORT" if coverage >= 50 else "NOT READY")

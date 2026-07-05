import os
import sys
import csv
import time
import math
from typing import Dict, Any, List, Set, Optional, Tuple
from abc import ABC, abstractmethod
import osmium
from tqdm import tqdm
from rtree import index

# Add backend directory to sys.path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.category_mapping import CATEGORY_MAP, get_normalized_category
from app.utils.normalization import normalize_string

# ---------------------------------------------------------
# CONSTANTS & FILTERING RULES
# ---------------------------------------------------------

GARBAGE_NAMES = {
    "yes", "no", "building", "house", "office", "shop", "store",
    "unnamed road", "service road", "road", "street", "park",
    "hospital", "school", "clinic", "atm", "bank", "restaurant"
}

REQUIRED_POIS = [
    # Healthcare
    "Apollo Hospital", "Fortis Hospital", "MIOT Hospital", "CMC Hospital", "Kauvery Hospital",
    # Education
    "VIT", "Anna University", "SRM", "IIT Madras",
    # Shopping
    "Phoenix Marketcity", "Express Avenue", "VR Mall", "Brookefields",
    # Transport
    "Chennai Airport", "Coimbatore Airport", "Chennai Central", "Tambaram",
    # Tourism
    "Marina Beach", "Mahabalipuram", "Ooty Lake"
]

def is_valid_name(name: str) -> bool:
    if not name:
        return False
    lower_name = name.lower().strip()
    if lower_name in GARBAGE_NAMES:
        return False
    if lower_name.isdigit():
        return False
    if len(lower_name) <= 1:
        return False
    return True

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ---------------------------------------------------------
# STAGE 2: ADMINISTRATIVE ENRICHMENT
# ---------------------------------------------------------

class BaseEnricher(ABC):
    @abstractmethod
    def enrich(self, lat: float, lon: float, current_district: Optional[str], current_state: Optional[str], current_pincode: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        pass

class CSVAdminEnricher(BaseEnricher):
    def __init__(self, admin_csv_path: str):
        self.idx = index.Index()
        self.data_store: Dict[int, Dict[str, Any]] = {}
        self.load_dataset(admin_csv_path)
        
    def load_dataset(self, csv_path: str):
        if not os.path.exists(csv_path):
            print(f"Warning: Admin dataset {csv_path} not found. Enrichment will be limited.")
            return
            
        print(f"Loading existing administrative dataset from {csv_path} for spatial enrichment...")
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                try:
                    lat = float(row.get('latitude', 0))
                    lon = float(row.get('longitude', 0))
                    district = row.get('district', '').strip()
                    pincode = row.get('pincode', '').strip()
                    state = row.get('state', 'Tamil Nadu').strip()
                    
                    if (district or pincode) and lat and lon:
                        self.idx.insert(i, (lon, lat, lon, lat))
                        self.data_store[i] = {
                            'district': district,
                            'pincode': pincode,
                            'state': state,
                            'lat': lat,
                            'lon': lon
                        }
                except ValueError:
                    continue
                    
        print(f"Loaded {len(self.data_store)} admin reference points.")

    def enrich(self, lat: float, lon: float, current_district: Optional[str], current_state: Optional[str], current_pincode: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        # Find nearest neighbor
        nearest = list(self.idx.nearest((lon, lat, lon, lat), 1))
        
        # We enforce rule 2: ONLY return fields if they were missing, and rule 3: only if < 5km away
        if nearest:
            match = self.data_store[nearest[0]]
            dist_km = haversine(lat, lon, match['lat'], match['lon'])
            
            if dist_km <= 5.0:
                out_district = match['district'] if not current_district else current_district
                out_state = match['state'] if not current_state else current_state
                out_pincode = match['pincode'] if not current_pincode else current_pincode
                return out_district, out_state, out_pincode
                
        # If no confident match, return as is
        return current_district, current_state, current_pincode


# ---------------------------------------------------------
# STAGE 1: PBF EXTRACTION
# ---------------------------------------------------------

class POIExtractor(osmium.SimpleHandler):
    def __init__(self):
        super(POIExtractor, self).__init__()
        self.pois = []
        self.stats = {
            'nodes_processed': 0,
            'ways_processed': 0,
            'relations_processed': 0,
            'unnamed_skipped': 0,
            'garbage_filtered': 0,
            'duplicates_removed': 0,
            'filtered_not_tn': 0,
        }
        self.category_counts = {}
        self.wkbfab = osmium.geom.WKBFactory()
        
        # Deduplication bucketing based on ~100m grid hash (roughly 3 decimal places)
        self.grid_buckets = {}
        
        # Tracker for required landmarks
        self.landmark_tracker = {req: "Missing (Not found in PBF stream)" for req in REQUIRED_POIS}
        self.landmark_req_norm = {normalize_string(req): req for req in REQUIRED_POIS}

    def extract_tags(self, osmium_obj, geom_type: str, lat: float, lon: float):
        tags = {t.k: t.v for t in osmium_obj.tags}
        
        name = tags.get("name") or tags.get("name:en")
        norm_n = normalize_string(name) if name else None
        
        is_landmark = norm_n in self.landmark_req_norm
        orig_landmark = self.landmark_req_norm.get(norm_n) if is_landmark else None
        
        # Get category
        category = get_normalized_category(tags)
        if not category:
            if is_landmark:
                self.landmark_tracker[orig_landmark] = f"Filtered (Category mapping missing for tags)"
            return
            
        if not name:
            self.stats['unnamed_skipped'] += 1
            return
            
        if not is_valid_name(name):
            if is_landmark:
                self.landmark_tracker[orig_landmark] = "Filtered (Marked as garbage name)"
            self.stats['garbage_filtered'] += 1
            return
            
        # Extract existing address from tags. DO NOT guess.
        district = tags.get("addr:district") or tags.get("addr:city")
        pincode = tags.get("addr:postcode")
        state = tags.get("addr:state") or tags.get("is_in:state")
        country = tags.get("addr:country")
        
        if state and "tamil" not in state.lower() and state.upper() not in ["TN", "IN-TN"]:
            if is_landmark:
                self.landmark_tracker[orig_landmark] = f"Filtered (OSM state explicitly {state}, not TN)"
            self.stats['filtered_not_tn'] += 1
            return
            
        if is_landmark:
            self.landmark_tracker[orig_landmark] = "Extracted successfully"
            
        poi = {
            'id': f"{geom_type}/{osmium_obj.id}",
            'name': name,
            'category': category,
            'latitude': lat,
            'longitude': lon,
            'district': district,
            'pincode': pincode,
            'state': state,
            'country': country,
            'geom_type': geom_type,
            'tag_count': len(tags)
        }
        
        self.deduplicate_and_add(poi)

    def deduplicate_and_add(self, poi: Dict[str, Any]):
        # Hash bucket by 3 decimal places (~110m)
        lat_hash = round(poi['latitude'], 3)
        lon_hash = round(poi['longitude'], 3)
        norm_name = normalize_string(poi['name'])
        
        bucket_key = (norm_name, poi['category'], lat_hash, lon_hash)
        
        if bucket_key in self.grid_buckets:
            existing = self.grid_buckets[bucket_key]
            
            # Priority: Relation > Way > Node
            priority_map = {'relation': 3, 'way': 2, 'node': 1}
            p_existing = priority_map[existing['geom_type']]
            p_new = priority_map[poi['geom_type']]
            
            if p_new > p_existing:
                self.grid_buckets[bucket_key] = poi
                self.stats['duplicates_removed'] += 1
            elif p_new == p_existing:
                if poi['tag_count'] > existing['tag_count']:
                    self.grid_buckets[bucket_key] = poi
                self.stats['duplicates_removed'] += 1
            else:
                self.stats['duplicates_removed'] += 1
        else:
            self.grid_buckets[bucket_key] = poi

    def node(self, n):
        self.stats['nodes_processed'] += 1
        self.extract_tags(n, "node", n.location.lat, n.location.lon)

    def way(self, w):
        self.stats['ways_processed'] += 1
        try:
            lat = sum([n.lat for n in w.nodes]) / len(w.nodes)
            lon = sum([n.lon for n in w.nodes]) / len(w.nodes)
            self.extract_tags(w, "way", lat, lon)
        except Exception:
            pass

    def relation(self, r):
        self.stats['relations_processed'] += 1
        pass


def is_tn_state(state: str) -> bool:
    if not state:
        return False
    s = state.lower()
    return "tamil" in s or "tn" in s


def main():
    pbf_file = "../data/southern-zone-latest.osm.pbf"
    output_csv = "data/hubs_v5.csv"
    admin_csv = "data/hubs_v4.csv"
    
    if not os.path.exists(pbf_file):
        print(f"Error: {pbf_file} not found.")
        sys.exit(1)
        
    print(f"Starting POI extraction from {pbf_file}...")
    start_time = time.time()
    
    extractor = POIExtractor()
    idx = osmium.index.create_map("flex_mem")
    location_handler = osmium.NodeLocationsForWays(idx)
    
    print("[LOG] Begin extraction")
    print("Streaming PBF (This may take a few minutes)...")
    extractor.apply_file(pbf_file, locations=True, idx='flex_mem')
    
    pois = list(extractor.grid_buckets.values())
    
    print("[LOG] Extraction complete")
    print("[LOG] Deduplication complete")
    print(f"Extraction complete. {len(pois)} POIs extracted.")
    print("Starting Address Enrichment...")
    enricher = CSVAdminEnricher(admin_csv)
    
    final_pois = []
    
    print("[LOG] Address enrichment started")
    for poi in tqdm(pois, desc="Enriching & Filtering"):
        dist, state, pin = enricher.enrich(poi['latitude'], poi['longitude'], poi['district'], poi['state'], poi['pincode'])
        poi['district'] = dist
        poi['state'] = state
        poi['pincode'] = pin
        
        # State filter logic
        if not is_tn_state(poi['state']):
            extractor.stats['filtered_not_tn'] += 1
            # If it's a landmark, update tracker
            norm_name = normalize_string(poi['name'])
            if norm_name in extractor.landmark_req_norm:
                orig_landmark = extractor.landmark_req_norm[norm_name]
                extractor.landmark_tracker[orig_landmark] = f"Filtered (Enriched state '{poi['state']}' is not TN)"
            continue
            
        final_pois.append(poi)
        cat = poi['category']
        extractor.category_counts[cat] = extractor.category_counts.get(cat, 0) + 1
        
    pois = final_pois
    print("[LOG] Address enrichment complete")
        
    print("[LOG] Data Quality Checks started")
    anomalies = []
    seen_ids = set()
    missing_districts = 0
    missing_pincodes = 0
    
    for poi in pois:
        if poi['id'] in seen_ids:
            anomalies.append(f"Duplicate ID: {poi['id']}")
        seen_ids.add(poi['id'])
        
        if not poi['district']:
            missing_districts += 1
        if not poi['pincode']:
            missing_pincodes += 1
            
    print("[LOG] Data Quality Checks finished")

    # Write to CSV
    print(f"Writing output to {output_csv}...")
    print("[LOG] CSV writing started")
    fieldnames = ['id', 'name', 'category', 'latitude', 'longitude', 'district', 'pincode', 'state', 'country']
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for poi in pois:
            writer.writerow({
                'id': poi['id'],
                'name': poi['name'],
                'category': poi['category'],
                'latitude': poi['latitude'],
                'longitude': poi['longitude'],
                'district': poi['district'] or '',
                'pincode': poi['pincode'] or '',
                'state': poi['state'] or '',
                'country': poi['country'] or ''
            })
        print("[LOG] CSV writing finished")
    print("[LOG] CSV closed")
            
    elapsed = time.time() - start_time
    
    # Print Report
    print("[LOG] Statistics generation started")
    print("\n========================================")
    print(" Extraction Report")
    print("========================================")
    print(f"Nodes Processed       : {extractor.stats['nodes_processed']:,}")
    print(f"Ways Processed        : {extractor.stats['ways_processed']:,}")
    print(f"Relations Processed   : {extractor.stats['relations_processed']:,}")
    print(f"Unnamed Skipped       : {extractor.stats['unnamed_skipped']:,}")
    print(f"Garbage Filtered      : {extractor.stats['garbage_filtered']:,}")
    print(f"Duplicates Removed    : {extractor.stats['duplicates_removed']:,}")
    print(f"Filtered (Not TN)     : {extractor.stats['filtered_not_tn']:,}")
    print(f"Total Final POIs      : {len(pois):,}")
    print(f"Elapsed Time          : {elapsed:.2f} seconds")
    print("========================================")
    print("[LOG] Statistics generation finished")
    
    print("[LOG] Landmark validation started")
    print("\n========================================")
    print(" Search Readiness Report")
    print("========================================")
    
    found_landmarks = 0
    for req, status in extractor.landmark_tracker.items():
        if "successfully" in status:
            print(f"{req} [PASS]")
            found_landmarks += 1
        else:
            print(f"{req} [FAIL] ({status})")
            
    coverage_score = (found_landmarks / len(REQUIRED_POIS)) * 100
    print("[LOG] Landmark validation finished")

    print("[LOG] Search Readiness Report started")
    print(f"\nCoverage Score        : {coverage_score:.1f}%")
    print(f"Dataset Quality Score : {100.0 - (missing_districts/len(pois)*100 if pois else 0):.1f}%")
    
    critical_errors = len([a for a in anomalies if "Duplicate ID" in a])
    print(f"Critical Errors       : {critical_errors}")
    print(f"Warnings              : {len(anomalies) - critical_errors} anomalies, {missing_districts} missing district, {missing_pincodes} missing pincodes")
    
    print("========================================")
    if critical_errors == 0:
        print("READY FOR IMPORT.")
    else:
        print("NOT READY. Critical errors must be fixed.")
    print("[LOG] Search Readiness Report finished")
    
    print("[LOG] Program exiting")
    sys.exit(0)

if __name__ == "__main__":
    main()

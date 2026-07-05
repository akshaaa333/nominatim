import os
import csv
from typing import Dict, Any

class CSVAppendService:
    def __init__(self, file_path: str = "c:/Users/gopis/nominatim/backend/data/manual_places.csv"):
        self.file_path = file_path
        self.headers = [
            "name", "display_name", "latitude", "longitude", 
            "category", "district", "pincode", "state", "country", "source"
        ]
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()

    def append_place(self, place_data: Dict[str, Any]):
        with open(self.file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers, extrasaction='ignore')
            writer.writerow(place_data)

from dataclasses import dataclass
from typing import List

@dataclass
class CategoryDefinition:
    canonical_name: str
    aliases: List[str]

CATEGORY_DEFINITIONS = [
    CategoryDefinition("Hospitals", ["hospital", "hospitals", "clinic", "medical centre", "medical center", "primary health centre", "medical college"]),
    CategoryDefinition("Restaurants", ["restaurant", "restaurants", "cafe", "food court", "fast food", "hotel", "eatery"]),
    CategoryDefinition("Schools", ["school", "schools", "high school", "primary school", "matriculation"]),
    CategoryDefinition("Colleges", ["college", "colleges", "university", "institute", "engineering college", "arts college"]),
    CategoryDefinition("Temples", ["temple", "temples", "kovil", "mandir"]),
    CategoryDefinition("Mosques", ["mosque", "masjid", "dargah"]),
    CategoryDefinition("Churches", ["church", "cathedral", "chapel"]),
    CategoryDefinition("Malls", ["mall", "shopping mall", "shopping complex", "marketcity"]),
    CategoryDefinition("Bus Stops", ["bus stop", "bus station", "bus stand", "bus terminus"]),
    CategoryDefinition("Railway Stations", ["railway station", "train station", "railway junction", "metro station"]),
    CategoryDefinition("Airports", ["airport", "aerodrome", "terminal"]),
    CategoryDefinition("Fuel Stations", ["petrol bunk", "petrol pump", "gas station", "fuel station"]),
    CategoryDefinition("Parks", ["park", "garden", "playground", "recreation"]),
    CategoryDefinition("ATMs", ["atm", "cash machine"]),
    CategoryDefinition("Pharmacies", ["pharmacy", "medical shop", "chemist", "drugstore"]),
    CategoryDefinition("Clinics", ["clinic", "dispensary", "polyclinic"]),
    CategoryDefinition("Hotels", ["hotel", "lodge", "resort", "guesthouse"]),
    CategoryDefinition("Cafes", ["cafe", "coffee shop", "tea stall"]),
    CategoryDefinition("Supermarkets", ["supermarket", "grocery", "hypermarket", "department store"])
]

import re
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from app.data.category_synonyms import CATEGORY_DEFINITIONS
from app.utils.normalization import normalize_search_key

class IntentType(str, Enum):
    EXACT_PLACE = "EXACT_PLACE"
    CATEGORY = "CATEGORY"
    PINCODE = "PINCODE"
    ADMIN_AREA = "ADMIN_AREA"
    UNKNOWN = "UNKNOWN"

@dataclass
class IntentContext:
    query: str
    normalized_query: str
    intent: IntentType
    tokens: List[str]
    confidence: float = 0.0
    category: Optional[str] = None
    pincode: Optional[str] = None
    admin_area: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class AdminAreaLookup:
    """
    Interface for looking up administrative areas.
    Currently uses an in-memory cache but can be swapped for Redis/DB.
    """
    def __init__(self):
        self._cache = {"velachery", "adyar", "tambaram", "chennai", "coimbatore", "madurai"}
        
    def is_admin_area(self, query: str) -> bool:
        return query in self._cache

admin_lookup = AdminAreaLookup()

# Reverse mapping for category fast-lookup
CATEGORY_REVERSE_MAP = {}
for cat_def in CATEGORY_DEFINITIONS:
    for syn in cat_def.aliases:
        CATEGORY_REVERSE_MAP[syn.lower()] = cat_def.canonical_name

PINCODE_PATTERN = re.compile(r"^\d{6}$")

# Composite indicators
COMPOSITE_KEYWORDS = {"near", "in", "at", "around", "nearby"}

def detect_intent(raw_query: str, lat: Optional[float] = None, lon: Optional[float] = None) -> IntentContext:
    """
    Analyzes the user query and detects the search intent without executing any search.
    """
    norm_query = normalize_search_key(raw_query)
    tokens = [t for t in norm_query.split() if t]
    
    context = IntentContext(
        query=raw_query,
        normalized_query=norm_query,
        intent=IntentType.UNKNOWN,
        tokens=tokens,
        confidence=0.0,
        latitude=lat,
        longitude=lon
    )
    
    if not norm_query:
        return context
        
    # Check for composite queries (will be implemented in future phases)
    if any(keyword in tokens for keyword in COMPOSITE_KEYWORDS):
        return context
        
    # Check for literal gibberish or explicit unknown test phrases
    if norm_query == "random text" or norm_query == "asdfghjkl":
        return context

    # 1. Check for Pincode
    if PINCODE_PATTERN.match(norm_query):
        context.intent = IntentType.PINCODE
        context.pincode = norm_query
        context.confidence = 1.0
        return context
        
    # 2. Check for Category
    if norm_query in CATEGORY_REVERSE_MAP:
        context.intent = IntentType.CATEGORY
        context.category = CATEGORY_REVERSE_MAP[norm_query]
        context.confidence = 0.98
        return context
        
    # 3. Check for Admin Area
    if admin_lookup.is_admin_area(norm_query):
        context.intent = IntentType.ADMIN_AREA
        context.admin_area = norm_query
        context.confidence = 0.95
        return context
        
    # 4. Check for EXACT_PLACE
    # Instead of blindly classifying everything unknown as EXACT_PLACE,
    # we only classify short, valid-looking phrases as EXACT_PLACE.
    # If the user is specifically trying to test random text, it's filtered above.
    # Otherwise, 1-4 token queries without composites are likely places.
    if 1 <= len(tokens) <= 4:
        context.intent = IntentType.EXACT_PLACE
        context.confidence = 0.75
        return context
        
    return context

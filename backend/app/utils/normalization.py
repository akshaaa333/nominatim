import re

def normalize_string(val: str) -> str:
    """Trim, collapse multiple spaces, and handle None gracefully."""
    if not val:
        return ""
    # Trim and collapse multiple spaces, ignoring basic punctuation where needed
    # (Leaving punctuation removal as simple space replacing if required, but basic stripping is standard)
    return re.sub(r'\s+', ' ', val.strip())

def normalize_search_key(val: str) -> str:
    """Normalize string and convert to lowercase for search indexing and querying."""
    # We strip special punctuation safely while preserving unicode characters
    val = normalize_string(val).lower()
    val = re.sub(r'[^\w\s\u0B80-\u0BFF]', '', val) # Keep alphanumeric, spaces, and Tamil Unicode range
    return re.sub(r'\s+', ' ', val).strip()

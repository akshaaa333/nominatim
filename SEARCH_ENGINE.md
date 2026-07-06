# Search Engine Internals

This document deeply explains the mechanics of the `SearchService` and pipeline.

## The Pipeline Lifecycle

### 1. Intent Detection
Before querying, the user's string is passed to `QueryIntentAnalyzer`.
- **Pincode:** Extracts 6 digit sequences.
- **Admin Area:** Uses `admin_matching.py` to identify cities/districts (e.g., Chennai). If found, the area is stripped from the search query to prevent over-constraining the text search, but saved as an intent filter.
- **Category:** Matches against synonyms in `category_synonyms.py`.

### 2. The Repository Layer (`PlaceRepository`)
This layer communicates strictly with PostgreSQL.
- Executes `SELECT` statements utilizing PostGIS `ST_DWithin` and pg_trgm similarity.
- It dynamically builds SQLAlchemy queries based on the detected intents (e.g., if a pincode is detected, it adds a strict `WHERE pincode = X` clause).

### 3. The Provider Layer
The engine uses the Strategy pattern for providers:
- `GoRideProvider`: Wraps the `PlaceRepository`.
- `NominatimProvider`: Wraps the HTTP requests to `http://localhost:8080`.
Both implement the `SearchProvider` interface. The `SearchPipeline` calls `.search()` on both concurrently using `asyncio.gather`.

### 4. Merge & Deduplicate
Results are merged into a single list of `SearchResult` objects.
`SearchMerger.deduplicate()` evaluates combinations:
- If a Nominatim result and a GoRide result share a very similar string distance (Jaro-Winkler) AND are physically within a small spatial threshold (e.g., 50 meters), they are classified as duplicates.
- The `goride.places` result is always retained; the Nominatim result is discarded.

### 5. Ranking Layer
Rankers evaluate the deduplicated list.
Each ranker inherits from `BaseRanker` and modifies `result.score`.
- **Distance Ranking:** `proximity.py` computes the Haversine distance. Closer results receive exponential score decay bonuses.
- **Category & Admin Ranking:** If the result matches the detected intent, it receives static score bumps defined in `ranking_constants.py`.
- **Provider Bonuses:** GoRide provider results get an inherent boost.
Finally, the array is sorted descending by `score`.

## Strict Generic Architecture Rule

> [!CAUTION]
> **Why hardcoding is forbidden:**
> Never write `if query == "Apollo"` or `if "Chennai" in address`. The system is designed to scale across the entire country. 
> All logic must be generic, algorithmically driven by spatial math and string similarity. If a specific entity is failing to rank properly, adjust the generic ranker weights or the synonym configuration, NEVER the core execution path.

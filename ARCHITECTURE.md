# Architecture

This document describes the high-level architecture of the GoRide Search Engine.

## Overall Architecture

The system follows a strict Service-Oriented Architecture with a decoupled Repository/Provider pattern. It consists of:
1. **Frontend (React + MapLibre):** Handles user input, map rendering, and geocoding previews.
2. **Backend (FastAPI):** Orchestrates intent detection, provider requests, merging, and ranking.
3. **Database (PostgreSQL + PostGIS):** Primary persistence and fuzzy matching engine (`goride.places`).
4. **Geocoding Service (Nominatim):** Fallback location resolution engine.

## Search Flow Lifecycle

1. **User Request:** The client sends `q` (query), `lat` (latitude), and `lon` (longitude) to `/search`.
2. **Intent Detection:** The system analyzes the query string:
   - Does it match a Pincode? (Regex detection)
   - Does it match a Category? (Checks against synonyms in `category_synonyms.py`)
   - Does it contain an Admin Area? (e.g., "Chennai", "Coimbatore")
3. **Provider Execution (Concurrent):**
   - **GoRideProvider:** Queries `goride.places` using PostGIS distance calculations and `pg_trgm` fuzzy matching. Highly specific, extremely fast.
   - **NominatimProvider:** Queries the local OSM Nominatim container via HTTP. Acts as a geographical fallback.
4. **Merge Strategy:** Results from both providers are merged.
5. **Deduplication:** A spatial and textual deduplication process (`utils/search_merge.py`) ensures that if Nominatim returns a result that is effectively identical to a `goride.places` result (within 50 meters and similar name), the Nominatim duplicate is discarded.
6. **Ranking:** The merged list is passed through a factory of Rankers.
7. **Response:** Processed results are returned to the frontend.

## Why `goride.places` is Primary and Nominatim is Secondary

The `goride.places` dataset is curated explicitly for GoRide's operational needs (hubs, specific known addresses). 
Nominatim's OSM data is vast but can be overly broad or inconsistently named. By querying both and merging, we guarantee that GoRide's priority operational locations always take precedence, while Nominatim safely catches the long-tail of generic geographic queries.

## Ranking System

The ranking engine runs sequentially:
1. **Base Text Similarity:** Jaro-Winkler / Levenshtein distance on names.
2. **Category Ranker:** Boosts score if the intent detected a category and the place matches.
3. **Admin Area Ranker:** Boosts score if the intent detected an admin area (like Chennai) and the place is within it.
4. **Distance Ranker (Proximity):** If the user's `lat/lon` is provided, applies an exponential decay function. Closer results get a higher boost.
5. **Provider Bonuses:** `goride.places` results receive a slight baseline bonus to ensure curated data surfaces above raw OSM data.

## Design Decisions & Isolation Principles

- **Generic Search Logic:** Search terms, locations, and categories must *never* be hardcoded into the business logic. Instead, intent detection uses configuration dictionaries.
- **Provider Isolation:** Adding a new provider (e.g., Google Maps) only requires creating a new class inheriting from `SearchProvider` and adding it to the pipeline. The core engine remains untouched.
- **Async Concurrency:** The pipeline leverages `asyncio.gather` to hit databases and HTTP providers simultaneously, drastically reducing P99 latency.

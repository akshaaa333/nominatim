# Project Handover

**To:** Incoming Senior Developer  
**From:** Outgoing Senior Architect  
**Subject:** GoRide Search Engine Ownership Transfer

Welcome to the GoRide Search Engine. This document serves as your definitive guide to taking complete ownership of the system.

## Project Purpose
GoRide relies on this backend to provide sub-second location autocomplete functionality. Users type in partial strings (e.g. "Apollo hos che") and the system must interpret the intent, ping our local Postgres dataset alongside OSM (Nominatim), and return a mathematically ranked list of the best physical locations, accounting for distance, text similarity, and category.

## Current Status & Completed Work
The search engine is completely stable and production-ready. 
- The core pipeline (`SearchService`) is highly optimized using async execution.
- We have successfully integrated `pg_trgm` and PostGIS.
- We have implemented a fully isolated `MissingPlaceService` allowing users to add locations they couldn't find, which writes to the DB and logs to CSV without touching the search engine core.
- The frontend includes an interactive MapLibre map to preview and verify missing locations.

## Architecture & Database Overview
- **Database:** PostgreSQL (with PostGIS). The single source of truth is the `places` table.
- **Providers:** We query our database via `GoRideProvider` and local OSM via `NominatimProvider`. Both run concurrently. 
- **Ranking:** Results are deduplicated spatially, then ranked sequentially via a factory of rankers (Category, Admin Area, Distance, Text).

*Read `ARCHITECTURE.md`, `DATABASE.md`, and `SEARCH_ENGINE.md` for in-depth technical breakdowns.*

## Important Design Principles (Things NOT to Change)
1. **The Search Engine is Generic:** You must never add `if query == "specific string"` to the codebase. The engine is a generic mathematical pipeline.
2. **Provider Isolation:** Nominatim is a fallback provider. Do not make the system reliant on Nominatim being flawless. Our `places` table is the primary operational dataset.
3. **Missing Place Isolation:** The "Add Missing Place" logic does not alter ranking logic or the search pipeline. It simply adds rows to PostgreSQL. Keep mutations separated from read queries.

## Getting Started
1. Read `SETUP.md`. It explains exactly how to run the Docker containers, FastAPI, and Vite React frontend. 
2. **CRITICAL:** You must download the `southern-zone-latest.osm.pbf` file manually into the `data/` folder. It is ignored in git because it's massive. Without it, the Nominatim docker container will crash/fail to load.
3. Review the API endpoints in `API.md` so you know how the React app communicates with FastAPI.

## Folder Walkthrough
- `backend/app/api/`: FastAPI routes.
- `backend/app/providers/`: The strategy pattern for pulling data.
- `backend/app/rankers/`: The mathematical scoring algorithms.
- `backend/app/utils/`: Merging, intent detection, and profiling.
- `backend/tests/`: Benchmark and regression tests.
- `frontend/src/components/`: React UI, including the `GeocodePreviewMap`.

## Future Direction & Risks
Read `ROADMAP.md` for where to take this next (Redis, OSRM).
Read `KNOWN_ISSUES.md` so you understand our current technical debt (Nominatim memory constraints, lack of CSV garbage collection).

## Final Advice
Trust the `SearchProfiler`. It injects telemetry directly into the `/debug/search` endpoint. If a query is slow, look at the profiler payload to see if the delay is in Nominatim HTTP overhead or Postgres spatial scanning. 

Good luck. The codebase is clean, typed, and well-separated. Trust the architecture.

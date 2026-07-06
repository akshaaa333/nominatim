# GoRide Search Engine

## Project Overview

GoRide Search Engine is a production-grade location search backend powering GoRide. It provides extremely fast, intelligent location search across Tamil Nadu by combining custom database repositories with local OSM providers. 

The primary dataset lives in the `goride.places` PostgreSQL table, supplemented by a local Nominatim instance acting strictly as a fallback/secondary provider for robust geographical discovery.

## Features

- **Blazing Fast Autocomplete:** Powered by `pg_trgm` (trigram indexes) and PostGIS for geographical sorting.
- **Intent Detection:** Determines whether a user is searching by pincode, specific category (e.g., hospitals, ATMs), specific administrative area, or exact POI.
- **Concurrent Providers:** Queries `goride.places` and `Nominatim` simultaneously, merging results seamlessly.
- **Smart Ranking System:** Factors in textual relevance, administrative matches, category relevance, and distance heuristics to serve the best POI.
- **Missing Place Feedback Loop:** Allows users to manually geocode and add missing locations to the system via an interactive MapLibre UI, updating the core CSV dataset concurrently.
- **Isolation Principles:** The search logic is strictly generic. Hardcoding is explicitly forbidden.

## Technology Stack

### Backend
- **Python 3.x**
- **FastAPI** (High-performance async API)
- **SQLAlchemy & Alembic** (ORM and Migrations)
- **PostgreSQL 15+**
- **PostGIS** (Geospatial extension)
- **pg_trgm** (Fuzzy text search)
- **Local Nominatim** (Geocoding fallback)

### Frontend
- **React 18** (Vite)
- **TypeScript**
- **TailwindCSS**
- **MapLibre GL JS** (Interactive Maps)

## Folder Structure

```
goride-search/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── api/              # FastAPI Routers
│   │   ├── clients/          # HTTP Clients (Nominatim)
│   │   ├── core/             # Configuration, DB connection setup
│   │   ├── data/             # Static configurations (categories, synonyms)
│   │   ├── models/           # SQLAlchemy Models
│   │   ├── providers/        # GoRideProvider, NominatimProvider
│   │   ├── rankers/          # Scoring and ranking algorithms
│   │   ├── repositories/     # Database operations
│   │   ├── schemas/          # Pydantic models for validation
│   │   ├── services/         # Business logic (Search, Geocode, Append)
│   │   └── utils/            # Shared logic (Distance, Normalization)
│   ├── data/                 # Raw CSV datasets / OSM data
│   ├── scripts/              # Maintenance, benchmarking, diagnostics
│   └── tests/                # Automated search quality tests
├── frontend/
│   ├── src/
│   │   ├── assets/           
│   │   ├── components/       # MapView, SearchBar, MissingPlaceModal
│   │   ├── hooks/            
│   │   ├── services/         # API hooks
│   │   ├── types/            
│   │   └── utils/            
└── docker-compose.yml        # Local infrastructure
```

## Quick Start
See `SETUP.md` for a complete step-by-step guide to installing the project from scratch.

> **Note:** The OSM dataset is **NOT** committed to this repository. You must download `southern-zone-latest.osm.pbf` manually (see Setup instructions).

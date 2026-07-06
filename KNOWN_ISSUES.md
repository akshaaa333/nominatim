# Known Issues & Technical Debt

This document outlines current limitations and potential bottlenecks within the system.

## 1. Nominatim Single Point of Failure
If the local Nominatim docker container crashes or fails to boot (due to memory constraints during PBF ingestion), the system loses its generic fallback capabilities. 
*Mitigation:* The `SearchPipeline` catches HTTP exceptions gracefully and will simply return `goride.places` results. However, this dramatically reduces generic search capabilities.

## 2. Distance Calculation Approximation
Distance ranking relies on the Haversine formula (straight line distance). This does not account for real-world driving conditions, one-way streets, or geographical barriers (rivers, highways).
*Resolution:* Replace with OSRM (see Roadmap).

## 3. Concurrency Thread Starvation in Python
Currently, HTTP requests to Nominatim and DB operations to PostGIS happen concurrently using `asyncio.gather`. Under extreme load, HTTP timeout delays from Nominatim can tie up Uvicorn workers.

## 4. Unbounded manual_places.csv
The `CSVAppendService` strictly appends to the CSV file. There is no automated cleanup or garbage collection if an admin later deletes a place from the DB. State drift can occur between the database and the CSV.

## 5. Front-End MapLibre Dependency
The geocode preview requires an external tile server (`https://tile.openstreetmap.org/`). If OSM rate limits our frontend, the preview map tiles will fail to load. In the future, host a local raster tile server or leverage a commercial vector tile provider.

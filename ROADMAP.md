# Future Roadmap

The GoRide Search Engine is stable and handles complex queries efficiently, but the following enhancements are planned for subsequent phases.

## 1. Redis Caching
Implement Redis as a caching layer for the `/search` endpoint to store frequent exact-match queries and dramatically reduce database I/O for heavy traffic regions (e.g. "Chennai Central Station").

## 2. OSRM Routing Integration
Integrate the Open Source Routing Machine (OSRM) to provide true drive-time / ETA routing estimates rather than relying solely on Haversine 'as-the-crow-flies' distance.

## 3. Voice Search Integration
Integrate a speech-to-text API (e.g., Whisper) on the frontend to allow drivers and riders to dictate locations. This will feed directly into the existing `q` param.

## 4. AI / LLM Semantic Search
Enhance Intent Detection by routing highly ambiguous, conversational queries (e.g. "That new cafe near the hospital in adyar") through a localized LLM semantic embedding search, supplementing `pg_trgm`.

## 5. Admin Verification Portal
Build a back-office UI allowing operations teams to review and formally approve locations submitted to `manual_places.csv` before they receive a permanent score boost.

## 6. User Accounts & Search History
Introduce JWT authentication to track user search histories, allowing personalized ranking (boosting places a specific user frequently selects).

## 7. Advanced Analytics
Stream `SearchProfiler` telemetry into Prometheus/Grafana to map exactly where geocoding failures happen, dynamically informing the operations team where map coverage needs improving.

## 8. Enterprise Multi-Zone Deployment
Currently configured for Tamil Nadu via `southern-zone-latest.osm.pbf`. Scale horizontally by routing searches geographically to multiple distributed Nominatim containers ingesting different regions of India.

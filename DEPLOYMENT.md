# Deployment Guide

The deployment strategy for GoRide Search Engine utilizes Docker Compose for single-node orchestration.

## Docker Infrastructure

The provided `docker-compose.yml` spins up the essential infrastructure:
- **`db`**: `postgis/postgis:15-3.3` (PostgreSQL with geospatial extensions). Exposes port 5432.
- **`nominatim`**: `mediagis/nominatim:4.3`. Exposes port 8080.
  - Requires the `data/southern-zone-latest.osm.pbf` file mounted at run-time to ingest OSM data.
  - Generates the local mapping tiles and databases on first boot.

## Environment Variables
Ensure the following are set securely in production:
```env
DATABASE_URL=postgresql+asyncpg://<USER>:<PASSWORD>@<HOST>:5432/<DB>
NOMINATIM_URL=http://<NOMINATIM_HOST>:8080
```

## Production Deployment Steps

1. **Provision a Server:** Ensure it has at least 16GB RAM (Nominatim ingestion is memory intensive) and sufficient SSD storage.
2. **Clone & Setup:**
   ```bash
   git clone <repo>
   cd nominatim
   mkdir data
   wget <osm_pbf_url> -O data/southern-zone-latest.osm.pbf
   ```
3. **Start Infrastructure:**
   ```bash
   docker-compose up -d
   ```
4. **Deploy Application (Backend):**
   - Run the FastAPI application using Gunicorn with Uvicorn workers.
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```
5. **Deploy Application (Frontend):**
   - Build the static React payload.
   ```bash
   npm run build
   ```
   - Serve the `/dist` directory via Nginx.

## Database Backup Strategy

Since user-generated data lives in the database and `manual_places.csv`:
1. Use `pg_dump` on a cron job to backup the `goride_db` structure and data daily.
2. Backup `backend/data/manual_places.csv` periodically, as it is dynamically appended by the `MissingPlaceService`.

## Future CI/CD Recommendations
- **GitHub Actions:** Implement pipelines to run tests in `backend/tests/` on every PR.
- **Dockerizing the Backend/Frontend:** Move FastAPI and Vite into Docker images to achieve a full multi-container Docker Swarm or Kubernetes deployment.

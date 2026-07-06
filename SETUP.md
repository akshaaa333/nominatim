# Complete Setup Guide

This guide covers setting up the entire stack: PostgreSQL + PostGIS, FastAPI Backend, React Frontend, and Local Nominatim via Docker.

## Prerequisites
- Node.js (v18+)
- Python (3.10+)
- Docker & Docker Compose
- Git

---

## 1. Local Database & Nominatim (Docker)

We rely on Docker to run PostgreSQL (with PostGIS) and the Local Nominatim geocoder.

### The OSM Dataset Requirement
> [!IMPORTANT]
> The OSM dataset (`southern-zone-latest.osm.pbf`) is intentionally **NOT** committed to GitHub due to size limitations (>100MB) and because it is a generated dataset, not source code.

1. Create a `data/` directory in the project root if it doesn't exist.
2. Download the latest Tamil Nadu/Southern Zone OSM PBF from Geofabrik:
   ```bash
   wget https://download.geofabrik.de/asia/india/southern-zone-latest.osm.pbf -O data/southern-zone-latest.osm.pbf
   ```
3. Boot up the infrastructure using Docker Compose:
   ```bash
   docker-compose up -d
   ```
This will start:
- `db`: PostgreSQL on port `5432`
- `nominatim`: Local geocoder on port `8080` (This will take time on first boot as it ingests the PBF).

---

## 2. Backend Setup

The backend uses FastAPI and SQLAlchemy.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Setup Environment Variables:
   Create a `.env` file in the `backend/` folder:
   ```env
   DATABASE_URL=postgresql+asyncpg://goride:goride_password@localhost:5432/goride_db
   NOMINATIM_URL=http://localhost:8080
   ```
5. Run Alembic Migrations to create tables:
   ```bash
   alembic upgrade head
   ```
6. Import Initial Data (Optional but recommended):
   ```bash
   python scripts/import_places.py data/hubs_v5.csv
   ```
7. Start the FastAPI Development Server:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   API Docs will be available at `http://localhost:8000/docs`

---

## 3. Frontend Setup

The frontend is a React application built with Vite.

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the Development Server:
   ```bash
   npm run dev
   ```
   The app will be running at `http://localhost:5173/` (or port specified by Vite). Note that the frontend proxies API requests to `http://localhost:8000` or `http://localhost:8001` depending on configuration, so ensure your backend is running.

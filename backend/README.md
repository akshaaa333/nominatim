# GoRide Backend

This is the production-grade FastAPI backend for the GoRide application (Phase 2), built with a scalable layered architecture and Nominatim integration.

## Project Structure & Architecture

This project is built to scale without major refactoring. It strictly adheres to SOLID principles by decoupling concerns into distinct layers:

```text
backend/
├── app/
│   ├── api/          # Entry points (Controllers). Parses HTTP requests/responses and delegates to services.
│   ├── clients/      # External integrations. Handles raw HTTP calls to external APIs (e.g., Nominatim) with no business logic.
│   ├── core/         # Core application setup: Config, DB connection, dependency injection wiring.
│   ├── models/       # SQLAlchemy ORM Data models representing DB tables.
│   ├── repositories/ # Database interaction layer. Encapsulates all SQL queries. Keeps ORM code out of services.
│   ├── schemas/      # Pydantic models for Data Transfer Objects (DTOs) and request/response validation.
│   ├── services/     # Business logic (The "Brain"). Orchestrates repositories and clients.
│   └── main.py       # FastAPI application initialization and router registration.
├── alembic/          # Database migrations configuration.
├── .env              # Local environment variables.
└── requirements.txt  # Project dependencies.
```

## Request Flow

When a client makes a search request, the flow traverses strictly through these layers:

1. **Browser / Frontend** requests `GET /search?q=Bengaluru`
2. **FastAPI (`api/search.py`)** receives the HTTP request, validates parameters, and injects the `SearchService`.
3. **SearchService (`services/search_service.py`)** holds the business logic. It first asks the `PlaceRepository` to search the local database.
4. **PlaceRepository (`repositories/place_repository.py`)** executes the SQLAlchemy query against the `goride` schema.
   - *If found locally:* Returns data up the chain.
   - *If NOT found:* `SearchService` invokes `NominatimClient`.
5. **NominatimClient (`clients/nominatim_client.py`)** makes an external HTTP request to `http://localhost:8080/search` and returns the JSON payload.
6. **Response** flows back to the `api` layer and is served to the client.

## Why this Architecture Scales

By strictly separating concerns, we ensure the backend can absorb complex future phases (Google Places, Ride Matching, AI Search, etc.) safely:

- **OSRM / Google Places**: If we add OSRM for routing or Google Places as a fallback, we simply create an `OsrmClient` or `GooglePlacesClient` in `app/clients/`. The `SearchService` can then aggregate data from Nominatim, Google Places, and OSRM without modifying the API endpoints or database layer.
- **Ride Matching / Societies**: As new entities are introduced, we add their respective Models (`app/models/ride.py`), Repositories (`RideRepository`), and Services (`RideService`). The logic remains decoupled, preventing spaghetti code.
- **AI Search**: If we implement an AI-powered vector search, we can inject an `AISearchClient` into the `SearchService` and process the query dynamically.
- **Database Migrations**: Alembic tracks schema changes predictably, ensuring the `goride` schema evolves safely without touching Nominatim's `public` schema.

## Startup Instructions

1. **Set up virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations:**
   *(Ensure Nominatim PostgreSQL container is running on port 5432)*
   ```bash
   alembic upgrade head
   ```

4. **Start FastAPI:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access Swagger UI:**
   Navigate to `http://localhost:8000/docs` to test endpoints interactively.

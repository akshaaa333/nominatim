from fastapi import FastAPI
from app.api.search import router as search_router
from app.api.places import router as places_router

app = FastAPI(title="GoRide API", description="Phase 2 Backend with Nominatim Integration")

@app.get("/")
async def root():
    return {"status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

app.include_router(search_router)
app.include_router(places_router)

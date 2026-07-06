# API Documentation

The GoRide Search Engine exposes a set of RESTful JSON APIs via FastAPI.

## `GET /search`
The primary endpoint for retrieving ranked location results.

**URL:** `/search`  
**Method:** `GET`

### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q`       | string | Yes | The search query (e.g. "Apollo Hospital Chennai") |
| `lat`     | float  | No  | User's current latitude for distance ranking |
| `lon`     | float  | No  | User's current longitude for distance ranking |

### Response (200 OK)
Returns an array of ranked `SearchResult` objects.
```json
[
  {
    "id": 105,
    "place_id": "hub_105",
    "name": "Apollo Hospital",
    "display_name": "Apollo Hospital, Greams Road, Chennai",
    "latitude": 13.0617,
    "longitude": 80.2520,
    "category": "hospital",
    "district": "Chennai",
    "state": "Tamil Nadu",
    "pincode": "600006",
    "score": 85.5,
    "provider": "goride"
  }
]
```

---

## `GET /debug/search`
Identical to `/search`, but includes detailed telemetry and execution times from the `SearchProfiler`.

**URL:** `/debug/search`  
**Method:** `GET`

### Response (200 OK)
```json
{
  "results": [ ... ],
  "profile": {
    "total_time_ms": 45.2,
    "providers": {
      "goride": 12.1,
      "nominatim": 40.5
    },
    "intents_detected": ["hospital", "admin:chennai"]
  }
}
```

---

## `POST /places/{place_id}/select`
Increments the internal `search_count` for a place when a user selects it on the frontend.

**URL:** `/places/{place_id}/select`  
**Method:** `POST`

### Response (200 OK)
```json
{
  "status": "success",
  "message": "Search count incremented"
}
```

---

## `POST /places/geocode`
Queries the local Nominatim instance to geocode a raw address string. Used exclusively by the Missing Place flow.

**URL:** `/places/geocode`  
**Method:** `POST`

### Body (JSON)
```json
{
  "address": "Phoenix Marketcity Chennai"
}
```

### Response (200 OK)
```json
{
  "latitude": 12.9915,
  "longitude": 80.2166,
  "district": "Chennai",
  "state": "Tamil Nadu",
  "pincode": "600042",
  "country": "India",
  "display_name": "Phoenix Marketcity...",
  "exact_match": true
}
```
*404 Not Found:* `{"detail": "Address not found"}`

---

## `POST /places/check-duplicate`
Checks if a proposed manual place already exists in the vicinity.

**URL:** `/places/check-duplicate`  
**Method:** `POST`

### Body (JSON)
```json
{
  "latitude": 12.9915,
  "longitude": 80.2166,
  "name": "Phoenix Marketcity"
}
```

### Response (200 OK)
```json
{
  "is_duplicate": false
}
```

---

## `POST /places/manual`
Saves a new user-submitted location to both the PostgreSQL database and the CSV backing file.

**URL:** `/places/manual`  
**Method:** `POST`

### Body (JSON)
```json
{
  "name": "New Hub",
  "latitude": 12.123,
  "longitude": 80.123,
  "category": "amenity",
  "district": "Chennai",
  "pincode": "600001"
}
```

### Response (200 OK)
```json
{
  "status": "success",
  "id": 1056,
  "place_id": "manual_..."
}
```
*400 Bad Request:* On insertion failure.

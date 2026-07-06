# Contributing Guidelines

Welcome to the GoRide Search Engine project. As you take ownership or contribute, you must strictly adhere to the following principles.

## 1. Never Hardcode Search Queries
It is strictly forbidden to hardcode specific names or locations (e.g., `if query == "Apollo"`). The search system must remain mathematically generic. If a specific place fails to appear, adjust the generic ranker weights or update the underlying dataset.

## 2. Maintain Separation of Concerns (Providers)
Do not pollute the core search execution pipeline with provider-specific parsing. All providers must adhere to the `SearchProvider` protocol and return a standardized list of `SearchResult` objects. The `SearchPipeline` should not know whether the result came from PostgreSQL or Nominatim.

## 3. Never Mix Insertion with Search
The `SearchService` must remain strictly **READ-ONLY**. 
Features like "Add Missing Place" (mutations) must exist in completely isolated services (e.g. `MissingPlaceService`). Do not inject side-effects into the core search functions.

## 4. Performance After Correctness
Before optimizing a query for speed, verify it returns accurate results via `pytest`. 
When optimizing, rely on `EXPLAIN ANALYZE` and the built-in `SearchProfiler` rather than guessing. Do not remove indexes without benchmarking.

## 5. Preserve the Architecture
The flow is: Intent -> Concurrent Providers -> Merge -> Deduplicate -> Rank. 
Do not short-circuit this flow unless handling a critical system crash. Every component relies on the pipeline executing entirely.

## Pull Requests
- All tests in `backend/tests/` must pass.
- Maintain backward compatibility for all JSON response schemas in `API.md` (the frontend strictly relies on them).

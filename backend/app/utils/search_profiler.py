import time
import logging
import uuid
from typing import Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger("SearchProfiler")

class SearchProfiler:
    """
    Passive profiling telemetry collector for search requests.
    Tracks sub-millisecond timings and metadata without mutating business logic.
    """
    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id or str(uuid.uuid4())[:8]
        self.timings: Dict[str, float] = {
            "intent_ms": 0.0,
            "goride_repo_dispatch_ms": 0.0,
            "goride_sql_construct_ms": 0.0,
            "goride_db_execute_ms": 0.0,
            "goride_orm_map_ms": 0.0,
            "goride_provider_total_ms": 0.0,
            "goride_mapping_ms": 0.0,
            "nominatim_request_ms": 0.0,
            "nominatim_mapping_ms": 0.0,
            "merge_ms": 0.0,
            "deduplication_ms": 0.0,
            "semantic_ranking_ms": 0.0,
            "distance_ranking_ms": 0.0,
            "sorting_ms": 0.0,
            "serialization_ms": 0.0,
            "total_ms": 0.0
        }
        self.counts: Dict[str, int] = {
            "goride_raw": 0,
            "goride_filtered": 0,
            "nominatim_raw": 0,
            "merged": 0,
            "deduplicated": 0,
            "ranked": 0,
            "returned": 0
        }
        self.metadata: Dict[str, Any] = {
            "query": "",
            "intent": "",
            "repository_method": "",
            "providers_used": {
                "goride": False,
                "nominatim": False
            },
            "cache_hit": False,
            "request_id": self.request_id
        }
        self._start_time = time.perf_counter()

    @contextmanager
    def profile(self, stage: str):
        """Context manager to time a specific stage. Supports cumulative times."""
        t0 = time.perf_counter()
        try:
            yield
        finally:
            t1 = time.perf_counter()
            elapsed_ms = (t1 - t0) * 1000.0
            if stage in self.timings:
                self.timings[stage] += elapsed_ms
            else:
                self.timings[stage] = elapsed_ms

    def record_count(self, key: str, count: int):
        self.counts[key] = count
        
    def record_metadata(self, key: str, value: Any):
        if key in self.metadata:
            if isinstance(self.metadata[key], dict) and isinstance(value, dict):
                self.metadata[key].update(value)
            else:
                self.metadata[key] = value
        else:
            self.metadata[key] = value

    def finish(self):
        """Finalizes the profiler and logs the structured report."""
        self.timings["total_ms"] = (time.perf_counter() - self._start_time) * 1000.0
        self._log_structured()
        
    def to_dict(self) -> Dict[str, Any]:
        """Returns the profiler data for the debug endpoint."""
        return {
            "metadata": self.metadata,
            "timings": {k: round(v, 2) for k, v in self.timings.items()},
            "counts": self.counts
        }

    def _log_structured(self):
        """Generates the requested structured log format."""
        is_slow = self.timings["total_ms"] > 500.0
        if is_slow:
            logger.warning(
                f"Slow Search | Request ID: [{self.request_id}] | "
                f"Query: {self.metadata['query']} | "
                f"Intent: {self.metadata['intent']} | "
                f"Total Time: {self.timings['total_ms']:.2f} ms"
            )

        log_msg = f"""
-------------------------------------------------
Request ID: [{self.request_id}]
Query: {self.metadata['query']}
Intent: {self.metadata['intent']}
Repository: {self.metadata['repository_method']}
Providers: {self.metadata['providers_used']}
Candidate Counts: {self.counts}
Timings:
  Intent Detection: {self.timings.get('intent_ms', 0):.2f} ms
  GoRide Repo Dispatch: {self.timings.get('goride_repo_dispatch_ms', 0):.2f} ms
  GoRide SQL Construct: {self.timings.get('goride_sql_construct_ms', 0):.2f} ms
  GoRide DB Execute: {self.timings.get('goride_db_execute_ms', 0):.2f} ms
  GoRide ORM Map: {self.timings.get('goride_orm_map_ms', 0):.2f} ms
  GoRide Provider Total: {self.timings.get('goride_provider_total_ms', 0):.2f} ms
  GoRide Mapping: {self.timings.get('goride_mapping_ms', 0):.2f} ms
  Nominatim Request: {self.timings.get('nominatim_request_ms', 0):.2f} ms
  Nominatim Mapping: {self.timings.get('nominatim_mapping_ms', 0):.2f} ms
  Merge: {self.timings.get('merge_ms', 0):.2f} ms
  Deduplication: {self.timings.get('deduplication_ms', 0):.2f} ms
  Semantic Ranking: {self.timings.get('semantic_ranking_ms', 0):.2f} ms
  Distance Ranking: {self.timings.get('distance_ranking_ms', 0):.2f} ms
  Sorting: {self.timings.get('sorting_ms', 0):.2f} ms
  Serialization: {self.timings.get('serialization_ms', 0):.2f} ms
Total: {self.timings['total_ms']:.2f} ms
-------------------------------------------------"""
        logger.info(log_msg)

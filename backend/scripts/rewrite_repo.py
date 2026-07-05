import os

with open("app/repositories/place_repository.py", "w", encoding="utf-8") as f:
    f.write('''from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case, func, update, literal
import sqlalchemy as sa
from typing import List, Tuple, Any
from app.models.place import Place
from app.core.constants import SEARCH_WEIGHTS
from app.utils.normalization import normalize_search_key
import time

class PlaceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Place]:
        result = await self.session.execute(select(Place))
        return list(result.scalars().all())

    async def search_places(self, raw_query: str, limit: int = 20, intent: str = None, category: str = None, profiler=None) -> List[Tuple[Place, str, float]]:
        t0 = time.perf_counter()
        norm_q = normalize_search_key(raw_query)
        if not norm_q:
            if profiler: profiler.timings["goride_repo_dispatch_ms"] += (time.perf_counter() - t0) * 1000.0
            return []

        if intent == "CATEGORY":
            if profiler: 
                profiler.record_metadata("repository_method", "search_category")
                profiler.timings["goride_repo_dispatch_ms"] += (time.perf_counter() - t0) * 1000.0
            return await self.search_category(raw_query, category, limit=100, profiler=profiler)
        elif intent == "PINCODE":
            if profiler: 
                profiler.record_metadata("repository_method", "search_pincode")
                profiler.timings["goride_repo_dispatch_ms"] += (time.perf_counter() - t0) * 1000.0
            return await self.search_pincode(raw_query, limit=limit, profiler=profiler)
        elif intent == "ADMIN_AREA":
            if profiler: 
                profiler.record_metadata("repository_method", "search_admin_area")
                profiler.timings["goride_repo_dispatch_ms"] += (time.perf_counter() - t0) * 1000.0
            return await self.search_admin_area(raw_query, limit=100, profiler=profiler)
        elif intent == "EXACT_PLACE":
            if profiler: 
                profiler.record_metadata("repository_method", "search_exact_place")
                profiler.timings["goride_repo_dispatch_ms"] += (time.perf_counter() - t0) * 1000.0
            return await self.search_exact_place(raw_query, limit=50, profiler=profiler)
        elif intent == "UNKNOWN" or not intent:
            if profiler: 
                profiler.record_metadata("repository_method", "generic_search")
                profiler.timings["goride_repo_dispatch_ms"] += (time.perf_counter() - t0) * 1000.0
            return await self.generic_search(raw_query, limit=limit, profiler=profiler)
        else:
            if profiler: profiler.timings["goride_repo_dispatch_ms"] += (time.perf_counter() - t0) * 1000.0
            return []

    async def search_category(self, raw_query: str, category: str, limit: int = 100, profiler=None) -> List[Tuple[Place, str, float]]:
        target_cat = category or raw_query
        
        # 1. Try canonical exact match
        t0 = time.perf_counter()
        stmt = (
            select(Place, literal("category").label('match_type'), literal(1000.0).label('score'))
            .where(Place.category == target_cat)
            .order_by(Place.search_count.desc())
            .limit(limit)
        )
        if profiler: profiler.timings["goride_sql_construct_ms"] += (time.perf_counter() - t0) * 1000.0
        
        t0 = time.perf_counter()
        result = await self.session.execute(stmt)
        if profiler: profiler.timings["goride_db_execute_ms"] += (time.perf_counter() - t0) * 1000.0
        
        t0 = time.perf_counter()
        rows = list(result.all())
        if profiler: profiler.timings["goride_orm_map_ms"] += (time.perf_counter() - t0) * 1000.0
        
        # 2. Fallback to ILIKE if no exact match found
        if not rows:
            t0 = time.perf_counter()
            stmt_fallback = (
                select(Place, literal("category").label('match_type'), literal(500.0).label('score'))
                .where(Place.category.ilike(f"%{raw_query}%"))
                .order_by(Place.search_count.desc())
                .limit(limit)
            )
            if profiler: profiler.timings["goride_sql_construct_ms"] += (time.perf_counter() - t0) * 1000.0
            
            t0 = time.perf_counter()
            result_fallback = await self.session.execute(stmt_fallback)
            if profiler: profiler.timings["goride_db_execute_ms"] += (time.perf_counter() - t0) * 1000.0
            
            t0 = time.perf_counter()
            rows = list(result_fallback.all())
            if profiler: profiler.timings["goride_orm_map_ms"] += (time.perf_counter() - t0) * 1000.0
            
        return rows

    async def search_pincode(self, raw_query: str, limit: int = 100, profiler=None) -> List[Tuple[Place, str, float]]:
        t0 = time.perf_counter()
        stmt = (
            select(Place, literal("pincode").label('match_type'), literal(float(SEARCH_WEIGHTS["pincode"])).label('score'))
            .where(Place.pincode == raw_query)
            .order_by(Place.search_count.desc())
            .limit(limit)
        )
        if profiler: profiler.timings["goride_sql_construct_ms"] += (time.perf_counter() - t0) * 1000.0
        
        t0 = time.perf_counter()
        result = await self.session.execute(stmt)
        if profiler: profiler.timings["goride_db_execute_ms"] += (time.perf_counter() - t0) * 1000.0
        
        t0 = time.perf_counter()
        rows = list(result.all())
        if profiler: profiler.timings["goride_orm_map_ms"] += (time.perf_counter() - t0) * 1000.0
        return rows

    async def search_admin_area(self, raw_query: str, limit: int = 100, profiler=None) -> List[Tuple[Place, str, float]]:
        t0 = time.perf_counter()
        # Admin areas optimized to use exact match and prefix match (b-tree index compatible)
        # We avoid fuzzy `%query%` matching
        where_clause = sa.or_(
            Place.district.ilike(f"{raw_query}%"),
            Place.state.ilike(f"{raw_query}%")
        )
        stmt = (
            select(Place, literal("district").label('match_type'), literal(float(SEARCH_WEIGHTS["district"])).label('score'))
            .where(where_clause)
            .order_by(Place.search_count.desc())
            .limit(limit)
        )
        if profiler: profiler.timings["goride_sql_construct_ms"] += (time.perf_counter() - t0) * 1000.0
        
        t0 = time.perf_counter()
        result = await self.session.execute(stmt)
        if profiler: profiler.timings["goride_db_execute_ms"] += (time.perf_counter() - t0) * 1000.0
        
        t0 = time.perf_counter()
        rows = list(result.all())
        if profiler: profiler.timings["goride_orm_map_ms"] += (time.perf_counter() - t0) * 1000.0
        return rows

    async def search_exact_place(self, raw_query: str, limit: int = 50, profiler=None) -> List[Tuple[Place, str, float]]:
        norm_q = normalize_search_key(raw_query)
        if not norm_q:
            return []
            
        all_results = []
        seen_ids = set()
        
        # Helper to execute a stage
        async def execute_stage(stage_name, stmt, stage_limit, score_label):
            nonlocal all_results
            t0 = time.perf_counter()
            if profiler: profiler.timings["goride_sql_construct_ms"] += (time.perf_counter() - t0) * 1000.0
            
            t0 = time.perf_counter()
            res = await self.session.execute(stmt)
            if profiler: profiler.timings["goride_db_execute_ms"] += (time.perf_counter() - t0) * 1000.0
            
            t0 = time.perf_counter()
            for row in res.all():
                if row[0].id not in seen_ids:
                    seen_ids.add(row[0].id)
                    all_results.append(row)
            if profiler: profiler.timings["goride_orm_map_ms"] += (time.perf_counter() - t0) * 1000.0
            if profiler: profiler.record_count(f"{stage_name}_candidates", len(all_results))

        # Stage 1: Exact Match (Limit 10)
        stmt_exact = (
            select(Place, literal("exact").label('match_type'), literal(float(SEARCH_WEIGHTS["exact"])).label('score'))
            .where(Place.search_key == norm_q)
            .order_by(Place.search_count.desc())
            .limit(10)
        )
        await execute_stage("exact", stmt_exact, 10, "exact")
        if len(all_results) >= 10: return all_results
            
        # Stage 2: Prefix Match (Limit 20)
        limit_prefix = 20 - len(all_results)
        stmt_prefix = (
            select(Place, literal("prefix").label('match_type'), literal(float(SEARCH_WEIGHTS["prefix"])).label('score'))
            .where(Place.search_key.like(f"{norm_q}%"))
        )
        if seen_ids:
            stmt_prefix = stmt_prefix.where(Place.id.notin_(list(seen_ids)))
        stmt_prefix = stmt_prefix.order_by(Place.search_count.desc()).limit(limit_prefix)
        
        await execute_stage("prefix", stmt_prefix, 20, "prefix")
        if len(all_results) >= 20: return all_results
            
        # Stage 3: Token Match (Limit 30)
        tokens = norm_q.split()
        if len(tokens) > 1:
            limit_token = 30 - len(all_results)
            conditions = [Place.search_key.ilike(f"%{tok}%") for tok in tokens]
            stmt_token = (
                select(Place, literal("token").label('match_type'), literal(float(SEARCH_WEIGHTS["fuzzy"])).label('score'))
                .where(sa.and_(*conditions))
            )
            if seen_ids:
                stmt_token = stmt_token.where(Place.id.notin_(list(seen_ids)))
            stmt_token = stmt_token.order_by(Place.search_count.desc()).limit(limit_token)
            
            await execute_stage("token", stmt_token, 30, "token")
            if len(all_results) >= 30: return all_results
            
        # Stage 4: Trigram Similarity (Limit 40)
        limit_trigram = 40 - len(all_results)
        sim_func = func.similarity(Place.search_key, norm_q)
        stmt_trigram = (
            select(Place, literal("fuzzy").label('match_type'), (sim_func * SEARCH_WEIGHTS["fuzzy"]).label('score'))
            .where(Place.search_key.op('%')(norm_q))
        )
        if seen_ids:
            stmt_trigram = stmt_trigram.where(Place.id.notin_(list(seen_ids)))
        stmt_trigram = stmt_trigram.order_by(sim_func.desc(), Place.search_count.desc()).limit(limit_trigram)
        
        await execute_stage("trigram", stmt_trigram, 40, "trigram")
        return all_results

    async def generic_search(self, raw_query: str, limit: int = 20, profiler=None) -> List[Tuple[Place, str, float]]:
        # Staged Generic Search (Short Circuit logic)
        norm_q = normalize_search_key(raw_query)
        if not norm_q:
            return []
            
        all_results = []
        seen_ids = set()
        
        # Helper to execute a stage
        async def execute_stage(stage_name, stmt, stage_limit):
            nonlocal all_results
            t0 = time.perf_counter()
            if profiler: profiler.timings["goride_sql_construct_ms"] += (time.perf_counter() - t0) * 1000.0
            
            t0 = time.perf_counter()
            res = await self.session.execute(stmt)
            if profiler: profiler.timings["goride_db_execute_ms"] += (time.perf_counter() - t0) * 1000.0
            
            t0 = time.perf_counter()
            for row in res.all():
                if row[0].id not in seen_ids:
                    seen_ids.add(row[0].id)
                    all_results.append(row)
            if profiler: profiler.timings["goride_orm_map_ms"] += (time.perf_counter() - t0) * 1000.0
            if profiler: profiler.record_count(f"generic_{stage_name}_candidates", len(all_results))

        # Stage 1: Pincode / Category / Exact
        stmt_s1 = (
            select(Place, literal("exact").label('match_type'), literal(float(SEARCH_WEIGHTS["exact"])).label('score'))
            .where(
                sa.or_(
                    Place.pincode == raw_query,
                    Place.category.ilike(f"{raw_query}%"),
                    Place.search_key == norm_q
                )
            )
            .order_by(Place.search_count.desc())
            .limit(10)
        )
        await execute_stage("exact", stmt_s1, 10)
        if len(all_results) >= 10: return all_results
            
        # Stage 2: Prefix / District
        limit_s2 = 20 - len(all_results)
        stmt_s2 = (
            select(Place, literal("prefix").label('match_type'), literal(float(SEARCH_WEIGHTS["prefix"])).label('score'))
            .where(
                sa.or_(
                    Place.search_key.like(f"{norm_q}%"),
                    Place.district.ilike(f"{raw_query}%")
                )
            )
        )
        if seen_ids: stmt_s2 = stmt_s2.where(Place.id.notin_(list(seen_ids)))
        stmt_s2 = stmt_s2.order_by(Place.search_count.desc()).limit(limit_s2)
        
        await execute_stage("prefix", stmt_s2, 20)
        if len(all_results) >= 20: return all_results

        # Stage 3: Tokens
        tokens = norm_q.split()
        if len(tokens) > 1:
            limit_s3 = 30 - len(all_results)
            conditions = [Place.search_key.ilike(f"%{tok}%") for tok in tokens]
            stmt_s3 = (
                select(Place, literal("token").label('match_type'), literal(float(SEARCH_WEIGHTS["fuzzy"])).label('score'))
                .where(sa.and_(*conditions))
            )
            if seen_ids: stmt_s3 = stmt_s3.where(Place.id.notin_(list(seen_ids)))
            stmt_s3 = stmt_s3.order_by(Place.search_count.desc()).limit(limit_s3)
            await execute_stage("token", stmt_s3, 30)
            if len(all_results) >= 30: return all_results
            
        # Stage 4: Trigram
        limit_s4 = 40 - len(all_results)
        sim_func = func.similarity(Place.search_key, norm_q)
        stmt_s4 = (
            select(Place, literal("fuzzy").label('match_type'), (sim_func * SEARCH_WEIGHTS["fuzzy"]).label('score'))
            .where(Place.search_key.op('%')(norm_q))
        )
        if seen_ids: stmt_s4 = stmt_s4.where(Place.id.notin_(list(seen_ids)))
        stmt_s4 = stmt_s4.order_by(sim_func.desc(), Place.search_count.desc()).limit(limit_s4)
        
        await execute_stage("trigram", stmt_s4, 40)
        return all_results

    async def increment_search_count(self, place_id: int):
        stmt = update(Place).where(Place.id == place_id).values(search_count=Place.search_count + 1)
        await self.session.execute(stmt)
        await self.session.commit()
''')

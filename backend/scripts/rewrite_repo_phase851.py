import re

with open("app/repositories/place_repository.py", "r", encoding="utf-8") as f:
    code = f.read()

# Add imports for constants
code = code.replace(
    "from app.core.constants import SEARCH_WEIGHTS",
    "from app.core.constants import SEARCH_WEIGHTS, EXACT_PLACE_CANDIDATE_LIMIT, CATEGORY_CANDIDATE_LIMIT, PINCODE_CANDIDATE_LIMIT, GENERIC_CANDIDATE_LIMIT, ADMIN_AREA_CANDIDATE_LIMIT"
)

# Fix intent dispatcher to use the new constants instead of hardcoded limits
code = code.replace(
    "return await self.search_category(raw_query, category, limit=100, profiler=profiler)",
    "return await self.search_category(raw_query, category, limit=CATEGORY_CANDIDATE_LIMIT, profiler=profiler)"
)
code = code.replace(
    "return await self.search_pincode(raw_query, limit=limit, profiler=profiler)",
    "return await self.search_pincode(raw_query, limit=PINCODE_CANDIDATE_LIMIT, profiler=profiler)"
)
code = code.replace(
    "return await self.search_admin_area(raw_query, limit=100, profiler=profiler)",
    "return await self.search_admin_area(raw_query, limit=ADMIN_AREA_CANDIDATE_LIMIT, profiler=profiler)"
)
code = code.replace(
    "return await self.search_exact_place(raw_query, limit=50, profiler=profiler)",
    "return await self.search_exact_place(raw_query, limit=EXACT_PLACE_CANDIDATE_LIMIT, profiler=profiler)"
)
code = code.replace(
    "return await self.generic_search(raw_query, limit=limit, profiler=profiler)",
    "return await self.generic_search(raw_query, limit=GENERIC_CANDIDATE_LIMIT, profiler=profiler)"
)

# Fix search_exact_place staged logic
search_exact_logic_old = """        # Stage 1: Exact Match (Limit 10)
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
        return all_results"""

search_exact_logic_new = """        # Stage 1: Exact Match
        stmt_exact = (
            select(Place, literal("exact").label('match_type'), literal(float(SEARCH_WEIGHTS["exact"])).label('score'))
            .where(Place.search_key == norm_q)
            .order_by(Place.search_count.desc())
            .limit(limit - len(all_results))
        )
        await execute_stage("exact", stmt_exact, limit, "exact")
        if len(all_results) >= limit: return all_results
            
        # Stage 2: Prefix Match
        stmt_prefix = (
            select(Place, literal("prefix").label('match_type'), literal(float(SEARCH_WEIGHTS["prefix"])).label('score'))
            .where(Place.search_key.like(f"{norm_q}%"))
        )
        if seen_ids:
            stmt_prefix = stmt_prefix.where(Place.id.notin_(list(seen_ids)))
        stmt_prefix = stmt_prefix.order_by(Place.search_count.desc()).limit(limit - len(all_results))
        
        await execute_stage("prefix", stmt_prefix, limit, "prefix")
        if len(all_results) >= limit: return all_results
            
        # Stage 3: Token Match
        tokens = norm_q.split()
        if len(tokens) > 1:
            conditions = [Place.search_key.ilike(f"%{tok}%") for tok in tokens]
            stmt_token = (
                select(Place, literal("token").label('match_type'), literal(float(SEARCH_WEIGHTS["fuzzy"])).label('score'))
                .where(sa.and_(*conditions))
            )
            if seen_ids:
                stmt_token = stmt_token.where(Place.id.notin_(list(seen_ids)))
            stmt_token = stmt_token.order_by(Place.search_count.desc()).limit(limit - len(all_results))
            
            await execute_stage("token", stmt_token, limit, "token")
            if len(all_results) >= limit: return all_results
            
        # Stage 4: Trigram Similarity
        sim_func = func.similarity(Place.search_key, norm_q)
        stmt_trigram = (
            select(Place, literal("fuzzy").label('match_type'), (sim_func * SEARCH_WEIGHTS["fuzzy"]).label('score'))
            .where(Place.search_key.op('%')(norm_q))
        )
        if seen_ids:
            stmt_trigram = stmt_trigram.where(Place.id.notin_(list(seen_ids)))
        stmt_trigram = stmt_trigram.order_by(sim_func.desc(), Place.search_count.desc()).limit(limit - len(all_results))
        
        await execute_stage("trigram", stmt_trigram, limit, "trigram")
        return all_results"""
code = code.replace(search_exact_logic_old, search_exact_logic_new)

# Fix generic_search staged logic
generic_search_logic_old = """        # Stage 1: Pincode / Category / Exact
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
                    (Place.district == raw_query) | (Place.district == raw_query.title())
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
        return all_results"""

generic_search_logic_new = """        # Stage 1: Pincode / Category / Exact
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
            .limit(limit - len(all_results))
        )
        await execute_stage("exact", stmt_s1, limit)
        if len(all_results) >= limit: return all_results
            
        # Stage 2: Prefix / District
        stmt_s2 = (
            select(Place, literal("prefix").label('match_type'), literal(float(SEARCH_WEIGHTS["prefix"])).label('score'))
            .where(
                sa.or_(
                    Place.search_key.like(f"{norm_q}%"),
                    (Place.district == raw_query) | (Place.district == raw_query.title())
                )
            )
        )
        if seen_ids: stmt_s2 = stmt_s2.where(Place.id.notin_(list(seen_ids)))
        stmt_s2 = stmt_s2.order_by(Place.search_count.desc()).limit(limit - len(all_results))
        
        await execute_stage("prefix", stmt_s2, limit)
        if len(all_results) >= limit: return all_results

        # Stage 3: Tokens
        tokens = norm_q.split()
        if len(tokens) > 1:
            conditions = [Place.search_key.ilike(f"%{tok}%") for tok in tokens]
            stmt_s3 = (
                select(Place, literal("token").label('match_type'), literal(float(SEARCH_WEIGHTS["fuzzy"])).label('score'))
                .where(sa.and_(*conditions))
            )
            if seen_ids: stmt_s3 = stmt_s3.where(Place.id.notin_(list(seen_ids)))
            stmt_s3 = stmt_s3.order_by(Place.search_count.desc()).limit(limit - len(all_results))
            await execute_stage("token", stmt_s3, limit)
            if len(all_results) >= limit: return all_results
            
        # Stage 4: Trigram
        sim_func = func.similarity(Place.search_key, norm_q)
        stmt_s4 = (
            select(Place, literal("fuzzy").label('match_type'), (sim_func * SEARCH_WEIGHTS["fuzzy"]).label('score'))
            .where(Place.search_key.op('%')(norm_q))
        )
        if seen_ids: stmt_s4 = stmt_s4.where(Place.id.notin_(list(seen_ids)))
        stmt_s4 = stmt_s4.order_by(sim_func.desc(), Place.search_count.desc()).limit(limit - len(all_results))
        
        await execute_stage("trigram", stmt_s4, limit)
        return all_results"""
code = code.replace(generic_search_logic_old, generic_search_logic_new)

with open("app/repositories/place_repository.py", "w", encoding="utf-8") as f:
    f.write(code)

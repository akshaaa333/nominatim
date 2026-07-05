import httpx
import asyncio
import time

async def test_search():
    base_url = "http://127.0.0.1:8000"
    queries = [
        "VIT",
        "phoenix",
        "PHOENIX",
        " phenix ",
        "sarvana",
        "velacherry",
        "hospital",
        "bus stand",
        "college"
    ]
    
    async with httpx.AsyncClient() as client:
        for q in queries:
            print(f"\n--- Searching: '{q}' ---")
            start = time.perf_counter()
            try:
                response = await client.get(f"{base_url}/search", params={"q": q}, timeout=10.0)
                elapsed_ms = (time.perf_counter() - start) * 1000
                print(f"Status: {response.status_code} | Time: {elapsed_ms:.2f} ms")
                
                results = response.json()
                print(f"Total Results: {len(results)}")
                
                if results and isinstance(results, list):
                    for i, r in enumerate(results[:3]):
                        name = r.get("display_name", r.get("name", "Unknown"))
                        match_type = r.get("match_type", "nominatim_fallback")
                        score = r.get("score", 0.0)
                        print(f"  {i+1}. {name} (Match: {match_type}, Score: {score})")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_search())

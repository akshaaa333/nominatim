import httpx
import asyncio

async def test_api():
    base_url = "http://127.0.0.1:8000"
    endpoints = [
        "/",
        "/health",
        "/places",
        "/search?q=VIT",
        "/search?q=Chennai"
    ]
    
    async with httpx.AsyncClient() as client:
        for ep in endpoints:
            print(f"\n--- Testing GET {ep} ---")
            try:
                response = await client.get(f"{base_url}{ep}", timeout=10.0)
                print(f"Status: {response.status_code}")
                # Print response nicely (truncated if too long)
                text = response.text
                if len(text) > 500:
                    print(f"Response: {text[:500]}... (truncated)")
                else:
                    print(f"Response: {text}")
            except Exception as e:
                print(f"Error: {e}")

asyncio.run(test_api())

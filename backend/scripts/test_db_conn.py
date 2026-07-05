import asyncio
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()
from app.core.database import AsyncSessionLocal

async def test():
    try:
        session = AsyncSessionLocal()
        result = await session.execute(text("SELECT 1"))
        print("OK", result.fetchall())
        await session.close()
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    asyncio.run(test())

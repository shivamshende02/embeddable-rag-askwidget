import asyncio
from app.core.database import engine
from app.core.config import get_settings

async def test_connection():
    settings = get_settings()
    print(f"DEBUG URL: {settings.DATABASE_URL}")
    try:
        async with engine.connect() as conn:
            print("Database connected successfully!")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
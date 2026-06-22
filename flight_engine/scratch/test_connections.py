import asyncio
import asyncpg
import redis
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

async def test_db():
    print(f"Connecting to database: {settings.DATABASE_URL} ...")
    try:
        # Convert sqlalchemy+asyncpg url to asyncpg url
        db_url = settings.DATABASE_URL
        if db_url.startswith("postgresql+asyncpg://"):
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        
        conn = await asyncpg.connect(db_url)
        print("Database connection SUCCESSFUL!")
        await conn.close()
        return True
    except Exception as e:
        print(f"Database connection FAILED: {e}")
        return False

def test_redis():
    print(f"Connecting to Redis: {settings.REDIS_URL} ...")
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        print("Redis connection SUCCESSFUL!")
        r.close()
        return True
    except Exception as e:
        print(f"Redis connection FAILED: {e}")
        return False

async def main():
    db_ok = await test_db()
    redis_ok = test_redis()
    if db_ok and redis_ok:
        print("\nAll connections are healthy!")
        sys.exit(0)
    else:
        print("\nSome connections failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

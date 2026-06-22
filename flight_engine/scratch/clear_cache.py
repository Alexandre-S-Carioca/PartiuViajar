import asyncio
import asyncpg
import redis
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

async def clear_database():
    print("Clearing PostgreSQL database tables...")
    try:
        db_url = settings.DATABASE_URL
        if db_url.startswith("postgresql+asyncpg://"):
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        
        conn = await asyncpg.connect(db_url)
        # Clear flights and historical price data
        await conn.execute("TRUNCATE TABLE flights CASCADE;")
        await conn.execute("TRUNCATE TABLE flight_price_history CASCADE;")
        print("PostgreSQL tables cleared SUCCESSFUL!")
        await conn.close()
        return True
    except Exception as e:
        print(f"Failed to clear PostgreSQL: {e}")
        return False

def clear_redis():
    print(f"Connecting to Redis: {settings.REDIS_URL} to clear cache...")
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.flushall()
        print("Redis cache cleared SUCCESSFUL!")
        r.close()
        return True
    except Exception as e:
        print(f"Failed to clear Redis: {e}")
        return False

async def main():
    redis_ok = clear_redis()
    db_ok = await clear_database()
    if redis_ok and db_ok:
        print("\nAll cache and database records cleared successfully!")
        sys.exit(0)
    else:
        print("\nSome operations failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

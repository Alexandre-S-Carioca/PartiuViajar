import sys
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from infrastructure.db import Base
from infrastructure.models import FlightModel, FlightPriceHistoryModel

async def init_models():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        # Caution: in production, you should use Alembic. 
        # For setup/testing here, we just create all tables.
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_models())
    print("Database tables created successfully!")

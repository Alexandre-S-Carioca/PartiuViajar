import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flight_engine.core.config import settings

async def add_column():
    print(f"Conectando ao banco PostgreSQL em: {settings.DATABASE_URL}...")
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.begin() as conn:
        print("Adicionando coluna 'base_price_brl' caso nao exista...")
        await conn.execute(text(
            "ALTER TABLE flights ADD COLUMN IF NOT EXISTS base_price_brl NUMERIC(10, 2) DEFAULT 0.00;"
        ))
        await conn.execute(text(
            "ALTER TABLE flights ALTER COLUMN base_price_brl SET NOT NULL;"
        ))
        print("Coluna 'base_price_brl' adicionada com sucesso!")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_column())

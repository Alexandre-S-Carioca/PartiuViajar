import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db import AsyncSessionLocal
from sqlalchemy import text

async def check_cities():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT city, COUNT(*) as total FROM accommodations GROUP BY city ORDER BY city")
        )
        rows = result.all()
        print("=== Cidades no banco de dados (tabela accommodations) ===")
        for row in rows:
            print(f"  Cidade: {row[0]!r}  |  Total: {row[1]}")
        
        print("\n=== Amostra de 5 registros ===")
        result2 = await session.execute(
            text("SELECT id, name, city, latitude, longitude FROM accommodations LIMIT 5")
        )
        for row in result2.all():
            print(f"  {row[1]} | city={row[2]!r} | lat={row[3]}, lon={row[4]}")

asyncio.run(check_cities())

import asyncio, asyncpg
async def main():
    conn = await asyncpg.connect('postgresql://alexandre:123456@192.168.0.150/postgres')
    await conn.execute('CREATE DATABASE flights_db')
    await conn.close()
asyncio.run(main())

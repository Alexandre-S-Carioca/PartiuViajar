import asyncio
import asyncpg
import urllib.parse

async def main():
    encoded_password = urllib.parse.quote_plus("T3@fW8#pK6")
    # Conecta no banco padrao "postgres" do novo servidor
    url = f"postgresql://Sistema:{encoded_password}@163.176.228.2:5432/postgres"
    print(f"Connecting to default database to create partiu_viajar...")
    try:
        conn = await asyncpg.connect(url)
        # Cria a base de dados
        await conn.execute('CREATE DATABASE partiu_viajar')
        print("Database 'partiu_viajar' created successfully!")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())

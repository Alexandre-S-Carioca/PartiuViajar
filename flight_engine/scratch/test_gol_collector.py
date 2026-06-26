import asyncio
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from infrastructure.collectors.gol_scrapestack_collector import GolScrapestackCollector

async def test():
    print("Iniciando teste direto no GolScrapestackCollector")
    collector = GolScrapestackCollector()
    
    origin = "FOR"
    destination = "REC"
    date = datetime(2026, 7, 1)
    
    print(f"Buscando voos: {origin} -> {destination} na data {date.strftime('%d/%m/%Y')}")
    
    flights = await collector.fetch_flights(origin, destination, date, 1)
    
    print("\n--- Resultados ---")
    if not flights:
        print("Nenhum voo retornado (provavelmente o Scrapestack negou acesso JS/Premium).")
    else:
        for f in flights:
            print(f"Voo: {f.airline} | {f.origin}->{f.destination} | Preço: R$ {f.price} | Duração: {f.duration}min")

if __name__ == "__main__":
    asyncio.run(test())

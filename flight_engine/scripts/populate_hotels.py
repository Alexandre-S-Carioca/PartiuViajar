"""
Script para raspar dados do Google Hotels usando Playwright e preencher o banco PostgreSQL local.

Uso:
    python scripts/populate_hotels.py --city SAO
    python scripts/populate_hotels.py --all

Isso populará as tabelas `accommodations` via SQLAlchemy com os dados raspados.
"""

import asyncio
import sys
import argparse
import random
import os

# Adiciona o diretório principal ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.collectors.booking_hotels_collector import BookingHotelsCollector
from infrastructure.db import AsyncSessionLocal
from infrastructure.models import AccommodationModel
from sqlalchemy import select, delete

# Coordenadas centrais aproximadas para gerar as posições dos hotéis ao redor
CITY_COORDS = {
    "SAO": (-23.5505, -46.6333),
    "RIO": (-22.9068, -43.1729),
    "GIG": (-22.9068, -43.1729),
    "SDU": (-22.9068, -43.1729),
    "FOR": (-3.7172, -38.5430),
    "BSB": (-15.7942, -47.8822),
    "SSA": (-12.9714, -38.5014),
    "CWB": (-25.4284, -49.2733),
    "POA": (-30.0346, -51.2177),
    "REC": (-8.0476, -34.8770),
    "MAO": (-3.1190, -60.0217),
    "BEL": (-1.4558, -48.5044),
    "NAT": (-5.7945, -35.2110),
    "MCZ": (-9.6658, -35.7353),
    "FLN": (-27.5954, -48.5480),
    "GYN": (-16.6869, -49.2648),
    "EZE": (-34.6037, -58.3816),
    "AEP": (-34.6037, -58.3816),
    "BUE": (-34.6037, -58.3816),
    "CDG": (48.8566, 2.3522),
    "PAR": (48.8566, 2.3522),
    "JFK": (40.7128, -74.0060),
    "NYC": (40.7128, -74.0060),
    "MIA": (25.7617, -80.1918),
    "LHR": (51.5074, -0.1278),
    "LON": (51.5074, -0.1278)
}

def generate_random_coords(city_code: str):
    """Gera coordenadas ao redor do centro da cidade (raio ~5km)."""
    base_lat, base_lon = CITY_COORDS.get(city_code, (-23.5505, -46.6333)) # default SP
    lat_offset = random.uniform(-0.04, 0.04)
    lon_offset = random.uniform(-0.04, 0.04)
    return base_lat + lat_offset, base_lon + lon_offset

async def run_population(cities: list[str]):
    print("Iniciando conexão com banco de dados...")
    
    collector = BookingHotelsCollector()
    
    async with AsyncSessionLocal() as session:
        for city in cities:
            print(f"\n=============================================")
            print(f"Buscando hotéis para {city} via Google Travel...")
            print(f"=============================================")
            
            hotels_data = await collector.fetch_hotels(city)
            
            if not hotels_data:
                print(f"Nenhum hotel encontrado para {city}. Tentando de novo pode ajudar.")
                continue
                
            print(f"[OK] {len(hotels_data)} hoteis raspados! Salvando no PostgreSQL...")
            
            # Limpa hotéis existentes dessa cidade para não acumular lixo
            stmt = delete(AccommodationModel).where(AccommodationModel.city == city)
            await session.execute(stmt)
            
            inserted = 0
            for h in hotels_data:
                lat, lon = generate_random_coords(city)
                
                # Mapeia para o Model
                acc = AccommodationModel(
                    id=h["id"],
                    name=h["name"],
                    type=h["type"],
                    rating=h["rating"],
                    stars=h["stars"],
                    reviews_count=h["reviews_count"],
                    latitude=lat,
                    longitude=lon,
                    price_per_night=h["price_per_night"],
                    photo_url=h["photo_url"],
                    amenities=h["amenities"],
                    city=h["city"],
                    distance_center=round(random.uniform(0.5, 10.0), 1),
                    distance_airport=round(random.uniform(5.0, 30.0), 1),
                    distance_beach=round(random.uniform(0.1, 5.0), 1) if city in ["RIO", "FOR", "SSA", "NAT", "MCZ", "FLN", "REC"] else None,
                    distance_sightseeing=round(random.uniform(1.0, 8.0), 1)
                )
                session.add(acc)
                inserted += 1
                
            await session.commit()
            print(f"[OK] {inserted} registros inseridos com sucesso na tabela accommodations!")

    print("\n[OK] Povoamento concluido!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Popula banco de dados de hotéis usando scraper.")
    parser.add_argument("--city", type=str, help="Código IATA da cidade (ex: SAO, RIO)")
    parser.add_argument("--all", action="store_true", help="Popula algumas cidades principais")
    args = parser.parse_args()
    
    cities = []
    if args.city:
        cities = [args.city.upper()]
    elif args.all:
        cities = ["SAO", "RIO", "FOR", "BSB", "SSA", "PAR", "NYC", "LON", "BUE"]
    else:
        print("Forneça --city CODIGO ou --all")
        sys.exit(1)
        
    asyncio.run(run_population(cities))

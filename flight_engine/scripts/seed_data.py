import asyncio
import sys
import os
from decimal import Decimal

# Set up python path so we can import from project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db import AsyncSessionLocal
from infrastructure.models import AccommodationModel
from sqlalchemy import select

ACCOMMODATIONS_DATA = [
    # --- FORTALEZA (FOR) ---
    {
        "id": "for_hotel_1",
        "name": "Gran Marquise Hotel",
        "type": "hotel",
        "rating": 9.2,
        "stars": 5,
        "reviews_count": 850,
        "latitude": -3.7258,
        "longitude": -38.4871,
        "price_per_night": Decimal("520.00"),  # Red (> 400)
        "photo_url": "https://picsum.photos/400/300?random=101",
        "amenities": ["Wi-Fi", "Piscina", "Academia", "Café da manhã", "Estacionamento", "Ar condicionado"],
        "city": "FOR",
        "distance_center": 4.5,
        "distance_airport": 11.2,
        "distance_beach": 0.05,
        "distance_sightseeing": 2.1
    },
    {
        "id": "for_pousada_1",
        "name": "Pousada Vila Jeri Fortaleza",
        "type": "pousada",
        "rating": 8.7,
        "stars": 4,
        "reviews_count": 120,
        "latitude": -3.7231,
        "longitude": -38.5025,
        "price_per_night": Decimal("180.00"),  # Yellow (150-250)
        "photo_url": "https://picsum.photos/400/300?random=102",
        "amenities": ["Wi-Fi", "Café da manhã", "Pet Friendly", "Ar condicionado"],
        "city": "FOR",
        "distance_center": 3.0,
        "distance_airport": 9.8,
        "distance_beach": 0.2,
        "distance_sightseeing": 1.2
    },
    {
        "id": "for_hostel_1",
        "name": "Alberque Fortaleza Hostel",
        "type": "hostel",
        "rating": 8.1,
        "stars": 3,
        "reviews_count": 340,
        "latitude": -3.7259,
        "longitude": -38.5175,
        "price_per_night": Decimal("85.00"),  # Green (<= 150)
        "photo_url": "https://picsum.photos/400/300?random=103",
        "amenities": ["Wi-Fi", "Piscina", "Ar condicionado"],
        "city": "FOR",
        "distance_center": 1.5,
        "distance_airport": 8.5,
        "distance_beach": 0.5,
        "distance_sightseeing": 0.3
    },
    {
        "id": "for_resort_1",
        "name": "Beach Park Acqua Resort",
        "type": "resort",
        "rating": 9.0,
        "stars": 5,
        "reviews_count": 1200,
        "latitude": -3.8422,
        "longitude": -38.3815,
        "price_per_night": Decimal("750.00"),  # Red (> 400)
        "photo_url": "https://picsum.photos/400/300?random=104",
        "amenities": ["Wi-Fi", "Piscina", "Academia", "Café da manhã", "Estacionamento", "Pet Friendly", "Ar condicionado"],
        "city": "FOR",
        "distance_center": 22.0,
        "distance_airport": 20.5,
        "distance_beach": 0.01,
        "distance_sightseeing": 0.1
    },
    {
        "id": "for_hotel_2",
        "name": "Hotel Seara Praia",
        "type": "hotel",
        "rating": 8.5,
        "stars": 4,
        "reviews_count": 620,
        "latitude": -3.7247,
        "longitude": -38.4908,
        "price_per_night": Decimal("310.00"),  # Orange (250-400)
        "photo_url": "https://picsum.photos/400/300?random=105",
        "amenities": ["Wi-Fi", "Piscina", "Academia", "Café da manhã", "Estacionamento", "Ar condicionado"],
        "city": "FOR",
        "distance_center": 4.1,
        "distance_airport": 10.9,
        "distance_beach": 0.1,
        "distance_sightseeing": 1.8
    },

    # --- SÃO PAULO (SAO) ---
    {
        "id": "sao_hotel_1",
        "name": "Hotel Pullman Ibirapuera",
        "type": "hotel",
        "rating": 9.1,
        "stars": 5,
        "reviews_count": 940,
        "latitude": -23.5855,
        "longitude": -46.6522,
        "price_per_night": Decimal("380.00"),  # Orange (250-400)
        "photo_url": "https://picsum.photos/400/300?random=201",
        "amenities": ["Wi-Fi", "Piscina", "Academia", "Estacionamento", "Pet Friendly", "Ar condicionado"],
        "city": "SAO",
        "distance_center": 5.2,
        "distance_airport": 6.8,  # Congonhas
        "distance_beach": None,
        "distance_sightseeing": 0.8  # Parque Ibirapuera
    },
    {
        "id": "sao_hotel_2",
        "name": "Renaissance São Paulo Hotel",
        "type": "hotel",
        "rating": 9.3,
        "stars": 5,
        "reviews_count": 1400,
        "latitude": -23.5594,
        "longitude": -46.6628,
        "price_per_night": Decimal("650.00"),  # Red (> 400)
        "photo_url": "https://picsum.photos/400/300?random=202",
        "amenities": ["Wi-Fi", "Piscina", "Academia", "Café da manhã", "Estacionamento", "Ar condicionado"],
        "city": "SAO",
        "distance_center": 2.5,
        "distance_airport": 8.2,
        "distance_beach": None,
        "distance_sightseeing": 0.5  # Avenida Paulista
    },
    {
        "id": "sao_pousada_1",
        "name": "Pousada Dona Maria Ibirapuera",
        "type": "pousada",
        "rating": 8.3,
        "stars": 3,
        "reviews_count": 80,
        "latitude": -23.5901,
        "longitude": -46.6450,
        "price_per_night": Decimal("140.00"),  # Green (<= 150)
        "photo_url": "https://picsum.photos/400/300?random=203",
        "amenities": ["Wi-Fi", "Café da manhã", "Pet Friendly"],
        "city": "SAO",
        "distance_center": 6.1,
        "distance_airport": 5.5,
        "distance_beach": None,
        "distance_sightseeing": 1.5
    },
    {
        "id": "sao_hostel_1",
        "name": "Olah Hostel Vila Mariana",
        "type": "hostel",
        "rating": 8.6,
        "stars": 3,
        "reviews_count": 210,
        "latitude": -23.5822,
        "longitude": -46.6389,
        "price_per_night": Decimal("90.00"),  # Green (<= 150)
        "photo_url": "https://picsum.photos/400/300?random=204",
        "amenities": ["Wi-Fi", "Café da manhã", "Pet Friendly", "Ar condicionado"],
        "city": "SAO",
        "distance_center": 4.8,
        "distance_airport": 7.0,
        "distance_beach": None,
        "distance_sightseeing": 1.1
    },
    {
        "id": "sao_resort_1",
        "name": "Club Med Lake Paradise",
        "type": "resort",
        "rating": 8.8,
        "stars": 5,
        "reviews_count": 480,
        "latitude": -23.5183,
        "longitude": -46.2236,
        "price_per_night": Decimal("890.00"),  # Red (> 400)
        "photo_url": "https://picsum.photos/400/300?random=205",
        "amenities": ["Wi-Fi", "Piscina", "Academia", "Café da manhã", "Estacionamento", "Ar condicionado"],
        "city": "SAO",
        "distance_center": 45.0,
        "distance_airport": 32.0,
        "distance_beach": None,
        "distance_sightseeing": 15.0
    },

    # --- RIO DE JANEIRO (RIO) ---
    {
        "id": "rio_hotel_1",
        "name": "Copacabana Palace",
        "type": "hotel",
        "rating": 9.6,
        "stars": 5,
        "reviews_count": 2100,
        "latitude": -22.9672,
        "longitude": -43.1789,
        "price_per_night": Decimal("1200.00"),  # Red (> 400)
        "photo_url": "https://picsum.photos/400/300?random=301",
        "amenities": ["Wi-Fi", "Piscina", "Academia", "Café da manhã", "Estacionamento", "Ar condicionado"],
        "city": "RIO",
        "distance_center": 8.5,
        "distance_airport": 22.0,  # Galeao
        "distance_beach": 0.01,
        "distance_sightseeing": 4.5  # Pao de Acucar
    },
    {
        "id": "rio_hotel_2",
        "name": "Arena Leme Hotel",
        "type": "hotel",
        "rating": 8.8,
        "stars": 4,
        "reviews_count": 920,
        "latitude": -22.9619,
        "longitude": -43.1664,
        "price_per_night": Decimal("350.00"),  # Orange (250-400)
        "photo_url": "https://picsum.photos/400/300?random=302",
        "amenities": ["Wi-Fi", "Piscina", "Academia", "Café da manhã", "Ar condicionado"],
        "city": "RIO",
        "distance_center": 9.2,
        "distance_airport": 23.5,
        "distance_beach": 0.02,
        "distance_sightseeing": 3.8
    },
    {
        "id": "rio_pousada_1",
        "name": "Pousada Santa Teresa",
        "type": "pousada",
        "rating": 9.0,
        "stars": 4,
        "reviews_count": 150,
        "latitude": -22.9238,
        "longitude": -43.1932,
        "price_per_night": Decimal("220.00"),  # Yellow (150-250)
        "photo_url": "https://picsum.photos/400/300?random=303",
        "amenities": ["Wi-Fi", "Piscina", "Café da manhã", "Pet Friendly", "Ar condicionado"],
        "city": "RIO",
        "distance_center": 2.5,
        "distance_airport": 18.0,
        "distance_beach": 4.5,
        "distance_sightseeing": 0.5  # Bonde de Santa Teresa
    },
    {
        "id": "rio_hostel_1",
        "name": "Books Hostel Lapa",
        "type": "hostel",
        "rating": 8.4,
        "stars": 3,
        "reviews_count": 450,
        "latitude": -22.9189,
        "longitude": -43.1812,
        "price_per_night": Decimal("75.00"),  # Green (<= 150)
        "photo_url": "https://picsum.photos/400/300?random=304",
        "amenities": ["Wi-Fi", "Café da manhã", "Ar condicionado"],
        "city": "RIO",
        "distance_center": 0.8,
        "distance_airport": 16.5,
        "distance_beach": 3.2,
        "distance_sightseeing": 0.2  # Arcos da Lapa
    },

    # --- SANTIAGO (SCL) ---
    {
        "id": "scl_hotel_1",
        "name": "W Santiago",
        "type": "hotel",
        "rating": 9.0,
        "stars": 5,
        "reviews_count": 560,
        "latitude": -33.4140,
        "longitude": -70.5996,
        "price_per_night": Decimal("480.00"),  # Red (> 400)
        "photo_url": "https://picsum.photos/400/300?random=401",
        "amenities": ["Wi-Fi", "Piscina", "Academia", "Estacionamento", "Ar condicionado"],
        "city": "SCL",
        "distance_center": 6.0,
        "distance_airport": 21.0,
        "distance_beach": None,
        "distance_sightseeing": 1.2  # Costanera Center
    },
    {
        "id": "scl_pousada_1",
        "name": "Casita de Providencia",
        "type": "pousada",
        "rating": 8.8,
        "stars": 4,
        "reviews_count": 95,
        "latitude": -33.4285,
        "longitude": -70.6120,
        "price_per_night": Decimal("210.00"),  # Yellow (150-250)
        "photo_url": "https://picsum.photos/400/300?random=402",
        "amenities": ["Wi-Fi", "Café da manhã", "Pet Friendly", "Ar condicionado"],
        "city": "SCL",
        "distance_center": 4.5,
        "distance_airport": 20.0,
        "distance_beach": None,
        "distance_sightseeing": 0.8
    },
    {
        "id": "scl_hostel_1",
        "name": "Santiago Backpackers",
        "type": "hostel",
        "rating": 8.2,
        "stars": 3,
        "reviews_count": 310,
        "latitude": -33.4361,
        "longitude": -70.6482,
        "price_per_night": Decimal("80.00"),  # Green (<= 150)
        "photo_url": "https://picsum.photos/400/300?random=403",
        "amenities": ["Wi-Fi", "Café da manhã"],
        "city": "SCL",
        "distance_center": 0.5,
        "distance_airport": 17.5,
        "distance_beach": None,
        "distance_sightseeing": 0.3  # Plaza de Armas
    }
]

async def seed():
    print("Starting database seeding...")
    async with AsyncSessionLocal() as session:
        for data in ACCOMMODATIONS_DATA:
            # Check if exists
            stmt = select(AccommodationModel).where(AccommodationModel.id == data["id"])
            res = await session.execute(stmt)
            exists = res.scalar_one_or_none()
            
            acc = AccommodationModel(
                id=data["id"],
                name=data["name"],
                type=data["type"],
                rating=data["rating"],
                stars=data["stars"],
                reviews_count=data["reviews_count"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                price_per_night=data["price_per_night"],
                photo_url=data["photo_url"],
                amenities=data["amenities"],
                city=data["city"],
                distance_center=data["distance_center"],
                distance_airport=data["distance_airport"],
                distance_beach=data["distance_beach"],
                distance_sightseeing=data["distance_sightseeing"]
            )
            
            if exists:
                print(f"Accommodation {data['name']} already exists, merging...")
                await session.merge(acc)
            else:
                print(f"Adding new accommodation {data['name']}...")
                session.add(acc)
                
        await session.commit()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())

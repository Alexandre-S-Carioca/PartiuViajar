import dramatiq
import asyncio
import logging
from typing import List
from workers.dramatiq_setup import redis_broker
from infrastructure.db import AsyncSessionLocal
from infrastructure.models import FlightModel, FlightPriceHistoryModel
from sqlalchemy.dialects.postgresql import insert

logger = logging.getLogger(__name__)

async def save_flights_async(flights_data: List[dict]):
    async with AsyncSessionLocal() as session:
        for f in flights_data:
            # Upsert na tabela flights
            stmt = insert(FlightModel).values(
                id=f["id"],
                airline=f["airline"],
                origin=f["origin"],
                destination=f["destination"],
                departure_date=f["departure_date"],
                arrival_date=f["arrival_date"],
                price=f["price"],
                currency=f["currency"],
                duration=f["duration"],
                stops=f["stops"],
                cabin_class=f["cabin_class"],
                booking_url=f["booking_url"],
                collected_at=f["collected_at"]
            )
            
            # Se já existe o id (pode não existir na prática dependendo da geração do UUID),
            # nós o atualizamos. Mas nossa regra de negócio aqui será inserir.
            # Como geramos UUID no domain, cada coleta tem um UUID novo.
            # Idealmente buscaríamos pelo Flight específico e apenas adicionaríamos no price history.
            
            await session.merge(FlightModel(**f))
            
            # Adiciona no historico
            history = FlightPriceHistoryModel(
                flight_id=f["id"],
                price=f["price"],
                currency=f["currency"],
                recorded_at=f["collected_at"]
            )
            session.add(history)
            
        await session.commit()
        logger.info(f"Saved {len(flights_data)} flights to DB.")

@dramatiq.actor(max_retries=3)
def save_flights_task(flights_data: List[dict]):
    """
    Background worker task to save collected flights to PostgreSQL.
    """
    logger.info("Executing background task to save flights.")
    asyncio.run(save_flights_async(flights_data))

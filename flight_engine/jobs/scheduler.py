from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

from sqlalchemy import select, func
from infrastructure.db import AsyncSessionLocal
from infrastructure.models import PriceAlertModel, FlightModel
from services.notification_service import NotificationService

async def periodic_price_update():
    logger.info("Running periodic_price_update job")
    # Aqui entraria a lógica de pegar voos monitorados e mandar pro bus/orchestrator
    pass

async def cache_cleanup():
    logger.info("Running cache_cleanup job")
    # Limpa dados antigos do redis se houver custom keys
    pass

async def history_cleanup():
    logger.info("Running history_cleanup job")
    # Limpa historico de precos velhos do postgres
    pass

async def check_price_alerts():
    logger.info("Running check_price_alerts job")
    try:
        async with AsyncSessionLocal() as session:
            alerts_stmt = select(PriceAlertModel)
            alerts_res = await session.execute(alerts_stmt)
            alerts = alerts_res.scalars().all()
            
            for alert in alerts:
                # Find cheapest flight for this route and date
                flight_stmt = (
                    select(FlightModel)
                    .where(
                        FlightModel.origin == alert.origin,
                        FlightModel.destination == alert.destination,
                        func.date(FlightModel.departure_date) == func.date(alert.departure_date)
                    )
                    .order_by(FlightModel.price.asc())
                    .limit(1)
                )
                flight_res = await session.execute(flight_stmt)
                cheapest = flight_res.scalar_one_or_none()
                
                if cheapest and cheapest.price <= alert.target_price:
                    NotificationService.send_price_alert(
                        email=alert.email,
                        origin=alert.origin,
                        destination=alert.destination,
                        target_price=float(alert.target_price),
                        current_price=float(cheapest.price),
                        telegram_chat_id=alert.telegram_chat_id
                    )
    except Exception as e:
        logger.error(f"Error checking price alerts: {e}")

async def periodic_hotel_update():
    logger.info("Running periodic_hotel_update job")
    try:
        from workers.tasks import update_hotels_task
        # All 27 Brazilian capitals (using their primary airport IATA codes)
        target_cities = [
            "SAO", "RIO", "FOR", "BSB", "SSA", "CWB", "POA", 
            "REC", "MAO", "BEL", "NAT", "MCZ", "FLN", "GYN",
            "VIX", "CNF", "CGR", "CGB", "SLZ", "THE", "JPA", 
            "AJU", "PMW", "PVH", "RBR", "BVB", "MCP"
        ]
        for city in target_cities:
            logger.info(f"Dispatching update_hotels_task for {city}")
            update_hotels_task.send(city)
    except Exception as e:
        logger.error(f"Error running periodic_hotel_update: {e}")

def setup_scheduler():
    scheduler.add_job(periodic_price_update, 'interval', hours=1)
    scheduler.add_job(cache_cleanup, 'interval', hours=12)
    scheduler.add_job(history_cleanup, 'cron', day_of_week='sun', hour=3)
    scheduler.add_job(check_price_alerts, 'interval', minutes=10) # check alerts every 10 minutes for testing/PoC
    scheduler.add_job(periodic_hotel_update, 'cron', hour=4, minute=0) # run daily at 4:00 AM
    scheduler.start()
    logger.info("Scheduler started")

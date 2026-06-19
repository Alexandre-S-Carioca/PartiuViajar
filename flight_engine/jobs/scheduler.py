from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

from sqlalchemy import select, func
from infrastructure.db import AsyncSessionLocal
from infrastructure.models import PriceAlertModel, FlightModel

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
                    logger.warning(
                        f"[ALERTA DE PREÇO DISPARADO] Rota {alert.origin} -> {alert.destination} por R$ {cheapest.price:.2f}! "
                        f"Alvo: R$ {alert.target_price:.2f}. Enviando e-mail para: {alert.email} | Telegram: {alert.telegram_chat_id or 'N/D'}"
                    )
    except Exception as e:
        logger.error(f"Error checking price alerts: {e}")

def setup_scheduler():
    scheduler.add_job(periodic_price_update, 'interval', hours=1)
    scheduler.add_job(cache_cleanup, 'interval', hours=12)
    scheduler.add_job(history_cleanup, 'cron', day_of_week='sun', hour=3)
    scheduler.add_job(check_price_alerts, 'interval', minutes=10) # check alerts every 10 minutes for testing/PoC
    scheduler.start()
    logger.info("Scheduler started")

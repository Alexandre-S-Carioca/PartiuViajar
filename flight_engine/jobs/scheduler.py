from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

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

def setup_scheduler():
    scheduler.add_job(periodic_price_update, 'interval', hours=1)
    scheduler.add_job(cache_cleanup, 'interval', hours=12)
    scheduler.add_job(history_cleanup, 'cron', day_of_week='sun', hour=3)
    scheduler.start()
    logger.info("Scheduler started")

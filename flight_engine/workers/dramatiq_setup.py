import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import Retries
from core.config import settings

# Setup Redis broker for Dramatiq
redis_broker = RedisBroker(url=settings.REDIS_URL)

# Adiciona o middleware de Retries. Quando falha max_retries vezes, 
# a mensagem vai para uma Dead Letter Queue nativa (ex: default.dead)
redis_broker.add_middleware(Retries(max_retries=3))

dramatiq.set_broker(redis_broker)

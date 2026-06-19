import logging
import abc

logger = logging.getLogger(__name__)

class BaseAlert(abc.ABC):
    @abc.abstractmethod
    async def send(self, message: str) -> bool:
        pass

class TelegramAlert(BaseAlert):
    async def send(self, message: str) -> bool:
        logger.info(f"Telegram Alert sent: {message}")
        return True

class EmailAlert(BaseAlert):
    async def send(self, message: str) -> bool:
        logger.info(f"Email Alert sent: {message}")
        return True

class WebhookAlert(BaseAlert):
    async def send(self, message: str) -> bool:
        logger.info(f"Webhook Alert sent: {message}")
        return True

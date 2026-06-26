import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_price_alert(email: str, origin: str, destination: str, target_price: float, current_price: float, telegram_chat_id: str = None):
        """
        Simula o envio de um alerta de preço.
        Em produção, essa função se conectaria a uma API de SMTP (como SendGrid, AWS SES) 
        ou à API do Telegram.
        Para o MVP, faremos o registro detalhado no console e salvaremos num arquivo de log.
        """
        message = (
            f"\\n{'='*50}\\n"
            f"🎯 ALERTA DE PREÇO ATINGIDO! 🎯\\n"
            f"De: {origin} -> Para: {destination}\\n"
            f"Preço Alvo: R$ {target_price:.2f}\\n"
            f"Preço Encontrado: R$ {current_price:.2f}\\n"
            f"Enviando e-mail para: {email}\\n"
        )
        if telegram_chat_id:
            message += f"Enviando mensagem para o Telegram ID: {telegram_chat_id}\\n"
        
        message += f"{'='*50}\\n"
        
        # Log no console
        logger.warning(message)
        
        # Grava em um arquivo de simulação para auditoria
        try:
            with open("alertas_disparados.log", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {message}")
        except Exception as e:
            logger.error(f"Erro ao gravar log do alerta: {e}")

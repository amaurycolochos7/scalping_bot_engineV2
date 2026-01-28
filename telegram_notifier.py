"""
Sistema de notificaciones por Telegram
"""
from telegram import Bot
from telegram.error import TelegramError
from config import Config
import logging
import asyncio

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        """Inicializa el bot de Telegram"""
        if Config.TELEGRAM_BOT_TOKEN:
            self.bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
            self.chat_id = Config.TELEGRAM_CHAT_ID
            logger.info("✅ Telegram notifier inicializado")
        else:
            self.bot = None
            logger.warning("⚠️ Telegram no configurado - las señales se mostrarán en consola")
    
    async def send_signal(self, message):
        """
        Envía una señal por Telegram
        
        Args:
            message: Texto del mensaje
        """
        if not self.bot:
            # Si no hay Telegram, mostrar en consola
            print("\n" + "="*50)
            print("🚀 NUEVA SEÑAL DETECTADA")
            print("="*50)
            print(message)
            print("="*50 + "\n")
            return True
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info("✅ Señal enviada por Telegram")
            return True
            
        except TelegramError as e:
            logger.error(f"❌ Error enviando mensaje por Telegram: {e}")
            # Fallback a consola
            print("\n" + message + "\n")
            return False
    
    def send_signal_sync(self, message):
        """Versión síncrona para compatibilidad"""
        try:
            asyncio.run(self.send_signal(message))
        except:
            # Si falla, mostrar en consola
            print("\n" + "="*50)
            print("🚀 NUEVA SEÑAL")
            print("="*50)
            print(message)
            print("="*50 + "\n")

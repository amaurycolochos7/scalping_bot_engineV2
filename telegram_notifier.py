"""
Sistema de notificaciones por Telegram
Envía señales a todos los usuarios autorizados
"""
from telegram import Bot
from telegram.error import TelegramError
from config import Config
import logging
import asyncio

logger = logging.getLogger(__name__)

# Importar gestión de keys
try:
    from keys_manager import get_authorized_chat_ids, cleanup_expired
    KEYS_ENABLED = True
except ImportError:
    KEYS_ENABLED = False
    logger.warning("⚠️ keys_manager no disponible - usando modo legacy")


class TelegramNotifier:
    def __init__(self):
        """Inicializa el bot de Telegram"""
        if Config.TELEGRAM_BOT_TOKEN:
            self.bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
            self.legacy_chat_id = Config.TELEGRAM_CHAT_ID
            logger.info("✅ Telegram notifier inicializado")
            if KEYS_ENABLED:
                logger.info("🔑 Sistema de keys habilitado")
        else:
            self.bot = None
            logger.warning("⚠️ Telegram no configurado - las señales se mostrarán en consola")
    
    async def send_signal(self, message):
        """
        Envía una señal a todos los usuarios autorizados
        
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
        
        # Obtener lista de usuarios autorizados
        if KEYS_ENABLED:
            cleanup_expired()  # Limpiar expirados
            chat_ids = get_authorized_chat_ids()
            if not chat_ids:
                logger.warning("⚠️ No hay usuarios autorizados - señal no enviada")
                print("\n" + "="*50)
                print("🚀 SEÑAL (sin usuarios autorizados)")
                print("="*50)
                print(message)
                print("="*50 + "\n")
                return False
        else:
            # Modo legacy: usar chat_id único
            chat_ids = [self.legacy_chat_id] if self.legacy_chat_id else []
        
        sent_count = 0
        error_count = 0
        
        for chat_id in chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='HTML'
                )
                sent_count += 1
            except TelegramError as e:
                error_count += 1
                logger.error(f"❌ Error enviando a {chat_id}: {e}")
        
        if sent_count > 0:
            logger.info(f"✅ Señal enviada a {sent_count}/{len(chat_ids)} usuarios")
            return True
        else:
            logger.error(f"❌ No se pudo enviar la señal a ningún usuario")
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

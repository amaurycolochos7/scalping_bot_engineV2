"""
Sistema de notificaciones por Telegram
Envía señales a todos los usuarios autorizados
"""
import requests
from config import Config
import logging

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
        """Inicializa el notificador de Telegram"""
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.legacy_chat_id = Config.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        
        if self.token:
            logger.info("✅ Telegram notifier inicializado")
            if KEYS_ENABLED:
                logger.info("🔑 Sistema de keys habilitado")
        else:
            logger.warning("⚠️ Telegram no configurado")
    
    def send_signal_sync(self, message):
        """
        Envía una señal a todos los usuarios autorizados (versión síncrona)
        """
        if not self.token:
            print("\n" + "="*50)
            print("🚀 NUEVA SEÑAL")
            print("="*50)
            print(message)
            print("="*50 + "\n")
            return True
        
        # Obtener lista de usuarios autorizados
        if KEYS_ENABLED:
            cleanup_expired()
            chat_ids = get_authorized_chat_ids()
            if not chat_ids:
                logger.warning("⚠️ No hay usuarios autorizados")
                return False
        else:
            chat_ids = [self.legacy_chat_id] if self.legacy_chat_id else []
        
        sent_count = 0
        
        for chat_id in chat_ids:
            try:
                response = requests.post(
                    self.api_url,
                    json={
                        'chat_id': chat_id,
                        'text': message,
                        'parse_mode': 'HTML'
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    sent_count += 1
                else:
                    logger.error(f"❌ Error enviando a {chat_id}: {response.text}")
                    
            except Exception as e:
                logger.error(f"❌ Error enviando a {chat_id}: {e}")
        
        if sent_count > 0:
            logger.info(f"✅ Señal enviada a {sent_count}/{len(chat_ids)} usuarios")
            return True
        
        return False

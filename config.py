"""
Configuracion global del Scalping Engine V2
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env desde el directorio del script
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # Binance API
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # Configuración de análisis
    MIN_VOLUME_24H = int(os.getenv('MIN_VOLUME_24H', 5000000))  # $5M
    MAX_CRYPTOS_TO_MONITOR = int(os.getenv('MAX_CRYPTOS_TO_MONITOR', 600))
    SCAN_INTERVAL_SECONDS = int(os.getenv('SCAN_INTERVAL_SECONDS', 60))
    
    # Timeframes
    TIMEFRAME_LONG = os.getenv('TIMEFRAME_LONG', '4h')
    TIMEFRAME_MEDIUM = os.getenv('TIMEFRAME_MEDIUM', '1h')
    TIMEFRAME_SHORT = os.getenv('TIMEFRAME_SHORT', '15m')
    
    # Confirmación
    MIN_CANDLES_CONFIRMATION = int(os.getenv('MIN_CANDLES_CONFIRMATION', 3))
    SIGNAL_COOLDOWN_HOURS = int(os.getenv('SIGNAL_COOLDOWN_HOURS', 2))
    
    # Take Profit / Stop Loss
    TP_PERCENTAGE = float(os.getenv('TP_PERCENTAGE', 10.0))
    SL_PERCENTAGE = float(os.getenv('SL_PERCENTAGE', 5.0))
    
    @classmethod
    def validate(cls):
        """Valida que la configuracion sea correcta"""
        if not cls.BINANCE_API_KEY or not cls.BINANCE_SECRET_KEY:
            raise ValueError("Falta configurar BINANCE_API_KEY y BINANCE_SECRET_KEY en .env")
        
        print("Configuracion cargada correctamente")
        print(f"Monitorearemos hasta {cls.MAX_CRYPTOS_TO_MONITOR} criptos")
        print(f"Volumen minimo: ${cls.MIN_VOLUME_24H:,} USD")
        print(f"Escaneo cada {cls.SCAN_INTERVAL_SECONDS}s")
        return True

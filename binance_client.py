"""
Cliente optimizado para Binance Futures API
"""
from binance.client import Client
from binance.exceptions import BinanceAPIException
from config import Config
import logging

logger = logging.getLogger(__name__)

class BinanceClient:
    def __init__(self):
        """Inicializa el cliente de Binance Futures"""
        self.client = Client(
            Config.BINANCE_API_KEY,
            Config.BINANCE_SECRET_KEY,
            tld='com'
        )
        logger.info("✅ Cliente Binance Futures inicializado")
    
    def get_all_usdt_pairs(self):
        """
        Obtiene todos los pares USDT disponibles en Binance FUTURES
        Filtra por volumen mínimo
        """
        try:
            # Obtener info del exchange de FUTURES
            exchange_info = self.client.futures_exchange_info()
            
            # Filtrar solo pares USDT que estén activos
            usdt_pairs = []
            for symbol_info in exchange_info['symbols']:
                if (symbol_info['symbol'].endswith('USDT') and 
                    symbol_info['status'] == 'TRADING' and
                    symbol_info['quoteAsset'] == 'USDT' and
                    symbol_info['contractType'] == 'PERPETUAL'):  # Solo perpetuos
                    usdt_pairs.append(symbol_info['symbol'])
            
            logger.info(f"📊 Encontrados {len(usdt_pairs)} pares USDT en Futures")
            
            # Filtrar por volumen
            filtered_pairs = self._filter_by_volume(usdt_pairs)
            
            return filtered_pairs
            
        except BinanceAPIException as e:
            logger.error(f"❌ Error obteniendo pares: {e}")
            return []
    
    
    def _filter_by_volume(self, pairs):
        """Filtra pares por volumen mínimo de 24h en Futures"""
        try:
            # Usar futures ticker para obtener volúmenes
            tickers = self.client.futures_ticker()
            
            # Convertir a diccionario para búsqueda rápida
            ticker_dict = {t['symbol']: float(t['quoteVolume']) for t in tickers}
            
            # Filtrar por volumen
            filtered = []
            for pair in pairs:
                volume = ticker_dict.get(pair, 0)
                if volume >= Config.MIN_VOLUME_24H:
                    filtered.append(pair)
            
            logger.info(f"✅ {len(filtered)} pares con volumen > ${Config.MIN_VOLUME_24H:,}")
            
            return sorted(filtered[:Config.MAX_CRYPTOS_TO_MONITOR])
            
        except Exception as e:
            logger.error(f"❌ Error filtrando por volumen: {e}")
            return pairs[:Config.MAX_CRYPTOS_TO_MONITOR]
    
    def get_klines(self, symbol, interval, limit=10):
        """
        Obtiene velas japonesas para un símbolo en FUTURES
        
        Args:
            symbol: Par de trading (ej: BTCUSDT)
            interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Número de velas a obtener
            
        Returns:
            Lista de velas en formato [timestamp, open, high, low, close, volume]
        """
        try:
            # Usar futures_klines en lugar de get_klines
            klines = self.client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            # Formatear datos
            formatted = []
            for k in klines:
                formatted.append({
                    'timestamp': k[0],
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5])
                })
            
            return formatted
            
        except BinanceAPIException as e:
            logger.error(f"❌ Error obteniendo velas de {symbol}: {e}")
            return []
    
    def get_current_price(self, symbol):
        """Obtiene el precio actual de un símbolo en Futures"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"❌ Error obteniendo precio de {symbol}: {e}")
            return None

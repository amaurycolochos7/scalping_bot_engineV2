"""
Descarga de datos históricos de Binance para entrenamiento de IA
"""
import pandas as pd
from binance_client import BinanceClient
from config import Config
import os
import logging
from datetime import datetime, timedelta
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataDownloader:
    def __init__(self, output_dir='data/historical'):
        """Inicializa el descargador de datos"""
        self.client = BinanceClient()
        self.output_dir = output_dir
        
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
    def download_all_data(self, months_back=12, limit_pairs=None):
        """
        Descarga datos históricos de múltiples pares de FUTURES
        
        Args:
            months_back: Meses hacia atrás (12 = 1 año máximo)
            limit_pairs: Si es None, descarga TODOS los pares disponibles
        """
        logger.info(f"🚀 Iniciando descarga de datos históricos de FUTURES")
        logger.info(f"📅 Período: {months_back} meses atrás (máximo)")
        logger.info(f"📊 Pares: TODOS los disponibles en Futures")
        
        # Obtener TODOS los pares líquidos de Futures
        all_pairs = self.client.get_all_usdt_pairs()
        
        if limit_pairs:
            pairs = all_pairs[:limit_pairs]
        else:
            pairs = all_pairs  # TODOS los pares
            
        logger.info(f"✅ {len(pairs)} pares seleccionados")
        
        # Timeframes a descargar
        timeframes = [Config.TIMEFRAME_LONG, Config.TIMEFRAME_MEDIUM, Config.TIMEFRAME_SHORT]
        
        total_downloads = len(pairs) * len(timeframes)
        current = 0
        success_count = 0
        failed_count = 0
        
        for pair in pairs:
            for timeframe in timeframes:
                current += 1
                logger.info(f"[{current}/{total_downloads}] Descargando {pair} {timeframe}...")
                
                try:
                    df = self.download_pair_data(pair, timeframe, months_back)
                    
                    if df is not None and len(df) > 0:
                        # Guardar a CSV
                        filename = f"{self.output_dir}/{pair}_{timeframe}.csv"
                        df.to_csv(filename, index=False)
                        logger.info(f"   ✅ {len(df)} velas guardadas")
                        success_count += 1
                    else:
                        logger.warning(f"   ⚠️ No se obtuvieron datos para {pair} {timeframe}")
                        failed_count += 1
                    
                    # Pausa para no saturar la API
                    time.sleep(0.3)
                    
                except Exception as e:
                    logger.error(f"   ❌ Error: {e}")
                    failed_count += 1
                    continue
        
        logger.info("\n" + "="*60)
        logger.info("✅ DESCARGA COMPLETADA")
        logger.info(f"📊 Éxito: {success_count} | Fallos: {failed_count}")
        logger.info(f"📁 Datos guardados en: {self.output_dir}")
        logger.info("="*60)
        
    def download_pair_data(self, symbol, interval, months_back=12):
        """
        Descarga datos de un par específico de FUTURES
        Descarga máximo 1 año o desde que se listó la moneda
        
        Returns:
            DataFrame con columnas: timestamp, open, high, low, close, volume
        """
        # Binance tiene límite de 1500 velas por request
        # Calculamos cuántas velas necesitamos según timeframe
        limit_map = {
            '15m': 1500,  # ~15 días
            '1h': 1500,   # ~62 días  
            '4h': 1500    # ~250 días
        }
        
        limit = limit_map.get(interval, 1500)
        
        # Para obtener 1 año completo necesitamos ajustar el límite
        if interval == '15m':
            limit = 1500  # ~15 días (necesitaríamos múltiples requests para 1 año)
        elif interval == '1h':
            limit = 1500  # ~62 días
        elif interval == '4h':
            limit = 1500  # ~8 meses (suficiente para cubrir casi 1 año)
        
        try:
            # Obtener datos del cliente Binance Futures
            klines = self.client.get_klines(symbol, interval, limit=limit)
            
            if not klines:
                return None
            
            # Convertir a DataFrame
            df = pd.DataFrame(klines)
            
            # Añadir metadatos
            df['symbol'] = symbol
            df['timeframe'] = interval
            
            # Filtrar solo último año (si hay más datos)
            if len(df) > 0:
                one_year_ago = datetime.now() - timedelta(days=365)
                one_year_ago_ms = int(one_year_ago.timestamp() * 1000)
                df = df[df['timestamp'] >= one_year_ago_ms]
            
            return df
            
        except Exception as e:
            logger.error(f"Error descargando {symbol}: {e}")
            return None

    def get_download_stats(self):
        """Obtiene estadísticas de los datos descargados"""
        if not os.path.exists(self.output_dir):
            return None
        
        files = [f for f in os.listdir(self.output_dir) if f.endswith('.csv')]
        total_size = sum(os.path.getsize(f"{self.output_dir}/{f}") for f in files)
        
        return {
            'total_files': len(files),
            'total_size_mb': total_size / (1024 * 1024),
            'data_dir': self.output_dir
        }

if __name__ == "__main__":
    print("""
    ==========================================
       DESCARGA DE DATOS HISTORICOS - FUTURES
       Para Entrenamiento de IA
    ==========================================
    """)
    
    downloader = DataDownloader()
    
    # Descargar 1 año máximo de TODAS las monedas disponibles en Futures
    downloader.download_all_data(months_back=12, limit_pairs=None)
    
    # Mostrar estadísticas
    stats = downloader.get_download_stats()
    if stats:
        print(f"\n📊 Estadísticas:")
        print(f"   Archivos: {stats['total_files']}")
        print(f"   Tamaño: {stats['total_size_mb']:.2f} MB")
    
    # Mostrar estadísticas
    stats = downloader.get_download_stats()
    if stats:
        print(f"\n📊 Estadísticas:")
        print(f"   Archivos: {stats['total_files']}")
        print(f"   Tamaño: {stats['total_size_mb']:.2f} MB")

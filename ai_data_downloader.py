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
        
    def download_all_data(self, months_back=12, limit_pairs=100):
        """
        Descarga datos históricos de múltiples pares
        
        Args:
            months_back: Meses hacia atrás (12 = 1 año, 24 = 2 años)
            limit_pairs: Número máximo de pares a descargar
        """
        logger.info(f"🚀 Iniciando descarga de datos históricos")
        logger.info(f"📅 Período: {months_back} meses atrás")
        logger.info(f"📊 Pares: hasta {limit_pairs}")
        
        # Obtener pares líquidos
        pairs = self.client.get_all_usdt_pairs()[:limit_pairs]
        logger.info(f"✅ {len(pairs)} pares seleccionados")
        
        # Timeframes a descargar
        timeframes = [Config.TIMEFRAME_LONG, Config.TIMEFRAME_MEDIUM, Config.TIMEFRAME_SHORT]
        
        total_downloads = len(pairs) * len(timeframes)
        current = 0
        
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
                        logger.info(f"   ✅ {len(df)} velas guardadas en {filename}")
                    else:
                        logger.warning(f"   ⚠️ No se obtuvieron datos para {pair} {timeframe}")
                    
                    # Pausa para no saturar la API
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"   ❌ Error: {e}")
                    continue
        
        logger.info("\n" + "="*60)
        logger.info("✅ DESCARGA COMPLETADA")
        logger.info(f"📁 Datos guardados en: {self.output_dir}")
        logger.info("="*60)
        
    def download_pair_data(self, symbol, interval, months_back=12):
        """
        Descarga datos de un par específico
        
        Returns:
            DataFrame con columnas: timestamp, open, high, low, close, volume
        """
        # Calcular límite de velas según timeframe
        limit_map = {
            '15m': 1000,  # ~10 días
            '1h': 1000,   # ~41 días
            '4h': 1000    # ~166 días
        }
        
        limit = limit_map.get(interval, 1000)
        
        # Para períodos largos, necesitamos múltiples requests
        all_data = []
        
        # Fecha de inicio
        end_time = datetime.now()
        start_time = end_time - timedelta(days=months_back * 30)
        
        try:
            # Obtener datos del cliente Binance
            klines = self.client.get_klines(symbol, interval, limit=limit)
            
            if not klines:
                return None
            
            # Convertir a DataFrame
            df = pd.DataFrame(klines)
            
            # Renombrar columnas para claridad
            df['symbol'] = symbol
            df['timeframe'] = interval
            
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
    ╔══════════════════════════════════════════╗
    ║   DESCARGA DE DATOS HISTÓRICOS           ║
    ║   Para Entrenamiento de IA               ║
    ╚══════════════════════════════════════════╝
    """)
    
    downloader = DataDownloader()
    
    # Descargar 1 año de datos, 100 pares más líquidos
    downloader.download_all_data(months_back=12, limit_pairs=100)
    
    # Mostrar estadísticas
    stats = downloader.get_download_stats()
    if stats:
        print(f"\n📊 Estadísticas:")
        print(f"   Archivos: {stats['total_files']}")
        print(f"   Tamaño: {stats['total_size_mb']:.2f} MB")

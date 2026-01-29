#!/usr/bin/env python
"""
Descarga de datos históricos de Binance FUTURES para entrenamiento de IA
Descarga 6 meses de datos de TODAS las criptomonedas de Futures
"""
import pandas as pd
from binance.client import Client
from config import Config
import os
import logging
from datetime import datetime, timedelta
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FuturesDataDownloader:
    def __init__(self, output_dir='data/historical'):
        """Inicializa el descargador de datos de Futures"""
        self.client = Client(Config.BINANCE_API_KEY, Config.BINANCE_SECRET_KEY)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def get_all_futures_pairs(self):
        """Obtiene TODOS los pares perpetuos de Binance Futures"""
        try:
            exchange_info = self.client.futures_exchange_info()
            
            pairs = []
            for symbol_info in exchange_info['symbols']:
                if (symbol_info['symbol'].endswith('USDT') and 
                    symbol_info['status'] == 'TRADING' and
                    symbol_info['contractType'] == 'PERPETUAL'):
                    pairs.append(symbol_info['symbol'])
            
            logger.info(f"📊 Encontrados {len(pairs)} pares perpetuos USDT en Futures")
            return sorted(pairs)
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo pares: {e}")
            return []
    
    def download_historical_klines(self, symbol, interval, months=6):
        """
        Descarga datos históricos haciendo múltiples requests si es necesario
        
        Args:
            symbol: Par de trading (ej: BTCUSDT)  
            interval: Timeframe (15m, 1h, 4h)
            months: Meses hacia atrás
        
        Returns:
            DataFrame con todos los datos
        """
        # Calcular fecha inicio
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        all_klines = []
        current_start = start_date
        
        while current_start < end_date:
            try:
                # Obtener máximo 1000 velas por request
                klines = self.client.futures_klines(
                    symbol=symbol,
                    interval=interval,
                    startTime=int(current_start.timestamp() * 1000),
                    limit=1000
                )
                
                if not klines:
                    break
                
                all_klines.extend(klines)
                
                # Mover al siguiente batch
                last_timestamp = klines[-1][0]
                current_start = datetime.fromtimestamp(last_timestamp / 1000) + timedelta(milliseconds=1)
                
                # Pequeña pausa para no saturar API
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error en batch: {e}")
                break
        
        if not all_klines:
            return None
        
        # Convertir a DataFrame
        df = pd.DataFrame(all_klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convertir tipos
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Solo las columnas necesarias
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
        # Eliminar duplicados
        df = df.drop_duplicates(subset=['timestamp'])
        
        return df
    
    def download_all_futures_data(self, months=6):
        """
        Descarga 6 meses de datos de TODAS las criptomonedas de Futures
        """
        print("""
    ╔══════════════════════════════════════════════════════╗
    ║   DESCARGA DE DATOS HISTÓRICOS - BINANCE FUTURES     ║
    ║   Para Entrenamiento de IA                           ║
    ╚══════════════════════════════════════════════════════╝
        """)
        
        # Obtener todos los pares de Futures
        pairs = self.get_all_futures_pairs()
        
        if not pairs:
            logger.error("❌ No se encontraron pares de Futures")
            return
        
        logger.info(f"📅 Período: {months} meses hacia atrás")
        logger.info(f"📊 Timeframe: 1h (óptimo para IA)")
        logger.info(f"🔄 Total pares a descargar: {len(pairs)}")
        logger.info("")
        
        success = 0
        failed = 0
        
        for i, pair in enumerate(pairs, 1):
            logger.info(f"[{i}/{len(pairs)}] Descargando {pair}...")
            
            try:
                # Descargar datos de 1h (balance entre detalle y tamaño)
                df = self.download_historical_klines(pair, '1h', months)
                
                if df is not None and len(df) > 100:
                    # Guardar CSV
                    filepath = f"{self.output_dir}/{pair}_1h.csv"
                    df.to_csv(filepath, index=False)
                    logger.info(f"   ✅ {len(df):,} velas guardadas")
                    success += 1
                else:
                    logger.warning(f"   ⚠️ Datos insuficientes")
                    failed += 1
                
                # Pausa para no saturar la API
                time.sleep(0.2)
                
            except Exception as e:
                logger.error(f"   ❌ Error: {e}")
                failed += 1
                continue
        
        # Resumen final
        print("\n" + "="*60)
        print("✅ DESCARGA COMPLETADA")
        print("="*60)
        print(f"📊 Éxito: {success} | Fallos: {failed}")
        print(f"📁 Datos guardados en: {self.output_dir}")
        
        # Estadísticas
        total_size = sum(
            os.path.getsize(f"{self.output_dir}/{f}") 
            for f in os.listdir(self.output_dir) 
            if f.endswith('.csv')
        )
        print(f"💾 Tamaño total: {total_size / (1024*1024):.2f} MB")
        print("="*60)
        
        return success


if __name__ == "__main__":
    downloader = FuturesDataDownloader()
    downloader.download_all_futures_data(months=6)

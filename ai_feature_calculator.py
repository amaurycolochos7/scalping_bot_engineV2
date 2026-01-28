"""
Calculador de Features Técnicos para IA
"""
import pandas as pd
import numpy as np
import ta
import os
import logging
from glob import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureCalculator:
    def __init__(self, data_dir='data/historical', output_dir='data/features'):
        """Inicializa el calculador de features"""
        self.data_dir = data_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def calculate_all_features(self):
        """Calcula features para todos los archivos descargados"""
        csv_files = glob(f"{self.data_dir}/*.csv")
        
        logger.info(f"🔍 Encontrados {len(csv_files)} archivos para procesar")
        
        for i, filepath in enumerate(csv_files, 1):
            filename = os.path.basename(filepath)
            logger.info(f"[{i}/{len(csv_files)}] Procesando {filename}...")
            
            try:
                df = pd.read_csv(filepath)
                df_features = self.calculate_features(df)
                
                if df_features is not None:
                    output_path = f"{self.output_dir}/{filename}"
                    df_features.to_csv(output_path, index=False)
                    logger.info(f"   ✅ {len(df_features)} filas con features guardadas")
                
            except Exception as e:
                logger.error(f"   ❌ Error: {e}")
                continue
        
        logger.info("\n✅ Cálculo de features completado")
    
    def calculate_features(self, df):
        """
        Calcula features técnicos para un DataFrame de velas
        
        Features incluidos:
        - RSI (14, 7)
        - MACD (12, 26, 9)
        - EMAs (7, 25, 50, 200)
        - Bollinger Bands
        - ATR
        - Volume Ratio
        - Price Change %
        """
        if df is None or len(df) < 200:
            return None
        
        # Asegurarse de que tenemos las columnas necesarias
        required = ['close', 'high', 'low', 'volume']
        if not all(col in df.columns for col in required):
            return None
        
        df = df.copy()
        
        # ===== MOMENTUM INDICATORS =====
        # RSI
        df['rsi_14'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        df['rsi_7'] = ta.momentum.RSIIndicator(df['close'], window=7).rsi()
        
        # MACD
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # ===== TREND INDICATORS =====
        # EMAs
        df['ema_7'] = ta.trend.EMAIndicator(df['close'], window=7).ema_indicator()
        df['ema_25'] = ta.trend.EMAIndicator(df['close'], window=25).ema_indicator()
        df['ema_50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
        df['ema_200'] = ta.trend.EMAIndicator(df['close'], window=200).ema_indicator()
        
        # Distancia del precio a las EMAs (%)
        df['dist_ema_50'] = ((df['close'] - df['ema_50']) / df['ema_50'] * 100)
        df['dist_ema_200'] = ((df['close'] - df['ema_200']) / df['ema_200'] * 100)
        
        # ===== VOLATILITY INDICATORS =====
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['close'])
        df['bb_high'] = bollinger.bollinger_hband()
        df['bb_low'] = bollinger.bollinger_lband()
        df['bb_mid'] = bollinger.bollinger_mavg()
        df['bb_width'] = ((df['bb_high'] - df['bb_low']) / df['bb_mid'] * 100)
        df['bb_position'] = ((df['close'] - df['bb_low']) / (df['bb_high'] - df['bb_low']))
        
        # ATR (Average True Range)
        df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
        
        # ===== VOLUME INDICATORS =====
        df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma_20']
        
        # ===== PRICE ACTION =====
        # Cambio de precio
        df['price_change_1'] = df['close'].pct_change(1) * 100
        df['price_change_3'] = df['close'].pct_change(3) * 100
        df['price_change_7'] = df['close'].pct_change(7) * 100
        
        # Velas verdes/rojas
        df['candle_type'] = (df['close'] > df['open']).astype(int)  # 1=green, 0=red
        
        # Contar velas verdes consecutivas
        df['green_streak'] = (df['candle_type'] == 1).astype(int).groupby(
            (df['candle_type'] != 1).cumsum()
        ).cumsum()
        
        df['red_streak'] = (df['candle_type'] == 0).astype(int).groupby(
            (df['candle_type'] != 0).cumsum()
        ).cumsum()
        
        # ===== TIME FEATURES =====
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # Eliminar filas con NaN (resultado de indicadores)
        df = df.dropna()
        
        return df

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║   CÁLCULO DE FEATURES TÉCNICOS           ║
    ║   RSI, MACD, EMAs, Bollinger, ATR        ║
    ╚══════════════════════════════════════════╝
    """)
    
    calculator = FeatureCalculator()
    calculator.calculate_all_features()

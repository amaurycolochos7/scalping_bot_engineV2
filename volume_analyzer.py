"""
Detector de Volumen Anormal
Identifica actividad inusual que puede indicar movimiento grande
"""
import pandas as pd
import numpy as np
import logging
from binance.client import Client
from config import Config

logger = logging.getLogger(__name__)


class VolumeAnalyzer:
    """Analiza patrones de volumen para detectar actividad de ballenas"""
    
    def __init__(self):
        self.client = Client(Config.BINANCE_API_KEY, Config.BINANCE_SECRET_KEY)
    
    def get_volume_analysis(self, symbol: str) -> dict:
        """
        Analiza el volumen reciente vs promedio
        
        Returns:
            dict con análisis de volumen
        """
        try:
            # Obtener últimas 100 velas de 1h para calcular promedio
            klines = self.client.futures_klines(
                symbol=symbol,
                interval='1h',
                limit=100
            )
            
            if not klines or len(klines) < 50:
                return None
            
            # Extraer volúmenes
            volumes = [float(k[5]) for k in klines]
            
            # Calcular métricas
            current_vol = volumes[-1]
            avg_vol = np.mean(volumes[:-1])  # Promedio sin la vela actual
            std_vol = np.std(volumes[:-1])
            
            # Ratio actual vs promedio
            vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
            
            # Z-score para detectar anomalías
            z_score = (current_vol - avg_vol) / std_vol if std_vol > 0 else 0
            
            # Interpretar
            if vol_ratio >= 5:
                interpretation = f"Volumen EXTREMO ({vol_ratio:.1f}x) - Ballenas activas"
                signal = "STRONG_MOVE"
                confidence = 85
            elif vol_ratio >= 3:
                interpretation = f"Volumen MUY ALTO ({vol_ratio:.1f}x) - Movimiento importante"
                signal = "STRONG_MOVE"
                confidence = 70
            elif vol_ratio >= 2:
                interpretation = f"Volumen ALTO ({vol_ratio:.1f}x) - Interés creciente"
                signal = "MOVE"
                confidence = 55
            elif vol_ratio <= 0.3:
                interpretation = f"Volumen MUY BAJO ({vol_ratio:.1f}x) - Calma antes de tormenta?"
                signal = "CALM"
                confidence = 40
            else:
                interpretation = f"Volumen normal ({vol_ratio:.1f}x)"
                signal = "NORMAL"
                confidence = 0
            
            return {
                'current_volume': current_vol,
                'average_volume': avg_vol,
                'volume_ratio': vol_ratio,
                'z_score': z_score,
                'interpretation': interpretation,
                'signal': signal,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error analizando volumen: {e}")
            return None
    
    def detect_volume_spike(self, symbol: str, timeframe='15m', threshold=3.0) -> dict:
        """
        Detecta picos de volumen en tiempo real
        
        Args:
            symbol: Par de trading
            timeframe: Timeframe a analizar
            threshold: Múltiplo del promedio para considerar spike
        
        Returns:
            dict con información del spike si lo hay
        """
        try:
            # Obtener últimas 50 velas
            klines = self.client.futures_klines(
                symbol=symbol,
                interval=timeframe,
                limit=50
            )
            
            if not klines or len(klines) < 20:
                return None
            
            # Analizar
            volumes = [float(k[5]) for k in klines]
            prices_close = [float(k[4]) for k in klines]
            
            current_vol = volumes[-1]
            avg_vol = np.mean(volumes[:-1])
            ratio = current_vol / avg_vol if avg_vol > 0 else 1
            
            # Dirección del movimiento
            price_change = (prices_close[-1] - prices_close[-2]) / prices_close[-2] * 100
            
            if ratio >= threshold:
                if price_change > 0:
                    direction = "BULLISH"
                    description = f"Spike de volumen ({ratio:.1f}x) con precio SUBIENDO"
                else:
                    direction = "BEARISH"
                    description = f"Spike de volumen ({ratio:.1f}x) con precio BAJANDO"
                
                return {
                    'detected': True,
                    'ratio': ratio,
                    'direction': direction,
                    'price_change': price_change,
                    'description': description,
                    'confidence': min(70 + (ratio - threshold) * 10, 95)
                }
            
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Error detectando spike de volumen: {e}")
            return None
    
    def get_volume_profile(self, symbol: str) -> dict:
        """
        Analiza el perfil de volumen para encontrar zonas de interés
        
        Returns:
            dict con zonas de alto volumen
        """
        try:
            # Obtener últimas 200 velas de 1h
            klines = self.client.futures_klines(
                symbol=symbol,
                interval='1h',
                limit=200
            )
            
            if not klines or len(klines) < 100:
                return None
            
            # Crear DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            for col in ['high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            # Dividir rango de precio en niveles
            price_min = df['low'].min()
            price_max = df['high'].max()
            n_levels = 20
            
            levels = np.linspace(price_min, price_max, n_levels + 1)
            volume_at_level = []
            
            for i in range(len(levels) - 1):
                low = levels[i]
                high = levels[i + 1]
                
                # Volumen acumulado en este rango
                mask = (df['low'] <= high) & (df['high'] >= low)
                vol = df.loc[mask, 'volume'].sum()
                
                volume_at_level.append({
                    'price_low': low,
                    'price_high': high,
                    'price_mid': (low + high) / 2,
                    'volume': vol
                })
            
            # Encontrar zonas de alto volumen (POC - Point of Control)
            volume_at_level.sort(key=lambda x: x['volume'], reverse=True)
            
            high_volume_zones = volume_at_level[:3]  # Top 3 zonas
            
            current_price = float(df['close'].iloc[-1])
            
            # Determinar si estamos cerca de una zona de alto volumen
            for zone in high_volume_zones:
                if zone['price_low'] <= current_price <= zone['price_high']:
                    return {
                        'zones': high_volume_zones,
                        'current_in_hvz': True,
                        'interpretation': f"Precio en zona de alto volumen (${zone['price_mid']:.4f})"
                    }
            
            return {
                'zones': high_volume_zones,
                'current_in_hvz': False,
                'interpretation': "Precio fuera de zonas de alto volumen"
            }
            
        except Exception as e:
            logger.error(f"Error analizando perfil de volumen: {e}")
            return None

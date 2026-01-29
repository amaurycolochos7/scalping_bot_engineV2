"""
Reconocimiento de Patrones de Precio
Detecta triángulos, cuñas, canales, doble techo/suelo, etc.
"""
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
import logging

logger = logging.getLogger(__name__)


class PatternRecognizer:
    """Detecta patrones técnicos en datos de precio"""
    
    def __init__(self):
        self.patterns_found = []
    
    def find_all_patterns(self, df: pd.DataFrame) -> list:
        """
        Busca todos los patrones en un DataFrame de velas
        
        Args:
            df: DataFrame con columnas: open, high, low, close, volume
        
        Returns:
            Lista de patrones encontrados con su tipo y confianza
        """
        patterns = []
        
        if len(df) < 50:
            return patterns
        
        # Encontrar soportes y resistencias
        support, resistance = self._find_support_resistance(df)
        
        # Detectar patrones de precio
        patterns.extend(self._detect_triangle(df))
        patterns.extend(self._detect_double_top_bottom(df, support, resistance))
        patterns.extend(self._detect_channel(df))
        
        # Detectar patrones de velas
        patterns.extend(self._detect_candle_patterns(df))
        
        return patterns
    
    def _find_support_resistance(self, df: pd.DataFrame, order=5):
        """Encuentra niveles de soporte y resistencia"""
        highs = df['high'].values
        lows = df['low'].values
        
        # Encontrar máximos y mínimos locales
        local_max_idx = argrelextrema(highs, np.greater, order=order)[0]
        local_min_idx = argrelextrema(lows, np.less, order=order)[0]
        
        resistance_levels = highs[local_max_idx] if len(local_max_idx) > 0 else []
        support_levels = lows[local_min_idx] if len(local_min_idx) > 0 else []
        
        return support_levels, resistance_levels
    
    def _detect_triangle(self, df: pd.DataFrame) -> list:
        """Detecta patrones de triángulo (ascendente, descendente, simétrico)"""
        patterns = []
        
        if len(df) < 20:
            return patterns
        
        # Usar últimas 20 velas
        recent = df.tail(20)
        highs = recent['high'].values
        lows = recent['low'].values
        
        # Calcular pendientes de máximos y mínimos
        x = np.arange(len(highs))
        
        # Regresión lineal de máxitos
        high_slope = np.polyfit(x, highs, 1)[0]
        low_slope = np.polyfit(x, lows, 1)[0]
        
        # Triángulo ascendente: mínimos subiendo, máximos planos
        if low_slope > 0.001 and abs(high_slope) < 0.001:
            patterns.append({
                'type': 'TRIANGLE_ASCENDING',
                'direction': 'BULLISH',
                'confidence': 70,
                'description': 'Triángulo ascendente - probable ruptura alcista'
            })
        
        # Triángulo descendente: máximos bajando, mínimos planos
        elif high_slope < -0.001 and abs(low_slope) < 0.001:
            patterns.append({
                'type': 'TRIANGLE_DESCENDING',
                'direction': 'BEARISH',
                'confidence': 70,
                'description': 'Triángulo descendente - probable ruptura bajista'
            })
        
        # Triángulo simétrico: ambos convergiendo
        elif high_slope < -0.0005 and low_slope > 0.0005:
            patterns.append({
                'type': 'TRIANGLE_SYMMETRIC',
                'direction': 'NEUTRAL',
                'confidence': 60,
                'description': 'Triángulo simétrico - ruptura inminente'
            })
        
        return patterns
    
    def _detect_double_top_bottom(self, df: pd.DataFrame, support, resistance) -> list:
        """Detecta doble techo y doble suelo"""
        patterns = []
        
        if len(df) < 30:
            return patterns
        
        recent = df.tail(30)
        highs = recent['high'].values
        lows = recent['low'].values
        current_price = recent['close'].iloc[-1]
        
        # Buscar doble techo (dos máximos similares)
        local_max_idx = argrelextrema(highs, np.greater, order=3)[0]
        if len(local_max_idx) >= 2:
            last_two_highs = highs[local_max_idx[-2:]]
            if abs(last_two_highs[0] - last_two_highs[1]) / last_two_highs[0] < 0.02:
                patterns.append({
                    'type': 'DOUBLE_TOP',
                    'direction': 'BEARISH',
                    'confidence': 75,
                    'description': f'Doble techo en ${last_two_highs[0]:.4f} - señal bajista'
                })
        
        # Buscar doble suelo (dos mínimos similares)
        local_min_idx = argrelextrema(lows, np.less, order=3)[0]
        if len(local_min_idx) >= 2:
            last_two_lows = lows[local_min_idx[-2:]]
            if abs(last_two_lows[0] - last_two_lows[1]) / last_two_lows[0] < 0.02:
                patterns.append({
                    'type': 'DOUBLE_BOTTOM',
                    'direction': 'BULLISH',
                    'confidence': 75,
                    'description': f'Doble suelo en ${last_two_lows[0]:.4f} - señal alcista'
                })
        
        return patterns
    
    def _detect_channel(self, df: pd.DataFrame) -> list:
        """Detecta canales de precio (alcista, bajista, lateral)"""
        patterns = []
        
        if len(df) < 20:
            return patterns
        
        recent = df.tail(20)
        closes = recent['close'].values
        x = np.arange(len(closes))
        
        # Calcular pendiente
        slope, intercept = np.polyfit(x, closes, 1)
        
        # Calcular R² para ver qué tan bien sigue el canal
        predicted = slope * x + intercept
        ss_res = np.sum((closes - predicted) ** 2)
        ss_tot = np.sum((closes - np.mean(closes)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        if r_squared > 0.7:  # Canal bien definido
            if slope > 0.001:
                patterns.append({
                    'type': 'CHANNEL_UP',
                    'direction': 'BULLISH',
                    'confidence': int(r_squared * 80),
                    'description': 'Canal alcista - tendencia clara'
                })
            elif slope < -0.001:
                patterns.append({
                    'type': 'CHANNEL_DOWN',
                    'direction': 'BEARISH',
                    'confidence': int(r_squared * 80),
                    'description': 'Canal bajista - tendencia clara'
                })
            else:
                patterns.append({
                    'type': 'CHANNEL_LATERAL',
                    'direction': 'NEUTRAL',
                    'confidence': int(r_squared * 70),
                    'description': 'Canal lateral - esperar ruptura'
                })
        
        return patterns
    
    def _detect_candle_patterns(self, df: pd.DataFrame) -> list:
        """Detecta patrones de velas japonesas"""
        patterns = []
        
        if len(df) < 5:
            return patterns
        
        # Últimas 3 velas
        c1 = df.iloc[-3]  # Hace 2 velas
        c2 = df.iloc[-2]  # Vela anterior
        c3 = df.iloc[-1]  # Última vela
        
        # Tamaño del cuerpo
        body_c2 = abs(c2['close'] - c2['open'])
        body_c3 = abs(c3['close'] - c3['open'])
        
        # Rango total
        range_c2 = c2['high'] - c2['low']
        range_c3 = c3['high'] - c3['low']
        
        # === ENGULFING ALCISTA ===
        # Vela roja seguida de vela verde que la "envuelve"
        if (c2['close'] < c2['open'] and  # c2 roja
            c3['close'] > c3['open'] and  # c3 verde
            c3['open'] < c2['close'] and  # c3 abre debajo del cierre de c2
            c3['close'] > c2['open']):    # c3 cierra arriba de apertura de c2
            patterns.append({
                'type': 'ENGULFING_BULLISH',
                'direction': 'BULLISH',
                'confidence': 80,
                'description': 'Envolvente alcista - posible reversión al alza'
            })
        
        # === ENGULFING BAJISTA ===
        if (c2['close'] > c2['open'] and  # c2 verde
            c3['close'] < c3['open'] and  # c3 roja
            c3['open'] > c2['close'] and  # c3 abre arriba del cierre de c2
            c3['close'] < c2['open']):    # c3 cierra debajo de apertura de c2
            patterns.append({
                'type': 'ENGULFING_BEARISH',
                'direction': 'BEARISH',
                'confidence': 80,
                'description': 'Envolvente bajista - posible reversión a la baja'
            })
        
        # === HAMMER (Martillo) ===
        # Cuerpo pequeño arriba, sombra inferior larga
        if range_c3 > 0:
            lower_shadow = min(c3['open'], c3['close']) - c3['low']
            upper_shadow = c3['high'] - max(c3['open'], c3['close'])
            
            if (lower_shadow > body_c3 * 2 and 
                upper_shadow < body_c3 * 0.5 and
                body_c3 < range_c3 * 0.3):
                patterns.append({
                    'type': 'HAMMER',
                    'direction': 'BULLISH',
                    'confidence': 75,
                    'description': 'Martillo - señal de reversión alcista'
                })
        
        # === SHOOTING STAR (Estrella fugaz) ===
        # Cuerpo pequeño abajo, sombra superior larga
        if range_c3 > 0:
            lower_shadow = min(c3['open'], c3['close']) - c3['low']
            upper_shadow = c3['high'] - max(c3['open'], c3['close'])
            
            if (upper_shadow > body_c3 * 2 and 
                lower_shadow < body_c3 * 0.5 and
                body_c3 < range_c3 * 0.3):
                patterns.append({
                    'type': 'SHOOTING_STAR',
                    'direction': 'BEARISH',
                    'confidence': 75,
                    'description': 'Estrella fugaz - señal de reversión bajista'
                })
        
        # === DOJI ===
        # Cuerpo muy pequeño (apertura ≈ cierre)
        if range_c3 > 0 and body_c3 / range_c3 < 0.1:
            patterns.append({
                'type': 'DOJI',
                'direction': 'NEUTRAL',
                'confidence': 60,
                'description': 'Doji - indecisión, posible cambio de tendencia'
            })
        
        return patterns
    
    def get_pattern_signal(self, patterns: list) -> dict:
        """
        Analiza los patrones encontrados y da una señal consolidada
        
        Returns:
            dict con signal, confidence, y reasons
        """
        if not patterns:
            return None
        
        bullish_score = 0
        bearish_score = 0
        reasons = []
        
        for p in patterns:
            if p['direction'] == 'BULLISH':
                bullish_score += p['confidence']
                reasons.append(f"✅ {p['description']}")
            elif p['direction'] == 'BEARISH':
                bearish_score += p['confidence']
                reasons.append(f"🔻 {p['description']}")
        
        # Determinar señal
        if bullish_score > bearish_score and bullish_score >= 70:
            return {
                'signal': 'LONG',
                'confidence': min(bullish_score, 95),
                'reasons': reasons
            }
        elif bearish_score > bullish_score and bearish_score >= 70:
            return {
                'signal': 'SHORT',
                'confidence': min(bearish_score, 95),
                'reasons': reasons
            }
        
        return None

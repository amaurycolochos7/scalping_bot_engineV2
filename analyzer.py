"""
Analizador Multi-Timeframe para detección de tendencias
"""
from config import Config
import logging

logger = logging.getLogger(__name__)

class MultiTimeframeAnalyzer:
    def __init__(self, binance_client):
        self.client = binance_client
    
    def analyze_symbol(self, symbol):
        """
        Analiza un símbolo en los 3 timeframes
        
        Returns:
            dict con:
                - signal: 'LONG', 'SHORT', o None
                - price: precio actual
                - analysis_4h: análisis del 4H
                - analysis_1h: análisis del 1H
                - analysis_15m: análisis del 15m
                - confirmed: bool si hay confirmación
        """
        try:
            # Obtener precio actual
            current_price = self.client.get_current_price(symbol)
            if not current_price:
                return None
            
            # Analizar cada timeframe
            analysis_4h = self._analyze_timeframe(symbol, Config.TIMEFRAME_LONG)
            analysis_1h = self._analyze_timeframe(symbol, Config.TIMEFRAME_MEDIUM)
            analysis_15m = self._analyze_timeframe(symbol, Config.TIMEFRAME_SHORT)
            
            # Determinar señal
            signal, confirmed = self._determine_signal(
                analysis_4h, analysis_1h, analysis_15m
            )
            
            return {
                'symbol': symbol,
                'price': current_price,
                'signal': signal,
                'confirmed': confirmed,
                'analysis_4h': analysis_4h,
                'analysis_1h': analysis_1h,
                'analysis_15m': analysis_15m
            }
            
        except Exception as e:
            logger.error(f"❌ Error analizando {symbol}: {e}")
            return None
    
    def _analyze_timeframe(self, symbol, interval):
        """
        Analiza un timeframe específico
        
        Returns:
            dict con:
                - trend: 'BULLISH', 'BEARISH', 'NEUTRAL'
                - candles: lista de últimas 6 velas ['green', 'red', ...]
                - consecutive_count: cuántas velas consecutivas del mismo color
        """
        # Obtener últimas 10 velas (mostramos 6)
        klines = self.client.get_klines(symbol, interval, limit=10)
        
        if not klines or len(klines) < 6:
            return {
                'trend': 'NEUTRAL',
                'candles': [],
                'consecutive_count': 0
            }
        
        # Analizar las últimas 6 velas
        candles = []
        for k in klines[-6:]:
            if k['close'] > k['open']:
                candles.append('green')
            elif k['close'] < k['open']:
                candles.append('red')
            else:
                candles.append('neutral')
        
        # Contar velas consecutivas del mismo color (desde la más reciente)
        consecutive_count = self._count_consecutive_candles(candles)
        
        # Determinar tendencia general
        green_count = candles.count('green')
        red_count = candles.count('red')
        
        if green_count >= 4:
            trend = 'BULLISH'
        elif red_count >= 4:
            trend = 'BEARISH'
        else:
            trend = 'NEUTRAL'
        
        return {
            'trend': trend,
            'candles': candles,
            'consecutive_count': consecutive_count,
            'color': candles[-1] if candles else 'neutral'
        }
    
    def _count_consecutive_candles(self, candles):
        """Cuenta velas consecutivas del mismo color desde la última"""
        if not candles:
            return 0
        
        last_color = candles[-1]
        count = 0
        
        # Contar desde el final hacia atrás
        for candle in reversed(candles):
            if candle == last_color and candle != 'neutral':
                count += 1
            else:
                break
        
        return count
    
    def _determine_signal(self, analysis_4h, analysis_1h, analysis_15m):
        """
        Determina si hay señal válida
        
        Reglas:
        - LONG: 4H alcista, 1H alcista, 15m tiene 3+ velas verdes consecutivas
        - SHORT: 4H bajista, 1H bajista, 15m tiene 3+ velas rojas consecutivas
        """
        # Verificar que tengamos datos válidos
        if not all([analysis_4h, analysis_1h, analysis_15m]):
            return None, False
        
        # Confirmación en 15m
        confirmed_15m = analysis_15m['consecutive_count'] >= Config.MIN_CANDLES_CONFIRMATION
        
        # SEÑAL LONG
        if (analysis_4h['trend'] == 'BULLISH' and
            analysis_1h['trend'] == 'BULLISH' and
            analysis_15m['color'] == 'green' and
            confirmed_15m):
            return 'LONG', True
        
        # SEÑAL SHORT
        if (analysis_4h['trend'] == 'BEARISH' and
            analysis_1h['trend'] == 'BEARISH' and
            analysis_15m['color'] == 'red' and
            confirmed_15m):
            return 'SHORT', True
        
        return None, False

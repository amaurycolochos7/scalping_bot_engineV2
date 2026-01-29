"""
Datos exclusivos de Binance Futures
Funding Rate, Open Interest, Long/Short Ratio
"""
import logging
from binance.client import Client
from config import Config

logger = logging.getLogger(__name__)


class FuturesAnalyzer:
    """Analiza métricas exclusivas de Futures"""
    
    def __init__(self):
        self.client = Client(Config.BINANCE_API_KEY, Config.BINANCE_SECRET_KEY)
    
    def get_funding_rate(self, symbol: str) -> dict:
        """
        Obtiene el Funding Rate actual
        
        Funding positivo alto → Muchos longs → Posible caída
        Funding negativo alto → Muchos shorts → Posible subida
        
        Returns:
            dict con rate, interpretation, signal
        """
        try:
            # Obtener funding rate actual
            funding = self.client.futures_funding_rate(symbol=symbol, limit=1)
            
            if not funding:
                return None
            
            rate = float(funding[0]['fundingRate']) * 100  # Convertir a porcentaje
            
            # Interpretar
            if rate > 0.1:
                interpretation = "Funding MUY ALTO - Exceso de longs"
                signal = "BEARISH"
                confidence = 70
            elif rate > 0.05:
                interpretation = "Funding alto - Mayoría long"
                signal = "BEARISH"
                confidence = 55
            elif rate < -0.1:
                interpretation = "Funding MUY NEGATIVO - Exceso de shorts"
                signal = "BULLISH"
                confidence = 70
            elif rate < -0.05:
                interpretation = "Funding negativo - Mayoría short"
                signal = "BULLISH"
                confidence = 55
            else:
                interpretation = "Funding neutral"
                signal = "NEUTRAL"
                confidence = 0
            
            return {
                'rate': rate,
                'rate_display': f"{rate:.4f}%",
                'interpretation': interpretation,
                'signal': signal,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo funding rate: {e}")
            return None
    
    def get_open_interest(self, symbol: str) -> dict:
        """
        Obtiene el Open Interest actual y su cambio
        
        OI subiendo + precio subiendo = Tendencia fuerte alcista
        OI subiendo + precio bajando = Tendencia fuerte bajista
        OI bajando = Posiciones cerrándose, debilidad
        
        Returns:
            dict con oi, change, interpretation, signal
        """
        try:
            # OI actual
            oi_data = self.client.futures_open_interest(symbol=symbol)
            current_oi = float(oi_data['openInterest'])
            
            # OI histórico para calcular cambio (últimas 24h)
            oi_hist = self.client.futures_open_interest_hist(
                symbol=symbol, 
                period='5m', 
                limit=288  # 24h en intervalos de 5m
            )
            
            if oi_hist and len(oi_hist) > 0:
                oi_24h_ago = float(oi_hist[0]['sumOpenInterest'])
                oi_change = ((current_oi - oi_24h_ago) / oi_24h_ago) * 100
            else:
                oi_change = 0
            
            # Interpretar
            if oi_change > 10:
                interpretation = "OI subiendo fuerte (+{:.1f}%) - Nueva actividad".format(oi_change)
                signal = "STRONG_TREND"
                confidence = 65
            elif oi_change > 5:
                interpretation = "OI subiendo (+{:.1f}%) - Interés creciente".format(oi_change)
                signal = "TREND"
                confidence = 50
            elif oi_change < -10:
                interpretation = "OI cayendo fuerte ({:.1f}%) - Posiciones cerrándose".format(oi_change)
                signal = "WEAK"
                confidence = 60
            elif oi_change < -5:
                interpretation = "OI cayendo ({:.1f}%) - Pérdida de interés".format(oi_change)
                signal = "WEAK"
                confidence = 45
            else:
                interpretation = "OI estable ({:.1f}%)".format(oi_change)
                signal = "NEUTRAL"
                confidence = 0
            
            return {
                'open_interest': current_oi,
                'oi_display': f"{current_oi:,.0f}",
                'change_24h': oi_change,
                'interpretation': interpretation,
                'signal': signal,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo open interest: {e}")
            return None
    
    def get_long_short_ratio(self, symbol: str) -> dict:
        """
        Obtiene el ratio Long/Short de las cuentas top
        
        Ratio > 2 → 66%+ están long → Posible reversión bajista
        Ratio < 0.5 → 66%+ están short → Posible reversión alcista
        
        Returns:
            dict con ratio, interpretation, signal
        """
        try:
            # Ratio de cuentas top
            ratio_data = self.client.futures_top_longshort_account_ratio(
                symbol=symbol, 
                period='1h', 
                limit=1
            )
            
            if not ratio_data:
                return None
            
            ratio = float(ratio_data[0]['longShortRatio'])
            long_pct = float(ratio_data[0]['longAccount']) * 100
            short_pct = float(ratio_data[0]['shortAccount']) * 100
            
            # Interpretar
            if ratio > 2.5:
                interpretation = f"Extremo LONG ({long_pct:.0f}%) - Riesgo de caída"
                signal = "BEARISH"
                confidence = 75
            elif ratio > 1.5:
                interpretation = f"Mayoría LONG ({long_pct:.0f}%)"
                signal = "BEARISH"
                confidence = 55
            elif ratio < 0.4:
                interpretation = f"Extremo SHORT ({short_pct:.0f}%) - Riesgo de subida"
                signal = "BULLISH"
                confidence = 75
            elif ratio < 0.67:
                interpretation = f"Mayoría SHORT ({short_pct:.0f}%)"
                signal = "BULLISH"
                confidence = 55
            else:
                interpretation = f"Equilibrado (L:{long_pct:.0f}%/S:{short_pct:.0f}%)"
                signal = "NEUTRAL"
                confidence = 0
            
            return {
                'ratio': ratio,
                'long_percent': long_pct,
                'short_percent': short_pct,
                'interpretation': interpretation,
                'signal': signal,
                'confidence': confidence
            }
            
        except Exception as e:
            # 403 = sin permisos VIP, ignorar silenciosamente
            if '403' in str(e) or 'Forbidden' in str(e):
                return None
            logger.debug(f"Long/short ratio no disponible: {e}")
            return None
    
    def get_full_futures_analysis(self, symbol: str) -> dict:
        """
        Análisis completo de métricas Futures
        
        Returns:
            dict con todas las métricas y señal consolidada
        """
        funding = self.get_funding_rate(symbol)
        oi = self.get_open_interest(symbol)
        ls_ratio = self.get_long_short_ratio(symbol)
        
        # Calcular señal consolidada
        bullish_score = 0
        bearish_score = 0
        reasons = []
        
        if funding and funding['signal'] == 'BULLISH':
            bullish_score += funding['confidence']
            reasons.append(f"📊 Funding: {funding['interpretation']}")
        elif funding and funding['signal'] == 'BEARISH':
            bearish_score += funding['confidence']
            reasons.append(f"📊 Funding: {funding['interpretation']}")
        
        if ls_ratio and ls_ratio['signal'] == 'BULLISH':
            bullish_score += ls_ratio['confidence']
            reasons.append(f"📊 Ratio L/S: {ls_ratio['interpretation']}")
        elif ls_ratio and ls_ratio['signal'] == 'BEARISH':
            bearish_score += ls_ratio['confidence']
            reasons.append(f"📊 Ratio L/S: {ls_ratio['interpretation']}")
        
        # OI no da dirección, solo fuerza
        if oi:
            reasons.append(f"📊 OI: {oi['interpretation']}")
        
        # Consolidar
        if bullish_score > bearish_score and bullish_score >= 60:
            signal = 'LONG'
            confidence = min(bullish_score, 90)
        elif bearish_score > bullish_score and bearish_score >= 60:
            signal = 'SHORT'
            confidence = min(bearish_score, 90)
        else:
            signal = None
            confidence = 0
        
        return {
            'funding': funding,
            'open_interest': oi,
            'long_short_ratio': ls_ratio,
            'signal': signal,
            'confidence': confidence,
            'reasons': reasons
        }

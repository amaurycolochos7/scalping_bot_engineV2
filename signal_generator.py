"""
Generador de mensajes de señales en el formato especificado
"""
from config import Config

class SignalGenerator:
    @staticmethod
    def generate_message(analysis):
        """
        Genera el mensaje formateado para Telegram
        
        Args:
            analysis: dict con los datos del análisis
        """
        symbol = analysis['symbol']
        price = analysis['price']
        signal = analysis['signal']
        analysis_4h = analysis['analysis_4h']
        analysis_1h = analysis['analysis_1h']
        analysis_15m = analysis['analysis_15m']
        
        # Calcular TP y SL
        if signal == 'LONG':
            tp = price * (1 + Config.TP_PERCENTAGE / 100)
            sl = price * (1 - Config.SL_PERCENTAGE / 100)
            signal_icon = '▲'
            signal_text = 'COMPRA / LONG'
        else:  # SHORT
            tp = price * (1 - Config.TP_PERCENTAGE / 100)
            sl = price * (1 + Config.SL_PERCENTAGE / 100)
            signal_icon = '▼'
            signal_text = 'VENTA / SHORT'
        
        # Construir mensaje
        message = f"""CONFIRMADO - {symbol}

Cripto: {symbol}

💰 Precio: ${price:.8f}

━━━ Análisis Multi-Timeframe ━━━
📊 4H: {SignalGenerator._format_trend(analysis_4h['trend'])}
   Velas: {SignalGenerator._format_candles(analysis_4h['candles'])}
📊 1H: {SignalGenerator._format_trend(analysis_1h['trend'])}
   Velas: {SignalGenerator._format_candles(analysis_1h['candles'])}
📊 15m: {signal_icon} {analysis_15m['consecutive_count']} velas {'VERDES' if signal == 'LONG' else 'ROJAS'}
   Velas: {SignalGenerator._format_candles(analysis_15m['candles'])}
   ✅ Confirmado ({Config.MIN_CANDLES_CONFIRMATION}+ velas)

━━━━━━━━━━━━━━━━━━━━
┏━ SEÑAL: {signal_text} {signal_icon}

✅ {signal_text} confirmado
   4H: {signal_icon} | 1H: {signal_icon} | 15m: {analysis_15m['consecutive_count']} velas {'verdes' if signal == 'LONG' else 'rojas'}

━━━ COPIAR ━━━

Moneda: {symbol}
Take Profit: ${tp:.8f}
Stop Loss: ${sl:.8f}"""

        return message
    
    @staticmethod
    def _format_trend(trend):
        """Formatea la tendencia con íconos"""
        if trend == 'BULLISH':
            return '▲ ALCISTA'
        elif trend == 'BEARISH':
            return '▼ BAJISTA'
        else:
            return '━ NEUTRAL'
    
    @staticmethod
    def _format_candles(candles):
        """Formatea las velas con emojis"""
        emoji_map = {
            'green': '🟢',
            'red': '🔴',
            'neutral': '⚪'
        }
        return ''.join([emoji_map.get(c, '⚪') for c in candles])

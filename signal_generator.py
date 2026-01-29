"""
Generador de mensajes de señales - Formato limpio y claro
"""
from config import Config


class SignalGenerator:
    @staticmethod
    def generate_message(analysis):
        """
        Genera el mensaje de señal con formato limpio
        Incluye explicación clara del por qué
        """
        symbol = analysis['symbol']
        price = analysis['price']
        signal = analysis['signal']
        confidence = analysis.get('confidence', 75)
        reasons = analysis.get('reasons', [])
        
        # Calcular TP y SL
        if signal == 'LONG':
            tp = price * (1 + Config.TP_PERCENTAGE / 100)
            sl = price * (1 - Config.SL_PERCENTAGE / 100)
            direction = "📈 LONG (COMPRA)"
            action = "El precio debería SUBIR"
        else:
            tp = price * (1 - Config.TP_PERCENTAGE / 100)
            sl = price * (1 + Config.SL_PERCENTAGE / 100)
            direction = "📉 SHORT (VENTA)"
            action = "El precio debería BAJAR"
        
        # Barra de confianza visual
        filled = int(confidence / 10)
        empty = 10 - filled
        confidence_bar = "█" * filled + "░" * empty
        
        # Construir razones
        reasons_text = ""
        if reasons:
            reasons_text = "\n".join([f"  • {r}" for r in reasons])
        else:
            reasons_text = "  • Análisis multi-timeframe confirmado"
        
        # Formato del precio
        if price >= 1:
            price_fmt = f"${price:,.4f}"
            tp_fmt = f"${tp:,.4f}"
            sl_fmt = f"${sl:,.4f}"
        else:
            price_fmt = f"${price:.8f}"
            tp_fmt = f"${tp:.8f}"
            sl_fmt = f"${sl:.8f}"
        
        message = f"""🚀 <b>SEÑAL {signal}</b> - {symbol}

💰 <b>Precio:</b> {price_fmt}
📊 <b>Confianza:</b> {confidence_bar} {confidence:.0f}%

━━━ {direction} ━━━
{action}

<b>¿Por qué?</b>
{reasons_text}

━━━ NIVELES ━━━
✅ Take Profit: {tp_fmt} (+{Config.TP_PERCENTAGE}%)
🛑 Stop Loss: {sl_fmt} (-{Config.SL_PERCENTAGE}%)

⚠️ Gestiona tu riesgo. No inviertas más de lo que puedes perder."""

        return message
    
    @staticmethod
    def generate_simple_analysis(symbol, data):
        """
        Genera un análisis simple para una moneda específica
        """
        price = data.get('price', 0)
        trend = data.get('trend', 'NEUTRAL')
        rsi = data.get('rsi', 50)
        
        if trend == 'BULLISH':
            trend_icon = "📈"
            trend_text = "Alcista"
        elif trend == 'BEARISH':
            trend_icon = "📉"
            trend_text = "Bajista"
        else:
            trend_icon = "➡️"
            trend_text = "Neutral"
        
        # RSI interpretación
        if rsi < 30:
            rsi_text = "Sobreventa (posible subida)"
        elif rsi > 70:
            rsi_text = "Sobrecompra (posible bajada)"
        else:
            rsi_text = "Normal"
        
        message = f"""📊 <b>Análisis de {symbol}</b>

💰 Precio: ${price:,.4f}
{trend_icon} Tendencia: {trend_text}
📈 RSI: {rsi:.1f} ({rsi_text})

⏳ Esperando confirmación de IA para señal..."""

        return message

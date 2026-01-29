"""
Analizador de IA Unificado
Combina patrones, datos de Futures, y volumen para señales de alta confianza
"""
import pandas as pd
import logging
from binance.client import Client
from config import Config
from pattern_recognition import PatternRecognizer
from futures_data import FuturesAnalyzer
from volume_analyzer import VolumeAnalyzer

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Analizador avanzado que combina múltiples fuentes"""
    
    def __init__(self):
        self.client = Client(Config.BINANCE_API_KEY, Config.BINANCE_SECRET_KEY)
        self.pattern_recognizer = PatternRecognizer()
        self.futures_analyzer = FuturesAnalyzer()
        self.volume_analyzer = VolumeAnalyzer()
        
        # Umbral mínimo de confianza para emitir señal
        self.min_confidence = 70
    
    def get_klines_df(self, symbol: str, interval: str = '1h', limit: int = 100) -> pd.DataFrame:
        """Obtiene datos de velas como DataFrame"""
        try:
            klines = self.client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            if not klines:
                return None
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            return df
            
        except Exception as e:
            logger.error(f"Error obteniendo datos: {e}")
            return None
    
    def analyze_symbol(self, symbol: str) -> dict:
        """
        Análisis completo de un símbolo usando IA
        
        Returns:
            dict con señal, confianza, y razones detalladas
        """
        logger.info(f"🔍 Analizando {symbol}...")
        
        # Obtener precio actual
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
        except:
            return None
        
        # 1. Obtener datos de velas
        df = self.get_klines_df(symbol, '1h', 100)
        if df is None:
            return None
        
        # 2. Análisis de patrones
        patterns = self.pattern_recognizer.find_all_patterns(df)
        pattern_signal = self.pattern_recognizer.get_pattern_signal(patterns)
        
        # 3. Datos de Futures
        futures_analysis = self.futures_analyzer.get_full_futures_analysis(symbol)
        
        # 4. Análisis de volumen
        volume_analysis = self.volume_analyzer.get_volume_analysis(symbol)
        volume_spike = self.volume_analyzer.detect_volume_spike(symbol)
        
        # === CONSOLIDAR SEÑALES ===
        bullish_score = 0
        bearish_score = 0
        all_reasons = []
        
        # Patrones
        if pattern_signal:
            if pattern_signal['signal'] == 'LONG':
                bullish_score += pattern_signal['confidence']
            elif pattern_signal['signal'] == 'SHORT':
                bearish_score += pattern_signal['confidence']
            all_reasons.extend(pattern_signal.get('reasons', []))
        
        # Futures data
        if futures_analysis and futures_analysis['signal']:
            if futures_analysis['signal'] == 'LONG':
                bullish_score += futures_analysis['confidence']
            elif futures_analysis['signal'] == 'SHORT':
                bearish_score += futures_analysis['confidence']
            all_reasons.extend(futures_analysis.get('reasons', []))
        
        # Volumen
        if volume_spike and volume_spike.get('detected'):
            if volume_spike['direction'] == 'BULLISH':
                bullish_score += volume_spike['confidence']
                all_reasons.append(f"📊 {volume_spike['description']}")
            elif volume_spike['direction'] == 'BEARISH':
                bearish_score += volume_spike['confidence']
                all_reasons.append(f"📊 {volume_spike['description']}")
        elif volume_analysis and volume_analysis['signal'] in ['STRONG_MOVE', 'MOVE']:
            all_reasons.append(f"📊 {volume_analysis['interpretation']}")
        
        # === DETERMINAR SEÑAL FINAL ===
        total_score = max(bullish_score, bearish_score)
        
        # Normalizar confianza (máximo 95%)
        if total_score > 0:
            # Promedio ponderado para no inflar demasiado
            confidence = min(95, int(total_score / 2) + 30)
        else:
            confidence = 0
        
        if bullish_score > bearish_score and confidence >= self.min_confidence:
            signal = 'LONG'
        elif bearish_score > bullish_score and confidence >= self.min_confidence:
            signal = 'SHORT'
        else:
            signal = None
        
        # === CONSTRUIR RESULTADO ===
        result = {
            'symbol': symbol,
            'price': current_price,
            'signal': signal,
            'confidence': confidence,
            'reasons': all_reasons[:5],  # Máximo 5 razones
            
            # Datos detallados
            'patterns': patterns,
            'futures': futures_analysis,
            'volume': volume_analysis,
            
            # Scores individuales
            'bullish_score': bullish_score,
            'bearish_score': bearish_score,
        }
        
        if signal:
            # Calcular TP/SL
            if signal == 'LONG':
                result['tp'] = current_price * (1 + Config.TP_PERCENTAGE / 100)
                result['sl'] = current_price * (1 - Config.SL_PERCENTAGE / 100)
            else:
                result['tp'] = current_price * (1 - Config.TP_PERCENTAGE / 100)
                result['sl'] = current_price * (1 + Config.SL_PERCENTAGE / 100)
            
            logger.info(f"✅ {symbol}: {signal} con {confidence}% confianza")
        else:
            logger.info(f"⏳ {symbol}: Sin señal clara (confianza {confidence}%)")
        
        return result
    
    def scan_all_pairs(self, limit: int = None) -> list:
        """
        Escanea todos los pares de Futures buscando señales
        
        Returns:
            Lista de señales encontradas
        """
        logger.info("🔄 Escaneando todos los pares de Futures...")
        
        # Obtener pares
        try:
            exchange_info = self.client.futures_exchange_info()
            pairs = [
                s['symbol'] for s in exchange_info['symbols']
                if s['symbol'].endswith('USDT') 
                and s['status'] == 'TRADING'
                and s['contractType'] == 'PERPETUAL'
            ]
        except Exception as e:
            logger.error(f"Error obteniendo pares: {e}")
            return []
        
        # Filtrar por volumen mínimo
        try:
            tickers = self.client.futures_ticker()
            high_volume_pairs = [
                t['symbol'] for t in tickers 
                if t['symbol'] in pairs and float(t['quoteVolume']) >= Config.MIN_VOLUME_24H
            ]
        except:
            high_volume_pairs = pairs
        
        if limit:
            high_volume_pairs = high_volume_pairs[:limit]
        
        logger.info(f"📊 Analizando {len(high_volume_pairs)} pares con alto volumen...")
        
        signals = []
        for symbol in high_volume_pairs:
            try:
                analysis = self.analyze_symbol(symbol)
                if analysis and analysis['signal']:
                    signals.append(analysis)
            except Exception as e:
                logger.error(f"Error analizando {symbol}: {e}")
                continue
        
        # Ordenar por confianza
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        logger.info(f"🎯 Encontradas {len(signals)} señales")
        return signals


if __name__ == "__main__":
    # Test rápido
    analyzer = AIAnalyzer()
    
    # Analizar BTC
    result = analyzer.analyze_symbol('BTCUSDT')
    
    if result:
        print(f"\n{'='*50}")
        print(f"Símbolo: {result['symbol']}")
        print(f"Precio: ${result['price']:,.2f}")
        print(f"Señal: {result['signal'] or 'NINGUNA'}")
        print(f"Confianza: {result['confidence']}%")
        print(f"\nRazones:")
        for r in result['reasons']:
            print(f"  {r}")
        print(f"{'='*50}")

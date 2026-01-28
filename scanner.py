"""
Escáner principal que analiza todas las criptomonedas en tiempo real
"""
import time
import logging
from binance_client import BinanceClient
from analyzer import MultiTimeframeAnalyzer
from signal_generator import SignalGenerator
from telegram_notifier import TelegramNotifier
from signal_tracker import SignalTracker
from config import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CryptoScanner:
    def __init__(self):
        """Inicializa el escáner"""
        logger.info("🚀 Iniciando Scalping Engine V2...")
        
        # Validar configuración
        Config.validate()
        
        # Inicializar componentes
        self.binance = BinanceClient()
        self.analyzer = MultiTimeframeAnalyzer(self.binance)
        self.notifier = TelegramNotifier()
        self.tracker = SignalTracker()
        
        # Obtener lista de pares a monitorear
        self.pairs = []
        
        logger.info("✅ Escáner inicializado correctamente")
    
    def start(self):
        """Inicia el escaneo continuo"""
        logger.info("🔍 Iniciando escaneo de mercado...")
        
        # Obtener pares
        self.pairs = self.binance.get_all_usdt_pairs()
        logger.info(f"📊 Monitoreando {len(self.pairs)} pares")
        
        # Mostrar estadísticas
        stats = self.tracker.get_stats()
        logger.info(f"📈 Señales enviadas: {stats['total']} (LONG: {stats['longs']}, SHORT: {stats['shorts']})")
        
        # Loop principal
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"🔄 Escaneo #{scan_count} - {len(self.pairs)} pares")
                logger.info(f"{'='*60}")
                
                signals_found = 0
                
                # Analizar cada par
                for i, symbol in enumerate(self.pairs, 1):
                    try:
                        # Mostrar progreso cada 50 pares
                        if i % 50 == 0:
                            logger.info(f"⏳ Progreso: {i}/{len(self.pairs)} pares analizados...")
                        
                        # Verificar si podemos enviar señal para este símbolo
                        if not self.tracker.can_send_signal(symbol):
                            continue
                        
                        # Analizar el símbolo
                        analysis = self.analyzer.analyze_symbol(symbol)
                        
                        if not analysis:
                            continue
                        
                        # Si hay señal confirmada
                        if analysis['confirmed'] and analysis['signal']:
                            signals_found += 1
                            logger.info(f"🎯 SEÑAL ENCONTRADA: {symbol} {analysis['signal']}")
                            
                            # Generar mensaje
                            message = SignalGenerator.generate_message(analysis)
                            
                            # Enviar notificación
                            self.notifier.send_signal_sync(message)
                            
                            # Registrar señal
                            self.tracker.register_signal(
                                symbol,
                                analysis['signal'],
                                analysis['price']
                            )
                        
                        # Pequeña pausa para no saturar la API
                        time.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"❌ Error analizando {symbol}: {e}")
                        continue
                
                logger.info(f"\n✅ Escaneo #{scan_count} completado")
                logger.info(f"🎯 Señales encontradas: {signals_found}")
                logger.info(f"⏰ Próximo escaneo en {Config.SCAN_INTERVAL_SECONDS}s...\n")
                
                # Esperar antes del próximo escaneo
                time.sleep(Config.SCAN_INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                logger.info("\n\n⛔ Deteniendo escáner...")
                break
            except Exception as e:
                logger.error(f"❌ Error en el loop principal: {e}")
                logger.info("⏰ Reintentando en 10 segundos...")
                time.sleep(10)
        
        logger.info("👋 Escáner detenido")
    
    def scan_single(self, symbol):
        """
        Escanea un solo símbolo (útil para testing)
        
        Args:
            symbol: Símbolo a analizar (ej: BTCUSDT)
        """
        logger.info(f"🔍 Analizando {symbol}...")
        
        analysis = self.analyzer.analyze_symbol(symbol)
        
        if not analysis:
            logger.error(f"❌ No se pudo analizar {symbol}")
            return
        
        # Mostrar resultado
        if analysis['confirmed'] and analysis['signal']:
            message = SignalGenerator.generate_message(analysis)
            print("\n" + "="*60)
            print("🎯 SEÑAL ENCONTRADA:")
            print("="*60)
            print(message)
            print("="*60 + "\n")
        else:
            logger.info(f"ℹ️ No hay señal confirmada para {symbol}")
            logger.info(f"   4H: {analysis['analysis_4h']['trend']}")
            logger.info(f"   1H: {analysis['analysis_1h']['trend']}")
            logger.info(f"   15m: {analysis['analysis_15m']['consecutive_count']} velas consecutivas")

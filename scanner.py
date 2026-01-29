"""
Escáner principal con IA avanzada
Analiza todas las criptomonedas de Futures en tiempo real
"""
import time
import logging
from ai_analyzer import AIAnalyzer
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
        """Inicializa el escáner con IA"""
        logger.info("🚀 Iniciando Scalping Engine V2 con IA...")
        
        # Validar configuración
        Config.validate()
        
        # Inicializar componentes
        self.analyzer = AIAnalyzer()
        self.notifier = TelegramNotifier()
        self.tracker = SignalTracker()
        
        logger.info("✅ Escáner con IA inicializado correctamente")
    
    def start(self):
        """Inicia el escaneo continuo con IA"""
        logger.info("🔍 Iniciando escaneo con IA...")
        
        # Mostrar estadísticas
        stats = self.tracker.get_stats()
        logger.info(f"📈 Señales enviadas: {stats['total']} (LONG: {stats['longs']}, SHORT: {stats['shorts']})")
        
        # Loop principal
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"🔄 Escaneo #{scan_count} con IA")
                logger.info(f"{'='*60}")
                
                # Escanear todos los pares con IA
                signals = self.analyzer.scan_all_pairs()
                
                signals_sent = 0
                for analysis in signals:
                    symbol = analysis['symbol']
                    
                    # Verificar cooldown
                    if not self.tracker.can_send_signal(symbol):
                        continue
                    
                    # Solo señales con buena confianza
                    if analysis['confidence'] >= 70:
                        logger.info(f"🎯 SEÑAL: {symbol} {analysis['signal']} ({analysis['confidence']}%)")
                        
                        # Generar mensaje
                        message = SignalGenerator.generate_message(analysis)
                        
                        # Enviar
                        self.notifier.send_signal_sync(message)
                        
                        # Registrar
                        self.tracker.register_signal(
                            symbol,
                            analysis['signal'],
                            analysis['price']
                        )
                        
                        signals_sent += 1
                        
                        # Pausa entre señales
                        time.sleep(1)
                
                logger.info(f"\n✅ Escaneo #{scan_count} completado")
                logger.info(f"🎯 Señales enviadas: {signals_sent}")
                logger.info(f"⏰ Próximo escaneo en {Config.SCAN_INTERVAL_SECONDS}s...\n")
                
                time.sleep(Config.SCAN_INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                logger.info("\n\n⛔ Deteniendo escáner...")
                break
            except Exception as e:
                logger.error(f"❌ Error en el loop: {e}")
                logger.info("⏰ Reintentando en 10 segundos...")
                time.sleep(10)
        
        logger.info("👋 Escáner detenido")
    
    def scan_single(self, symbol: str):
        """Analiza un solo símbolo"""
        logger.info(f"🔍 Analizando {symbol} con IA...")
        
        analysis = self.analyzer.analyze_symbol(symbol)
        
        if not analysis:
            logger.error(f"❌ No se pudo analizar {symbol}")
            return None
        
        # Mostrar resultado
        print(f"\n{'='*60}")
        print(f"📊 ANÁLISIS DE {symbol}")
        print(f"{'='*60}")
        print(f"💰 Precio: ${analysis['price']:,.4f}")
        print(f"📈 Señal: {analysis['signal'] or 'NINGUNA'}")
        print(f"📊 Confianza: {analysis['confidence']}%")
        
        if analysis['reasons']:
            print(f"\n¿Por qué?")
            for r in analysis['reasons']:
                print(f"  {r}")
        
        print(f"{'='*60}\n")
        
        return analysis

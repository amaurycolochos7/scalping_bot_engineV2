"""
Sistema de tracking de señales para evitar duplicados
"""
import json
import os
from datetime import datetime, timedelta
from config import Config
import logging

logger = logging.getLogger(__name__)

class SignalTracker:
    def __init__(self, db_file='signals_history.json'):
        """Inicializa el tracker de señales"""
        self.db_file = db_file
        self.signals = self._load_signals()
    
    def _load_signals(self):
        """Carga el historial de señales desde disco"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando señales: {e}")
                return {}
        return {}
    
    def _save_signals(self):
        """Guarda el historial de señales a disco"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.signals, f, indent=2)
        except Exception as e:
            logger.error(f"Error guardando señales: {e}")
    
    def can_send_signal(self, symbol):
        """
        Verifica si se puede enviar una señal para este símbolo
        (no se ha enviado una en las últimas X horas)
        """
        if symbol not in self.signals:
            return True
        
        last_signal_time = datetime.fromisoformat(self.signals[symbol]['timestamp'])
        cooldown = timedelta(hours=Config.SIGNAL_COOLDOWN_HOURS)
        
        if datetime.now() - last_signal_time > cooldown:
            return True
        
        return False
    
    def register_signal(self, symbol, signal_type, price):
        """Registra una señal enviada"""
        self.signals[symbol] = {
            'timestamp': datetime.now().isoformat(),
            'signal': signal_type,
            'price': price
        }
        self._save_signals()
        logger.info(f"📝 Señal registrada: {symbol} {signal_type} @ ${price}")
    
    def get_stats(self):
        """Obtiene estadísticas de señales enviadas"""
        total = len(self.signals)
        longs = sum(1 for s in self.signals.values() if s['signal'] == 'LONG')
        shorts = sum(1 for s in self.signals.values() if s['signal'] == 'SHORT')
        
        return {
            'total': total,
            'longs': longs,
            'shorts': shorts
        }

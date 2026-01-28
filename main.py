"""
Scalping Engine V2 - Punto de Entrada Principal
"""
import sys
from scanner import CryptoScanner

def main():
    """Función principal"""
    print("""
    ╔══════════════════════════════════════════╗
    ║     SCALPING ENGINE V2                   ║
    ║     Análisis Multi-Timeframe             ║
    ║     600+ Criptomonedas en Tiempo Real    ║
    ╚══════════════════════════════════════════╝
    """)
    
    scanner = CryptoScanner()
    scanner.start()

if __name__ == "__main__":
    main()

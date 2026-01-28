"""
Script de prueba para analizar una sola criptomoneda
"""
import sys
from scanner import CryptoScanner

def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python test_single.py BTCUSDT")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    
    if not symbol.endswith('USDT'):
        symbol += 'USDT'
    
    print(f"\n🔍 Testeando análisis de {symbol}...\n")
    
    scanner = CryptoScanner()
    scanner.scan_single(symbol)

if __name__ == "__main__":
    main()

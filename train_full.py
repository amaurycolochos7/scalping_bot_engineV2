#!/usr/bin/env python
"""
Script completo de entrenamiento de IA
1. Descarga 6 meses de datos de TODAS las criptos de Futures
2. Calcula features técnicos
3. Entrena modelo XGBoost
"""
import os
import sys

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   ENTRENAMIENTO COMPLETO DE IA - BINANCE FUTURES         ║
    ║   Este proceso puede tomar 30-60 minutos                 ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Paso 1: Descargar datos
    print("\n" + "="*60)
    print("📥 PASO 1: Descargando datos históricos de Futures (6 meses)")
    print("="*60)
    
    from ai_data_downloader import FuturesDataDownloader
    downloader = FuturesDataDownloader()
    success = downloader.download_all_futures_data(months=6)
    
    if not success or success == 0:
        print("❌ Error en la descarga de datos")
        return
    
    # Paso 2: Calcular features
    print("\n" + "="*60)
    print("🔢 PASO 2: Calculando features técnicos")
    print("="*60)
    
    from ai_feature_calculator import FeatureCalculator
    calculator = FeatureCalculator()
    calculator.calculate_all_features()
    
    # Paso 3: Entrenar modelo
    print("\n" + "="*60)
    print("🤖 PASO 3: Entrenando modelo XGBoost")
    print("="*60)
    
    from ai_trainer import AITrainer
    trainer = AITrainer()
    model = trainer.run_full_training()
    
    if model:
        print("\n" + "="*60)
        print("🎉 ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        print("="*60)
        print("📁 Modelo guardado en: models/xgboost_model.json")
        print("\n💡 Reinicia el bot para usar el nuevo modelo:")
        print("   python main.py")
        print("="*60)
    else:
        print("❌ Error en el entrenamiento")


if __name__ == "__main__":
    main()

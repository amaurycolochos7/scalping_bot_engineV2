"""
Entrenamiento del modelo XGBoost para validación de señales
"""
import pandas as pd
import numpy as np
from glob import glob
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AITrainer:
    def __init__(self, features_dir='data/features', model_dir='models'):
        """Inicializa el entrenador de IA"""
        self.features_dir = features_dir
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
    def prepare_dataset(self):
        """
        Prepara el dataset combinando todos los archivos de features
        y etiquetando señales como Success/Fail
        """
        logger.info("📊 Preparando dataset...")
        
        csv_files = glob(f"{self.features_dir}/*.csv")
        logger.info(f"   Archivos encontrados: {len(csv_files)}")
        
        all_data = []
        
        for filepath in csv_files:
            try:
                df = pd.read_csv(filepath)
                df = self.label_signals(df)
                
                if df is not None and len(df) > 0:
                    all_data.append(df)
                    
            except Exception as e:
                logger.error(f"   Error procesando {filepath}: {e}")
                continue
        
        if not all_data:
            logger.error("❌ No se pudo cargar ningún dataset")
            return None
        
        # Combinar todos los DataFrames
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"   ✅ Dataset combinado: {len(combined_df):,} filas")
        
        return combined_df
    
    def label_signals(self, df):
        """
        Etiqueta cada fila como SUCCESS (1) o FAIL (0)
        basado en si alcanzó TP antes que SL
        
        Lookforward: Mira las próximas N velas para ver qué pasó
        """
        if df is None or len(df) < 50:
            return None
        
        df = df.copy()
        df['label'] = 0  # Default: FAIL
        
        # Parámetros de TP/SL
        tp_pct = Config.TP_PERCENTAGE / 100
        sl_pct = Config.SL_PERCENTAGE / 100
        
        lookforward = 20  # Mirar hasta 20 velas adelante
        
        for i in range(len(df) - lookforward):
            entry_price = df.iloc[i]['close']
            
            # Calcular precios de TP y SL (asumimos LONG por simplicidad)
            tp_price = entry_price * (1 + tp_pct)
            sl_price = entry_price * (1 - sl_pct)
            
            # Mirar las próximas velas
            future_prices_high = df.iloc[i+1:i+1+lookforward]['high'].values
            future_prices_low = df.iloc[i+1:i+1+lookforward]['low'].values
            
            # Verificar si alcanzó TP o SL primero
            for high, low in zip(future_prices_high, future_prices_low):
                if high >= tp_price:
                    df.iloc[i, df.columns.get_loc('label')] = 1  # SUCCESS
                    break
                if low <= sl_price:
                    df.iloc[i, df.columns.get_loc('label')] = 0  # FAIL
                    break
        
        # Eliminar últimas filas sin label
        df = df.iloc[:-lookforward]
        
        return df
    
    def train_model(self, df):
        """Entrena el modelo XGBoost"""
        logger.info("🤖 Preparando features para entrenamiento...")
        
        # Seleccionar features relevantes
        feature_columns = [
            'rsi_14', 'rsi_7',
            'macd', 'macd_diff',
            'dist_ema_50', 'dist_ema_200',
            'bb_width', 'bb_position',
            'atr', 'volume_ratio',
            'price_change_1', 'price_change_3',
            'green_streak', 'red_streak'
        ]
        
        # Verificar que existan las columnas
        available_features = [f for f in feature_columns if f in df.columns]
        logger.info(f"   Features disponibles: {len(available_features)}")
        
        if len(available_features) < 5:
            logger.error("❌ No hay suficientes features")
            return None
        
        # Preparar X e y
        X = df[available_features].values
        y = df['label'].values
        
        logger.info(f"   Total samples: {len(X):,}")
        logger.info(f"   SUCCESS (1): {sum(y):,} ({sum(y)/len(y)*100:.1f}%)")
        logger.info(f"   FAIL (0): {len(y)-sum(y):,} ({(len(y)-sum(y))/len(y)*100:.1f}%)")
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"\n🎯 Entrenando XGBoost...")
        logger.info(f"   Train set: {len(X_train):,}")
        logger.info(f"   Test set: {len(X_test):,}")
        
        # Entrenar XGBoost
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=50
        )
        
        # Evaluar
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 RESULTADOS DEL ENTRENAMIENTO")
        logger.info(f"{'='*60}")
        logger.info(f"Accuracy: {accuracy*100:.2f}%\n")
        logger.info("Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['FAIL', 'SUCCESS']))
        
        logger.info("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        # Guardar modelo
        model_path = f"{self.model_dir}/xgboost_model.json"
        model.save_model(model_path)
        logger.info(f"\n✅ Modelo guardado en: {model_path}")
        
        # Guardar lista de features
        features_path = f"{self.model_dir}/feature_names.txt"
        with open(features_path, 'w') as f:
            f.write('\n'.join(available_features))
        logger.info(f"✅ Features guardadas en: {features_path}")
        
        return model
    
    def run_full_training(self):
        """Ejecuta el proceso completo de entrenamiento"""
        print("""
    ╔══════════════════════════════════════════╗
    ║   ENTRENAMIENTO DE IA - XGBoost          ║
    ║   Validador de Señales de Trading        ║
    ╚══════════════════════════════════════════╝
        """)
        
        # 1. Preparar dataset
        df = self.prepare_dataset()
        if df is None:
            return None
        
        # 2. Entrenar modelo
        model = self.train_model(df)
        
        if model:
            logger.info("\n" + "="*60)
            logger.info("🎉 ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
            logger.info("="*60)
            logger.info(f"📁 Modelo guardado en: {self.model_dir}/")
            logger.info("\n💡 Próximos pasos:")
            logger.info("   1. Integrar modelo en scanner.py")
            logger.info("   2. Ejecutar bot con validación de IA")
            logger.info("="*60)
        
        return model

if __name__ == "__main__":
    trainer = AITrainer()
    trainer.run_full_training()

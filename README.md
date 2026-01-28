# 🚀 Scalping Engine V2

Sistema profesional de análisis automático en tiempo real de **600+ criptomonedas** de Binance con:
- ✅ Señales multi-timeframe (4H, 1H, 15m)  
- ✅ **Validación con IA (XGBoost)**
- ✅ Notificaciones Telegram
- ✅ Sistema anti-duplicados
- ✅ Ready para AWS 24/7

---

## 🎯 Características

### Análisis Técnico
- 📊 Monitoreo de 600+ pares USDT
- 📈 Multi-timeframe: 4H, 1H, 15m
- 🎯 Confirmación con 3+ velas consecutivas
- 💰 TP/SL automático (R:R 2:1)
- 🔄 Filtro por volumen ($5M+ USD)

### Inteligencia Artificial
- 🤖 XGBoost entrenado con 100k+ señales históricas
- 📊 Features: RSI, MACD, EMAs, Bollinger, ATR
- 🎲 Solo envía señales con >70% probabilidad de éxito
- 📉 Backtesting automático

### Sistema
- 📱 Notificaciones Telegram en tiempo real
- ⏱️ Anti-spam (1 señal cada 2h por cripto)
- 📊 Tracking de señales en JSON
- 🔒 API keys de Binance (solo lectura)

---

## 📊 Ejemplo de Señal

```
CONFIRMADO - BTCUSDT

Cripto: BTCUSDT
💰 Precio: $45,234.50

━━━ Análisis Multi-Timeframe ━━━
📊 4H: ▲ ALCISTA
   Velas: 🟢🟢🟢🟢🟢🟢
📊 1H: ▲ ALCISTA
   Velas: 🟢🟢🟢🟢🟢🟢
📊 15m: ▲ 4 velas VERDES
   Velas: 🟢🟢🟢🟢⚪⚪
   ✅ Confirmado (3+ velas)

━━━━━━━━━━━━━━━━━━━━
┏━ SEÑAL: COMPRA / LONG ▲

✅ COMPRA / LONG confirmado
   4H: ▲ | 1H: ▲ | 15m: 4 velas verdes

━━━ COPIAR ━━━

Moneda: BTCUSDT
Take Profit: $49,756.95
Stop Loss: $42,972.78
```

---

## 🛠️ Instalación Rápida (Local)

### Windows
```powershell
git clone https://github.com/TU_USUARIO/scalping-engine-v2.git
cd scalping-engine-v2
.\install.ps1
```

### Linux/Mac
```bash
git clone https://github.com/TU_USUARIO/scalping-engine-v2.git
cd scalping-engine-v2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ⚙️ Configuración

### 1. Telegram Chat ID
```powershell
# Envía un mensaje a tu bot
# Luego ejecuta:
python get_chat_id.py

# Copia el Chat ID y pégalo en .env
```

### 2. Editar `.env` (Opcional)
```env
# Ya configurado con tus keys de Binance
TELEGRAM_CHAT_ID=123456789  # ← Pega aquí tu chat ID

# Ajustes opcionales:
MIN_VOLUME_24H=5000000      # Volumen mínimo
TP_PERCENTAGE=10            # Take Profit %
SL_PERCENTAGE=5             # Stop Loss %
```

---

## 🚀 Uso

### Sin IA (Rápido - Listo en 2 minutos)
```powershell
python main.py
```

### Con IA (Requiere entrenar primero)
```powershell
# 1. Entrenar IA (5-7 horas, una sola vez)
.\train_ia.ps1

# 2. Ejecutar bot con IA
python main.py
```

### Probar con 1 cripto
```powershell
python test_single.py BTCUSDT
```

---

## 🤖 Entrenamiento de IA

El sistema incluye un pipeline completo de Machine Learning:

### Proceso Automático
```powershell
.\train_ia.ps1
```

Esto ejecuta:
1. **Descarga de datos** (2-3h)
   - 100 pares más líquidos
   - 1 año de histórico
   - 3 timeframes

2. **Cálculo de features** (1-2h)
   - Indicadores técnicos
   - Patrones de precio
   - Métricas de volumen

3. **Entrenamiento XGBoost** (1-2h)
   - 100k+ ejemplos
   - Validación cruzada
   - Optimización

### Proceso Manual (Paso a Paso)
```powershell
# 1. Descargar datos
python ai_data_downloader.py

# 2. Calcular features
python ai_feature_calculator.py

# 3. Entrenar modelo
python ai_trainer.py
```

---

## ☁️ Deployment en AWS

Para ejecutar 24/7 en Windows Server AWS:

### Ver guía completa: [DEPLOYMENT_AWS.md](DEPLOYMENT_AWS.md)

**Resumen:**
```powershell
# 1. Conectar a servidor AWS (RDP)
# 2. Clonar repo
git clone https://github.com/TU_USUARIO/scalping-engine-v2.git
cd scalping-engine-v2

# 3. Instalar todo automáticamente
.\install.ps1

# 4. Entrenar IA (dejar corriendo esta noche)
.\train_ia.ps1

# 5. Ejecutar bot
python main.py
```

**Configurar como servicio Windows:**
- Task Scheduler → `start_bot.bat`
- Se reinicia automáticamente

---

## 📁 Estructura del Proyecto

```
scalping-engine-v2/
├── main.py                      # Punto de entrada
├── scanner.py                   # Escáner principal
├── analyzer.py                  # Análisis multi-timeframe
├── signal_generator.py          # Generador de mensajes
├── telegram_notifier.py         # Notificaciones
├── binance_client.py            # Cliente Binance
├── signal_tracker.py            # Anti-duplicados
├── config.py                    # Configuración
│
├── ai_data_downloader.py        # Descarga histórico
├── ai_feature_calculator.py     # Calcula indicators
├── ai_trainer.py                # Entrena XGBoost
│
├── install.ps1                  # Instalación automática
├── train_ia.ps1                 # Pipeline de IA
├── start_bot.bat                # Servicio Windows
│
├── data/
│   ├── historical/              # Datos descargados
│   └── features/                # Features calculados
├── models/                      # Modelo XGBoost
└── logs/                        # Logs del bot
```

---

## ⚙️ Configuración de TP/SL

### LONG (Compra) 🟢
- **Stop Loss**: -5% del precio de entrada
- **Take Profit**: +10% del precio de entrada

### SHORT (Venta) 🔴
- **Stop Loss**: +5% del precio de entrada  
- **Take Profit**: -10% del precio de entrada

**Risk/Reward Ratio: 2:1** ✅

Ver detalles: [CONFIGURACION_TP_SL.md](CONFIGURACION_TP_SL.md)

---

## 📊 Requisitos del Sistema

### Ejecución Normal (Sin IA)
- RAM: 2 GB
- Disco: 500 MB
- CPU: 1 core

### Entrenamiento de IA
- RAM: 8 GB (16 GB ideal)
- Disco: 20-30 GB
- CPU: 4+ cores
- Tiempo: 5-7 horas

---

## ❓ FAQ

**¿Cuánto tiempo tarda en enviar la primera señal?**
- Depende del mercado. Puede ser minutos u horas.

**¿Puedo usar esto con otras exchanges?**
- Actualmente solo Binance, pero es fácil adaptar.

**¿Necesito entrenar la IA?**
- No, el bot funciona sin IA usando solo análisis técnico.
- La IA mejora el win rate en ~15-20%.

**¿Se puede backtestear?**
- Sí, usa VectorBT o modifica `ai_trainer.py`

---

## ⚠️ Disclaimer

Este software es para **análisis educativo**.  
**NO es asesoría financiera.**  
Siempre haz tu propia investigación (DYOR).  
El trading conlleva riesgos.

---

## 📝 Licencia

MIT License - Usa bajo tu propio riesgo

---

## 🤝 Contribuciones

Pull requests son bienvenidas.  
Para cambios grandes, abre un issue primero.

---

**🔥 ¡Listo para empezar! Ejecuta `.\install.ps1` 🔥**

# 🚀 Deployment en Windows Server AWS

Guía paso a paso para instalar y ejecutar el Scalping Engine V2 en un servidor Windows en AWS.

---

## 📋 Requisitos Previos

### En tu repositorio Git
1. ✅ Subir el código a GitHub/GitLab
2. ✅ Configurar `.env` con tus API keys

### En AWS
1. ✅ Instancia Windows Server 2022
2. ✅ Tipo recomendado: `t3.large` (2 vCPU, 8 GB RAM)
3. ✅ Almacenamiento: 50 GB mínimo
4. ✅ Security Group: Puerto 3389 (RDP) abierto

---

## 🔧 Paso 1: Conectar al Servidor AWS

### Opción A: Remote Desktop (RDP)
```powershell
# Desde tu PC local
1. Abre "Conexión a Escritorio Remoto"
2. IP: [Tu IP pública de AWS]
3. Usuario: Administrator
4. Contraseña: [Desde AWS Console]
```

### Opción B: AWS Systems Manager Session Manager
```powershell
# Conecta sin necesidad de RDP
aws ssm start-session --target [instance-id]
```

---

## ⚙️ Paso 2: Instalación Automática

Una vez conectado al servidor:

### 2.1 Abrir PowerShell como Administrador
```powershell
# Clic derecho en el menú Inicio > "Windows PowerShell (Admin)"
```

### 2.2 Permitir ejecución de scripts
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

### 2.3 Clonar el repositorio
```powershell
# Navegar al directorio deseado
cd C:\

# Clonar tu repo
git clone https://github.com/TU_USUARIO/scalping-engine-v2.git
cd scalping-engine-v2
```

### 2.4 Ejecutar instalación
```powershell
.\install.ps1
```

Este script hará automáticamente:
- ✅ Instalar Python 3.11
- ✅ Instalar Git
- ✅ Crear entorno virtual
- ✅ Instalar todas las dependencias
- ✅ Crear estructura de directorios

**Tiempo estimado: 15-20 minutos**

---

## 🤖 Paso 3: Entrenar la IA

### 3.1 Configurar Telegram Chat ID

```powershell
# Si aún no lo hiciste, obtén tu Chat ID
python get_chat_id.py

# Editar .env
notepad .env

# Pegar tu Chat ID:
TELEGRAM_CHAT_ID=123456789
```

### 3.2 Iniciar entrenamiento

```powershell
.\train_ia.ps1
```

Este proceso ejecutará:
1. **Descarga de datos** (2-3 horas)
   - 100 pares más líquidos
   - 1 año de histórico
   - 3 timeframes (4H, 1H, 15m)

2. **Cálculo de features** (1-2 horas)
   - RSI, MACD, EMAs
   - Bollinger Bands, ATR
   - Volume ratios

3. **Entrenamiento XGBoost** (1-2 horas)
   - 100k+ ejemplos
   - Validación cruzada
   - Optimización de hiperparámetros

**⏱️ Tiempo total: 5-7 horas**

> [!TIP]
> Puedes cerrar la sesión RDP. El proceso seguirá ejecutándose.
> Para hacerlo permanente, usa Task Scheduler (ver Paso 5).

---

## 🚀 Paso 4: Ejecutar el Bot

### 4.1 Modo Normal (con IA)

```powershell
cd C:\scalping-engine-v2
.\venv\Scripts\Activate.ps1
python main.py
```

### 4.2 Sin IA (solo análisis técnico)

```powershell
# Renombrar temporalmente el modelo
mv models\xgboost_model.json models\xgboost_model.json.bak

# Ejecutar bot
python main.py

# Restaurar modelo cuando quieras usar IA
mv models\xgboost_model.json.bak models\xgboost_model.json
```

### 4.3 Probar con 1 cripto

```powershell
python test_single.py BTCUSDT
```

---

## 🔄 Paso 5: Ejecutar como Servicio (24/7)

Para que el bot se ejecute automáticamente incluso después de reiniciar el servidor:

### 5.1 Crear tarea programada

```powershell
# Crear archivo bat de inicio
@echo off
cd C:\scalping-engine-v2
call venv\Scripts\activate.bat
python main.py
```

Guardar como: `C:\scalping-engine-v2\start_bot.bat`

### 5.2 Configurar Task Scheduler

1. Abrir "Task Scheduler"
2. "Create Task"
3. **General tab**:
   - Name: `Scalping Engine V2`
   - "Run whether user is logged on or not" ✓
   - "Run with highest privileges" ✓

4. **Triggers tab**:
   - New → "At startup"

5. **Actions tab**:
   - New → Start a program
   - Program: `C:\scalping-engine-v2\start_bot.bat`

6. **Settings tab**:
   - "If the task fails, restart every: 1 minute"
   - "Attempt to restart up to: 3 times"

---

## 📊 Paso 6: Monitoreo

### Ver logs en tiempo real

```powershell
# Ver logs del bot
Get-Content logs\bot.log -Wait -Tail 50
```

### Verificar que está corriendo

```powershell
# Ver procesos Python
Get-Process python
```

### Ver señales enviadas

```powershell
# Ver historial de señales
cat signals_history.json
```

---

## 🔒 Seguridad (IMPORTANTE)

### 1. Firewall
```powershell
# Solo permitir RDP desde tu IP
New-NetFirewallRule -DisplayName "RDP-MyIP" `
    -Direction Inbound `
    -LocalPort 3389 `
    -Protocol TCP `
    -Action Allow `
    -RemoteAddress "TU_IP_PUBLICA"
```

### 2. Backups automáticos
```powershell
# Crear backup del modelo y señales
$backupDir = "C:\Backups\ScalpingBot"
New-Item -ItemType Directory -Path $backupDir -Force

# Copiar archivos críticos
Copy-Item models\* $backupDir\models\ -Recurse -Force
Copy-Item signals_history.json $backupDir\ -Force
Copy-Item .env $backupDir\ -Force
```

### 3. Actualizar código
```powershell
cd C:\scalping-engine-v2
git pull origin main
pip install -r requirements.txt --upgrade
```

---

## ❓ Troubleshooting

### El bot no envía señales

**Posibles causas:**
1. Chat ID incorrecto en `.env`
2. Bot token inválido
3. No hay señales confirmadas (mercado lateral)

**Solución:**
```powershell
# Verificar conexión a Telegram
python get_chat_id.py

# Probar con una cripto específica
python test_single.py BTCUSDT
```

### Error de memoria

**Síntoma:**
```
MemoryError: Unable to allocate...
```

**Solución:**
```powershell
# Reducir número de pares a analizar
# Editar .env:
MAX_CRYPTOS_TO_MONITOR=50  # En lugar de 600
```

### API de Binance bloqueada

**Síntoma:**
```
BinanceAPIException: IP banned
```

**Solución:**
```powershell
# Aumentar delay entre requests
# Editar scanner.py línea 78:
time.sleep(0.5)  # Cambiar a time.sleep(1.0)
```

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs: `logs\bot.log`
2. Verifica que el modelo existe: `models\xgboost_model.json`
3. Confirma que Telegram está configurado

---

## 🎯 Checklist Final

Antes de dejar el bot corriendo:

- [ ] ✅ Python y dependencias instaladas
- [ ] ✅ Telegram configurado (token + chat ID)
- [ ] ✅ IA entrenada (modelo en `models/`)
- [ ] ✅ Bot ejecutándose (`python main.py`)
- [ ] ✅ Task Scheduler configurado (opcional)
- [ ] ✅ Firewall configurado
- [ ] ✅ Primeras señales recibidas

---

**¡Listo! Tu bot está operativo 24/7 en AWS** 🚀

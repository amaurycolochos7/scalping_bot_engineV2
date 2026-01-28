# ============================================
# SCRIPT DE INSTALACIÓN COMPLETA
# Windows Server AWS - Scalping Engine V2
# ============================================

Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  SCALPING ENGINE V2 - AWS SETUP          ║" -ForegroundColor Yellow
Write-Host "║  Instalación Completa con IA             ║" -ForegroundColor Yellow
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Variables
$PYTHON_VERSION = "3.11"
$PROJECT_DIR = "C:\ScalpingEngineV2"

# 1. Verificar Python
Write-Host "[1/7] Verificando Python $PYTHON_VERSION..." -ForegroundColor Green
try {
    $pythonVer = python --version 2>&1
    Write-Host "   ✅ $pythonVer encontrado" -ForegroundColor White
}
catch {
    Write-Host "   ❌ Python no instalado" -ForegroundColor Red
    Write-Host "   Descargando Python..." -ForegroundColor Yellow
    
    # Descargar Python
    $pythonUrl = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
    
    # Instalar Python (silencioso)
    Write-Host "   Instalando Python..." -ForegroundColor Yellow
    Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    
    Write-Host "   ✅ Python instalado" -ForegroundColor Green
}

# 2. Verificar Git
Write-Host ""
Write-Host "[2/7] Verificando Git..." -ForegroundColor Green
try {
    $gitVer = git --version 2>&1
    Write-Host "   ✅ $gitVer encontrado" -ForegroundColor White
}
catch {
    Write-Host "   ❌ Git no instalado" -ForegroundColor Red
    Write-Host "   Descargando Git..." -ForegroundColor Yellow
    
    # Descargar Git
    $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
    $gitInstaller = "$env:TEMP\git-installer.exe"
    
    Invoke-WebRequest -Uri $gitUrl -OutFile $gitInstaller
    
    # Instalar Git
    Write-Host "   Instalando Git..." -ForegroundColor Yellow
    Start-Process -FilePath $gitInstaller -ArgumentList "/SILENT" -Wait
    
    Write-Host "   ✅ Git instalado" -ForegroundColor Green
}

# 3. Clonar repositorio
Write-Host ""
Write-Host "[3/7] Clonando repositorio..." -ForegroundColor Green
Write-Host "   📁 Destino: $PROJECT_DIR" -ForegroundColor White

if (Test-Path $PROJECT_DIR) {
    Write-Host "   ⚠️ El directorio ya existe. Actualizando..." -ForegroundColor Yellow
    Set-Location $PROJECT_DIR
    git pull origin main
}
else {
    Write-Host "   Ingresa la URL de tu repositorio Git:" -ForegroundColor Yellow
    $repoUrl = Read-Host "   URL"
    
    git clone $repoUrl $PROJECT_DIR
    Set-Location $PROJECT_DIR
}

Write-Host "   ✅ Repositorio listo" -ForegroundColor Green

# 4. Crear entorno virtual
Write-Host ""
Write-Host "[4/7] Creando entorno virtual Python..." -ForegroundColor Green
python -m venv venv
Write-Host "   ✅ Entorno virtual creado" -ForegroundColor Green

# 5. Activar e instalar dependencias
Write-Host ""
Write-Host "[5/7] Instalando dependencias..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

Write-Host "   Actualizando pip..." -ForegroundColor White
python -m pip install --upgrade pip --quiet

Write-Host "   Instalando paquetes (esto puede tardar 5-10 minutos)..." -ForegroundColor White
pip install -r requirements.txt --quiet

Write-Host "   ✅ Todas las dependencias instaladas" -ForegroundColor Green

# 6. Configurar variables de entorno
Write-Host ""
Write-Host "[6/7] Configurando variables de entorno..." -ForegroundColor Green

if (Test-Path ".env") {
    Write-Host "   ⚠️ Archivo .env ya existe" -ForegroundColor Yellow
    $overwrite = Read-Host "   ¿Quieres configurar Telegram Chat ID ahora? (s/n)"
    
    if ($overwrite -eq "s") {
        $chatId = Read-Host "   Ingresa tu Telegram Chat ID"
        (Get-Content .env) -replace 'TELEGRAM_CHAT_ID=.*', "TELEGRAM_CHAT_ID=$chatId" | Set-Content .env
        Write-Host "   ✅ Chat ID actualizado" -ForegroundColor Green
    }
}
else {
    Write-Host "   ❌ Archivo .env no encontrado" -ForegroundColor Red
}

# 7. Crear directorios necesarios
Write-Host ""
Write-Host "[7/7] Creando estructura de directorios..." -ForegroundColor Green
$dirs = @("data", "data\historical", "data\features", "models", "logs")

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   ✅ Creado: $dir" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  ✅ INSTALACIÓN COMPLETADA               ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos pasos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  ENTRENAR LA IA (5-7 horas):" -ForegroundColor White
Write-Host "   .\train_ia.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "2️⃣  EJECUTAR EL BOT:" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3️⃣  PROBAR CON 1 CRIPTO:" -ForegroundColor White
Write-Host "   python test_single.py BTCUSDT" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Ubicación: $PROJECT_DIR" -ForegroundColor Gray
Write-Host ""

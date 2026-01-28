# ============================================
# SCRIPT DE ENTRENAMIENTO DE IA COMPLETO
# Ejecuta todo el pipeline en orden
# ============================================

Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  ENTRENAMIENTO DE IA - PIPELINE          ║" -ForegroundColor Yellow
Write-Host "║  Tiempo estimado: 5-7 horas              ║" -ForegroundColor Yellow
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor White
& .\venv\Scripts\Activate.ps1

$startTime = Get-Date

# PASO 1: Descargar datos históricos
Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PASO 1/3: Descarga de Datos Históricos" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "⏱️  Tiempo estimado: 2-3 horas" -ForegroundColor Gray
Write-Host ""

python ai_data_downloader.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Error en la descarga de datos" -ForegroundColor Red
    exit 1
}

# PASO 2: Calcular features técnicos
Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PASO 2/3: Cálculo de Features Técnicos" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "⏱️  Tiempo estimado: 1-2 horas" -ForegroundColor Gray
Write-Host ""

python ai_feature_calculator.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Error calculando features" -ForegroundColor Red
    exit 1
}

# PASO 3: Entrenar modelo XGBoost
Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PASO 3/3: Entrenamiento de XGBoost" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "⏱️  Tiempo estimado: 1-2 horas" -ForegroundColor Gray
Write-Host ""

python ai_trainer.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Error entrenando modelo" -ForegroundColor Red
    exit 1
}

# Resumen final
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🎉 ENTRENAMIENTO COMPLETADO             ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏱️  Tiempo total: $($duration.Hours)h $($duration.Minutes)m" -ForegroundColor White
Write-Host ""
Write-Host "📊 Estadísticas:" -ForegroundColor Yellow

# Verificar que existan los archivos
if (Test-Path "models\xgboost_model.json") {
    $modelSize = (Get-Item "models\xgboost_model.json").Length / 1MB
    Write-Host "   ✅ Modelo: models\xgboost_model.json ($([math]::Round($modelSize, 2)) MB)" -ForegroundColor Green
}

if (Test-Path "data\historical") {
    $dataCount = (Get-ChildItem "data\historical" -Filter *.csv).Count
    Write-Host "   ✅ Datos descargados: $dataCount archivos" -ForegroundColor Green
}

if (Test-Path "data\features") {
    $featCount = (Get-ChildItem "data\features" -Filter *.csv).Count
    Write-Host "   ✅ Features calculados: $featCount archivos" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Próximo paso:" -ForegroundColor Yellow
Write-Host "   python main.py   # Ejecutar bot con IA" -ForegroundColor Cyan
Write-Host ""

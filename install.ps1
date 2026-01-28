# ============================================
# COMPLETE INSTALLATION SCRIPT
# Windows Server AWS - Scalping Engine V2
# ============================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  SCALPING ENGINE V2 - AWS SETUP          " -ForegroundColor Yellow
Write-Host "  Complete Installation with AI           " -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$PYTHON_VERSION = "3.11"
$PROJECT_DIR = "C:\ScalpingEngineV2"

# 1. Check Python
Write-Host "[1/7] Checking Python $PYTHON_VERSION..." -ForegroundColor Green
try {
    $pythonVer = python --version 2>&1
    Write-Host "   OK: $pythonVer found" -ForegroundColor White
}
catch {
    Write-Host "   ERROR: Python not installed" -ForegroundColor Red
    Write-Host "   Downloading Python..." -ForegroundColor Yellow
    
    # Download Python
    $pythonUrl = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
    
    # Install Python (silent)
    Write-Host "   Installing Python..." -ForegroundColor Yellow
    Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    
    Write-Host "   OK: Python installed" -ForegroundColor Green
}

# 2. Check Git
Write-Host ""
Write-Host "[2/7] Checking Git..." -ForegroundColor Green
try {
    $gitVer = git --version 2>&1
    Write-Host "   OK: $gitVer found" -ForegroundColor White
}
catch {
    Write-Host "   ERROR: Git not installed" -ForegroundColor Red
    Write-Host "   Downloading Git..." -ForegroundColor Yellow
    
    # Download Git
    $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
    $gitInstaller = "$env:TEMP\git-installer.exe"
    
    Invoke-WebRequest -Uri $gitUrl -OutFile $gitInstaller
    
    # Install Git
    Write-Host "   Installing Git..." -ForegroundColor Yellow
    Start-Process -FilePath $gitInstaller -ArgumentList "/SILENT" -Wait
    
    Write-Host "   OK: Git installed" -ForegroundColor Green
}

# 3. Clone repository
Write-Host ""
Write-Host "[3/7] Cloning repository..." -ForegroundColor Green
Write-Host "   Destination: $PROJECT_DIR" -ForegroundColor White

if (Test-Path $PROJECT_DIR) {
    Write-Host "   WARNING: Directory exists. Updating..." -ForegroundColor Yellow
    Set-Location $PROJECT_DIR
    git pull origin main
}
else {
    Write-Host "   Enter your Git repository URL:" -ForegroundColor Yellow
    $repoUrl = Read-Host "   URL"
    
    git clone $repoUrl $PROJECT_DIR
    Set-Location $PROJECT_DIR
}

Write-Host "   OK: Repository ready" -ForegroundColor Green

# 4. Create virtual environment
Write-Host ""
Write-Host "[4/7] Creating Python virtual environment..." -ForegroundColor Green
python -m venv venv
Write-Host "   OK: Virtual environment created" -ForegroundColor Green

# 5. Activate and install dependencies
Write-Host ""
Write-Host "[5/7] Installing dependencies..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

Write-Host "   Updating pip..." -ForegroundColor White
python -m pip install --upgrade pip --quiet

Write-Host "   Installing packages (this may take 5-10 minutes)..." -ForegroundColor White
pip install -r requirements.txt --quiet

Write-Host "   OK: All dependencies installed" -ForegroundColor Green

# 6. Configure environment variables
Write-Host ""
Write-Host "[6/7] Configuring environment variables..." -ForegroundColor Green

if (Test-Path ".env") {
    Write-Host "   WARNING: .env file exists" -ForegroundColor Yellow
    $overwrite = Read-Host "   Configure Telegram Chat ID now? (y/n)"
    
    if ($overwrite -eq "y") {
        $chatId = Read-Host "   Enter your Telegram Chat ID"
        (Get-Content .env) -replace 'TELEGRAM_CHAT_ID=.*', "TELEGRAM_CHAT_ID=$chatId" | Set-Content .env
        Write-Host "   OK: Chat ID updated" -ForegroundColor Green
    }
}
else {
    Write-Host "   ERROR: .env file not found" -ForegroundColor Red
}

# 7. Create necessary directories
Write-Host ""
Write-Host "[7/7] Creating directory structure..." -ForegroundColor Green
$dirs = @("data", "data\historical", "data\features", "models", "logs")

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   OK: Created $dir" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  INSTALLATION COMPLETED                  " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. TRAIN THE AI (5-7 hours):" -ForegroundColor White
Write-Host "   .\train_ia.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. RUN THE BOT:" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. TEST WITH 1 CRYPTO:" -ForegroundColor White
Write-Host "   python test_single.py BTCUSDT" -ForegroundColor Cyan
Write-Host ""
Write-Host "Location: $PROJECT_DIR" -ForegroundColor Gray
Write-Host ""

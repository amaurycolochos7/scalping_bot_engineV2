# Archivo de inicio para Windows Service
@echo off
cd /d "C:\ScalpingEngineV2"
call venv\Scripts\activate.bat
python main.py
pause

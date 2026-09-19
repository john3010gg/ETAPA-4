@echo off
if "%~1"=="" (
    echo Uso: bot.bat ^<Archivo.bot^>
    exit /b 1
)
python main.py "%~1"

@echo off
if "%~1"=="" (
    echo Uso: ContBot.bat ^<Archivo.bot^>
    exit /b 1
)
python main.py "%~1"

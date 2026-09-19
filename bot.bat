@echo off
if "%~1"=="" (
    echo Uso: bot ^<Archivo.bot^>
    exit /b 1
)
python "%~dp0Etapa4\main.py" %*

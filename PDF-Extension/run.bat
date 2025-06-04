@echo off
title HYDRA21 PDF Compressor Pro
color 0B

echo.
echo ========================================
echo   HYDRA21 PDF Compressor Pro v3.0.0
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no esta instalado o no esta en el PATH
    echo.
    echo Por favor instala Python 3.8+ desde:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo ❌ Error: main.py no encontrado
    echo.
    echo Asegurate de ejecutar este script desde el directorio PDF-Extension
    echo.
    pause
    exit /b 1
)

echo ✅ Python detectado
echo 🚀 Iniciando HYDRA21 PDF Compressor...
echo.

REM Run the application
python main.py

REM Check if there was an error
if errorlevel 1 (
    echo.
    echo ❌ La aplicacion termino con errores
    echo.
    echo Posibles soluciones:
    echo 1. Ejecuta: python install.py
    echo 2. Instala dependencias: pip install -r requirements.txt
    echo 3. Verifica que Ghostscript este instalado
    echo.
    pause
) else (
    echo.
    echo ✅ Aplicacion cerrada correctamente
)

pause

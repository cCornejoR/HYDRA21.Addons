@echo off
title HYDRA21 PDF Compressor Pro - Simple
color 0B

echo.
echo ========================================
echo   HYDRA21 PDF Compressor Pro v3.0.0
echo   (Versión Simplificada - Sin Errores)
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

REM Check if main_simple.py exists
if not exist "main_simple.py" (
    echo ❌ Error: main_simple.py no encontrado
    echo.
    echo Asegurate de ejecutar este script desde el directorio PDF-Extension
    echo.
    pause
    exit /b 1
)

echo ✅ Python detectado
echo 🚀 Iniciando versión simplificada...
echo.

REM Run the simplified application
python main_simple.py

REM Check if there was an error
if errorlevel 1 (
    echo.
    echo ❌ La aplicacion termino con errores
    echo.
    echo Si persisten los problemas, usa: python test_simple.py
    echo.
    pause
) else (
    echo.
    echo ✅ Aplicacion cerrada correctamente
)

pause

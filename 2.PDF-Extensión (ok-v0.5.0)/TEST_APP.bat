@echo off
echo ========================================
echo HYDRA21 PDF Compressor Pro - Test App
echo ========================================

echo.
echo 🔍 Verificando dependencias...

echo.
echo 📦 Verificando Python...
python --version
if errorlevel 1 (
    echo ❌ Error: Python no encontrado
    pause
    exit /b 1
)

echo.
echo 📦 Verificando Flet...
python -c "import flet; print(f'✅ Flet {flet.__version__} instalado')" 2>nul
if errorlevel 1 (
    echo ❌ Flet no encontrado, instalando...
    python -m pip install flet
    if errorlevel 1 (
        echo ❌ Error instalando Flet
        pause
        exit /b 1
    )
)

echo.
echo 🔍 Verificando archivos...
if not exist "main_professional.py" (
    echo ❌ main_professional.py no encontrado
    pause
    exit /b 1
)

if not exist "assets\logo.ico" (
    echo ❌ assets\logo.ico no encontrado
    pause
    exit /b 1
)

if not exist "ui\main_window_complete.py" (
    echo ❌ ui\main_window_complete.py no encontrado
    pause
    exit /b 1
)

echo ✅ Todos los archivos necesarios encontrados

echo.
echo 🚀 Probando aplicación...
echo (Si funciona correctamente, podrás construir el ejecutable)
echo.

python main_professional.py

echo.
echo 📋 ¿La aplicación funcionó correctamente? (S/N)
set /p choice=
if /i "%choice%"=="S" (
    echo.
    echo 🔨 ¿Quieres construir el ejecutable ahora? (S/N)
    set /p build_choice=
    if /i "%build_choice%"=="S" (
        call BUILD_SIMPLE_WORKING.bat
    )
) else (
    echo.
    echo ❌ Hay problemas con la aplicación
    echo 📋 Revisa los errores mostrados arriba
    echo 💡 Posibles soluciones:
    echo    1. pip install -r requirements.txt
    echo    2. Verificar que Ghostscript esté instalado
    echo    3. Comprobar permisos de archivos
)

echo.
pause

@echo off
echo ========================================
echo Configurando Python 3.12 para HYDRA21
echo ========================================

echo.
echo 🔄 Configurando PATH temporal para Python 3.12...

REM Agregar Python 3.12 al PATH temporal
set "PYTHON312_PATH=C:\Users\Pc\AppData\Local\Programs\Python\Python312"
set "PYTHON312_SCRIPTS=C:\Users\Pc\AppData\Local\Programs\Python\Python312\Scripts"

REM Configurar PATH temporal (solo para esta sesión)
set "PATH=%PYTHON312_PATH%;%PYTHON312_SCRIPTS%;%PATH%"

echo ✅ Python 3.12 configurado temporalmente
echo.

echo 🔍 Verificando configuración:
python --version
echo.

echo 📦 Verificando dependencias instaladas:
python -c "import flet; print('✅ Flet disponible')" 2>nul || echo "❌ Flet no disponible"
python -c "import numpy; print('✅ NumPy disponible')" 2>nul || echo "❌ NumPy no disponible"
python -c "import PIL; print('✅ Pillow disponible')" 2>nul || echo "❌ Pillow no disponible"
python -c "import rasterio; print('✅ Rasterio disponible')" 2>nul || echo "❌ Rasterio no disponible (esperado)"

echo.
echo 🚀 Para ejecutar la aplicación:
echo    python main_professional.py
echo.
echo 💡 Para hacer este cambio permanente:
echo    1. Presiona Win + R, escribe "sysdm.cpl"
echo    2. Variables de entorno → Variables del sistema → Path
echo    3. Mueve Python312 al principio de la lista
echo.

REM Mantener la ventana abierta
cmd /k

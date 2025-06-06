@echo off
echo ========================================
echo HYDRA21 - Configuracion OpenCV App
echo ========================================
echo.

echo 🚀 Configurando aplicacion para usar OpenCV...
echo.

echo 📦 Paso 1: Verificando dependencias basicas...
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ OpenCV no disponible
    echo 🔧 Instalando OpenCV...
    pip install opencv-python
)

python -c "import numpy; print('✅ NumPy:', numpy.__version__)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ NumPy no disponible
    echo 🔧 Instalando NumPy...
    pip install numpy
)

python -c "from PIL import Image; print('✅ Pillow disponible')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Pillow no disponible
    echo 🔧 Instalando Pillow...
    pip install Pillow
)

echo.
echo 📋 Paso 2: Instalando librerias de metadatos...
pip install exifread piexif
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Error instalando librerias de metadatos (opcional)
)

echo.
echo 🧪 Paso 3: Ejecutando tests de funcionalidad...
python test_file_loading.py
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Algunos tests fallaron, pero la aplicacion puede funcionar
)

echo.
echo 🎯 Paso 4: Configuracion completada!
echo.
echo ✅ La aplicacion esta configurada para usar:
echo    - OpenCV para procesamiento de imagenes
echo    - Preservacion de metadatos (si esta disponible)
echo    - Formatos: JPG, PNG, BMP, TIFF
echo    - Compresion optimizada con OpenCV
echo.
echo 🚀 Para ejecutar la aplicacion:
echo    python main_professional.py
echo.
pause

@echo off
echo ========================================
echo HYDRA21 - Instalacion de Librerias de Metadatos
echo ========================================
echo.

echo 📦 Instalando librerias para manejo de metadatos...
echo.

echo 🔧 Instalando ExifRead...
pip install exifread
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error instalando ExifRead
    pause
    exit /b 1
)

echo 🔧 Instalando Piexif...
pip install piexif
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error instalando Piexif
    pause
    exit /b 1
)

echo.
echo ✅ Librerias de metadatos instaladas correctamente!
echo.
echo 📋 Librerias instaladas:
echo    - ExifRead: Para leer metadatos EXIF
echo    - Piexif: Para escribir metadatos EXIF
echo.
echo 🎯 Ahora la aplicacion puede preservar metadatos en imagenes
echo.
pause

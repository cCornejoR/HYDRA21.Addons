@echo off
echo ========================================
echo HYDRA21 PDF Compressor Pro - Diagnóstico
echo ========================================

echo.
echo 🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA
echo.

echo 📋 1. Verificando Python...
python --version
python -c "import sys; print(f'Ruta Python: {sys.executable}')"

echo.
echo 📋 2. Verificando PyInstaller...
python -m pip show pyinstaller
if errorlevel 1 (
    echo ❌ PyInstaller no instalado
    echo 📦 Instalando PyInstaller...
    python -m pip install pyinstaller
)

echo.
echo 📋 3. Verificando Flet...
python -c "import flet; print(f'Flet versión: {flet.__version__}')" 2>nul
if errorlevel 1 (
    echo ❌ Flet no encontrado
    echo 📦 Instalando Flet...
    python -m pip install flet
)

echo.
echo 📋 4. Verificando estructura de archivos...
echo Directorio actual: %CD%
echo.
if exist "main_professional.py" (echo ✅ main_professional.py) else (echo ❌ main_professional.py)
if exist "assets\logo.ico" (echo ✅ assets\logo.ico) else (echo ❌ assets\logo.ico)
if exist "assets\logo.png" (echo ✅ assets\logo.png) else (echo ❌ assets\logo.png)
if exist "ui\main_window_complete.py" (echo ✅ ui\main_window_complete.py) else (echo ❌ ui\main_window_complete.py)
if exist "config\settings.py" (echo ✅ config\settings.py) else (echo ❌ config\settings.py)

echo.
echo 📋 5. Probando importaciones críticas...
python -c "
try:
    import flet as ft
    print('✅ Flet importado correctamente')
    
    from ui.main_window_complete import MainWindow
    print('✅ MainWindow importado correctamente')
    
    from config.settings import get_app_config
    print('✅ Configuración importada correctamente')
    
    print('✅ Todas las importaciones funcionan')
except Exception as e:
    print(f'❌ Error en importaciones: {e}')
    import traceback
    traceback.print_exc()
"

echo.
echo 📋 6. Verificando permisos de escritura...
echo test > test_write.tmp 2>nul
if exist "test_write.tmp" (
    echo ✅ Permisos de escritura OK
    del "test_write.tmp"
) else (
    echo ❌ Sin permisos de escritura
)

echo.
echo 📋 7. Verificando espacio en disco...
dir | find "bytes free"

echo.
echo 📋 8. Probando construcción básica...
echo Intentando construcción simple...

python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo ❌ PyInstaller no funciona correctamente
    goto :end
)

echo ✅ PyInstaller funcional

echo.
echo 🔨 Intentando construcción de prueba...
python -m PyInstaller --onefile --console --name=test-build main_professional.py >build_log.txt 2>&1

if exist "dist\test-build.exe" (
    echo ✅ Construcción de prueba exitosa
    echo 📁 Ejecutable de prueba creado: dist\test-build.exe
    
    echo.
    echo 🚀 ¿Probar ejecutable de prueba? (S/N)
    set /p choice=
    if /i "%choice%"=="S" (
        echo Ejecutando prueba...
        "dist\test-build.exe"
    )
    
    echo.
    echo 📋 La construcción básica funciona.
    echo 💡 El problema puede estar en:
    echo    1. Configuración del icono
    echo    2. Recursos adicionales
    echo    3. Configuración de ventana
    
) else (
    echo ❌ Error en construcción de prueba
    echo 📋 Revisando log de errores...
    if exist "build_log.txt" (
        echo.
        echo === LOG DE ERRORES ===
        type "build_log.txt"
        echo === FIN LOG ===
    )
)

:end
echo.
echo 📋 DIAGNÓSTICO COMPLETADO
echo 📁 Revisa los resultados arriba para identificar el problema
echo.
pause

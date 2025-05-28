@echo off
REM Natural Regrade Plugin - Quick Deployment Script
REM This script copies the compiled plugin to Civil 3D for testing

echo ============================================
echo  Natural Regrade Plugin - Quick Deploy
echo ============================================
echo.

REM Check if Civil 3D directory exists
set "CIVIL3D_PATH=C:\Program Files\Autodesk\AutoCAD 2025"
if not exist "%CIVIL3D_PATH%" (
    echo ERROR: Civil 3D 2025 not found at %CIVIL3D_PATH%
    echo Please check your Civil 3D installation path
    pause
    exit /b 1
)

REM Create Plugins directory if it doesn't exist
set "PLUGIN_DIR=%CIVIL3D_PATH%\Plugins"
if not exist "%PLUGIN_DIR%" (
    echo Creating Plugins directory...
    mkdir "%PLUGIN_DIR%"
)

REM Copy main DLL
echo Copying NaturalRegrade-extension.dll...
copy "bin\Debug\NaturalRegrade-extension.dll" "%PLUGIN_DIR%\" >nul
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy main DLL. Check permissions.
    echo Try running this script as Administrator.
    pause
    exit /b 1
)

REM Copy dependencies
echo Copying dependency DLLs...
copy "lib\*.dll" "%PLUGIN_DIR%\" >nul

echo.
echo ============================================
echo  DEPLOYMENT SUCCESSFUL!
echo ============================================
echo.
echo Plugin copied to: %PLUGIN_DIR%
echo.
echo NEXT STEPS:
echo 1. Open Civil 3D 2025
echo 2. Type: NETLOAD
echo 3. Select: NaturalRegrade-extension.dll
echo 4. Type: NATURALREGRADE
echo.
echo OR simply type: NATURALREGRADE
echo (if plugin loads automatically)
echo.
pause

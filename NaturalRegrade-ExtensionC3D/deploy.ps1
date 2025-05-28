# Natural Regrade Plugin - PowerShell Deployment Script
# This script copies the compiled plugin to Civil 3D for testing

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Natural Regrade Plugin - Quick Deploy" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Civil 3D directory exists
$Civil3DPath = "C:\Program Files\Autodesk\AutoCAD 2025"
if (-not (Test-Path $Civil3DPath)) {
    Write-Host "ERROR: Civil 3D 2025 not found at $Civil3DPath" -ForegroundColor Red
    Write-Host "Please check your Civil 3D installation path" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create Plugins directory if it doesn't exist
$PluginDir = Join-Path $Civil3DPath "Plugins"
if (-not (Test-Path $PluginDir)) {
    Write-Host "Creating Plugins directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $PluginDir -Force | Out-Null
}

try {
    # Copy main DLL
    Write-Host "Copying NaturalRegrade-extension.dll..." -ForegroundColor Green
    $sourceDLL = "bin\Debug\NaturalRegrade-extension.dll"
    if (Test-Path $sourceDLL) {
        Copy-Item $sourceDLL $PluginDir -Force
        Write-Host "✓ Main DLL copied successfully" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Source DLL not found at $sourceDLL" -ForegroundColor Red
        Write-Host "Please run 'dotnet build' first" -ForegroundColor Red
        exit 1
    }

    # Copy dependencies
    Write-Host "Copying dependency DLLs..." -ForegroundColor Green
    if (Test-Path "lib\*.dll") {
        Copy-Item "lib\*.dll" $PluginDir -Force
        Write-Host "✓ Dependencies copied successfully" -ForegroundColor Green
    } else {
        Write-Host "WARNING: No dependency DLLs found in lib folder" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host " DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Plugin copied to: $PluginDir" -ForegroundColor White
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Open Civil 3D 2025" -ForegroundColor White
    Write-Host "2. Type: NETLOAD" -ForegroundColor White
    Write-Host "3. Select: NaturalRegrade-extension.dll" -ForegroundColor White
    Write-Host "4. Type: NATURALREGRADE" -ForegroundColor White
    Write-Host ""
    Write-Host "OR simply type: NATURALREGRADE" -ForegroundColor Yellow
    Write-Host "(if plugin loads automatically)" -ForegroundColor Gray
    Write-Host ""

} catch {
    Write-Host "ERROR: Failed to copy files" -ForegroundColor Red
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Try running PowerShell as Administrator" -ForegroundColor Yellow
    exit 1
}

Read-Host "Press Enter to exit"

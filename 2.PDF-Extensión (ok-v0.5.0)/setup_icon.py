"""
Script para configurar correctamente el icono en Windows
"""

import os
import sys
import shutil
from pathlib import Path

def setup_icon_for_windows():
    """Configurar icono para que aparezca correctamente en Windows"""
    
    print("🔧 Configurando icono para Windows...")
    
    # Verificar que el icono existe
    icon_path = Path("assets/logo.ico")
    if not icon_path.exists():
        print(f"❌ Error: Icono no encontrado en {icon_path}")
        return False
    
    # Copiar icono a la raíz para que PyInstaller lo encuentre fácilmente
    root_icon = Path("logo.ico")
    if not root_icon.exists():
        shutil.copy2(icon_path, root_icon)
        print(f"✅ Icono copiado a: {root_icon}")
    
    # Crear archivo de recursos de Windows
    rc_content = '''
#include <windows.h>

// Icono principal de la aplicación
IDI_ICON1 ICON "assets/logo.ico"

// Información de versión
VS_VERSION_INFO VERSIONINFO
FILEVERSION 0,5,0,0
PRODUCTVERSION 0,5,0,0
FILEFLAGSMASK 0x3fL
FILEFLAGS 0x0L
FILEOS 0x40004L
FILETYPE 0x1L
FILESUBTYPE 0x0L
BEGIN
    BLOCK "StringFileInfo"
    BEGIN
        BLOCK "040904b0"
        BEGIN
            VALUE "CompanyName", "HYDRA21"
            VALUE "FileDescription", "HYDRA21 PDF Compressor Pro"
            VALUE "FileVersion", "0.5.0"
            VALUE "InternalName", "HYDRA21-PDF-Compressor-Pro"
            VALUE "LegalCopyright", "© 2024 HYDRA21"
            VALUE "OriginalFilename", "HYDRA21-PDF-Compressor-Pro.exe"
            VALUE "ProductName", "HYDRA21 PDF Compressor Pro"
            VALUE "ProductVersion", "0.5.0"
        END
    END
    BLOCK "VarFileInfo"
    BEGIN
        VALUE "Translation", 0x409, 1200
    END
END
'''
    
    # Guardar archivo de recursos
    rc_file = Path("app_resources.rc")
    with open(rc_file, 'w', encoding='utf-8') as f:
        f.write(rc_content)
    
    print(f"✅ Archivo de recursos creado: {rc_file}")
    
    return True

def create_manifest():
    """Crear archivo manifest para Windows"""
    
    manifest_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="0.5.0.0"
    processorArchitecture="*"
    name="HYDRA21.PDF.Compressor.Pro"
    type="win32"
  />
  <description>HYDRA21 PDF Compressor Pro</description>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="*"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
    </windowsSettings>
  </application>
</assembly>'''
    
    manifest_file = Path("app.manifest")
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    
    print(f"✅ Archivo manifest creado: {manifest_file}")

def main():
    """Función principal"""
    print("🔧 Configurando icono para Windows...")
    
    if setup_icon_for_windows():
        create_manifest()
        print("\n✅ Configuración completada")
        print("🚀 Ahora ejecuta REBUILD_WITH_ICON.bat para crear el ejecutable")
    else:
        print("\n❌ Error en la configuración")

if __name__ == "__main__":
    main()

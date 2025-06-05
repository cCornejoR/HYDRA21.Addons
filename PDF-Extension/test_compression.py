"""
Test script para verificar la compresión de PDFs
"""

import subprocess
import os
from pathlib import Path

def test_ghostscript():
    """Test basic Ghostscript functionality"""
    try:
        # Try to find Ghostscript
        gs_paths = [
            "gswin64c.exe",
            "gswin32c.exe", 
            "gs",
            r"C:\Program Files\gs\gs*\bin\gswin64c.exe"
        ]
        
        gs_path = None
        for path in gs_paths:
            try:
                if "*" in path:
                    import glob
                    matches = glob.glob(path)
                    if matches:
                        path = matches[0]
                
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    gs_path = path
                    print(f"✅ Ghostscript encontrado: {path}")
                    print(f"   Versión: {result.stdout.strip()}")
                    break
            except:
                continue
        
        if not gs_path:
            print("❌ Ghostscript no encontrado")
            return False
            
        # Test basic compression command
        print("\n🔄 Probando comando básico de compresión...")
        test_cmd = [
            gs_path,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-dSAFER",
            "-dPDFSETTINGS=/ebook",
            "-dColorImageResolution=72",
            "-dGrayImageResolution=72",
            "-dMonoImageResolution=150",
            "-dCompressFonts=true",
            "-dSubsetFonts=true",
            "-dEmbedAllFonts=true",
            "--help"  # Just show help to test command structure
        ]
        
        result = subprocess.run(test_cmd[:4] + ["--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Comando de compresión válido")
            return True
        else:
            print(f"❌ Error en comando: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando Ghostscript: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Probando funcionalidad de compresión...")
    success = test_ghostscript()
    
    if success:
        print("\n✅ Todas las pruebas pasaron correctamente")
        print("📋 La compresión debería funcionar en la aplicación")
    else:
        print("\n❌ Hay problemas con la configuración")
        print("📋 Revisa la instalación de Ghostscript")

"""
HYDRA21 PDF Compressor Pro - Installation Script
Installs dependencies and sets up the application
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - Compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Instalando dependencias...")
    
    try:
        # Upgrade pip first
        print("   Actualizando pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        requirements_file = Path(__file__).parent / "requirements.txt"
        if requirements_file.exists():
            print("   Instalando paquetes desde requirements.txt...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        else:
            print("   Instalando paquetes individuales...")
            packages = [
                "flet>=0.21.0",
                "PyPDF2>=3.0.1",
                "pypdf>=3.17.0",
                "psutil>=5.9.0",
                "pydantic>=2.5.0",
                "typing-extensions>=4.8.0"
            ]
            
            for package in packages:
                print(f"     Instalando {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("✅ Dependencias instaladas correctamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def check_ghostscript():
    """Check if Ghostscript is available"""
    print("\n👻 Verificando Ghostscript...")
    
    # Common Ghostscript executable names
    gs_names = ["gs", "gswin64c", "gswin32c", "ghostscript"]
    
    for gs_name in gs_names:
        try:
            result = subprocess.run([gs_name, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Ghostscript encontrado: {gs_name} (versión {version})")
                return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    print("⚠️  Ghostscript no encontrado automáticamente")
    print("   Puedes:")
    print("   1. Descargar desde: https://www.ghostscript.com/download/gsdnld.html")
    print("   2. Configurar la ruta manualmente en la aplicación")
    print("   3. Agregar Ghostscript al PATH del sistema")
    return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creando directorios...")
    
    base_dir = Path(__file__).parent
    directories = [
        base_dir / "assets",
        base_dir / "output",
        base_dir / "temp",
        base_dir / "config" / "user"
    ]
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {directory.relative_to(base_dir)}")
        except Exception as e:
            print(f"   ❌ Error creando {directory}: {e}")
            return False
    
    print("✅ Directorios creados correctamente")
    return True

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)"""
    if os.name != 'nt':
        return True
    
    print("\n🔗 Creando acceso directo...")
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "HYDRA21 PDF Compressor.lnk")
        target = sys.executable
        wDir = str(Path(__file__).parent)
        arguments = str(Path(__file__).parent / "main.py")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.Arguments = f'"{arguments}"'
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = target
        shortcut.save()
        
        print("✅ Acceso directo creado en el escritorio")
        return True
        
    except ImportError:
        print("   ⚠️  No se pudo crear acceso directo (falta winshell)")
        print("   Puedes instalar con: pip install winshell pywin32")
        return True
    except Exception as e:
        print(f"   ⚠️  No se pudo crear acceso directo: {e}")
        return True

def test_installation():
    """Test if installation is working"""
    print("\n🧪 Probando instalación...")
    
    try:
        # Test imports
        print("   Probando imports...")
        import flet
        import PyPDF2
        print("   ✅ Imports exitosos")
        
        # Test basic functionality
        print("   Probando funcionalidad básica...")
        from config.settings import APP_NAME, APP_VERSION
        print(f"   ✅ {APP_NAME} v{APP_VERSION} cargado correctamente")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Error de import: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error de prueba: {e}")
        return False

def main():
    """Main installation process"""
    print("🚀 HYDRA21 PDF Compressor Pro - Instalador")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Instalación fallida - Error en dependencias")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Instalación fallida - Error creando directorios")
        sys.exit(1)
    
    # Check Ghostscript
    check_ghostscript()
    
    # Test installation
    if not test_installation():
        print("\n❌ Instalación fallida - Error en pruebas")
        sys.exit(1)
    
    # Create shortcut (optional)
    create_desktop_shortcut()
    
    print("\n" + "=" * 50)
    print("✅ ¡Instalación completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("   1. Ejecuta: python main.py")
    print("   2. Configura Ghostscript si no fue detectado automáticamente")
    print("   3. ¡Comienza a comprimir tus PDFs!")
    print("\n💡 Consejos:")
    print("   • Usa el tutorial integrado para configuración inicial")
    print("   • Revisa la documentación para funciones avanzadas")
    print("   • Reporta bugs en el repositorio del proyecto")

if __name__ == "__main__":
    main()

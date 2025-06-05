"""
HYDRA21 Orthophoto Processor Pro - Installation Script
Automated installation and dependency management
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - Compatible")
    return True

def check_pip():
    """Check if pip is available"""
    print("📦 Checking pip...")
    
    try:
        import pip
        print("✅ pip disponible")
        return True
    except ImportError:
        print("❌ pip no encontrado")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📥 Installing dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt no encontrado")
        return False
    
    try:
        # Install dependencies
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencias instaladas correctamente")
            return True
        else:
            print("❌ Error instalando dependencias:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando pip: {e}")
        return False

def check_dependencies():
    """Check if all dependencies are available"""
    print("🔍 Checking dependencies...")
    
    dependencies = [
        ("flet", "Flet GUI framework"),
        ("rasterio", "Rasterio geospatial library"),
        ("numpy", "NumPy numerical computing")
    ]
    
    all_available = True
    
    for dep_name, description in dependencies:
        try:
            __import__(dep_name)
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description} - No disponible")
            all_available = False
    
    return all_available

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    base_dir = Path(__file__).parent
    directories = [
        "output",
        "temp",
        "assets"
    ]
    
    for dir_name in directories:
        dir_path = base_dir / dir_name
        try:
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Directory created: {dir_name}")
        except Exception as e:
            print(f"❌ Error creating {dir_name}: {e}")
            return False
    
    return True

def test_application():
    """Test if the application can start"""
    print("🧪 Testing application...")
    
    try:
        # Import main components
        sys.path.insert(0, str(Path(__file__).parent))
        
        from config.settings import APP_NAME, APP_VERSION
        print(f"✅ Configuration loaded: {APP_NAME} v{APP_VERSION}")
        
        # Test theme manager
        from ui.themes.theme_manager import ThemeManager
        print("✅ Theme manager available")
        
        # Test processing engine
        from core.orthophoto_engine import OrthophotoProcessor
        print("✅ Processing engine available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main installation function"""
    print("=" * 60)
    print("HYDRA21 Orthophoto Processor Pro - Installation")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check pip
    if not check_pip():
        print("💡 Install pip first: python -m ensurepip --upgrade")
        return False
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        return False
    
    # Check if dependencies are already installed
    if check_dependencies():
        print("✅ All dependencies already available")
    else:
        print("📥 Installing missing dependencies...")
        if not install_dependencies():
            print("❌ Failed to install dependencies")
            return False
        
        # Check again after installation
        if not check_dependencies():
            print("❌ Some dependencies still missing after installation")
            return False
    
    # Test application
    if not test_application():
        print("❌ Application test failed")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Installation completed successfully!")
    print("🚀 To start the application, run:")
    print("   python main_professional.py")
    print("\n💡 Or use the legacy version:")
    print("   python main.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Installation failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

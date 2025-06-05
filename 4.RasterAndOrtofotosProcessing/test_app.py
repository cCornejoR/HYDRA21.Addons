"""
HYDRA21 Orthophoto Processor Pro - Quick Test
Test the application with improved functionality
"""

import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test all imports"""
    print("🧪 Testing imports...")
    
    try:
        import flet as ft
        print("✅ Flet imported successfully")
    except ImportError as e:
        print(f"❌ Flet import failed: {e}")
        return False
    
    try:
        from config.settings import APP_NAME, APP_VERSION, THEME_CONFIG
        print(f"✅ Config imported: {APP_NAME} v{APP_VERSION}")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from ui.themes.theme_manager import ThemeManager
        print("✅ Theme manager imported")
    except ImportError as e:
        print(f"❌ Theme manager import failed: {e}")
        return False
    
    try:
        from core.orthophoto_engine import OrthophotoProcessor
        print("✅ Processing engine imported")
    except ImportError as e:
        print(f"❌ Processing engine import failed: {e}")
        return False
    
    try:
        from ui.components.tabbed_interface import TabbedInterface
        print("✅ UI components imported")
    except ImportError as e:
        print(f"❌ UI components import failed: {e}")
        return False
    
    return True

def test_theme_system():
    """Test theme system"""
    print("\n🎨 Testing theme system...")
    
    try:
        from config.settings import THEME_CONFIG, DirectoryConfig
        from ui.themes.theme_manager import ThemeManager
        
        # Test theme manager
        theme_manager = ThemeManager(DirectoryConfig.get_config_dir())
        
        # Test light theme
        light_theme = theme_manager.get_theme()
        print(f"✅ Light theme loaded: {len(light_theme)} colors")
        
        # Test dark theme
        theme_manager.set_theme(True)
        dark_theme = theme_manager.get_theme()
        print(f"✅ Dark theme loaded: {len(dark_theme)} colors")
        
        # Test theme colors
        primary_color = theme_manager.get_color('primary')
        print(f"✅ Primary color: {primary_color}")
        
        return True
        
    except Exception as e:
        print(f"❌ Theme system test failed: {e}")
        return False

def test_processing_engine():
    """Test processing engine"""
    print("\n⚙️ Testing processing engine...")
    
    try:
        from core.orthophoto_engine import OrthophotoProcessor
        
        # Create processor
        processor = OrthophotoProcessor()
        print("✅ Processor created")
        
        # Test file info (with dummy file)
        test_file = Path("test.tif")
        if test_file.exists():
            info = processor.get_file_info(test_file)
            print(f"✅ File info test: {info}")
        else:
            print("⚠️ No test file available for file info test")
        
        return True
        
    except Exception as e:
        print(f"❌ Processing engine test failed: {e}")
        return False

def test_ui_components():
    """Test UI components creation"""
    print("\n🖼️ Testing UI components...")
    
    try:
        import flet as ft
        from config.settings import THEME_CONFIG
        from ui.themes.theme_manager import ThemeManager
        from config.settings import DirectoryConfig
        
        # Create a dummy page for testing
        class DummyPage:
            def __init__(self):
                self.overlay = []
                self.controls = []
            
            def update(self):
                pass
            
            def run_thread_safe(self, func):
                func()
        
        dummy_page = DummyPage()
        
        # Test theme manager
        theme_manager = ThemeManager(DirectoryConfig.get_config_dir())
        theme = theme_manager.get_theme()
        
        # Test file manager
        from ui.components.file_manager import FileManager
        file_manager = FileManager(dummy_page, theme)
        print("✅ File manager created")
        
        # Test progress display
        from ui.components.progress_display import ProgressDisplay
        progress_display = ProgressDisplay(theme)
        print("✅ Progress display created")
        
        # Test processing options
        from ui.components.processing_options import ProcessingOptions
        processing_options = ProcessingOptions(theme, page=dummy_page)
        print("✅ Processing options created")
        
        # Test results panel
        from ui.components.results_panel import ResultsPanel
        results_panel = ResultsPanel(dummy_page, theme)
        print("✅ Results panel created")
        
        return True
        
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("HYDRA21 Orthophoto Processor Pro - Quick Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Theme System", test_theme_system),
        ("Processing Engine", test_processing_engine),
        ("UI Components", test_ui_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready to run.")
        print("\n🚀 To start the application:")
        print("   python main_professional.py")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("\n🔧 Try running the installation script:")
        print("   python install.py")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

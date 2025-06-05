"""
HYDRA21 PDF Compressor Pro - Professional PDF Processing Application
Complete PDF processing suite with modern Flet interface

Features:
- Advanced PDF Compression with Ghostscript integration
- PDF Merging and Splitting capabilities
- Batch processing with comprehensive progress tracking
- Dynamic theme switching (light/dark mode)
- Professional statistics and results panel
- Drag-and-drop file support
- Real-time progress indicators and status updates
- Direct file/folder access after operations

Author: HYDRA21
Version: 3.0.0 - Professional Edition
"""

import flet as ft
import sys
import os
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the complete professional main window
from ui.main_window_complete import MainWindow
from config.settings import (
    APP_NAME, APP_VERSION,
    DirectoryConfig
)

def main(page: ft.Page):
    """Professional PDF Compressor - Main Application Entry Point"""
    
    # Setup output directory
    setup_output_directory()
    
    # Configure page properties with fixed size
    page.title = f"{APP_NAME} v{APP_VERSION} - Professional Edition"
    page.window.width = 850
    page.window.height = 900
    page.window.min_width = 850
    page.window.min_height = 900
    page.window.resizable = False
    page.window.maximizable = False

    page.window.center()
    page.scroll = ft.ScrollMode.AUTO

    # Set application icon for window and taskbar
    try:
        # Buscar icono en diferentes ubicaciones
        icon_paths = [
            Path(__file__).parent / "assets" / "logo.ico",
            Path("assets") / "logo.ico",
            Path("logo.ico")
        ]

        icon_path = None
        for path in icon_paths:
            if path.exists():
                icon_path = path
                break

        if icon_path:
            # Configurar icono de ventana (esto afecta la barra de tareas)
            page.window.icon = str(icon_path.absolute())
            print(f"✅ Icono configurado: {icon_path.absolute()}")
        else:
            print(f"⚠️ Icono no encontrado en ninguna ubicación")
            # Listar ubicaciones buscadas para debug
            for i, path in enumerate(icon_paths):
                print(f"   {i+1}. {path.absolute()} - {'✅' if path.exists() else '❌'}")

        # Configurar propiedades de ventana para Windows
        page.window.skip_task_bar = False
        page.window.always_on_top = False
        page.window.title_bar_hidden = False
        page.window.title_bar_buttons_hidden = False

    except Exception as e:
        print(f"❌ Error configurando icono: {e}")
        import traceback
        traceback.print_exc()
    
    # Configure theme and appearance
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    
    # Professional blue theme
    page.theme = ft.Theme(
        use_material3=True,
        color_scheme_seed="#2563eb",
    )
    
    # Handle window close event
    def on_window_event(e):
        if e.data == "close":
            try:
                print("🔄 Cerrando aplicación...")
                # Clean shutdown - stop any running operations
                if hasattr(page, 'main_window') and page.main_window:
                    page.main_window.cleanup()
                page.window.destroy()
            except Exception as ex:
                print(f"⚠️ Error during shutdown: {ex}")
    
    page.on_window_event = on_window_event
    
    # Initialize main application
    try:
        print("🚀 Inicializando HYDRA21 PDF Compressor Pro...")
        
        # Create and add main window
        main_window = MainWindow(page)
        page.main_window = main_window  # Store reference for cleanup
        
        page.add(main_window)
        page.update()
        
        print("✅ Aplicación iniciada correctamente")
        print("🎨 Interfaz profesional cargada")
        print("📁 Directorio de salida configurado")
        print("📋 Listo para procesar PDFs")
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        
        # Show professional error dialog
        show_error_dialog(page, e)

def setup_output_directory():
    """Setup the default output directory structure"""
    try:
        dir_config = DirectoryConfig.get_default()
        dir_config.ensure_directories()
        
        # Create operation-specific subdirectories
        subdirs = ['compressed', 'merged', 'split']
        for subdir in subdirs:
            (dir_config.output_dir / subdir).mkdir(exist_ok=True)
        
        print(f"📁 Directorio de salida configurado: {dir_config.output_dir}")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not setup output directory: {e}")

def show_error_dialog(page: ft.Page, error: Exception):
    """Show professional error dialog"""
    error_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.ERROR_OUTLINE, color="#dc2626", size=28),
            ft.Text("Error de Inicialización", size=20, weight=ft.FontWeight.BOLD, color="#dc2626")
        ], spacing=12),
        content=ft.Container(
            content=ft.Column([
                ft.Text(
                    "No se pudo inicializar la aplicación profesional:",
                    size=16,
                    weight=ft.FontWeight.W_500
                ),
                ft.Container(height=12),
                ft.Container(
                    content=ft.Text(
                        str(error),
                        size=14,
                        color="#dc2626"
                    ),
                    padding=12,
                    bgcolor="#fef2f2",
                    border_radius=8,
                    border=ft.border.all(1, "#fecaca")
                ),
                ft.Container(height=16),
                ft.Text("Posibles soluciones:", size=14, weight=ft.FontWeight.W_500),
                ft.Text("• Ejecutar: python install.py", size=12),
                ft.Text("• Verificar instalación de Ghostscript", size=12),
                ft.Text("• Comprobar permisos de escritura", size=12),
                ft.Text("• Reinstalar dependencias", size=12),
            ], spacing=4),
            width=400
        ),
        actions=[
            ft.TextButton(
                "Cerrar Aplicación",
                on_click=lambda _: page.window.close(),
                style=ft.ButtonStyle(color="#dc2626")
            )
        ],
    )
    
    page.overlay.append(error_dialog)
    error_dialog.open = True
    page.update()

def run_app():
    """Run the professional PDF application"""
    try:
        # Set up assets directory
        assets_dir = current_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Run Flet app
        ft.app(
            target=main,
            assets_dir=str(assets_dir) if assets_dir.exists() else None,
            view=ft.AppView.FLET_APP
        )
        
    except KeyboardInterrupt:
        print("\n👋 Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"❌ Error crítico en la aplicación: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure clean exit
        try:
            sys.exit(0)
        except:
            os._exit(0)

if __name__ == "__main__":
    print(f"🚀 Iniciando {APP_NAME} v{APP_VERSION} - Professional Edition...")
    print(f"📁 Directorio de trabajo: {current_dir}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    # Run the application
    run_app()

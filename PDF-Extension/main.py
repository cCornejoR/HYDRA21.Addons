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

try:
    from ui.main_window_professional import MainWindow
    PROFESSIONAL_VERSION = True
except ImportError:
    print("⚠️ Professional version not available, using standard version")
    from ui.main_window import MainWindow
    PROFESSIONAL_VERSION = False
from config.settings import (
    APP_NAME, APP_VERSION,
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    DirectoryConfig
)

def main(page: ft.Page):
    """Main application entry point"""
    
    # Configure page properties
    page.title = f"{APP_NAME} v{APP_VERSION}"
    page.window_width = WINDOW_WIDTH
    page.window_height = WINDOW_HEIGHT
    page.window_min_width = WINDOW_MIN_WIDTH
    page.window_min_height = WINDOW_MIN_HEIGHT
    page.window_resizable = True
    page.window_maximizable = True
    page.window_center = True
    
    # Set window icon (if available)
    try:
        icon_path = current_dir / "assets" / "icon.ico"
        if icon_path.exists():
            page.window_icon = str(icon_path)
    except Exception:
        pass  # Icon not critical
    
    # Configure page theme and appearance
    page.theme_mode = ft.ThemeMode.LIGHT  # Will be overridden by theme manager
    page.padding = 0
    page.spacing = 0
    
    # Disable default shadows for clean look (user preference)
    page.theme = ft.Theme(
        use_material3=True,
        color_scheme_seed="#2563eb",  # Blue color scheme preference
    )
    
    # Handle window close event
    def on_window_event(e):
        if e.data == "close":
            # Clean shutdown
            try:
                # Stop any running operations
                print("Cerrando aplicación...")

            except Exception as ex:
                print(f"Error during shutdown: {ex}")
            finally:
                import sys; sys.exit(0)
    
    page.window_prevent_close = True
    page.on_window_event = on_window_event
    
    # Create and initialize main window
    try:
        # Simple test to see if basic UI works
        page.add(
            ft.Column([
                ft.Text(
                    f"🚀 {APP_NAME} v{APP_VERSION}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color="#2563eb"
                ),
                ft.Text(
                    "Aplicación de procesamiento de PDFs",
                    size=16,
                    color="#64748b"
                ),
                ft.Container(height=20),
                ft.ElevatedButton(
                    text="Inicializar Aplicación Completa",
                    on_click=lambda _: init_full_app(),
                    bgcolor="#2563eb",
                    color="white"
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True
            )
        )

        def init_full_app():
            try:
                page.clean()
                # Create professional main window
                main_window = MainWindow(page)
                page.main_window = main_window  # Store reference for cleanup
                page.add(main_window)
                page.update()
                print("✅ Aplicación profesional inicializada correctamente")
            except Exception as e:
                print(f"❌ Error inicializando aplicación: {e}")
                page.clean()
                page.add(
                    ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color="#dc2626", size=48),
                        ft.Text("Error de Inicialización", size=20, weight=ft.FontWeight.BOLD, color="#dc2626"),
                        ft.Text(f"Error: {str(e)}", color="#dc2626"),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            text="Reintentar",
                            on_click=lambda _: init_full_app(),
                            style=ft.ButtonStyle(bgcolor="#2563eb", color="white")
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12)
                )
                page.update()

        page.update()
        
        # Show simple welcome message
        print("✅ Aplicación iniciada correctamente")
        print("� Interfaz de usuario cargada")
        print("📋 Listo para procesar PDFs")
        
    except Exception as e:
        # Show error dialog if main window fails to initialize
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("❌ Error de Inicialización", color="#dc2626"),
            content=ft.Text(
                f"No se pudo inicializar la aplicación:\n\n{str(e)}\n\n"
                "Posibles soluciones:\n"
                "• Verificar que Ghostscript esté instalado\n"
                "• Comprobar permisos de escritura\n"
                "• Reinstalar dependencias",
                size=14
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: (lambda: __import__('sys').exit(0))())
            ],
        )
        
        page.overlay.append(error_dialog)
        error_dialog.open = True
        page.update()

def run_app():
    """Run the application with proper error handling"""
    try:
        # Set up assets directory
        assets_dir = current_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Run Flet app
        ft.app(
            target=main,
            assets_dir=str(assets_dir) if assets_dir.exists() else None,
            view=ft.AppView.FLET_APP  # Desktop app view
        )
        
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario")
    except Exception as e:
        print(f"Error crítico en la aplicación: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure clean exit
        try:
            sys.exit(0)
        except:
            os._exit(0)

if __name__ == "__main__":
    print(f"🚀 Iniciando {APP_NAME} v{APP_VERSION}...")
    print(f"📁 Directorio de trabajo: {current_dir}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    # Run the application
    run_app()

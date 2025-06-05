"""
HYDRA21 Orthophoto Processor Pro - Professional Application
Complete orthophoto processing suite with modern Flet interface

Features:
- Advanced orthophoto processing with geospatial data preservation
- Multiple export formats (GeoTIFF, JPEG, PNG) with georeferenciation
- Batch processing with comprehensive progress tracking
- Dynamic theme switching (light/dark mode) with blue color scheme
- Professional statistics and results panel
- Drag-and-drop file support
- Real-time progress indicators and status updates
- Direct file/folder access after operations

Author: HYDRA21
Version: 1.0.0 - Professional Edition
"""

import flet as ft
import sys
import os
import threading
from pathlib import Path
from typing import Dict, Any

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import components
from config.settings import (
    APP_NAME, APP_VERSION, DirectoryConfig, get_app_config
)
from ui.themes.theme_manager import ThemeManager
from ui.components.tabbed_interface import TabbedInterface
from core.orthophoto_engine import OrthophotoProcessor

class MainWindow(ft.Column):
    """Professional Orthophoto Processor Main Window"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.config = get_app_config()
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(DirectoryConfig.get_config_dir())
        self.theme = self.theme_manager.get_theme()
        
        # Initialize processing engine
        self.processor = OrthophotoProcessor()
        
        # UI Components
        self.header = None
        self.tabbed_interface = None
        self.status_bar = None
        
        # State
        self.is_processing = False
        self.current_operation = None
        
        self._setup_page()
        self._setup_ui()
        self._setup_callbacks()
        
        super().__init__(
            controls=self._build_layout(),
            spacing=0,
            expand=True
        )
    
    def _setup_page(self):
        """Setup page configuration"""
        # Apply theme to page
        self.theme_manager.apply_to_page(self.page)
        
        # Configure page properties
        self.page.title = f"{APP_NAME} v{APP_VERSION}"
        self.page.window.width = 1000
        self.page.window.height = 800
        self.page.window.min_width = 900
        self.page.window.min_height = 700
        self.page.window.center()
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 0
        
        # Set window icon if available
        icon_path = current_dir / "assets" / "icon.ico"
        if icon_path.exists():
            self.page.window.icon = str(icon_path)
    
    def _setup_ui(self):
        """Setup UI components"""
        # Create header
        self.header = self._create_header()
        
        # Create tabbed interface
        self.tabbed_interface = TabbedInterface(self.page, self.theme)
        
        # Create status bar
        self.status_bar = self._create_status_bar()
    
    def _setup_callbacks(self):
        """Setup callbacks and event handlers"""
        # Theme change listener
        self.theme_manager.add_listener(self._on_theme_changed)
        
        # Processing engine callbacks
        self.processor.set_callbacks(
            progress_callback=self._on_progress_update,
            statistics_callback=self._on_statistics_update,
            error_callback=self._on_error
        )
    
    def _build_layout(self) -> list:
        """Build the main layout"""
        return [
            self.header,
            ft.Container(
                content=self.tabbed_interface,
                expand=True,
                padding=ft.padding.all(24)
            ),
            self.status_bar
        ]
    
    def _create_header(self) -> ft.Container:
        """Create application header"""
        return ft.Container(
            content=ft.Row([
                # Logo and title
                ft.Row([
                    ft.Icon(
                        ft.Icons.SATELLITE_ALT,
                        size=32,
                        color=self.theme['primary']
                    ),
                    ft.Column([
                        ft.Text(
                            APP_NAME,
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=self.theme['on_surface']
                        ),
                        ft.Text(
                            f"v{APP_VERSION} - Professional Edition",
                            size=12,
                            color=self.theme['on_surface_variant']
                        )
                    ], spacing=0)
                ], spacing=12),
                
                # Header actions
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.HELP_OUTLINE,
                        icon_color=self.theme['on_surface_variant'],
                        tooltip="Ayuda",
                        on_click=self._show_help
                    ),
                    ft.IconButton(
                        icon=ft.Icons.INFO_OUTLINE,
                        icon_color=self.theme['on_surface_variant'],
                        tooltip="Acerca de",
                        on_click=self._show_about
                    ),
                    self.theme_manager.create_theme_toggle_button(
                        on_click=self._on_theme_toggle
                    )
                ], spacing=4)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            bgcolor=self.theme['surface'],
            border=ft.border.only(bottom=ft.BorderSide(1, self.theme['border']))
        )
    
    def _create_status_bar(self) -> ft.Container:
        """Create status bar"""
        return ft.Container(
            content=ft.Row([
                ft.Text(
                    "Listo",
                    size=12,
                    color=self.theme['on_surface_variant']
                ),
                ft.Text(
                    f"Directorio de salida: {DirectoryConfig.get_output_dir()}",
                    size=12,
                    color=self.theme['on_surface_variant']
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=24, vertical=8),
            bgcolor=self.theme['surface_variant'],
            border=ft.border.only(top=ft.BorderSide(1, self.theme['border']))
        )
    
    def _on_theme_changed(self, new_theme: Dict[str, str]):
        """Handle theme change"""
        self.theme = new_theme
        
        # Update page theme
        self.theme_manager.apply_to_page(self.page)
        
        # Update component themes
        if self.tabbed_interface:
            self.tabbed_interface.set_theme(new_theme)
        
        # Update header and status bar
        self._update_header_theme()
        self._update_status_bar_theme()
        
        self.page.update()
    
    def _on_theme_toggle(self, e):
        """Handle theme toggle button click"""
        # Theme is already toggled by the button, just update UI
        pass
    
    def _update_header_theme(self):
        """Update header theme"""
        if self.header:
            self.header.bgcolor = self.theme['surface']
            self.header.border = ft.border.only(bottom=ft.BorderSide(1, self.theme['border']))
            
            # Update header content colors
            header_row = self.header.content
            if isinstance(header_row, ft.Row):
                # Update logo icon color
                logo_row = header_row.controls[0]
                if isinstance(logo_row, ft.Row):
                    logo_row.controls[0].color = self.theme['primary']
                    
                    # Update title colors
                    title_column = logo_row.controls[1]
                    if isinstance(title_column, ft.Column):
                        title_column.controls[0].color = self.theme['on_surface']
                        title_column.controls[1].color = self.theme['on_surface_variant']
    
    def _update_status_bar_theme(self):
        """Update status bar theme"""
        if self.status_bar:
            self.status_bar.bgcolor = self.theme['surface_variant']
            self.status_bar.border = ft.border.only(top=ft.BorderSide(1, self.theme['border']))
            
            # Update status text colors
            status_row = self.status_bar.content
            if isinstance(status_row, ft.Row):
                for control in status_row.controls:
                    if isinstance(control, ft.Text):
                        control.color = self.theme['on_surface_variant']
    
    def _on_progress_update(self, message: str, progress: float, details: str = ""):
        """Handle progress updates from processing engine"""
        def update_ui():
            if self.tabbed_interface and hasattr(self.tabbed_interface, 'progress_display'):
                self.tabbed_interface.progress_display.show_progress(message, progress, details)
            self.page.update()
        
        # Update UI from main thread
        self.page.run_thread_safe(update_ui)
    
    def _on_statistics_update(self, stats: Dict[str, Any]):
        """Handle statistics updates from processing engine"""
        def update_ui():
            if self.tabbed_interface and hasattr(self.tabbed_interface, 'progress_display'):
                self.tabbed_interface.progress_display.update_statistics(stats)
            self.page.update()
        
        # Update UI from main thread
        self.page.run_thread_safe(update_ui)
    
    def _on_error(self, error_message: str):
        """Handle errors from processing engine"""
        def show_error():
            self._show_error_dialog("Error de Procesamiento", error_message)
        
        # Show error from main thread
        self.page.run_thread_safe(show_error)
    
    def _show_help(self, e):
        """Show help dialog"""
        help_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("📖 Ayuda - Orthophoto Processor Pro"),
            content=ft.Column([
                ft.Text("Guía rápida de uso:", weight=ft.FontWeight.BOLD),
                ft.Text("1. 📁 Selecciona archivos de ortofoto en la pestaña 'Archivos'"),
                ft.Text("2. ⚙️ Configura las opciones de procesamiento"),
                ft.Text("3. 🚀 Inicia el procesamiento"),
                ft.Text("4. 📊 Revisa los resultados y accede a los archivos"),
                ft.Divider(),
                ft.Text("Formatos soportados:", weight=ft.FontWeight.BOLD),
                ft.Text("• Entrada: TIF, TIFF, ECW, JP2, IMG, BIL, BIP, BSQ"),
                ft.Text("• Salida: GeoTIFF, JPEG, PNG (con georreferenciación)"),
                ft.Divider(),
                ft.Text("Características:", weight=ft.FontWeight.BOLD),
                ft.Text("• Preservación de datos geoespaciales"),
                ft.Text("• Múltiples opciones de compresión"),
                ft.Text("• Procesamiento por lotes"),
                ft.Text("• Estadísticas detalladas"),
            ], height=400, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self._close_dialog(help_dialog))
            ]
        )
        
        self.page.overlay.append(help_dialog)
        help_dialog.open = True
        self.page.update()
    
    def _show_about(self, e):
        """Show about dialog"""
        about_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"ℹ️ Acerca de {APP_NAME}"),
            content=ft.Column([
                ft.Text(f"Versión: {APP_VERSION}", weight=ft.FontWeight.BOLD),
                ft.Text("Professional Edition"),
                ft.Divider(),
                ft.Text("Procesador profesional de ortofotos con preservación de datos geoespaciales."),
                ft.Divider(),
                ft.Text("Características principales:", weight=ft.FontWeight.BOLD),
                ft.Text("🗺️ Procesamiento de ortofotos georreferenciadas"),
                ft.Text("🔄 Múltiples formatos de entrada y salida"),
                ft.Text("📊 Estadísticas detalladas de procesamiento"),
                ft.Text("🎨 Interfaz moderna con tema oscuro/claro"),
                ft.Text("⚡ Procesamiento por lotes eficiente"),
                ft.Divider(),
                ft.Text("Tecnologías utilizadas:", weight=ft.FontWeight.BOLD),
                ft.Text("• Flet (Flutter para Python)"),
                ft.Text("• Rasterio (Procesamiento geoespacial)"),
                ft.Text("• GDAL (Biblioteca geoespacial)"),
                ft.Text("• NumPy (Computación numérica)"),
                ft.Divider(),
                ft.Text("© 2024 HYDRA21 - Orthophoto Processor Pro", 
                       size=12, color=self.theme['on_surface_variant'])
            ], height=400, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self._close_dialog(about_dialog))
            ]
        )
        
        self.page.overlay.append(about_dialog)
        about_dialog.open = True
        self.page.update()
    
    def _show_error_dialog(self, title: str, message: str):
        """Show error dialog"""
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"❌ {title}"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self._close_dialog(error_dialog))
            ]
        )
        
        self.page.overlay.append(error_dialog)
        error_dialog.open = True
        self.page.update()
    
    def _close_dialog(self, dialog):
        """Close dialog"""
        dialog.open = False
        self.page.update()

def main(page: ft.Page):
    """Professional Orthophoto Processor - Main Application Entry Point"""
    
    # Setup output directory
    setup_output_directory()
    
    # Initialize main application
    try:
        print("🚀 Inicializando HYDRA21 Orthophoto Processor Pro...")
        
        # Create and add main window
        main_window = MainWindow(page)
        page.main_window = main_window  # Store reference for cleanup
        
        page.add(main_window)
        page.update()
        
        print("✅ Aplicación iniciada correctamente")
        print("🎨 Interfaz profesional cargada")
        print("📁 Directorio de salida configurado")
        print("🗺️ Listo para procesar ortofotos")
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        
        # Show professional error dialog
        show_error_dialog(page, e)

def setup_output_directory():
    """Setup output directory"""
    try:
        output_dir = DirectoryConfig.get_output_dir()
        print(f"📁 Directorio de salida: {output_dir}")
        return output_dir
    except Exception as e:
        print(f"⚠️ Error configurando directorio de salida: {e}")
        return None

def show_error_dialog(page: ft.Page, error: Exception):
    """Show critical error dialog"""
    error_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("❌ Error Crítico"),
        content=ft.Column([
            ft.Text("Ha ocurrido un error crítico al inicializar la aplicación:"),
            ft.Text(str(error), color="red"),
            ft.Text("Por favor, verifique la instalación y las dependencias.")
        ]),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: page.window.close())
        ]
    )
    
    page.overlay.append(error_dialog)
    error_dialog.open = True
    page.update()

def run_app():
    """Run the professional orthophoto application"""
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

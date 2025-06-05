"""
HYDRA21 PDF Compressor Pro - Professional Main Window
Complete PDF processing application with advanced features and modern UI
"""

import flet as ft
import threading
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime

# Core imports
from config.settings import get_app_config, DirectoryConfig, GS_QUALITY_PRESETS
from config.ghostscript_config import GhostscriptConfig
from core.ghostscript_manager import GhostscriptManager
from core.pdf_processor import PDFProcessor, BatchProgress
from core.file_manager import FileManager

# UI imports
from ui.themes.theme_manager import ThemeManager
from ui.themes.modern_components import create_modern_button, create_modern_card, create_modern_dropdown

class MainWindow(ft.Column):
    """Main application window"""

    def __init__(self, page: ft.Page):
        self.page = page

        # Load configuration
        self.config = get_app_config()
        self.dir_config = DirectoryConfig.get_default()
        self.dir_config.ensure_directories()

        # Initialize managers
        self.theme_manager = ThemeManager(self.dir_config.config_dir)
        self.gs_config = GhostscriptConfig(self.dir_config.config_dir)
        self.file_manager = FileManager(
            supported_extensions=self.config['files']['supported_extensions'],
            max_file_size_mb=self.config['files']['max_file_size_mb']
        )

        # Initialize processors (will be set up after Ghostscript config)
        self.gs_manager = None
        self.pdf_processor = None

        # UI state
        self.current_operation = "compress"  # compress, merge, split
        self.selected_files: List[Path] = []
        self.is_processing = False

        # UI components
        self.app_bar = None
        self.main_content = None
        self.operation_tabs = None
        self.file_selector = None
        self.quality_dropdown = None
        self.progress_display = None
        self.batch_progress_display = None
        self.statistics_panel = None
        self.tutorial_modal = None

        # Setup
        self._setup_page()
        self._setup_ghostscript()
        self._setup_theme()

        # Build UI components
        self._initialize_ui_components()

        # Initialize Column with proper controls
        super().__init__(
            controls=[],
            spacing=0,
            expand=True
        )

        # Add controls after initialization
        self.controls = [
            self.app_bar,
            self.main_content
        ]

    def _initialize_ui_components(self):
        """Initialize all UI components"""
        # Create app bar
        self.app_bar = self._create_app_bar()

        # Create main content
        self.main_content = self._create_main_content()

        # Create tutorial modal
        self._create_tutorial_modal()
    
    def _setup_page(self):
        """Setup page configuration"""
        self.page.title = self.config['app']['name']
        self.page.window_width = self.config['window']['width']
        self.page.window_height = self.config['window']['height']
        self.page.window_min_width = self.config['window']['min_width']
        self.page.window_min_height = self.config['window']['min_height']
        self.page.window_resizable = True
        self.page.window_maximizable = True
        
    def _setup_ghostscript(self):
        """Setup Ghostscript configuration"""
        gs_info = self.gs_config.get_ghostscript_info()
        
        if gs_info['verified']:
            # Ghostscript is configured and working
            self.gs_manager = GhostscriptManager(gs_info['path'])
            self.pdf_processor = PDFProcessor(self.gs_manager, self.dir_config.output_dir)
        else:
            # Need to configure Ghostscript
            self.gs_manager = None
            self.pdf_processor = None
    
    def _setup_theme(self):
        """Setup theme management"""
        # Add theme change listener
        self.theme_manager.add_listener(self._on_theme_changed)
        
        # Apply initial theme
        self.theme_manager.apply_to_page(self.page)
    
    def _create_app_bar(self):
        """Create application bar"""
        theme = self.theme_manager.get_theme()
        
        self.app_bar = ft.Container(
            content=ft.Row([
                # App title and logo
                ft.Row([
                    ft.Icon(ft.Icons.PICTURE_AS_PDF, color=theme['primary'], size=28),
                    ft.Text(
                        self.config['app']['name'],
                        size=18,
                        weight=ft.FontWeight.W_600,
                        color=theme['on_surface']
                    )
                ], spacing=12),
                
                # Action buttons
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.HELP_OUTLINE,
                        icon_color=theme['on_surface_variant'],
                        tooltip="Tutorial y Ayuda",
                        on_click=self._show_tutorial
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        icon_color=theme['on_surface_variant'],
                        tooltip="Configuración",
                        on_click=self._show_settings
                    ),
                    self.theme_manager.create_theme_toggle_button(self._on_theme_toggle)
                ], spacing=8)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=theme['surface'],
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            border=ft.border.only(bottom=ft.BorderSide(1, theme['border']))
        )
    
    def _create_main_content(self):
        """Create main content area with improved layout"""
        theme = self.theme_manager.get_theme()

        # Initialize components
        self._create_operation_tabs()
        self._create_file_selector(theme)
        self._create_quality_dropdown(theme)
        self._create_progress_displays(theme)
        self._create_statistics_panel(theme)

        # Main content with centered, symmetric layout
        self.main_content = ft.Container(
            content=ft.Column([
                # Operation tabs - full width
                self.operation_tabs,

                # Main content area - centered with max width
                ft.Container(
                    content=ft.Column([
                        # File selection section
                        self._create_file_section(),

                        # Operation controls section
                        self._create_controls_section(),

                        # Action buttons section
                        self._create_buttons_section(),

                        # Progress section
                        self._create_progress_section(),

                        # Results section
                        self._create_results_section()

                    ],
                    spacing=32,
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.symmetric(horizontal=32, vertical=24),
                    expand=True,
                    alignment=ft.alignment.top_center
                )
            ], spacing=0),
            expand=True,
            bgcolor=theme['background']
        )

    def _create_file_selector(self, theme):
        """Create file selector component"""
        try:
            self.file_selector = FileSelector(
                theme=theme,
                file_manager=self.file_manager,
                on_files_selected=self._on_files_selected,
                allow_multiple=True,
                max_files=self.config['files']['max_batch_files']
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize file selector: {e}")
            # Use fallback component
            from ui.components.fallback_components import FallbackFileSelector
            self.file_selector = FallbackFileSelector(theme, self._on_files_selected)

    def _create_quality_dropdown(self, theme):
        """Create quality dropdown component"""
        try:
            quality_options = [
                ft.dropdown.Option(key=key, text=preset['name'])
                for key, preset in GS_QUALITY_PRESETS.items()
            ]

            self.quality_dropdown = create_modern_dropdown(
                label="Calidad de Compresión",
                options=quality_options,
                value=self.config['ghostscript']['default_quality'],
                theme=theme,
                width=300
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize quality dropdown: {e}")
            # Use fallback dropdown
            from ui.components.fallback_components import create_fallback_dropdown
            quality_options = [
                ft.dropdown.Option(key=key, text=preset['name'])
                for key, preset in GS_QUALITY_PRESETS.items()
            ]
            self.quality_dropdown = create_fallback_dropdown(
                "Calidad de Compresión", quality_options,
                self.config['ghostscript']['default_quality'], theme, 300
            )

    def _create_progress_displays(self, theme):
        """Create progress display components"""
        try:
            self.progress_display = ProgressDisplay(theme=theme)
            self.batch_progress_display = BatchProgressDisplay(theme=theme)
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize progress displays: {e}")
            # Use fallback components
            from ui.components.fallback_components import (
                FallbackProgressDisplay, FallbackBatchProgressDisplay
            )
            self.progress_display = FallbackProgressDisplay(theme)
            self.batch_progress_display = FallbackBatchProgressDisplay(theme)

    def _create_statistics_panel(self, theme):
        """Create statistics panel component"""
        try:
            self.statistics_panel = StatisticsPanel(
                theme=theme,
                file_manager=self.file_manager,
                on_open_file=self._open_file,
                on_open_folder=self._open_folder
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize statistics panel: {e}")
            # Use fallback component
            from ui.components.fallback_components import FallbackStatisticsPanel
            self.statistics_panel = FallbackStatisticsPanel(
                theme, self.file_manager, self._open_file, self._open_folder
            )

    def _create_file_section(self):
        """Create file selection section"""
        theme = self.theme_manager.get_theme()

        if not self.file_selector:
            return ft.Container(
                content=ft.Text("Error: File selector not available", color=theme['error']),
                padding=20
            )

        return create_modern_card([
            ft.Row([
                ft.Icon(ft.Icons.FOLDER_OPEN, color=theme['primary'], size=24),
                ft.Text(
                    "Selección de Archivos",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=theme['on_surface']
                )
            ], spacing=12),
            ft.Container(height=16),
            self.file_selector
        ], theme, width=800)

    def _create_controls_section(self):
        """Create operation controls section"""
        controls = self._create_operation_controls()
        if controls:
            return ft.Container(
                content=controls,
                width=800,
                alignment=ft.alignment.center
            )
        return ft.Container()

    def _create_buttons_section(self):
        """Create action buttons section"""
        buttons = self._create_action_buttons()
        return ft.Container(
            content=buttons,
            width=800,
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=16)
        )

    def _create_progress_section(self):
        """Create progress displays section"""
        if not self.progress_display or not self.batch_progress_display:
            return ft.Container()

        return ft.Container(
            content=ft.Column([
                self.progress_display,
                self.batch_progress_display
            ], spacing=16),
            width=800,
            alignment=ft.alignment.center
        )

    def _create_results_section(self):
        """Create results/statistics section"""
        if not self.statistics_panel:
            return ft.Container()

        return ft.Container(
            content=self.statistics_panel,
            width=800,
            alignment=ft.alignment.center
        )

    def _create_operation_tabs(self):
        """Create operation selection tabs"""
        theme = self.theme_manager.get_theme()
        
        tabs = [
            ft.Tab(
                text="Comprimir PDFs",
                icon=ft.Icons.COMPRESS,
                content=ft.Container()
            ),
            ft.Tab(
                text="Fusionar PDFs", 
                icon=ft.Icons.MERGE,
                content=ft.Container()
            ),
            ft.Tab(
                text="Dividir PDF",
                icon=ft.Icons.CONTENT_CUT,
                content=ft.Container()
            )
        ]
        
        self.operation_tabs = ft.Tabs(
            tabs=tabs,
            selected_index=0,
            on_change=self._on_operation_changed,
            indicator_color=theme['primary'],
            label_color=theme['on_surface'],
            unselected_label_color=theme['on_surface_variant']
        )
    
    def _create_operation_controls(self):
        """Create operation-specific controls"""
        theme = self.theme_manager.get_theme()
        
        if self.current_operation == "compress":
            return create_modern_card([
                ft.Text(
                    "Configuración de Compresión",
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=theme['on_surface']
                ),
                ft.Row([
                    self.quality_dropdown,
                    ft.Column([
                        ft.Text(
                            "Descripción:",
                            size=12,
                            weight=ft.FontWeight.W_500,
                            color=theme['on_surface_variant']
                        ),
                        ft.Text(
                            self._get_quality_description(),
                            size=12,
                            color=theme['on_surface_variant']
                        )
                    ], spacing=4, expand=True)
                ], spacing=16)
            ], theme)
            
        elif self.current_operation == "merge":
            return create_modern_card([
                ft.Text(
                    "Configuración de Fusión",
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=theme['on_surface']
                ),
                ft.Text(
                    "Los archivos se fusionarán en el orden seleccionado.",
                    size=14,
                    color=theme['on_surface_variant']
                ),
                ft.TextField(
                    label="Nombre del archivo fusionado",
                    value="documento_fusionado.pdf",
                    width=400,
                    bgcolor=theme['input_bg'],
                    border_color=theme['input_border'],
                    focused_border_color=theme['input_focused_border']
                )
            ], theme)
            
        elif self.current_operation == "split":
            return create_modern_card([
                ft.Text(
                    "Configuración de División",
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=theme['on_surface']
                ),
                ft.Row([
                    ft.TextField(
                        label="Página inicial",
                        value="1",
                        width=120,
                        bgcolor=theme['input_bg'],
                        border_color=theme['input_border'],
                        focused_border_color=theme['input_focused_border']
                    ),
                    ft.TextField(
                        label="Página final (opcional)",
                        hint_text="Dejar vacío para todas",
                        width=150,
                        bgcolor=theme['input_bg'],
                        border_color=theme['input_border'],
                        focused_border_color=theme['input_focused_border']
                    )
                ], spacing=16),
                ft.Text(
                    "Nota: Solo se puede dividir un archivo a la vez.",
                    size=12,
                    color=theme['on_surface_variant']
                )
            ], theme)
        
        return ft.Container()
    
    def _create_action_buttons(self):
        """Create action buttons"""
        theme = self.theme_manager.get_theme()
        
        # Check if Ghostscript is configured
        if not self.gs_manager:
            return create_modern_card([
                ft.Row([
                    ft.Icon(ft.Icons.WARNING, color=theme['warning'], size=24),
                    ft.Column([
                        ft.Text(
                            "Ghostscript no configurado",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color=theme['warning']
                        ),
                        ft.Text(
                            "Necesitas configurar Ghostscript para usar la aplicación.",
                            size=14,
                            color=theme['on_surface_variant']
                        )
                    ], spacing=4, expand=True),
                    create_modern_button(
                        text="Configurar",
                        icon=ft.Icons.SETTINGS,
                        on_click=self._show_tutorial,
                        style="primary",
                        theme=theme
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], theme)
        
        # Action button text based on operation
        button_texts = {
            "compress": "Comprimir PDFs",
            "merge": "Fusionar PDFs", 
            "split": "Dividir PDF"
        }
        
        button_icons = {
            "compress": ft.Icons.COMPRESS,
            "merge": ft.Icons.MERGE,
            "split": ft.Icons.CONTENT_CUT
        }
        
        return ft.Row([
            create_modern_button(
                text=button_texts[self.current_operation],
                icon=button_icons[self.current_operation],
                on_click=self._start_processing,
                style="primary",
                theme=theme,
                disabled=not self.selected_files or self.is_processing,
                width=200
            ),
            create_modern_button(
                text="Limpiar",
                icon=ft.Icons.CLEAR,
                on_click=self._clear_all,
                style="secondary",
                theme=theme,
                disabled=self.is_processing
            )
        ], spacing=16, alignment=ft.MainAxisAlignment.CENTER)
    
    def _create_tutorial_modal(self):
        """Create tutorial modal"""
        try:
            self.tutorial_modal = TutorialModal(
                theme=self.theme_manager.get_theme(),
                gs_config=self.gs_config,
                on_setup_complete=self._on_tutorial_complete
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize tutorial modal: {e}")
            # Use fallback component
            from ui.components.fallback_components import FallbackTutorialModal
            self.tutorial_modal = FallbackTutorialModal(
                self.theme_manager.get_theme(), self.gs_config, self._on_tutorial_complete
            )

        # Show setup tip only once
        try:
            gs_info = self.gs_config.get_ghostscript_info()
            if not gs_info['verified']:
                print("💡 Tip: Usa el menú 'Ayuda > Tutorial' para configurar Ghostscript")
        except Exception as e:
            print(f"⚠️ Warning: Could not check Ghostscript status: {e}")
            print("💡 Tip: Verifica la configuración de Ghostscript manualmente")
    
    def _get_quality_description(self) -> str:
        """Get description for selected quality"""
        quality = self.quality_dropdown.value if self.quality_dropdown else "medium"
        return GS_QUALITY_PRESETS.get(quality, {}).get("description", "")
    
    def _on_theme_changed(self, theme: Dict[str, str]):
        """Handle theme change"""
        # Update app bar
        if self.app_bar:
            self.app_bar.bgcolor = theme['surface']
            self.app_bar.border = ft.border.only(bottom=ft.BorderSide(1, theme['border']))
        
        # Update other components
        self._refresh_ui_components()
        
        self.update()
    
    def _on_theme_toggle(self, e):
        """Handle theme toggle"""
        # Theme is already toggled by the button, just refresh UI
        self._refresh_ui_components()
    
    def _refresh_ui_components(self):
        """Refresh UI components with new theme"""
        theme = self.theme_manager.get_theme()
        
        # Update file selector theme
        if self.file_selector:
            self.file_selector.theme = theme
        
        # Update progress displays theme
        if self.progress_display:
            self.progress_display.theme = theme
        
        if self.batch_progress_display:
            self.batch_progress_display.theme = theme
        
        # Update statistics panel theme
        if self.statistics_panel:
            self.statistics_panel.theme = theme
        
        # Update tutorial modal theme
        if self.tutorial_modal:
            self.tutorial_modal.theme = theme
        
        # Rebuild main content to apply theme changes
        self._create_main_content()
        self.update()
    
    def _on_operation_changed(self, e):
        """Handle operation tab change"""
        operation_map = {0: "compress", 1: "merge", 2: "split"}
        self.current_operation = operation_map.get(e.control.selected_index, "compress")
        
        # Update file selector based on operation
        if self.current_operation == "split":
            self.file_selector.allow_multiple = False
            self.file_selector.max_files = 1
        else:
            self.file_selector.allow_multiple = True
            self.file_selector.max_files = self.config['files']['max_batch_files']
        
        # Refresh UI
        self._refresh_ui_components()
    
    def _on_files_selected(self, files: List[Path]):
        """Handle file selection"""
        self.selected_files = files
        
        # Update action buttons
        self._refresh_ui_components()
    
    def _show_tutorial(self, e):
        """Show tutorial modal"""
        if self.tutorial_modal:
            self.tutorial_modal.show()
    
    def _show_settings(self, e):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        pass
    
    def _on_tutorial_complete(self):
        """Handle tutorial completion"""
        # Refresh Ghostscript setup
        self._setup_ghostscript()
        
        # Refresh UI
        self._refresh_ui_components()
        
        # Show success message
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text("¡Configuración completada! Ya puedes usar la aplicación."),
                bgcolor=self.theme_manager.get_color('success')
            )
        )

    def _start_processing(self, e):
        """Start PDF processing operation"""
        if not self.selected_files or not self.gs_manager:
            return

        self.is_processing = True
        self._refresh_ui_components()

        # Hide statistics panel if visible
        if self.statistics_panel.is_visible:
            self.statistics_panel.hide()

        # Start processing in background thread
        threading.Thread(
            target=self._process_files,
            daemon=True
        ).start()

    def _process_files(self):
        """Process files in background thread"""
        try:
            if self.current_operation == "compress":
                self._process_compression()
            elif self.current_operation == "merge":
                self._process_merge()
            elif self.current_operation == "split":
                self._process_split()
        except Exception as e:
            self._show_error(f"Error inesperado: {str(e)}")
        finally:
            self.is_processing = False
            self._refresh_ui_components()

    def _process_compression(self):
        """Process PDF compression"""
        quality = self.quality_dropdown.value if self.quality_dropdown else "medium"

        if len(self.selected_files) == 1:
            # Single file compression
            self.progress_display.show_progress("Iniciando compresión...", 0)

            def progress_callback(message: str):
                self.progress_display.show_progress(message, None)

            result = self.pdf_processor.compress_single_pdf(
                input_path=self.selected_files[0],
                quality=quality,
                progress_callback=progress_callback
            )

            self.progress_display.hide_progress()
            self.statistics_panel.show_single_operation_stats(result, "compresión")

        else:
            # Batch compression
            def progress_callback(progress: BatchProgress):
                self.batch_progress_display.show_batch_progress(
                    current_file=progress.current_file,
                    total_files=progress.total_files,
                    filename=progress.current_filename,
                    operation=progress.current_operation
                )

            stats = self.pdf_processor.compress_batch(
                input_paths=self.selected_files,
                quality=quality,
                progress_callback=progress_callback
            )

            self.batch_progress_display.hide_progress()
            self.statistics_panel.show_compression_stats(stats)

    def _process_merge(self):
        """Process PDF merge"""
        self.progress_display.show_progress("Iniciando fusión...", 0)

        def progress_callback(message: str):
            self.progress_display.show_progress(message, None)

        # Get output filename from UI (implement this)
        output_filename = "documento_fusionado.pdf"

        result = self.pdf_processor.merge_pdfs(
            input_paths=self.selected_files,
            output_filename=output_filename,
            progress_callback=progress_callback
        )

        self.progress_display.hide_progress()
        self.statistics_panel.show_single_operation_stats(result, "fusión")

    def _process_split(self):
        """Process PDF split"""
        if not self.selected_files:
            return

        self.progress_display.show_progress("Iniciando división...", 0)

        def progress_callback(message: str):
            self.progress_display.show_progress(message, None)

        # Get page range from UI (implement this)
        start_page = 1
        end_page = None

        result = self.pdf_processor.split_pdf(
            input_path=self.selected_files[0],
            start_page=start_page,
            end_page=end_page,
            progress_callback=progress_callback
        )

        self.progress_display.hide_progress()
        self.statistics_panel.show_single_operation_stats(result, "división")

    def _clear_all(self, e):
        """Clear all selections and reset UI"""
        self.selected_files.clear()

        if self.file_selector:
            self.file_selector.clear_files()

        if self.statistics_panel.is_visible:
            self.statistics_panel.hide()

        self.progress_display.hide_progress()
        self.batch_progress_display.hide_progress()

        self._refresh_ui_components()

    def _open_file(self, file_path: Path):
        """Open file with default application"""
        success = self.file_manager.open_file(file_path)
        if not success:
            self._show_error(f"No se pudo abrir el archivo: {file_path.name}")

    def _open_folder(self, folder_path: Path):
        """Open folder in file explorer"""
        success = self.file_manager.open_folder(folder_path)
        if not success:
            self._show_error(f"No se pudo abrir la carpeta: {folder_path}")

    def _show_error(self, message: str):
        """Show error message"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=self.theme_manager.get_color('error')
            )
        )

    def _show_success(self, message: str):
        """Show success message"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=self.theme_manager.get_color('success')
            )
        )

    def _show_warning(self, message: str):
        """Show warning message"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=self.theme_manager.get_color('warning')
            )
        )

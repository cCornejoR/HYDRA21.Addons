"""
HYDRA21 Orthophoto Processor Pro - Tabbed Interface
Professional tabbed interface for different processing operations
"""

import flet as ft
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path

from ui.components.file_manager import FileManager
from ui.components.progress_display import ProgressDisplay
from ui.components.processing_options import ProcessingOptions
from ui.components.results_panel import ResultsPanel
from core.orthophoto_engine import OrthophotoProcessor
from core.opencv_processor import OpenCVProcessor
from config.settings import DirectoryConfig
import threading

class TabbedInterface(ft.Column):
    """Professional tabbed interface for orthophoto processing"""
    
    def __init__(self, page: ft.Page, theme: Dict[str, str]):
        self.page = page
        self.theme = theme
        
        # State
        self.current_tab = 0
        self.selected_files: List[Path] = []
        self.processing_results = None
        self.is_processing = False

        # Processing engines
        self.processor = OrthophotoProcessor()
        self.opencv_processor = OpenCVProcessor()

        # Determine which processor to use based on available libraries
        try:
            import rasterio
            self.use_opencv = False
            print("🗺️ Usando OrthophotoProcessor (GDAL/Rasterio disponible)")
        except ImportError:
            self.use_opencv = True
            print("📷 Usando OpenCVProcessor (GDAL/Rasterio no disponible)")
        
        # Components
        self.file_manager = None
        self.processing_options = None
        self.progress_display = None
        self.results_panel = None
        self.tabs_container = None
        
        self._setup_components()
        
        super().__init__(
            controls=self._build_layout(),
            spacing=0,
            expand=True
        )
    
    def _setup_components(self):
        """Setup tab components"""
        # File manager
        self.file_manager = FileManager(
            self.page,
            self.theme,
            on_files_selected=self._on_files_selected
        )
        
        # Processing options
        self.processing_options = ProcessingOptions(
            self.theme,
            on_process_start=self._on_process_start,
            page=self.page
        )
        
        # Progress display
        self.progress_display = ProgressDisplay(
            self.theme,
            show_spinner=True,
            show_progress_bar=True,
            show_details=True,
            show_statistics=True
        )
        
        # Results panel
        self.results_panel = ResultsPanel(
            self.page,
            self.theme
        )
        
        # Initially hide progress
        self.progress_display.visible = False
    
    def _build_layout(self) -> List[ft.Control]:
        """Build the tabbed interface layout"""
        # Create tab bar
        tab_bar = self._create_tab_bar()
        
        # Create content container
        content_container = ft.Container(
            content=self._get_current_tab_content(),
            bgcolor=self.theme['surface'],
            border_radius=ft.border_radius.only(
                bottom_left=12,
                bottom_right=12,
                top_right=12
            ),
            border=ft.border.all(1, self.theme['border']),
            padding=ft.padding.all(24),
            expand=True
        )
        
        return [
            tab_bar,
            content_container
        ]
    
    def _create_tab_bar(self) -> ft.Container:
        """Create the tab bar"""
        tabs = [
            {"icon": ft.Icons.FOLDER_OPEN, "text": "Archivos", "id": 0},
            {"icon": ft.Icons.SETTINGS, "text": "Opciones", "id": 1},
            {"icon": ft.Icons.PLAY_ARROW, "text": "Procesar", "id": 2},
            {"icon": ft.Icons.ASSESSMENT, "text": "Resultados", "id": 3}
        ]
        
        tab_buttons = []
        for tab in tabs:
            is_active = tab["id"] == self.current_tab
            
            # Determine if tab should be enabled
            enabled = True
            if tab["id"] == 1:  # Options tab
                enabled = len(self.selected_files) > 0
            elif tab["id"] == 2:  # Process tab
                enabled = len(self.selected_files) > 0
            elif tab["id"] == 3:  # Results tab
                enabled = self.processing_results is not None
            
            tab_button = self._create_tab_button(
                tab["icon"],
                tab["text"],
                tab["id"],
                is_active,
                enabled
            )
            tab_buttons.append(tab_button)
        
        return ft.Container(
            content=ft.Row(
                tab_buttons,
                spacing=0,
                alignment=ft.MainAxisAlignment.START
            ),
            padding=ft.padding.only(left=24, right=24, top=24)
        )
    
    def _create_tab_button(
        self,
        icon: str,
        text: str,
        tab_id: int,
        is_active: bool,
        enabled: bool
    ) -> ft.Container:
        """Create a tab button"""
        
        # Colors based on state
        if not enabled:
            bg_color = "transparent"
            text_color = self.theme['on_surface_variant']
            icon_color = self.theme['on_surface_variant']
            border_color = "transparent"
        elif is_active:
            bg_color = self.theme['surface']
            text_color = self.theme['primary']
            icon_color = self.theme['primary']
            border_color = self.theme['border']
        else:
            bg_color = "transparent"
            text_color = self.theme['on_surface_variant']
            icon_color = self.theme['on_surface_variant']
            border_color = "transparent"
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=icon_color, size=20),
                ft.Text(
                    text,
                    color=text_color,
                    size=14,
                    weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.NORMAL
                )
            ], spacing=8, tight=True),
            bgcolor=bg_color,
            border_radius=ft.border_radius.only(top_left=12, top_right=12),
            border=ft.border.only(
                left=ft.BorderSide(1, border_color),
                right=ft.BorderSide(1, border_color),
                top=ft.BorderSide(1, border_color)
            ) if is_active else None,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            on_click=lambda e, tid=tab_id: self._switch_tab(tid) if enabled else None,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )
    
    def _switch_tab(self, tab_id: int):
        """Switch to specified tab"""
        if tab_id != self.current_tab:
            self.current_tab = tab_id
            self._update_interface()
    
    def _get_current_tab_content(self) -> ft.Control:
        """Get content for current tab"""
        if self.current_tab == 0:  # Files
            return self.file_manager
        elif self.current_tab == 1:  # Options
            return self.processing_options
        elif self.current_tab == 2:  # Process
            return self._create_process_tab()
        elif self.current_tab == 3:  # Results
            return self.results_panel
        else:
            return ft.Text("Tab no encontrada")
    
    def _create_process_tab(self) -> ft.Column:
        """Create the processing tab content"""
        return ft.Column([
            # Header
            ft.Row([
                ft.Text(
                    "🚀 Procesamiento",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=self.theme['on_surface']
                )
            ]),
            
            # Processing summary
            self._create_processing_summary(),
            
            # Progress display
            self.progress_display,
            
            # Control buttons
            self._create_process_controls()
            
        ], spacing=24, expand=True)
    
    def _create_processing_summary(self) -> ft.Container:
        """Create processing summary"""
        if not self.selected_files:
            return ft.Container(
                content=ft.Text(
                    "No hay archivos seleccionados para procesar",
                    color=self.theme['on_surface_variant']
                )
            )
        
        # Get processing options
        options = self.processing_options.get_options()
        
        summary_items = [
            f"📁 {len(self.selected_files)} archivo(s) seleccionado(s)",
            f"📤 Formato de salida: {options.get('output_format', 'GeoTIFF')}",
            f"🗜️ Compresión: {options.get('compression', 'LZW')}",
            f"🎯 Perfil: {options.get('export_profile', 'Análisis GIS')}"
        ]
        
        if options.get('quality'):
            summary_items.append(f"⭐ Calidad: {options['quality']}%")
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Resumen del procesamiento:",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=self.theme['on_surface']
                ),
                ft.Column([
                    ft.Text(item, size=14, color=self.theme['on_surface_variant'])
                    for item in summary_items
                ], spacing=4)
            ], spacing=12),
            padding=ft.padding.all(16),
            bgcolor=self.theme['surface_variant'],
            border_radius=8,
            border=ft.border.all(1, self.theme['border'])
        )
    
    def _create_process_controls(self) -> ft.Row:
        """Create processing control buttons"""
        return ft.Row([
            ft.ElevatedButton(
                text="Iniciar Procesamiento",
                icon=ft.Icons.PLAY_ARROW,
                bgcolor=self.theme['primary'],
                color=self.theme['on_primary'],
                width=200,
                height=45,
                on_click=self._start_processing,
                disabled=len(self.selected_files) == 0
            ),
            ft.ElevatedButton(
                text="Cancelar",
                icon=ft.Icons.STOP,
                bgcolor=self.theme['error'],
                color=self.theme['on_primary'],
                width=120,
                height=45,
                on_click=self._cancel_processing,
                visible=False  # Initially hidden
            )
        ], spacing=16)
    
    def _on_files_selected(self, files: List[Path]):
        """Handle file selection"""
        self.selected_files = files
        self.processing_options.set_files(files)
        self._update_interface()
    
    def _on_process_start(self, options: Dict[str, Any]):
        """Handle process start from options tab"""
        # Switch to process tab
        self.current_tab = 2
        self._update_interface()
        
        # Start processing
        self._start_processing(None)
    
    def _start_processing(self, e):
        """Start the processing operation"""
        if not self.selected_files or self.is_processing:
            return

        self.is_processing = True

        # Show progress
        self.progress_display.visible = True
        self.progress_display.reset()
        self.progress_display.show_progress("Iniciando procesamiento...", 0)

        # Get processing options
        options = self.processing_options.get_options()

        # Get output directory
        output_dir = Path(options.get("output_directory", DirectoryConfig.get_output_dir()))

        # Choose processor and setup callbacks
        if self.use_opencv:
            # Use OpenCV processor
            current_processor = self.opencv_processor
            current_processor.set_progress_callback(
                lambda progress, message: self._on_progress_update(message, progress)
            )
            current_processor.set_statistics_callback(self._on_statistics_update)
        else:
            # Use GDAL/Rasterio processor
            current_processor = self.processor
            current_processor.set_callbacks(
                progress_callback=self._on_progress_update,
                statistics_callback=self._on_statistics_update,
                error_callback=self._on_error_update
            )

        # Start processing in background thread
        def process_files():
            try:
                if self.use_opencv:
                    # OpenCV processing
                    compression_method = self._get_opencv_compression_method(options.get("compression", "high_quality"))
                    results = current_processor.process_files(
                        input_files=self.selected_files,
                        output_dir=output_dir,
                        compression_method=compression_method,
                        quality=options.get("quality", 90),
                        preserve_metadata=options.get("preserve_crs", True),
                        max_workers=None  # Use optimal CPU count (75% of available cores)
                    )
                else:
                    # GDAL/Rasterio processing
                    results = current_processor.process_files(
                        input_files=self.selected_files,
                        output_dir=output_dir,
                        export_profile=options.get("export_profile", "gis_analysis"),
                        compression=self._get_compression_method(options.get("compression", "lossless")),
                        quality=options.get("quality"),
                        preserve_crs=options.get("preserve_crs", True),
                        max_workers=None  # Use optimal CPU count (75% of available cores)
                    )

                # Update results on main thread
                self.page.run_thread_safe(lambda: self._on_processing_complete(results, output_dir))

            except Exception as e:
                # Handle errors on main thread
                self.page.run_thread_safe(lambda: self._on_processing_error(str(e)))

        # Start processing thread
        import threading
        processing_thread = threading.Thread(target=process_files, daemon=True)
        processing_thread.start()

        self._update_interface()
    
    def _cancel_processing(self, e):
        """Cancel the processing operation"""
        if self.is_processing:
            self.processor.cancel_processing()
            self.is_processing = False
            self.progress_display.hide_progress()
            self._update_interface()

    def _get_compression_method(self, compression_preset: str) -> str:
        """Convert compression preset to actual compression method for GDAL"""
        compression_map = {
            "lossless": "LZW",
            "high": "DEFLATE",
            "medium": "JPEG",
            "low": "JPEG"
        }
        return compression_map.get(compression_preset, "LZW")

    def _get_opencv_compression_method(self, compression_preset: str) -> str:
        """Convert compression preset to OpenCV compression method"""
        opencv_compression_map = {
            "lossless": "lossless",
            "high": "high_quality",
            "medium": "medium",
            "low": "low"
        }
        return opencv_compression_map.get(compression_preset, "high_quality")

    def _on_progress_update(self, message: str, progress: float, details: str = ""):
        """Handle progress updates from processor"""
        def update_ui():
            if self.progress_display:
                self.progress_display.show_progress(message, progress, details)
            self.page.update()

        # Ensure UI update happens on main thread
        if hasattr(self.page, 'run_thread_safe'):
            self.page.run_thread_safe(update_ui)
        else:
            update_ui()

    def _on_statistics_update(self, stats: Dict[str, Any]):
        """Handle statistics updates from processor"""
        def update_ui():
            if self.progress_display:
                self.progress_display.update_statistics(stats)
            self.page.update()

        # Ensure UI update happens on main thread
        if hasattr(self.page, 'run_thread_safe'):
            self.page.run_thread_safe(update_ui)
        else:
            update_ui()

    def _on_error_update(self, error_message: str):
        """Handle error updates from processor"""
        def update_ui():
            # Show error in progress display
            if self.progress_display:
                self.progress_display.show_progress(
                    f"❌ Error: {error_message}",
                    None,
                    "Procesamiento detenido por error"
                )
            self.page.update()

        # Ensure UI update happens on main thread
        if hasattr(self.page, 'run_thread_safe'):
            self.page.run_thread_safe(update_ui)
        else:
            update_ui()

    def _on_processing_complete(self, results: Dict[str, Any], output_dir: Path):
        """Handle processing completion"""
        self.is_processing = False
        self.processing_results = results

        # Hide progress display
        self.progress_display.hide_progress()

        # Update results panel
        if self.results_panel:
            self.results_panel.set_results(results, output_dir)

        # Switch to results tab
        self.current_tab = 3
        self._update_interface()

    def _on_processing_error(self, error_message: str):
        """Handle processing errors"""
        self.is_processing = False

        # Show error message
        self.progress_display.show_progress(
            f"❌ Error crítico: {error_message}",
            None,
            "El procesamiento ha fallado"
        )

        self._update_interface()
    
    def _update_interface(self):
        """Update the entire interface"""
        # Rebuild layout
        self.controls.clear()
        self.controls.extend(self._build_layout())
        
        # Update page
        if hasattr(self.page, 'update'):
            self.page.update()
    
    def set_theme(self, new_theme: Dict[str, str]):
        """Update theme for all components"""
        self.theme = new_theme
        
        # Update component themes
        if self.file_manager:
            self.file_manager.set_theme(new_theme)
        if self.processing_options:
            self.processing_options.set_theme(new_theme)
        if self.progress_display:
            self.progress_display.set_theme(new_theme)
        if self.results_panel:
            self.results_panel.set_theme(new_theme)
        
        # Update interface
        self._update_interface()

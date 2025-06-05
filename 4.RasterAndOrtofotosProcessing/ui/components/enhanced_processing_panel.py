"""
HYDRA21 Orthophoto Processor Pro - Enhanced Processing Panel
Advanced processing interface with real-time logging, progress tracking, and testing capabilities
"""

import flet as ft
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any

from core.orthophoto_engine import OrthophotoProcessor
from utils.logger import get_logger
from config.settings import THEME_CONFIG

class EnhancedProcessingPanel(ft.Column):
    """Enhanced processing panel with comprehensive monitoring and controls"""
    
    def __init__(
        self,
        theme: Dict[str, str],
        on_files_selected: Optional[Callable] = None,
        page: Optional[ft.Page] = None
    ):
        super().__init__()
        self.theme = theme
        self.on_files_selected = on_files_selected
        self.page = page
        
        # Initialize components
        self.processor = OrthophotoProcessor(verbose=True)
        self.logger = get_logger()
        
        # Processing state
        self.is_processing = False
        self.current_files = []
        self.processing_thread = None
        
        # UI Components
        self._create_components()
        self._setup_layout()
        
        # Setup processor callbacks
        self.processor.set_callbacks(
            progress_callback=self._on_progress_update,
            statistics_callback=self._on_statistics_update,
            error_callback=self._on_error_update
        )
    
    def _create_components(self):
        """Create UI components"""
        
        # Header
        self.header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.ROCKET_LAUNCH, color=self.theme["primary"], size=24),
                ft.Text(
                    "Procesamiento Avanzado",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=self.theme["on_surface"]
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.icons.HELP_OUTLINE,
                    tooltip="Ayuda sobre procesamiento",
                    on_click=self._show_help
                )
            ]),
            padding=ft.padding.all(16),
            bgcolor=self.theme["surface_variant"],
            border_radius=8
        )
        
        # File selection area
        self.file_picker = ft.FilePicker(on_result=self._on_files_picked)
        
        self.file_selection_area = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton(
                        "Seleccionar Archivos",
                        icon=ft.icons.FOLDER_OPEN,
                        on_click=lambda _: self.file_picker.pick_files(
                            dialog_title="Seleccionar archivos para procesar",
                            file_type=ft.FilePickerFileType.CUSTOM,
                            allowed_extensions=["tif", "tiff", "ecw", "jp2", "img"]
                        ),
                        bgcolor=self.theme["primary"],
                        color=self.theme["on_primary"]
                    ),
                    ft.ElevatedButton(
                        "Test de Procesamiento",
                        icon=ft.icons.SCIENCE,
                        on_click=self._run_processing_test,
                        bgcolor=self.theme["secondary"],
                        color=self.theme["on_primary"]
                    )
                ]),
                ft.Divider(),
                self._create_files_list()
            ]),
            padding=ft.padding.all(16),
            bgcolor=self.theme["surface"],
            border_radius=8,
            border=ft.border.all(1, self.theme["border"])
        )
        
        # Processing controls
        self.processing_controls = ft.Container(
            content=ft.Row([
                ft.ElevatedButton(
                    "Iniciar Procesamiento",
                    icon=ft.icons.PLAY_ARROW,
                    on_click=self._start_processing,
                    bgcolor=self.theme["success"],
                    color="white",
                    disabled=True
                ),
                ft.ElevatedButton(
                    "Pausar",
                    icon=ft.icons.PAUSE,
                    on_click=self._pause_processing,
                    disabled=True
                ),
                ft.ElevatedButton(
                    "Cancelar",
                    icon=ft.icons.STOP,
                    on_click=self._cancel_processing,
                    bgcolor=self.theme["error"],
                    color="white",
                    disabled=True
                ),
                ft.Container(expand=True),
                ft.Text(
                    "Estado: Listo",
                    color=self.theme["on_surface_variant"]
                )
            ]),
            padding=ft.padding.all(16),
            bgcolor=self.theme["surface_variant"],
            border_radius=8
        )
        
        # Progress section
        self.progress_section = self._create_progress_section()
        
        # Log viewer
        self.log_viewer = self._create_log_viewer()
        
        # Statistics panel
        self.statistics_panel = self._create_statistics_panel()
    
    def _create_files_list(self) -> ft.Container:
        """Create files list display"""
        self.files_list = ft.ListView(
            height=150,
            spacing=4
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Archivos seleccionados:",
                    weight=ft.FontWeight.BOLD,
                    color=self.theme["on_surface"]
                ),
                self.files_list
            ]),
            visible=False
        )
    
    def _create_progress_section(self) -> ft.Container:
        """Create progress tracking section"""
        self.overall_progress = ft.ProgressBar(
            value=0,
            bgcolor=self.theme["surface_variant"],
            color=self.theme["primary"]
        )
        
        self.current_file_progress = ft.ProgressBar(
            value=0,
            bgcolor=self.theme["surface_variant"],
            color=self.theme["secondary"]
        )
        
        self.progress_text = ft.Text(
            "Esperando...",
            color=self.theme["on_surface_variant"]
        )
        
        self.current_file_text = ft.Text(
            "",
            color=self.theme["on_surface_variant"]
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Progreso General",
                    weight=ft.FontWeight.BOLD,
                    color=self.theme["on_surface"]
                ),
                self.overall_progress,
                self.progress_text,
                ft.Divider(),
                ft.Text(
                    "Archivo Actual",
                    weight=ft.FontWeight.BOLD,
                    color=self.theme["on_surface"]
                ),
                self.current_file_progress,
                self.current_file_text
            ]),
            padding=ft.padding.all(16),
            bgcolor=self.theme["surface"],
            border_radius=8,
            border=ft.border.all(1, self.theme["border"]),
            visible=False
        )
    
    def _create_log_viewer(self) -> ft.Container:
        """Create log viewer component"""
        self.log_text = ft.ListView(
            height=200,
            spacing=2,
            auto_scroll=True
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        "Registro de Procesamiento",
                        weight=ft.FontWeight.BOLD,
                        color=self.theme["on_surface"]
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.icons.CLEAR,
                        tooltip="Limpiar registro",
                        on_click=self._clear_log
                    )
                ]),
                self.log_text
            ]),
            padding=ft.padding.all(16),
            bgcolor=self.theme["surface"],
            border_radius=8,
            border=ft.border.all(1, self.theme["border"]),
            visible=False
        )
    
    def _create_statistics_panel(self) -> ft.Container:
        """Create statistics display panel"""
        self.stats_content = ft.Column([
            ft.Text(
                "Estadísticas de Procesamiento",
                weight=ft.FontWeight.BOLD,
                color=self.theme["on_surface"]
            ),
            ft.Text("No hay datos disponibles", color=self.theme["on_surface_variant"])
        ])
        
        return ft.Container(
            content=self.stats_content,
            padding=ft.padding.all(16),
            bgcolor=self.theme["surface"],
            border_radius=8,
            border=ft.border.all(1, self.theme["border"]),
            visible=False
        )
    
    def _setup_layout(self):
        """Setup the main layout"""
        self.controls = [
            self.header,
            self.file_selection_area,
            self.processing_controls,
            self.progress_section,
            self.log_viewer,
            self.statistics_panel
        ]
        
        # Add file picker to page overlay
        if self.page:
            self.page.overlay.append(self.file_picker)
    
    def _on_files_picked(self, e: ft.FilePickerResultEvent):
        """Handle file selection"""
        if e.files:
            self.current_files = [Path(f.path) for f in e.files]
            self._update_files_list()
            self._enable_processing_controls()
            self._add_log_entry(f"📁 Seleccionados {len(self.current_files)} archivo(s)")
    
    def _update_files_list(self):
        """Update the files list display"""
        self.files_list.controls.clear()
        
        for file_path in self.current_files:
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            
            file_item = ft.ListTile(
                leading=ft.Icon(ft.icons.INSERT_DRIVE_FILE, color=self.theme["primary"]),
                title=ft.Text(file_path.name, color=self.theme["on_surface"]),
                subtitle=ft.Text(f"{file_size:.2f} MB", color=self.theme["on_surface_variant"]),
                trailing=ft.IconButton(
                    icon=ft.icons.REMOVE_CIRCLE_OUTLINE,
                    tooltip="Remover archivo",
                    on_click=lambda _, path=file_path: self._remove_file(path)
                )
            )
            self.files_list.controls.append(file_item)
        
        self.file_selection_area.content.controls[2].visible = len(self.current_files) > 0
        
        if self.page:
            self.page.update()
    
    def _remove_file(self, file_path: Path):
        """Remove file from selection"""
        if file_path in self.current_files:
            self.current_files.remove(file_path)
            self._update_files_list()
            
            if not self.current_files:
                self._disable_processing_controls()
    
    def _enable_processing_controls(self):
        """Enable processing controls"""
        self.processing_controls.content.controls[0].disabled = False  # Start button
        if self.page:
            self.page.update()
    
    def _disable_processing_controls(self):
        """Disable processing controls"""
        self.processing_controls.content.controls[0].disabled = True  # Start button
        if self.page:
            self.page.update()
    
    def _add_log_entry(self, message: str, level: str = "info"):
        """Add entry to log viewer"""
        timestamp = time.strftime("%H:%M:%S")
        
        # Color based on level
        color = self.theme["on_surface"]
        if level == "error":
            color = self.theme["error"]
        elif level == "warning":
            color = self.theme["warning"]
        elif level == "success":
            color = self.theme["success"]
        
        log_entry = ft.Text(
            f"[{timestamp}] {message}",
            color=color,
            size=12
        )
        
        self.log_text.controls.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.log_text.controls) > 100:
            self.log_text.controls.pop(0)
        
        if self.page:
            self.page.update()
    
    def _clear_log(self, e):
        """Clear log viewer"""
        self.log_text.controls.clear()
        if self.page:
            self.page.update()
    
    def _show_help(self, e):
        """Show help dialog"""
        help_dialog = ft.AlertDialog(
            title=ft.Text("Ayuda - Procesamiento Avanzado"),
            content=ft.Text(
                "1. Seleccione archivos usando 'Seleccionar Archivos'\n"
                "2. Use 'Test de Procesamiento' para verificar funcionalidad\n"
                "3. Haga clic en 'Iniciar Procesamiento' para comenzar\n"
                "4. Monitoree el progreso en tiempo real\n"
                "5. Revise los logs para detalles del procesamiento"
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self._close_dialog(help_dialog))
            ]
        )
        
        if self.page:
            self.page.dialog = help_dialog
            help_dialog.open = True
            self.page.update()
    
    def _close_dialog(self, dialog):
        """Close dialog"""
        dialog.open = False
        if self.page:
            self.page.update()

    def _run_processing_test(self, e):
        """Run processing test"""
        self._add_log_entry("🧪 Iniciando test de procesamiento...", "info")

        def run_test():
            try:
                result = self.processor.test_processing()

                if result["success"]:
                    self._add_log_entry("✅ Test de procesamiento exitoso", "success")
                    self._show_test_results(result["results"])
                else:
                    self._add_log_entry(f"❌ Test falló: {result['error']}", "error")

            except Exception as ex:
                self._add_log_entry(f"❌ Error en test: {str(ex)}", "error")

        # Run test in background thread
        test_thread = threading.Thread(target=run_test)
        test_thread.daemon = True
        test_thread.start()

    def _show_test_results(self, results: Dict[str, Any]):
        """Show test results in dialog"""
        processed = len(results.get("processed_files", []))
        failed = len(results.get("failed_files", []))
        time_taken = results.get("processing_time", 0)

        result_text = f"""
Test de Procesamiento Completado:

✅ Archivos procesados: {processed}
❌ Archivos fallidos: {failed}
⏱️ Tiempo: {time_taken:.2f} segundos

Métodos de compresión disponibles:
{', '.join(results.get('compression_methods_used', {}).keys()) or 'Ninguno'}
        """

        test_dialog = ft.AlertDialog(
            title=ft.Text("Resultados del Test"),
            content=ft.Text(result_text),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self._close_dialog(test_dialog))
            ]
        )

        if self.page:
            self.page.dialog = test_dialog
            test_dialog.open = True
            self.page.update()

    def _start_processing(self, e):
        """Start processing files"""
        if not self.current_files:
            self._add_log_entry("❌ No hay archivos seleccionados", "error")
            return

        if self.is_processing:
            self._add_log_entry("⚠️ Procesamiento ya en curso", "warning")
            return

        self.is_processing = True
        self._update_processing_state(True)

        # Show progress sections
        self.progress_section.visible = True
        self.log_viewer.visible = True
        self.statistics_panel.visible = True

        if self.page:
            self.page.update()

        self._add_log_entry(f"🚀 Iniciando procesamiento de {len(self.current_files)} archivo(s)", "info")

        # Start processing in background thread
        self.processing_thread = threading.Thread(target=self._process_files_background)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def _process_files_background(self):
        """Background processing method"""
        try:
            # Get output directory (you might want to make this configurable)
            output_dir = Path("./output")

            # Process files
            results = self.processor.process_files(
                input_files=self.current_files,
                output_dir=output_dir,
                compression="LZW",
                quality=85
            )

            # Update UI with results
            self._on_processing_complete(results)

        except Exception as e:
            self._add_log_entry(f"❌ Error crítico: {str(e)}", "error")
            self._on_processing_complete(None)

    def _pause_processing(self, e):
        """Pause processing"""
        # Implementation depends on processor capabilities
        self._add_log_entry("⏸️ Pausa solicitada", "warning")

    def _cancel_processing(self, e):
        """Cancel processing"""
        if self.is_processing:
            self.processor.is_processing = False
            self._add_log_entry("🛑 Cancelación solicitada", "warning")

    def _update_processing_state(self, processing: bool):
        """Update UI based on processing state"""
        controls = self.processing_controls.content.controls

        # Start button
        controls[0].disabled = processing
        # Pause button
        controls[1].disabled = not processing
        # Cancel button
        controls[2].disabled = not processing

        # Status text
        status_text = "Procesando..." if processing else "Listo"
        controls[4].value = f"Estado: {status_text}"

        if self.page:
            self.page.update()

    def _on_progress_update(self, message: str, progress: float, details: str = ""):
        """Handle progress updates from processor"""
        # Update progress bars
        self.overall_progress.value = progress / 100.0
        self.progress_text.value = message

        if details:
            self.current_file_text.value = details

        # Add to log
        self._add_log_entry(f"📊 {message} ({progress:.1f}%)")

        if self.page:
            self.page.update()

    def _on_statistics_update(self, stats: Dict[str, Any]):
        """Handle statistics updates from processor"""
        # Update statistics panel
        stats_text = []

        if "files_processed" in stats:
            stats_text.append(f"📁 Archivos procesados: {stats['files_processed']}/{stats.get('total_files', 0)}")

        if "processing_speed" in stats:
            stats_text.append(f"⚡ Velocidad: {stats['processing_speed']:.1f} MB/s")

        if "current_file" in stats:
            stats_text.append(f"📄 Archivo actual: {stats['current_file']}")

        # Update UI
        self.stats_content.controls = [
            ft.Text(
                "Estadísticas de Procesamiento",
                weight=ft.FontWeight.BOLD,
                color=self.theme["on_surface"]
            )
        ]

        for stat in stats_text:
            self.stats_content.controls.append(
                ft.Text(stat, color=self.theme["on_surface_variant"])
            )

        if self.page:
            self.page.update()

    def _on_error_update(self, error_message: str):
        """Handle error updates from processor"""
        self._add_log_entry(f"❌ {error_message}", "error")

    def _on_processing_complete(self, results: Optional[Dict[str, Any]]):
        """Handle processing completion"""
        self.is_processing = False
        self._update_processing_state(False)

        if results:
            processed = len(results.get("processed_files", []))
            failed = len(results.get("failed_files", []))
            time_taken = results.get("processing_time", 0)

            self._add_log_entry(f"🎉 Procesamiento completado: {processed} exitosos, {failed} fallidos en {time_taken:.2f}s", "success")

            # Show completion dialog
            self._show_completion_dialog(results)
        else:
            self._add_log_entry("❌ Procesamiento terminado con errores", "error")

    def _show_completion_dialog(self, results: Dict[str, Any]):
        """Show processing completion dialog"""
        processed = len(results.get("processed_files", []))
        failed = len(results.get("failed_files", []))
        time_taken = results.get("processing_time", 0)
        compression_ratio = results.get("compression_ratio", 0)

        result_text = f"""
Procesamiento Completado:

✅ Archivos procesados: {processed}
❌ Archivos fallidos: {failed}
⏱️ Tiempo total: {time_taken:.2f} segundos
🗜️ Ratio de compresión: {compression_ratio:.1f}%

¿Desea abrir la carpeta de salida?
        """

        completion_dialog = ft.AlertDialog(
            title=ft.Text("Procesamiento Completado"),
            content=ft.Text(result_text),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self._close_dialog(completion_dialog)),
                ft.ElevatedButton(
                    "Abrir Carpeta",
                    icon=ft.icons.FOLDER_OPEN,
                    on_click=lambda _: self._open_output_folder()
                )
            ]
        )

        if self.page:
            self.page.dialog = completion_dialog
            completion_dialog.open = True
            self.page.update()

    def _open_output_folder(self):
        """Open output folder in file explorer"""
        import subprocess
        import platform

        output_dir = Path("./output")

        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(output_dir)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(output_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(output_dir)])

            self._add_log_entry("📂 Carpeta de salida abierta", "success")
        except Exception as e:
            self._add_log_entry(f"❌ No se pudo abrir carpeta: {e}", "error")

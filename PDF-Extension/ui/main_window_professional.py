"""
HYDRA21 PDF Compressor Pro - Professional Main Window
Complete PDF processing application with advanced features and modern UI
"""

import flet as ft
import threading
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Core imports
from config.settings import get_app_config, DirectoryConfig, GS_QUALITY_PRESETS
from config.ghostscript_config import GhostscriptConfig
from core.ghostscript_manager import GhostscriptManager
from core.pdf_processor import PDFProcessor, BatchProgress
from core.file_manager import FileManager

class MainWindow(ft.Column):
    """Professional PDF Compressor Main Window"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        
        # Load configuration
        self.config = get_app_config()
        self.dir_config = DirectoryConfig.get_default()
        self.dir_config.ensure_directories()
        
        # Initialize managers
        self.gs_config = GhostscriptConfig(self.dir_config.config_dir)
        self.file_manager = FileManager(
            supported_extensions=self.config['files']['supported_extensions'],
            max_file_size_mb=self.config['files']['max_file_size_mb']
        )
        
        # Initialize processors
        self.gs_manager = None
        self.pdf_processor = None
        
        # UI state
        self.current_operation = "compress"
        self.selected_files: List[Path] = []
        self.is_processing = False
        self.is_dark_mode = False
        self.processing_stats = {}
        
        # UI components
        self.file_picker = None
        self.quality_dropdown = None
        self.progress_container = None
        self.results_panel = None
        self.theme_toggle = None
        
        # Setup
        self._setup_ghostscript()
        self._setup_ui()
        
        # Initialize Column
        super().__init__(
            controls=self._build_layout(),
            spacing=0,
            expand=True
        )
    
    def _setup_ghostscript(self):
        """Setup Ghostscript configuration"""
        try:
            gs_info = self.gs_config.get_ghostscript_info()
            if gs_info['verified']:
                self.gs_manager = GhostscriptManager(gs_info['path'])
                self.pdf_processor = PDFProcessor(self.gs_manager, self.dir_config.output_dir)
                print("✅ Ghostscript configurado correctamente")
            else:
                print("⚠️ Ghostscript no encontrado - funcionalidad limitada")
        except Exception as e:
            print(f"⚠️ Error configurando Ghostscript: {e}")
    
    def _setup_ui(self):
        """Setup UI components"""
        # File picker
        self.file_picker = ft.FilePicker(on_result=self._on_files_selected)
        self.page.overlay.append(self.file_picker)
        
        # Quality dropdown
        self.quality_dropdown = ft.Dropdown(
            label="Calidad de Compresión",
            value="medium",
            options=[
                ft.dropdown.Option("high", "Alta Calidad - Máxima calidad para impresión"),
                ft.dropdown.Option("medium", "Calidad Media - Balance óptimo"),
                ft.dropdown.Option("low", "Baja Calidad - Máxima compresión"),
            ],
            width=400,
            bgcolor="#ffffff",
            border_color="#e2e8f0"
        )
        
        # Theme toggle
        self.theme_toggle = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Cambiar a modo oscuro",
            on_click=self._toggle_theme,
            icon_color="#64748b"
        )
    
    def _build_layout(self):
        """Build the main layout"""
        return [
            self._create_header(),
            self._create_main_content()
        ]
    
    def _create_header(self):
        """Create application header"""
        return ft.Container(
            content=ft.Row([
                # Logo and title
                ft.Row([
                    ft.Icon(ft.Icons.PICTURE_AS_PDF, color="#2563eb", size=32),
                    ft.Column([
                        ft.Text(
                            "HYDRA21 PDF Compressor Pro",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color="#2563eb"
                        ),
                        ft.Text(
                            "Procesamiento Profesional de PDFs",
                            size=14,
                            color="#64748b"
                        )
                    ], spacing=2)
                ], spacing=16),
                
                # Header actions
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.HELP_OUTLINE,
                        tooltip="Ayuda y Tutorial",
                        on_click=self._show_help,
                        icon_color="#64748b"
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        tooltip="Configuración",
                        on_click=self._show_settings,
                        icon_color="#64748b"
                    ),
                    self.theme_toggle
                ], spacing=8)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(24),
            bgcolor="#f8fafc" if not self.is_dark_mode else "#1e293b",
            border=ft.border.only(bottom=ft.BorderSide(2, "#e2e8f0"))
        )
    
    def _create_main_content(self):
        """Create main content area"""
        return ft.Container(
            content=ft.Column([
                # Operation tabs
                self._create_operation_tabs(),
                
                # Main processing area
                ft.Container(
                    content=ft.Column([
                        # File selection section
                        self._create_file_section(),
                        
                        # Settings section
                        self._create_settings_section(),
                        
                        # Action buttons
                        self._create_action_section(),
                        
                        # Progress section
                        self._create_progress_section(),
                        
                        # Results section
                        self._create_results_section()
                        
                    ], spacing=32),
                    padding=ft.padding.symmetric(horizontal=40, vertical=32),
                    expand=True
                )
            ], spacing=0),
            expand=True,
            bgcolor="#ffffff" if not self.is_dark_mode else "#0f172a"
        )
    
    def _create_operation_tabs(self):
        """Create operation selection tabs"""
        return ft.Container(
            content=ft.Tabs(
                tabs=[
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
                ],
                selected_index=0,
                on_change=self._on_operation_changed,
                indicator_color="#2563eb",
                label_color="#2563eb",
                unselected_label_color="#64748b"
            ),
            bgcolor="#f8fafc" if not self.is_dark_mode else "#1e293b",
            padding=ft.padding.symmetric(horizontal=24, vertical=16)
        )
    
    def _create_file_section(self):
        """Create file selection section"""
        return self._create_card([
            ft.Row([
                ft.Icon(ft.Icons.FOLDER_OPEN, color="#2563eb", size=24),
                ft.Text(
                    "Selección de Archivos",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color="#1e293b" if not self.is_dark_mode else "#f1f5f9"
                )
            ], spacing=12),
            
            ft.Container(height=16),
            
            # File selection area with drag-and-drop
            ft.Container(
                content=ft.Column([
                    ft.ElevatedButton(
                        text="Seleccionar Archivos PDF",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=self._select_files,
                        style=ft.ButtonStyle(
                            bgcolor="#2563eb",
                            color="white",
                            padding=ft.padding.symmetric(horizontal=24, vertical=16)
                        )
                    ),
                    ft.Container(height=12),
                    ft.Text(
                        "O arrastra archivos PDF aquí",
                        size=14,
                        color="#64748b",
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=16),
                    self._create_file_list()
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=24,
                border=ft.border.all(2, "#e2e8f0"),
                border_radius=12,
                bgcolor="#f8fafc" if not self.is_dark_mode else "#1e293b"
            )
        ])
    
    def _create_settings_section(self):
        """Create settings section"""
        if self.current_operation == "compress":
            return self._create_card([
                ft.Row([
                    ft.Icon(ft.Icons.TUNE, color="#2563eb", size=24),
                    ft.Text(
                        "Configuración de Compresión",
                        size=18,
                        weight=ft.FontWeight.W_600,
                        color="#1e293b" if not self.is_dark_mode else "#f1f5f9"
                    )
                ], spacing=12),
                
                ft.Container(height=16),
                self.quality_dropdown
            ])
        return ft.Container()
    
    def _create_action_section(self):
        """Create action buttons section"""
        if not self.gs_manager:
            return self._create_card([
                ft.Row([
                    ft.Icon(ft.Icons.WARNING, color="#f59e0b", size=24),
                    ft.Column([
                        ft.Text(
                            "Ghostscript no configurado",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color="#f59e0b"
                        ),
                        ft.Text(
                            "Instala Ghostscript para funcionalidad completa",
                            size=14,
                            color="#64748b"
                        )
                    ], spacing=4, expand=True),
                    ft.ElevatedButton(
                        text="Configurar",
                        icon=ft.Icons.SETTINGS,
                        on_click=self._show_help,
                        style=ft.ButtonStyle(bgcolor="#f59e0b", color="white")
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ])
        
        return ft.Row([
            ft.ElevatedButton(
                text=self._get_action_text(),
                icon=self._get_action_icon(),
                on_click=self._start_processing,
                disabled=not self.selected_files or self.is_processing,
                style=ft.ButtonStyle(
                    bgcolor="#2563eb",
                    color="white",
                    padding=ft.padding.symmetric(horizontal=32, vertical=16)
                )
            ),
            ft.ElevatedButton(
                text="Limpiar",
                icon=ft.Icons.CLEAR,
                on_click=self._clear_all,
                disabled=self.is_processing,
                style=ft.ButtonStyle(
                    bgcolor="#f1f5f9",
                    color="#2563eb",
                    padding=ft.padding.symmetric(horizontal=24, vertical=16)
                )
            )
        ], spacing=16, alignment=ft.MainAxisAlignment.CENTER)
    
    def _create_progress_section(self):
        """Create progress indicators section"""
        self.progress_container = ft.Container(
            content=ft.Column([
                # Single file progress
                ft.Container(
                    content=ft.Column([
                        ft.Text("", size=14, color="#2563eb"),
                        ft.ProgressBar(visible=False, color="#2563eb")
                    ], spacing=8),
                    visible=False
                ),
                
                # Batch progress
                ft.Container(
                    content=ft.Column([
                        ft.Text("", size=14, color="#2563eb"),
                        ft.Row([
                            ft.ProgressRing(visible=False, color="#2563eb", width=20, height=20),
                            ft.Text("", size=12, color="#64748b")
                        ], spacing=8)
                    ], spacing=8),
                    visible=False
                )
            ], spacing=16),
            visible=False
        )
        return self.progress_container
    
    def _create_results_section(self):
        """Create results panel"""
        self.results_panel = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="#059669", size=24),
                    ft.Text(
                        "Resultados del Procesamiento",
                        size=18,
                        weight=ft.FontWeight.W_600,
                        color="#1e293b" if not self.is_dark_mode else "#f1f5f9"
                    )
                ], spacing=12),
                
                ft.Container(height=16),
                
                # Statistics will be added here dynamically
                ft.Column([], spacing=8),
                
                ft.Container(height=16),
                
                # Action buttons
                ft.Row([
                    ft.ElevatedButton(
                        text="Abrir Archivo",
                        icon=ft.Icons.OPEN_IN_NEW,
                        on_click=self._open_result_file,
                        style=ft.ButtonStyle(bgcolor="#059669", color="white")
                    ),
                    ft.ElevatedButton(
                        text="Mostrar en Carpeta",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=self._show_in_folder,
                        style=ft.ButtonStyle(bgcolor="#3b82f6", color="white")
                    ),
                    ft.ElevatedButton(
                        text="Procesar Más",
                        icon=ft.Icons.ADD,
                        on_click=self._process_more,
                        style=ft.ButtonStyle(bgcolor="#2563eb", color="white")
                    )
                ], spacing=12, alignment=ft.MainAxisAlignment.CENTER)
            ]),
            padding=24,
            bgcolor="#ecfdf5" if not self.is_dark_mode else "#064e3b",
            border_radius=12,
            border=ft.border.all(1, "#a7f3d0"),
            visible=False
        )
        return self.results_panel

    def _create_card(self, content):
        """Create a styled card container"""
        return ft.Container(
            content=ft.Column(content, spacing=0),
            padding=24,
            bgcolor="#ffffff" if not self.is_dark_mode else "#1e293b",
            border_radius=12,
            border=ft.border.all(1, "#e2e8f0"),
            width=800,
            margin=ft.margin.only(bottom=24)
        )

    def _create_file_list(self):
        """Create file list display"""
        if not self.selected_files:
            return ft.Text(
                "No hay archivos seleccionados",
                size=14,
                color="#64748b",
                text_align=ft.TextAlign.CENTER
            )

        file_items = []
        for i, file_path in enumerate(self.selected_files):
            file_items.append(
                ft.Row([
                    ft.Icon(ft.Icons.PICTURE_AS_PDF, color="#dc2626", size=20),
                    ft.Text(
                        file_path.name,
                        size=14,
                        color="#1e293b" if not self.is_dark_mode else "#f1f5f9",
                        expand=True
                    ),
                    ft.Text(
                        f"{file_path.stat().st_size / (1024*1024):.1f} MB",
                        size=12,
                        color="#64748b"
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=16,
                        on_click=lambda e, idx=i: self._remove_file(idx),
                        icon_color="#dc2626"
                    )
                ], spacing=8)
            )

        return ft.Column([
            ft.Text(
                f"✅ {len(self.selected_files)} archivo(s) seleccionado(s)",
                size=14,
                weight=ft.FontWeight.W_500,
                color="#059669"
            ),
            ft.Container(height=8),
            ft.Column(file_items, spacing=4)
        ])

    # Event handlers
    def _on_files_selected(self, e):
        """Handle file selection"""
        if e.files:
            self.selected_files = [Path(f.path) for f in e.files]
            self.update()

    def _on_operation_changed(self, e):
        """Handle operation tab change"""
        operations = ["compress", "merge", "split"]
        self.current_operation = operations[e.control.selected_index]
        self.update()

    def _select_files(self, e):
        """Open file picker"""
        self.file_picker.pick_files(
            allow_multiple=self.current_operation != "split",
            allowed_extensions=["pdf"]
        )

    def _remove_file(self, index):
        """Remove file from selection"""
        if 0 <= index < len(self.selected_files):
            self.selected_files.pop(index)
            self.update()

    def _toggle_theme(self, e):
        """Toggle between light and dark theme"""
        self.is_dark_mode = not self.is_dark_mode
        self.theme_toggle.icon = ft.Icons.LIGHT_MODE if self.is_dark_mode else ft.Icons.DARK_MODE
        self.theme_toggle.tooltip = "Cambiar a modo claro" if self.is_dark_mode else "Cambiar a modo oscuro"

        # Update page theme
        self.page.theme_mode = ft.ThemeMode.DARK if self.is_dark_mode else ft.ThemeMode.LIGHT
        self.page.update()
        self.update()

    def _start_processing(self, e):
        """Start PDF processing"""
        if not self.selected_files or not self.gs_manager:
            return

        self.is_processing = True
        self.results_panel.visible = False
        self._show_progress("Iniciando procesamiento...")

        # Start processing in background thread
        threading.Thread(target=self._process_files, daemon=True).start()
        self.update()

    def _process_files(self):
        """Process files in background thread"""
        try:
            start_time = time.time()

            if self.current_operation == "compress":
                self._process_compression()
            elif self.current_operation == "merge":
                self._process_merge()
            elif self.current_operation == "split":
                self._process_split()

            # Calculate processing time
            processing_time = time.time() - start_time
            self.processing_stats['processing_time'] = processing_time

            # Show results
            self._show_results()

        except Exception as e:
            self._show_error(f"Error durante el procesamiento: {str(e)}")
        finally:
            self.is_processing = False
            self._hide_progress()
            self.update()

    def _process_compression(self):
        """Process PDF compression"""
        quality = self.quality_dropdown.value
        total_original_size = 0
        total_compressed_size = 0

        for i, file_path in enumerate(self.selected_files):
            self._update_progress(f"Comprimiendo {file_path.name}...", i + 1, len(self.selected_files))

            original_size = file_path.stat().st_size
            total_original_size += original_size

            # Simulate compression (replace with actual Ghostscript call)
            result = self.pdf_processor.compress_single_pdf(
                input_path=file_path,
                quality=quality,
                progress_callback=lambda msg: self._update_progress(msg, i + 1, len(self.selected_files))
            )

            if result.success:
                compressed_size = result.output_path.stat().st_size
                total_compressed_size += compressed_size

        # Store statistics
        self.processing_stats = {
            'operation': 'compression',
            'files_processed': len(self.selected_files),
            'original_size': total_original_size,
            'final_size': total_compressed_size,
            'compression_ratio': ((total_original_size - total_compressed_size) / total_original_size) * 100,
            'space_saved': total_original_size - total_compressed_size
        }

    def _process_merge(self):
        """Process PDF merge"""
        self._update_progress("Fusionando archivos PDF...", 1, 1)

        # Simulate merge (replace with actual implementation)
        result = self.pdf_processor.merge_pdfs(
            input_paths=self.selected_files,
            output_filename="documento_fusionado.pdf"
        )

        if result.success:
            self.processing_stats = {
                'operation': 'merge',
                'files_processed': len(self.selected_files),
                'output_file': result.output_path
            }

    def _process_split(self):
        """Process PDF split"""
        if self.selected_files:
            file_path = self.selected_files[0]
            self._update_progress(f"Dividiendo {file_path.name}...", 1, 1)

            # Simulate split (replace with actual implementation)
            result = self.pdf_processor.split_pdf(
                input_path=file_path,
                start_page=1,
                end_page=None
            )

            if result.success:
                self.processing_stats = {
                    'operation': 'split',
                    'files_processed': 1,
                    'output_dir': result.output_path
                }

    def _show_progress(self, message):
        """Show progress indicator"""
        self.progress_container.visible = True
        progress_text = self.progress_container.content.controls[0].content.controls[0]
        progress_bar = self.progress_container.content.controls[0].content.controls[1]

        progress_text.value = message
        progress_bar.visible = True
        self.progress_container.content.controls[0].visible = True
        self.update()

    def _update_progress(self, message, current=None, total=None):
        """Update progress with batch information"""
        if current and total:
            batch_container = self.progress_container.content.controls[1]
            batch_text = batch_container.content.controls[0]
            batch_ring = batch_container.content.controls[1].controls[0]
            batch_info = batch_container.content.controls[1].controls[1]

            batch_text.value = message
            batch_ring.visible = True
            batch_info.value = f"Archivo {current} de {total}"
            batch_container.visible = True

        self.update()

    def _hide_progress(self):
        """Hide progress indicators"""
        self.progress_container.visible = False
        self.update()

    def _show_results(self):
        """Show processing results"""
        stats = self.processing_stats
        results_content = self.results_panel.content.controls[2]  # Statistics column
        results_content.controls.clear()

        if stats.get('operation') == 'compression':
            results_content.controls.extend([
                ft.Row([
                    ft.Text("Archivos procesados:", weight=ft.FontWeight.W_500),
                    ft.Text(str(stats['files_processed']), color="#2563eb")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Tamaño original:", weight=ft.FontWeight.W_500),
                    ft.Text(f"{stats['original_size'] / (1024*1024):.1f} MB", color="#64748b")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Tamaño comprimido:", weight=ft.FontWeight.W_500),
                    ft.Text(f"{stats['final_size'] / (1024*1024):.1f} MB", color="#059669")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Ratio de compresión:", weight=ft.FontWeight.W_500),
                    ft.Text(f"{stats['compression_ratio']:.1f}%", color="#2563eb", weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Espacio ahorrado:", weight=ft.FontWeight.W_500),
                    ft.Text(f"{stats['space_saved'] / (1024*1024):.1f} MB", color="#059669", weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Tiempo de procesamiento:", weight=ft.FontWeight.W_500),
                    ft.Text(f"{stats['processing_time']:.1f}s", color="#64748b")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ])

        self.results_panel.visible = True
        self.update()

    def _show_error(self, message):
        """Show error message"""
        # Create error snackbar
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message, color="white"),
                bgcolor="#dc2626"
            )
        )

    def _clear_all(self, e):
        """Clear all selections and reset UI"""
        self.selected_files.clear()
        self.results_panel.visible = False
        self.progress_container.visible = False
        self.update()

    def _get_action_text(self):
        """Get action button text based on operation"""
        texts = {
            "compress": "Comprimir PDFs",
            "merge": "Fusionar PDFs",
            "split": "Dividir PDF"
        }
        return texts.get(self.current_operation, "Procesar")

    def _get_action_icon(self):
        """Get action button icon based on operation"""
        icons = {
            "compress": ft.Icons.COMPRESS,
            "merge": ft.Icons.MERGE,
            "split": ft.Icons.CONTENT_CUT
        }
        return icons.get(self.current_operation, ft.Icons.PLAY_ARROW)

    # Result panel actions
    def _open_result_file(self, e):
        """Open the processed file"""
        if self.processing_stats.get('output_file'):
            self.file_manager.open_file(self.processing_stats['output_file'])

    def _show_in_folder(self, e):
        """Show result in folder"""
        output_dir = self.dir_config.output_dir / self.current_operation
        self.file_manager.open_folder(output_dir)

    def _process_more(self, e):
        """Reset interface for more processing"""
        self._clear_all(e)

    def _show_help(self, e):
        """Show help dialog"""
        help_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Ayuda - HYDRA21 PDF Compressor Pro"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("🚀 Bienvenido al Compresor Profesional de PDFs", weight=ft.FontWeight.BOLD),
                    ft.Container(height=12),
                    ft.Text("Funciones principales:"),
                    ft.Text("• Compresión: Reduce el tamaño de archivos PDF"),
                    ft.Text("• Fusión: Combina múltiples PDFs en uno"),
                    ft.Text("• División: Extrae páginas específicas"),
                    ft.Container(height=12),
                    ft.Text("Para funcionalidad completa, instala Ghostscript:"),
                    ft.Text("https://www.ghostscript.com/download/gsdnld.html", color="#2563eb"),
                ], spacing=4),
                width=400
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self._close_dialog(help_dialog))
            ]
        )
        self.page.overlay.append(help_dialog)
        help_dialog.open = True
        self.page.update()

    def _show_settings(self, e):
        """Show settings dialog"""
        settings_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Configuración"),
            content=ft.Text("Panel de configuración en desarrollo..."),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self._close_dialog(settings_dialog))
            ]
        )
        self.page.overlay.append(settings_dialog)
        settings_dialog.open = True
        self.page.update()

    def _close_dialog(self, dialog):
        """Close dialog"""
        dialog.open = False
        self.page.update()

    def cleanup(self):
        """Cleanup resources"""
        # Stop any running operations
        self.is_processing = False
        print("🧹 Limpieza de recursos completada")

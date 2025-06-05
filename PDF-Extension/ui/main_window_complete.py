"""
HYDRA21 PDF Compressor Pro - Complete Professional Main Window
Full PDF compression functionality with real Ghostscript integration
"""

import flet as ft
import threading
import time
import subprocess
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Core imports
from config.settings import get_app_config, DirectoryConfig, GS_QUALITY_PRESETS
from config.ghostscript_config import GhostscriptConfig

class MainWindow(ft.Column):
    """Complete Professional PDF Compressor Main Window"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        
        # Load configuration
        self.config = get_app_config()
        self.dir_config = DirectoryConfig.get_default()
        self.dir_config.ensure_directories()
        
        # Create output subdirectories
        self.output_dir = self.dir_config.output_dir / "compressed"
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize Ghostscript
        self.gs_config = GhostscriptConfig(self.dir_config.config_dir)
        self.gs_path = self._detect_ghostscript()
        
        # UI state
        self.selected_files: List[Path] = []
        self.is_processing = False
        self.processing_stats = {}
        self.current_quality = "medium"
        self.is_dark_mode = False
        self.operation_history = []
        
        # UI components
        self.file_picker = None
        self.file_list_container = None
        self.quality_dropdown = None
        self.progress_container = None
        self.results_panel = None
        self.process_button = None
        self.clear_button = None
        
        # Setup UI
        self._setup_ui()
        
        # Initialize Column
        super().__init__(
            controls=self._build_layout(),
            spacing=0,
            expand=True
        )
    
    def _detect_ghostscript(self):
        """Detect Ghostscript installation"""
        try:
            gs_info = self.gs_config.get_ghostscript_info()
            if gs_info['verified']:
                print(f"✅ Ghostscript encontrado: {gs_info['path']}")
                return gs_info['path']
            else:
                # Try common paths
                common_paths = [
                    "gswin64c.exe",
                    "gswin32c.exe", 
                    "gs",
                    r"C:\Program Files\gs\gs*\bin\gswin64c.exe",
                    r"C:\Program Files (x86)\gs\gs*\bin\gswin32c.exe"
                ]
                
                for path in common_paths:
                    try:
                        if "*" in path:
                            # Handle wildcard paths
                            import glob
                            matches = glob.glob(path)
                            if matches:
                                path = matches[0]
                        
                        result = subprocess.run([path, "--version"], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            print(f"✅ Ghostscript encontrado: {path}")
                            return path
                    except:
                        continue
                
                print("⚠️ Ghostscript no encontrado - funcionalidad limitada")
                return None
        except Exception as e:
            print(f"⚠️ Error detectando Ghostscript: {e}")
            return None
    
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
                ft.dropdown.Option("high", "Alta Calidad - Mejor para impresión (150 DPI)"),
                ft.dropdown.Option("medium", "Calidad Media - Balance óptimo (72 DPI)"),
                ft.dropdown.Option("low", "Baja Calidad - Máxima compresión (36 DPI)"),
            ],
            width=500,
            bgcolor="#ffffff",
            border_color="#e2e8f0",
            on_change=self._on_quality_changed
        )
        
        # File list container
        self.file_list_container = ft.Column(spacing=8)
        
        # Progress container
        self.progress_container = ft.Container(
            content=ft.Column([
                # Single file progress
                ft.Container(
                    content=ft.Column([
                        ft.Text("", size=14, color="#2563eb"),
                        ft.ProgressBar(visible=False, color="#2563eb", height=8)
                    ], spacing=8),
                    visible=False
                ),
                
                # Batch progress
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.ProgressRing(visible=False, color="#2563eb", width=24, height=24),
                            ft.Text("", size=14, color="#2563eb", expand=True)
                        ], spacing=12),
                        ft.Text("", size=12, color="#64748b")
                    ], spacing=8),
                    visible=False
                )
            ], spacing=16),
            visible=False,
            padding=20,
            bgcolor="#f0f9ff",
            border_radius=12,
            border=ft.border.all(1, "#bae6fd")
        )
        
        # Results panel
        self.results_panel = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="#059669", size=28),
                    ft.Text(
                        "Compresión Completada",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#059669"
                    )
                ], spacing=12),
                
                ft.Container(height=16),
                
                # Statistics container
                ft.Column([], spacing=8),
                
                ft.Container(height=20),
                
                # Action buttons
                ft.Row([
                    ft.ElevatedButton(
                        text="Abrir Archivo",
                        icon=ft.Icons.OPEN_IN_NEW,
                        on_click=self._open_result_file,
                        style=ft.ButtonStyle(
                            bgcolor="#059669",
                            color="white",
                            padding=ft.padding.symmetric(horizontal=20, vertical=12)
                        )
                    ),
                    ft.ElevatedButton(
                        text="Mostrar en Carpeta",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=self._show_in_folder,
                        style=ft.ButtonStyle(
                            bgcolor="#3b82f6",
                            color="white",
                            padding=ft.padding.symmetric(horizontal=20, vertical=12)
                        )
                    ),
                    ft.ElevatedButton(
                        text="Procesar Más",
                        icon=ft.Icons.ADD,
                        on_click=self._process_more,
                        style=ft.ButtonStyle(
                            bgcolor="#2563eb",
                            color="white",
                            padding=ft.padding.symmetric(horizontal=20, vertical=12)
                        )
                    )
                ], spacing=12, alignment=ft.MainAxisAlignment.CENTER)
            ]),
            padding=24,
            bgcolor="#ecfdf5",
            border_radius=12,
            border=ft.border.all(1, "#a7f3d0"),
            visible=False
        )
        
        # Action buttons
        self.process_button = ft.ElevatedButton(
            text="Comprimir PDFs",
            icon=ft.Icons.COMPRESS,
            on_click=self._start_compression,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor="#2563eb",
                color="white",
                padding=ft.padding.symmetric(horizontal=32, vertical=16)
            )
        )
        
        self.clear_button = ft.ElevatedButton(
            text="Limpiar",
            icon=ft.Icons.CLEAR,
            on_click=self._clear_all,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor="#f1f5f9",
                color="#2563eb",
                padding=ft.padding.symmetric(horizontal=24, vertical=16)
            )
        )
    
    def _build_layout(self):
        """Build the main layout"""
        return [
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.PICTURE_AS_PDF, color="#2563eb", size=32),
                        ft.Column([
                            ft.Text(
                                "HYDRA21 PDF Compressor Pro",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color="#2563eb"
                            ),
                            ft.Text(
                                "Compresión Profesional de PDFs con Ghostscript",
                                size=14,
                                color="#64748b"
                            )
                        ], spacing=2)
                    ], spacing=16),
                    
                    # Ghostscript status
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE if self.gs_path else ft.Icons.WARNING,
                                color="#059669" if self.gs_path else "#f59e0b",
                                size=20
                            ),
                            ft.Text(
                                "Ghostscript OK" if self.gs_path else "Ghostscript no encontrado",
                                size=12,
                                color="#059669" if self.gs_path else "#f59e0b",
                                weight=ft.FontWeight.W_500
                            )
                        ], spacing=8),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        bgcolor="#ecfdf5" if self.gs_path else "#fffbeb",
                        border_radius=20,
                        border=ft.border.all(1, "#a7f3d0" if self.gs_path else "#fed7aa")
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=24,
                bgcolor="#f8fafc",
                border=ft.border.only(bottom=ft.BorderSide(2, "#e2e8f0"))
            ),
            
            # Main content
            ft.Container(
                content=ft.Column([
                    # File selection section
                    self._create_file_section(),
                    
                    # Settings section
                    self._create_settings_section(),
                    
                    # Action buttons
                    self._create_action_section(),
                    
                    # Progress section
                    self.progress_container,
                    
                    # Results section
                    self.results_panel
                    
                ], spacing=32),
                padding=ft.padding.symmetric(horizontal=40, vertical=32),
                expand=True,
                bgcolor="#ffffff"
            )
        ]

    def _create_file_section(self):
        """Create file selection section"""
        return self._create_card([
            ft.Row([
                ft.Icon(ft.Icons.FOLDER_OPEN, color="#2563eb", size=24),
                ft.Text(
                    "Selección de Archivos PDF",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color="#1e293b"
                )
            ], spacing=12),

            ft.Container(height=16),

            # File selection area
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
                        "Selecciona uno o más archivos PDF para comprimir",
                        size=14,
                        color="#64748b",
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=16),
                    self.file_list_container
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=24,
                border=ft.border.all(2, "#e2e8f0"),
                border_radius=12,
                bgcolor="#f8fafc"
            )
        ])

    def _create_settings_section(self):
        """Create settings section"""
        if not self.gs_path:
            return self._create_card([
                ft.Row([
                    ft.Icon(ft.Icons.WARNING, color="#f59e0b", size=24),
                    ft.Column([
                        ft.Text(
                            "Ghostscript Requerido",
                            size=16,
                            weight=ft.FontWeight.W_600,
                            color="#f59e0b"
                        ),
                        ft.Text(
                            "Instala Ghostscript para habilitar la compresión de PDFs",
                            size=14,
                            color="#64748b"
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            "Descarga desde: https://www.ghostscript.com/download/gsdnld.html",
                            size=12,
                            color="#2563eb"
                        )
                    ], spacing=4, expand=True)
                ], alignment=ft.MainAxisAlignment.START)
            ])

        return self._create_card([
            ft.Row([
                ft.Icon(ft.Icons.TUNE, color="#2563eb", size=24),
                ft.Text(
                    "Configuración de Compresión",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color="#1e293b"
                )
            ], spacing=12),

            ft.Container(height=16),
            self.quality_dropdown,

            ft.Container(height=12),
            ft.Text(
                self._get_quality_description(),
                size=12,
                color="#64748b"
            )
        ])

    def _create_action_section(self):
        """Create action buttons section"""
        return ft.Row([
            self.process_button,
            self.clear_button
        ], spacing=16, alignment=ft.MainAxisAlignment.CENTER)

    def _create_card(self, content):
        """Create a styled card container"""
        return ft.Container(
            content=ft.Column(content, spacing=0),
            padding=24,
            bgcolor="#ffffff",
            border_radius=12,
            border=ft.border.all(1, "#e2e8f0"),
            width=800,
            margin=ft.margin.only(bottom=24)
        )

    # Event handlers
    def _select_files(self, e):
        """Open file picker"""
        self.file_picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["pdf"],
            dialog_title="Seleccionar archivos PDF para comprimir"
        )

    def _on_files_selected(self, e):
        """Handle file selection"""
        if e.files:
            self.selected_files = [Path(f.path) for f in e.files]
            self._update_file_list()
            self._update_buttons()

    def _on_quality_changed(self, e):
        """Handle quality dropdown change"""
        self.current_quality = e.control.value
        self.update()

    def _update_file_list(self):
        """Update the file list display"""
        self.file_list_container.controls.clear()

        if not self.selected_files:
            self.file_list_container.controls.append(
                ft.Text(
                    "No hay archivos seleccionados",
                    size=14,
                    color="#64748b",
                    text_align=ft.TextAlign.CENTER
                )
            )
        else:
            # Summary
            total_size = sum(f.stat().st_size for f in self.selected_files)
            self.file_list_container.controls.append(
                ft.Text(
                    f"✅ {len(self.selected_files)} archivo(s) seleccionado(s) - {total_size / (1024*1024):.1f} MB total",
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color="#059669"
                )
            )

            self.file_list_container.controls.append(ft.Container(height=8))

            # File list
            for i, file_path in enumerate(self.selected_files):
                try:
                    file_size = file_path.stat().st_size / (1024*1024)
                    self.file_list_container.controls.append(
                        ft.Row([
                            ft.Text(f"{i+1}.", size=12, color="#64748b", width=30),
                            ft.Icon(ft.Icons.PICTURE_AS_PDF, color="#dc2626", size=16),
                            ft.Text(
                                file_path.name,
                                size=13,
                                color="#1e293b",
                                expand=True,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            ft.Text(
                                f"{file_size:.1f} MB",
                                size=12,
                                color="#64748b",
                                width=60
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=16,
                                on_click=lambda e, idx=i: self._remove_file(idx),
                                icon_color="#dc2626",
                                tooltip="Remover archivo"
                            )
                        ], spacing=8)
                    )
                except Exception as ex:
                    print(f"Error reading file {file_path}: {ex}")

        self.update()

    def _remove_file(self, index):
        """Remove file from selection"""
        if 0 <= index < len(self.selected_files):
            self.selected_files.pop(index)
            self._update_file_list()
            self._update_buttons()

    def _update_buttons(self):
        """Update button states"""
        has_files = len(self.selected_files) > 0
        self.process_button.disabled = not has_files or not self.gs_path or self.is_processing
        self.clear_button.disabled = not has_files or self.is_processing
        self.update()

    def _get_quality_description(self):
        """Get description for current quality setting"""
        descriptions = {
            "high": "Mejor calidad visual, archivos más grandes. Ideal para documentos que se van a imprimir.",
            "medium": "Balance entre calidad y tamaño. Recomendado para la mayoría de casos.",
            "low": "Máxima compresión, menor calidad. Ideal para archivos que solo se verán en pantalla."
        }
        return descriptions.get(self.current_quality, "")

    def _clear_all(self, e):
        """Clear all selections and reset UI"""
        self.selected_files.clear()
        self.results_panel.visible = False
        self.progress_container.visible = False
        self._update_file_list()
        self._update_buttons()

    def _start_compression(self, e):
        """Start PDF compression process"""
        if not self.selected_files or not self.gs_path or self.is_processing:
            return

        self.is_processing = True
        self.results_panel.visible = False
        self._show_progress("Iniciando compresión...")
        self._update_buttons()

        # Start compression in background thread
        threading.Thread(target=self._compress_files, daemon=True).start()

    def _compress_files(self):
        """Compress files in background thread"""
        try:
            start_time = time.time()
            total_original_size = 0
            total_compressed_size = 0
            successful_files = []
            failed_files = []

            for i, file_path in enumerate(self.selected_files):
                try:
                    # Update progress
                    self.page.run_thread(lambda: self._update_batch_progress(
                        f"Comprimiendo: {file_path.name}",
                        i + 1,
                        len(self.selected_files)
                    ))

                    # Get original size
                    original_size = file_path.stat().st_size
                    total_original_size += original_size

                    # Compress file
                    output_path = self._compress_single_file(file_path)

                    if output_path and output_path.exists():
                        compressed_size = output_path.stat().st_size
                        total_compressed_size += compressed_size
                        successful_files.append({
                            'original': file_path,
                            'compressed': output_path,
                            'original_size': original_size,
                            'compressed_size': compressed_size
                        })
                        print(f"✅ Comprimido: {file_path.name} ({original_size/1024/1024:.1f}MB → {compressed_size/1024/1024:.1f}MB)")
                    else:
                        failed_files.append(file_path)
                        print(f"❌ Falló: {file_path.name}")

                except Exception as e:
                    print(f"Error comprimiendo {file_path}: {e}")
                    failed_files.append(file_path)

            # Calculate statistics
            processing_time = time.time() - start_time
            compression_ratio = 0
            if total_original_size > 0:
                compression_ratio = ((total_original_size - total_compressed_size) / total_original_size) * 100

            self.processing_stats = {
                'successful_files': successful_files,
                'failed_files': failed_files,
                'total_files': len(self.selected_files),
                'successful_count': len(successful_files),
                'failed_count': len(failed_files),
                'original_size': total_original_size,
                'compressed_size': total_compressed_size,
                'compression_ratio': compression_ratio,
                'space_saved': total_original_size - total_compressed_size,
                'processing_time': processing_time
            }

            # Show results
            self.page.run_thread(self._show_results)

        except Exception as e:
            print(f"Error durante la compresión: {e}")
            self.page.run_thread(lambda: self._show_error(f"Error durante la compresión: {str(e)}"))
        finally:
            self.is_processing = False
            self.page.run_thread(self._hide_progress)
            self.page.run_thread(self._update_buttons)

    def _compress_single_file(self, input_path: Path) -> Optional[Path]:
        """Compress a single PDF file using Ghostscript"""
        try:
            # Generate output filename
            output_filename = f"{input_path.stem}_compressed.pdf"
            output_path = self.output_dir / output_filename

            # Ensure unique filename
            counter = 1
            while output_path.exists():
                output_filename = f"{input_path.stem}_compressed_{counter}.pdf"
                output_path = self.output_dir / output_filename
                counter += 1

            # Quality settings for Ghostscript
            quality_settings = {
                "high": {
                    "dPDFSETTINGS": "/printer",
                    "dColorImageResolution": "150",
                    "dGrayImageResolution": "150",
                    "dMonoImageResolution": "300"
                },
                "medium": {
                    "dPDFSETTINGS": "/ebook",
                    "dColorImageResolution": "72",
                    "dGrayImageResolution": "72",
                    "dMonoImageResolution": "150"
                },
                "low": {
                    "dPDFSETTINGS": "/screen",
                    "dColorImageResolution": "36",
                    "dGrayImageResolution": "36",
                    "dMonoImageResolution": "72"
                }
            }

            settings = quality_settings.get(self.current_quality, quality_settings["medium"])

            # Build Ghostscript command
            cmd = [
                self.gs_path,
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                "-dSAFER",
                f"-dPDFSETTINGS={settings['dPDFSETTINGS']}",
                f"-dColorImageResolution={settings['dColorImageResolution']}",
                f"-dGrayImageResolution={settings['dGrayImageResolution']}",
                f"-dMonoImageResolution={settings['dMonoImageResolution']}",
                "-dCompressFonts=true",
                "-dSubsetFonts=true",
                "-dEmbedAllFonts=true",
                f"-sOutputFile={output_path}",
                str(input_path)
            ]

            # Execute Ghostscript
            print(f"🔄 Ejecutando: {' '.join(cmd[:5])}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.output_dir)
            )

            if result.returncode == 0 and output_path.exists():
                return output_path
            else:
                print(f"❌ Ghostscript error: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print(f"❌ Timeout comprimiendo {input_path.name}")
            return None
        except Exception as e:
            print(f"❌ Error comprimiendo {input_path.name}: {e}")
            return None

    # Progress and UI update methods
    def _show_progress(self, message):
        """Show progress indicator"""
        self.progress_container.visible = True
        progress_container = self.progress_container.content.controls[0]
        progress_text = progress_container.content.controls[0]
        progress_bar = progress_container.content.controls[1]

        progress_text.value = message
        progress_bar.visible = True
        progress_container.visible = True
        self.update()

    def _update_batch_progress(self, message, current, total):
        """Update batch progress with current file information"""
        self.progress_container.visible = True
        batch_container = self.progress_container.content.controls[1]
        batch_row = batch_container.content.controls[0]
        batch_ring = batch_row.controls[0]
        batch_text = batch_row.controls[1]
        batch_info = batch_container.content.controls[1]

        batch_text.value = message
        batch_ring.visible = True
        batch_info.value = f"Procesando archivo {current} de {total}"
        batch_container.visible = True
        self.update()

    def _hide_progress(self):
        """Hide progress indicators"""
        self.progress_container.visible = False
        self.update()

    def _show_results(self):
        """Show compression results"""
        stats = self.processing_stats
        results_content = self.results_panel.content.controls[2]  # Statistics column
        results_content.controls.clear()

        # Add statistics
        if stats['successful_count'] > 0:
            results_content.controls.extend([
                ft.Row([
                    ft.Text("Archivos procesados:", weight=ft.FontWeight.W_500, size=14),
                    ft.Text(f"{stats['successful_count']}/{stats['total_files']}", color="#2563eb", weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Text("Tamaño original:", weight=ft.FontWeight.W_500, size=14),
                    ft.Text(f"{stats['original_size'] / (1024*1024):.1f} MB", color="#64748b")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Text("Tamaño comprimido:", weight=ft.FontWeight.W_500, size=14),
                    ft.Text(f"{stats['compressed_size'] / (1024*1024):.1f} MB", color="#059669", weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Text("Ratio de compresión:", weight=ft.FontWeight.W_500, size=14),
                    ft.Text(f"{stats['compression_ratio']:.1f}%", color="#2563eb", weight=ft.FontWeight.BOLD, size=16)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Text("Espacio ahorrado:", weight=ft.FontWeight.W_500, size=14),
                    ft.Text(f"{stats['space_saved'] / (1024*1024):.1f} MB", color="#059669", weight=ft.FontWeight.BOLD, size=16)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Text("Tiempo de procesamiento:", weight=ft.FontWeight.W_500, size=14),
                    ft.Text(f"{stats['processing_time']:.1f}s", color="#64748b")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ])

            # Add failed files info if any
            if stats['failed_count'] > 0:
                results_content.controls.append(ft.Container(height=8))
                results_content.controls.append(
                    ft.Text(f"⚠️ {stats['failed_count']} archivo(s) no se pudieron comprimir",
                           color="#f59e0b", size=12)
                )
        else:
            results_content.controls.append(
                ft.Text("❌ No se pudo comprimir ningún archivo", color="#dc2626", weight=ft.FontWeight.W_500)
            )

        self.results_panel.visible = True
        self.update()

    def _show_error(self, message):
        """Show error message"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message, color="white"),
                bgcolor="#dc2626",
                duration=5000
            )
        )

    # Result panel actions
    def _open_result_file(self, e):
        """Open the first compressed file"""
        if self.processing_stats.get('successful_files'):
            file_info = self.processing_stats['successful_files'][0]
            output_path = file_info['compressed']
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(str(output_path))
                elif os.name == 'posix':  # macOS and Linux
                    subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(output_path)])
                print(f"📂 Abriendo archivo: {output_path}")
            except Exception as e:
                self._show_error(f"No se pudo abrir el archivo: {e}")

    def _show_in_folder(self, e):
        """Show output folder in file explorer"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['explorer', str(self.output_dir)])
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(self.output_dir)])
            print(f"📂 Abriendo carpeta: {self.output_dir}")
        except Exception as e:
            self._show_error(f"No se pudo abrir la carpeta: {e}")

    def _process_more(self, e):
        """Reset interface for more processing"""
        self._clear_all(e)

    def cleanup(self):
        """Cleanup resources"""
        self.is_processing = False
        print("🧹 Limpieza de recursos completada")

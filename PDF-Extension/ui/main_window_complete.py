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

        # Set fixed window size with scroll
        self.page.window.width = 850
        self.page.window.height = 900
        self.page.window.resizable = False
        self.page.scroll = ft.ScrollMode.AUTO

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

        # Advanced Ghostscript settings
        self.gs_advanced_settings = {
            'color_conversion': 'RGB',
            'image_compression': 'JPEG',
            'font_embedding': True,
            'optimize_for': 'web',
            'preserve_transparency': True,
            'downsample_images': True
        }

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
        self._setup_keyboard_shortcuts()

        # Initialize Column
        super().__init__(
            controls=self._build_layout(),
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO
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
                        ft.Text("", size=12, color=self._get_secondary_text_color())
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
        """Build the main layout with theme support"""
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
                                color=self._get_secondary_text_color()
                            )
                        ], spacing=2)
                    ], spacing=16),

                    # Header actions
                    ft.Row([
                        # Ghostscript status
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE if self.gs_path else ft.Icons.WARNING,
                                    color="#059669" if self.gs_path else "#f59e0b",
                                    size=16
                                ),
                                ft.Text(
                                    "GS OK" if self.gs_path else "GS Missing",
                                    size=11,
                                    color="#059669" if self.gs_path else "#f59e0b",
                                    weight=ft.FontWeight.W_500
                                )
                            ], spacing=6),
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            bgcolor="#ecfdf5" if self.gs_path else "#fffbeb",
                            border_radius=16,
                            border=ft.border.all(1, "#a7f3d0" if self.gs_path else "#fed7aa")
                        ),

                        # Action buttons
                        ft.IconButton(
                            icon=ft.Icons.HISTORY,
                            tooltip="Historial de operaciones",
                            on_click=self._show_history,
                            icon_color=self._get_icon_color()
                        ),
                        ft.IconButton(
                            icon=ft.Icons.HELP_OUTLINE,
                            tooltip="Ayuda y tutorial",
                            on_click=self._show_help,
                            icon_color=self._get_icon_color()
                        ),
                        ft.IconButton(
                            icon=ft.Icons.SETTINGS,
                            tooltip="Configuración",
                            on_click=self._show_settings,
                            icon_color=self._get_icon_color()
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DARK_MODE if not self.is_dark_mode else ft.Icons.LIGHT_MODE,
                            tooltip="Cambiar tema",
                            on_click=self._toggle_theme,
                            icon_color=self._get_icon_color()
                        )
                    ], spacing=8)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=24,
                bgcolor=self._get_header_bg_color(),
                border=ft.border.only(bottom=ft.BorderSide(2, self._get_border_color()))
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

                ], spacing=32, scroll=ft.ScrollMode.AUTO),
                padding=ft.padding.symmetric(horizontal=40, vertical=32),
                expand=True,
                bgcolor=self._get_bg_color()
            )
        ]

    def _get_header_bg_color(self):
        """Get header background color based on theme"""
        return "#0f172a" if self.is_dark_mode else "#f8fafc"

    def _create_file_section(self):
        """Create file selection section"""
        return self._create_card([
            ft.Row([
                ft.Icon(ft.Icons.FOLDER_OPEN, color="#2563eb", size=24),
                ft.Text(
                    "Selección de Archivos PDF",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=self._get_text_color()
                )
            ], spacing=12),

            ft.Container(height=16),

            # File selection area with drag-and-drop
            ft.Container(
                content=ft.Column([
                    # Drag and drop area
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.CLOUD_UPLOAD, size=48, color="#2563eb"),
                            ft.Text(
                                "Arrastra archivos PDF aquí",
                                size=16,
                                weight=ft.FontWeight.W_500,
                                color="#2563eb"
                            ),
                            ft.Text(
                                "o haz clic para seleccionar",
                                size=14,
                                color="#64748b"
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                        padding=32,
                        border=ft.border.all(2, "#2563eb"),
                        border_radius=12,
                        bgcolor="#f0f9ff",
                        on_click=self._select_files
                    ),

                    ft.Container(height=16),

                    ft.Row([
                        ft.ElevatedButton(
                            text="Seleccionar Archivos",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=self._select_files,
                            style=ft.ButtonStyle(
                                bgcolor="#2563eb",
                                color="white",
                                padding=ft.padding.symmetric(horizontal=20, vertical=12)
                            )
                        ),
                        ft.ElevatedButton(
                            text="Ejemplo Demo",
                            icon=ft.Icons.PLAY_ARROW,
                            on_click=self._load_demo_files,
                            style=ft.ButtonStyle(
                                bgcolor="#059669",
                                color="white",
                                padding=ft.padding.symmetric(horizontal=20, vertical=12)
                            )
                        )
                    ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),

                    ft.Container(height=16),
                    self.file_list_container
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=24,
                border=ft.border.all(1, "#e2e8f0"),
                border_radius=12,
                bgcolor=self._get_surface_color()
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
                    color=self._get_text_color()
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
        """Create a styled card container with theme support"""
        return ft.Container(
            content=ft.Column(content, spacing=0),
            padding=24,
            bgcolor=self._get_card_bg_color(),
            border_radius=12,
            border=ft.border.all(1, self._get_border_color()),
            width=750,  # Reduced width for new window size
            margin=ft.margin.only(bottom=24)
        )

    def _get_card_bg_color(self):
        """Get card background color based on theme"""
        return "#1e293b" if self.is_dark_mode else "#ffffff"

    def _get_border_color(self):
        """Get border color based on theme"""
        return "#374151" if self.is_dark_mode else "#e2e8f0"

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
                            ft.Text(f"{i+1}.", size=12, color=self._get_secondary_text_color(), width=30),
                            ft.Icon(ft.Icons.PICTURE_AS_PDF, color="#dc2626", size=16),
                            ft.Text(
                                file_path.name,
                                size=13,
                                color=self._get_text_color(),
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

            # Add to history
            self._add_to_history()

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
        """Compress a single PDF file using Ghostscript with advanced settings"""
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

            # Enhanced quality settings for Ghostscript
            quality_settings = {
                "high": {
                    "dPDFSETTINGS": "/printer",
                    "dColorImageResolution": "150",
                    "dGrayImageResolution": "150",
                    "dMonoImageResolution": "300",
                    "dColorImageDownsampleType": "/Bicubic"
                },
                "medium": {
                    "dPDFSETTINGS": "/ebook",
                    "dColorImageResolution": "72",
                    "dGrayImageResolution": "72",
                    "dMonoImageResolution": "150",
                    "dColorImageDownsampleType": "/Average"
                },
                "low": {
                    "dPDFSETTINGS": "/screen",
                    "dColorImageResolution": "36",
                    "dGrayImageResolution": "36",
                    "dMonoImageResolution": "72",
                    "dColorImageDownsampleType": "/Subsample"
                }
            }

            settings = quality_settings.get(self.current_quality, quality_settings["medium"])

            # Build simplified and reliable Ghostscript command
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
            print(f"🔄 Ejecutando compresión: {input_path.name}")
            print(f"   Configuración: {self.current_quality} | Preset: {settings['dPDFSETTINGS']}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.output_dir)
            )

            if result.returncode == 0 and output_path.exists():
                print(f"✅ Compresión exitosa: {output_path.name}")
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
        """Show compression results with improved dark mode support"""
        stats = self.processing_stats
        results_content = self.results_panel.content.controls[2]  # Statistics column
        results_content.controls.clear()

        # Define colors based on theme
        primary_text_color = self._get_text_color()
        secondary_text_color = self._get_secondary_text_color()
        success_color = "#10b981" if self.is_dark_mode else "#059669"
        accent_color = "#3b82f6" if self.is_dark_mode else "#2563eb"
        warning_color = "#f59e0b"
        error_color = "#ef4444" if self.is_dark_mode else "#dc2626"

        # Add statistics
        if stats['successful_count'] > 0:
            results_content.controls.extend([
                ft.Row([
                    ft.Text("Archivos procesados:", weight=ft.FontWeight.W_500, size=14, color=primary_text_color),
                    ft.Text(f"{stats['successful_count']}/{stats['total_files']}", color=accent_color, weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Text("Tamaño original:", weight=ft.FontWeight.W_500, size=14, color=primary_text_color),
                    ft.Text(f"{stats['original_size'] / (1024*1024):.1f} MB", color=secondary_text_color)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Text("Tamaño comprimido:", weight=ft.FontWeight.W_500, size=14, color=primary_text_color),
                    ft.Text(f"{stats['compressed_size'] / (1024*1024):.1f} MB", color=success_color, weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Text("Ratio de compresión:", weight=ft.FontWeight.W_500, size=14, color=primary_text_color),
                    ft.Text(f"{stats['compression_ratio']:.1f}%", color=accent_color, weight=ft.FontWeight.BOLD, size=16)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Text("Espacio ahorrado:", weight=ft.FontWeight.W_500, size=14, color=primary_text_color),
                    ft.Text(f"{stats['space_saved'] / (1024*1024):.1f} MB", color=success_color, weight=ft.FontWeight.BOLD, size=16)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Text("Tiempo de procesamiento:", weight=ft.FontWeight.W_500, size=14, color=primary_text_color),
                    ft.Text(f"{stats['processing_time']:.1f}s", color=secondary_text_color)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Container(height=8),

                # Additional stats with better visibility
                ft.Row([
                    ft.Text("Configuración utilizada:", weight=ft.FontWeight.W_500, size=13, color=primary_text_color),
                    ft.Text(f"Calidad {self.current_quality.title()}", color=accent_color, size=12)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Text("Compresión promedio:", weight=ft.FontWeight.W_500, size=13, color=primary_text_color),
                    ft.Text(f"{stats['compression_ratio']:.1f}% por archivo", color=success_color, size=12)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ])

            # Add failed files info if any
            if stats['failed_count'] > 0:
                results_content.controls.append(ft.Container(height=8))
                results_content.controls.append(
                    ft.Text(f"⚠️ {stats['failed_count']} archivo(s) no se pudieron comprimir",
                           color=warning_color, size=12, weight=ft.FontWeight.W_500)
                )
        else:
            results_content.controls.append(
                ft.Text("❌ No se pudo comprimir ningún archivo", color=error_color, weight=ft.FontWeight.W_500)
            )

        # Update results panel background for dark mode
        self.results_panel.bgcolor = "#1f2937" if self.is_dark_mode else "#ecfdf5"
        self.results_panel.border = ft.border.all(1, "#374151" if self.is_dark_mode else "#a7f3d0")

        self.results_panel.visible = True
        self.update()

    def _show_error(self, message):
        """Show error message"""
        snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor="#dc2626",
            duration=5000
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()

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

    # Theme and UI methods
    def _get_icon_color(self):
        """Get icon color based on current theme"""
        return "#f1f5f9" if self.is_dark_mode else "#64748b"

    def _get_bg_color(self):
        """Get background color based on current theme"""
        return "#0f172a" if self.is_dark_mode else "#ffffff"

    def _get_surface_color(self):
        """Get surface color based on current theme"""
        return "#1e293b" if self.is_dark_mode else "#f8fafc"

    def _get_text_color(self):
        """Get text color based on current theme"""
        return "#f1f5f9" if self.is_dark_mode else "#1e293b"

    def _toggle_theme(self, e):
        """Toggle between light and dark theme"""
        self.is_dark_mode = not self.is_dark_mode

        # Update page theme
        self.page.theme_mode = ft.ThemeMode.DARK if self.is_dark_mode else ft.ThemeMode.LIGHT
        self.page.update()

        # Rebuild the interface with new theme
        self.controls.clear()
        self.controls.extend(self._build_layout())
        self.update()

        print(f"🎨 Tema cambiado a: {'Oscuro' if self.is_dark_mode else 'Claro'}")

    def _show_history(self, e):
        """Show operation history dialog with improved centering"""
        history_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.HISTORY, color="#2563eb", size=24),
                ft.Text("Historial de Operaciones", size=18, weight=ft.FontWeight.BOLD, color=self._get_text_color())
            ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Historial de compresiones realizadas:",
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self._get_text_color(),
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=12),
                    self._create_history_list(),
                    ft.Container(height=16),
                    ft.Row([
                        ft.ElevatedButton(
                            text="Limpiar Historial",
                            icon=ft.Icons.CLEAR_ALL,
                            on_click=self._clear_history,
                            style=ft.ButtonStyle(
                                bgcolor="#f59e0b",
                                color="white",
                                padding=ft.padding.symmetric(horizontal=16, vertical=8)
                            )
                        ),
                        ft.ElevatedButton(
                            text="Exportar Historial",
                            icon=ft.Icons.DOWNLOAD,
                            on_click=self._export_history,
                            style=ft.ButtonStyle(
                                bgcolor="#2563eb",
                                color="white",
                                padding=ft.padding.symmetric(horizontal=16, vertical=8)
                            )
                        )
                    ], spacing=12, alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=520,
                height=420,
                bgcolor=self._get_card_bg_color(),
                border_radius=12,
                padding=16
            ),
            actions=[
                ft.Row([
                    ft.TextButton(
                        "Cerrar",
                        on_click=lambda _: self._close_dialog(history_dialog),
                        style=ft.ButtonStyle(color=self._get_text_color())
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ],
            bgcolor=self._get_card_bg_color()
        )
        self.page.overlay.append(history_dialog)
        history_dialog.open = True
        self.page.update()

    def _create_history_list(self):
        """Create centered history list widget with improved styling"""
        if not self.operation_history:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.HISTORY_TOGGLE_OFF, size=48, color=self._get_secondary_text_color()),
                    ft.Container(height=8),
                    ft.Text(
                        "No hay operaciones en el historial",
                        size=14,
                        color=self._get_secondary_text_color(),
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Text(
                        "Las compresiones realizadas aparecerán aquí",
                        size=12,
                        color=self._get_secondary_text_color(),
                        text_align=ft.TextAlign.CENTER
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                padding=32,
                alignment=ft.alignment.center,
                height=250
            )

        history_items = []
        for i, operation in enumerate(reversed(self.operation_history[-10:])):  # Show last 10
            history_items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Text(f"#{len(self.operation_history) - i}", size=11, color="#ffffff", weight=ft.FontWeight.BOLD),
                                bgcolor="#2563eb",
                                border_radius=12,
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                width=35
                            ),
                            ft.Text(operation.get('timestamp', 'N/A'), size=12, color=self._get_secondary_text_color()),
                            ft.Container(
                                content=ft.Text(f"{operation.get('files_count', 0)} archivos", size=11, color="#ffffff", weight=ft.FontWeight.W_500),
                                bgcolor="#059669",
                                border_radius=8,
                                padding=ft.padding.symmetric(horizontal=6, vertical=2)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(height=4),
                        ft.Row([
                            ft.Text(
                                f"Compresión: {operation.get('compression_ratio', 0):.1f}%",
                                size=11,
                                color="#2563eb",
                                weight=ft.FontWeight.W_500
                            ),
                            ft.Text(
                                f"Ahorrado: {operation.get('space_saved', 0) / (1024*1024):.1f} MB",
                                size=11,
                                color="#059669",
                                weight=ft.FontWeight.W_500
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ], spacing=2),
                    padding=12,
                    bgcolor=self._get_input_bg_color(),
                    border_radius=8,
                    border=ft.border.all(1, self._get_border_color()),
                    margin=ft.margin.only(bottom=6)
                )
            )

        return ft.Container(
            content=ft.Column(history_items, spacing=4, scroll=ft.ScrollMode.AUTO),
            height=250,
            border_radius=8,
            border=ft.border.all(1, self._get_border_color()),
            padding=8
        )

    def _clear_history(self, e):
        """Clear operation history"""
        self.operation_history.clear()
        snack_bar = ft.SnackBar(content=ft.Text("Historial limpiado"), bgcolor="#059669")
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()

    def _export_history(self, e):
        """Export history to file"""
        try:
            import json
            from datetime import datetime

            export_file = self.output_dir / f"historial_compresion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.operation_history, f, indent=2, ensure_ascii=False)

            snack_bar = ft.SnackBar(content=ft.Text(f"Historial exportado: {export_file.name}"), bgcolor="#059669")
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()
        except Exception as ex:
            self._show_error(f"Error exportando historial: {ex}")

    def _show_help(self, e):
        """Show help dialog with comprehensive information"""
        help_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.HELP_OUTLINE, color="#2563eb", size=24),
                ft.Text("Ayuda - HYDRA21 PDF Compressor Pro", size=18, weight=ft.FontWeight.BOLD)
            ], spacing=12),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("🚀 Compresor Profesional de PDFs", size=16, weight=ft.FontWeight.BOLD, color="#2563eb"),
                    ft.Container(height=12),

                    ft.Text("Funciones principales:", size=14, weight=ft.FontWeight.W_500, color=self._get_text_color()),
                    ft.Text("• Compresión avanzada con Ghostscript", size=12, color=self._get_text_color()),
                    ft.Text("• Múltiples niveles de calidad", size=12, color=self._get_text_color()),
                    ft.Text("• Procesamiento por lotes", size=12, color=self._get_text_color()),
                    ft.Text("• Estadísticas detalladas", size=12, color=self._get_text_color()),
                    ft.Text("• Historial de operaciones", size=12, color=self._get_text_color()),
                    ft.Container(height=12),

                    ft.Text("Niveles de calidad:", size=14, weight=ft.FontWeight.W_500, color=self._get_text_color()),
                    ft.Text("• Alta: Mejor para impresión (150 DPI)", size=12, color="#059669"),
                    ft.Text("• Media: Balance óptimo (72 DPI)", size=12, color="#2563eb"),
                    ft.Text("• Baja: Máxima compresión (36 DPI)", size=12, color="#f59e0b"),
                    ft.Container(height=12),

                    ft.Text("Atajos de teclado:", size=14, weight=ft.FontWeight.W_500, color=self._get_text_color()),
                    ft.Text("• Ctrl+O: Seleccionar archivos", size=12, color=self._get_text_color()),
                    ft.Text("• Ctrl+Enter: Iniciar compresión", size=12, color=self._get_text_color()),
                    ft.Text("• Ctrl+L: Limpiar selección", size=12, color=self._get_text_color()),
                    ft.Text("• Ctrl+D: Cambiar tema", size=12, color=self._get_text_color()),
                    ft.Container(height=12),

                    ft.Text("Ghostscript:", size=14, weight=ft.FontWeight.W_500, color=self._get_text_color()),
                    ft.Text("Descarga desde: https://www.ghostscript.com/download/gsdnld.html",
                           size=11, color="#2563eb"),
                    ft.Text("Versión recomendada: 10.0 o superior", size=11, color=self._get_secondary_text_color()),
                ], spacing=4),
                width=450,
                height=400
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self._close_dialog(help_dialog))
            ]
        )
        self.page.overlay.append(help_dialog)
        help_dialog.open = True
        self.page.update()

    def _show_settings(self, e):
        """Show compact settings dialog with advanced Ghostscript options"""

        # Create tabs for better organization
        settings_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="General",
                    icon=ft.Icons.SETTINGS,
                    content=self._create_general_settings_tab()
                ),
                ft.Tab(
                    text="Ghostscript",
                    icon=ft.Icons.TUNE,
                    content=self._create_ghostscript_settings_tab()
                ),
                ft.Tab(
                    text="Avanzado",
                    icon=ft.Icons.ENGINEERING,
                    content=self._create_advanced_settings_tab()
                )
            ],
            height=350
        )

        settings_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.SETTINGS, color="#2563eb", size=20),
                ft.Text("Configuración", size=16, weight=ft.FontWeight.BOLD)
            ], spacing=8),
            content=ft.Container(
                content=settings_tabs,
                width=480,
                height=380
            ),
            actions=[
                ft.Row([
                    ft.TextButton(
                        "Restablecer",
                        icon=ft.Icons.RESTORE,
                        on_click=self._reset_settings
                    ),
                    ft.TextButton(
                        "Cerrar",
                        on_click=lambda _: self._close_dialog(settings_dialog)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]
        )
        self.page.overlay.append(settings_dialog)
        settings_dialog.open = True
        self.page.update()

    def _create_general_settings_tab(self):
        """Create general settings tab content with scroll"""
        return ft.Container(
            content=ft.Column([
                # Theme setting
                ft.Row([
                    ft.Icon(ft.Icons.PALETTE, size=16, color="#2563eb"),
                    ft.Text("Tema:", size=13, weight=ft.FontWeight.W_500, color=self._get_text_color()),
                    ft.Switch(
                        value=self.is_dark_mode,
                        on_change=self._toggle_theme,
                        active_color="#2563eb",
                        scale=0.8
                    ),
                    ft.Text("Modo oscuro", size=11, color=self._get_secondary_text_color())
                ], spacing=8),

                ft.Divider(height=1, color="#e2e8f0"),

                # Output directory
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.FOLDER, size=16, color="#2563eb"),
                        ft.Text("Directorio de salida:", size=13, weight=ft.FontWeight.W_500, color=self._get_text_color())
                    ], spacing=8),
                    ft.Container(
                        content=ft.Text(
                            str(self.output_dir).replace(str(Path.home()), "~"),
                            size=11,
                            color=self._get_secondary_text_color(),
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        padding=6,
                        bgcolor=self._get_input_bg_color(),
                        border_radius=4,
                        border=ft.border.all(1, "#e2e8f0")
                    ),
                    ft.ElevatedButton(
                        text="Cambiar",
                        icon=ft.Icons.EDIT,
                        on_click=self._change_output_dir,
                        style=ft.ButtonStyle(
                            bgcolor="#2563eb",
                            color="white",
                            padding=ft.padding.symmetric(horizontal=12, vertical=6)
                        ),
                        height=32
                    )
                ], spacing=6),

                ft.Divider(height=1, color="#e2e8f0"),

                # Ghostscript status
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.EXTENSION, size=16, color="#2563eb"),
                        ft.Text("Estado de Ghostscript:", size=13, weight=ft.FontWeight.W_500, color=self._get_text_color())
                    ], spacing=8),
                    ft.Row([
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE if self.gs_path else ft.Icons.ERROR,
                            color="#059669" if self.gs_path else "#dc2626",
                            size=16
                        ),
                        ft.Text(
                            "Instalado y funcionando" if self.gs_path else "No encontrado",
                            size=11,
                            color="#059669" if self.gs_path else "#dc2626"
                        )
                    ], spacing=6),
                    ft.ElevatedButton(
                        text="Detectar",
                        icon=ft.Icons.REFRESH,
                        on_click=self._detect_ghostscript_manual,
                        style=ft.ButtonStyle(
                            bgcolor="#059669",
                            color="white",
                            padding=ft.padding.symmetric(horizontal=12, vertical=6)
                        ),
                        height=32
                    )
                ], spacing=6)
            ], spacing=12, scroll=ft.ScrollMode.AUTO),
            padding=16
        )

    def _create_ghostscript_settings_tab(self):
        """Create Ghostscript settings tab content with scroll"""
        return ft.Container(
            content=ft.Column([
                # Quality presets
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.HIGH_QUALITY, size=16, color="#2563eb"),
                        ft.Text("Presets de Calidad:", size=13, weight=ft.FontWeight.W_500, color=self._get_text_color())
                    ], spacing=8),
                    ft.Dropdown(
                        label="Preset",
                        value=self.current_quality,
                        options=[
                            ft.dropdown.Option("high", "Alta - Impresión (150 DPI)"),
                            ft.dropdown.Option("medium", "Media - Web (72 DPI)"),
                            ft.dropdown.Option("low", "Baja - Móvil (36 DPI)"),
                            ft.dropdown.Option("custom", "Personalizado")
                        ],
                        width=200,
                        text_size=11,
                        on_change=self._on_quality_changed
                    )
                ], spacing=6),

                ft.Divider(height=1, color="#e2e8f0"),

                # Color conversion
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.COLOR_LENS, size=16, color="#2563eb"),
                        ft.Text("Conversión de Color:", size=13, weight=ft.FontWeight.W_500, color=self._get_text_color())
                    ], spacing=8),
                    ft.Dropdown(
                        value=self.gs_advanced_settings['color_conversion'],
                        options=[
                            ft.dropdown.Option("RGB", "RGB - Color completo"),
                            ft.dropdown.Option("CMYK", "CMYK - Impresión"),
                            ft.dropdown.Option("Gray", "Escala de grises"),
                            ft.dropdown.Option("DeviceN", "Automático")
                        ],
                        width=200,
                        text_size=11,
                        on_change=lambda e: self._update_gs_setting('color_conversion', e.control.value)
                    )
                ], spacing=6),

                ft.Divider(height=1, color="#e2e8f0"),

                # Image compression
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.COMPRESS, size=16, color="#2563eb"),
                        ft.Text("Compresión de Imágenes:", size=13, weight=ft.FontWeight.W_500, color=self._get_text_color())
                    ], spacing=8),
                    ft.Dropdown(
                        value=self.gs_advanced_settings['image_compression'],
                        options=[
                            ft.dropdown.Option("JPEG", "JPEG - Mejor compresión"),
                            ft.dropdown.Option("ZIP", "ZIP - Sin pérdida"),
                            ft.dropdown.Option("LZW", "LZW - Compatibilidad"),
                            ft.dropdown.Option("CCITTFax", "CCITT - Monocromo")
                        ],
                        width=200,
                        text_size=11,
                        on_change=lambda e: self._update_gs_setting('image_compression', e.control.value)
                    )
                ], spacing=6),

                ft.Divider(height=1, color="#e2e8f0"),

                # Optimization target
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.TUNE, size=16, color="#2563eb"),
                        ft.Text("Optimizar para:", size=13, weight=ft.FontWeight.W_500, color=self._get_text_color())
                    ], spacing=8),
                    ft.Dropdown(
                        value=self.gs_advanced_settings['optimize_for'],
                        options=[
                            ft.dropdown.Option("web", "Web - Carga rápida"),
                            ft.dropdown.Option("print", "Impresión - Alta calidad"),
                            ft.dropdown.Option("archive", "Archivo - Preservación"),
                            ft.dropdown.Option("mobile", "Móvil - Tamaño mínimo")
                        ],
                        width=200,
                        text_size=11,
                        on_change=lambda e: self._update_gs_setting('optimize_for', e.control.value)
                    )
                ], spacing=6)
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            padding=16
        )

    def _create_advanced_settings_tab(self):
        """Create advanced settings tab content with scroll"""
        return ft.Container(
            content=ft.Column([
                # Font settings
                ft.Row([
                    ft.Icon(ft.Icons.FONT_DOWNLOAD, size=16, color="#2563eb"),
                    ft.Text("Configuración de Fuentes:", size=13, weight=ft.FontWeight.W_500, color=self._get_text_color())
                ], spacing=8),

                ft.Row([
                    ft.Checkbox(
                        label="Incrustar fuentes",
                        value=self.gs_advanced_settings['font_embedding'],
                        on_change=lambda e: self._update_gs_setting('font_embedding', e.control.value),
                        scale=0.8
                    ),
                    ft.Checkbox(
                        label="Submuestrear imágenes",
                        value=self.gs_advanced_settings['downsample_images'],
                        on_change=lambda e: self._update_gs_setting('downsample_images', e.control.value),
                        scale=0.8
                    )
                ], spacing=20),

                ft.Checkbox(
                    label="Preservar transparencia",
                    value=self.gs_advanced_settings['preserve_transparency'],
                    on_change=lambda e: self._update_gs_setting('preserve_transparency', e.control.value),
                    scale=0.8
                ),

                ft.Divider(height=1, color="#e2e8f0"),

                # Performance settings
                ft.Row([
                    ft.Icon(ft.Icons.SPEED, size=16, color="#2563eb"),
                    ft.Text("Rendimiento:", size=13, weight=ft.FontWeight.W_500, color=self._get_text_color())
                ], spacing=8),

                ft.Row([
                    ft.Text("Hilos de procesamiento:", size=11, color=self._get_text_color()),
                    ft.Dropdown(
                        value="auto",
                        options=[
                            ft.dropdown.Option("1", "1 hilo"),
                            ft.dropdown.Option("2", "2 hilos"),
                            ft.dropdown.Option("4", "4 hilos"),
                            ft.dropdown.Option("auto", "Automático")
                        ],
                        width=120,
                        text_size=10
                    )
                ], spacing=8),

                ft.Divider(height=1, color="#e2e8f0"),

                # Output settings
                ft.Row([
                    ft.Icon(ft.Icons.OUTPUT, size=16, color="#2563eb"),
                    ft.Text("Configuración de Salida:", size=13, weight=ft.FontWeight.W_500, color=self._get_text_color())
                ], spacing=8),

                ft.Row([
                    ft.Text("Versión PDF:", size=11, color=self._get_text_color()),
                    ft.Dropdown(
                        value="1.4",
                        options=[
                            ft.dropdown.Option("1.3", "PDF 1.3"),
                            ft.dropdown.Option("1.4", "PDF 1.4"),
                            ft.dropdown.Option("1.5", "PDF 1.5"),
                            ft.dropdown.Option("1.6", "PDF 1.6"),
                            ft.dropdown.Option("1.7", "PDF 1.7")
                        ],
                        width=120,
                        text_size=10
                    )
                ], spacing=8),

                ft.Row([
                    ft.Text("Sufijo de archivo:", size=11, color=self._get_text_color()),
                    ft.TextField(
                        value="_compressed",
                        width=120,
                        text_size=10,
                        border_color="#e2e8f0"
                    )
                ], spacing=8)
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
            padding=16
        )

    def _update_gs_setting(self, key, value):
        """Update Ghostscript advanced setting"""
        self.gs_advanced_settings[key] = value
        print(f"🔧 Configuración actualizada: {key} = {value}")

    def _reset_settings(self, e):
        """Reset all settings to defaults"""
        self.gs_advanced_settings = {
            'color_conversion': 'RGB',
            'image_compression': 'JPEG',
            'font_embedding': True,
            'optimize_for': 'web',
            'preserve_transparency': True,
            'downsample_images': True
        }
        self.current_quality = "medium"
        snack_bar = ft.SnackBar(content=ft.Text("Configuración restablecida"), bgcolor="#059669")
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()
        self.update()

    def _get_secondary_text_color(self):
        """Get secondary text color based on theme"""
        return "#94a3b8" if self.is_dark_mode else "#64748b"

    def _get_input_bg_color(self):
        """Get input background color based on theme"""
        return "#1e293b" if self.is_dark_mode else "#f8fafc"

    def _change_output_dir(self, e):
        """Change output directory"""
        # This would typically open a directory picker
        snack_bar = ft.SnackBar(content=ft.Text("Función de cambio de directorio en desarrollo"), bgcolor="#f59e0b")
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()

    def _detect_ghostscript_manual(self, e):
        """Manually detect Ghostscript"""
        old_path = self.gs_path
        self.gs_path = self._detect_ghostscript()

        if self.gs_path != old_path:
            self._update_buttons()
            snack_bar = ft.SnackBar(
                content=ft.Text("Ghostscript detectado correctamente" if self.gs_path else "Ghostscript no encontrado"),
                bgcolor="#059669" if self.gs_path else "#dc2626"
            )
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()

    def _close_dialog(self, dialog):
        """Close dialog"""
        dialog.open = False
        self.page.update()

    def _load_demo_files(self, e):
        """Load demo files for testing"""
        snack_bar = ft.SnackBar(
            content=ft.Text("Función demo: Selecciona archivos PDF reales para probar la compresión"),
            bgcolor="#2563eb"
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()

    def _add_to_history(self):
        """Add current operation to history"""
        from datetime import datetime

        if self.processing_stats:
            history_entry = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'files_count': self.processing_stats.get('successful_count', 0),
                'compression_ratio': self.processing_stats.get('compression_ratio', 0),
                'space_saved': self.processing_stats.get('space_saved', 0),
                'processing_time': self.processing_stats.get('processing_time', 0),
                'quality': self.current_quality,
                'original_size': self.processing_stats.get('original_size', 0),
                'compressed_size': self.processing_stats.get('compressed_size', 0)
            }

            self.operation_history.append(history_entry)

            # Keep only last 50 operations
            if len(self.operation_history) > 50:
                self.operation_history = self.operation_history[-50:]

            print(f"📝 Operación añadida al historial: {history_entry['files_count']} archivos, {history_entry['compression_ratio']:.1f}% compresión")

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        def on_keyboard(e):
            if e.key == "o" and e.ctrl:
                self._select_files(None)
            elif e.key == "Enter" and e.ctrl:
                self._start_compression(None)
            elif e.key == "l" and e.ctrl:
                self._clear_all(None)
            elif e.key == "d" and e.ctrl:
                self._toggle_theme(None)
            elif e.key == "h" and e.ctrl:
                self._show_history(None)

        self.page.on_keyboard_event = on_keyboard
        print("⌨️ Atajos de teclado configurados")

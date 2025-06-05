"""
PDF Merger Component for HYDRA21 PDF Compressor Pro
Provides PDF merging functionality with drag-and-drop reordering
"""

import flet as ft
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
import PyPDF2
import threading
import time

class PDFMerger(ft.Column):
    """PDF Merger component with drag-and-drop file ordering"""
    
    def __init__(self, page: ft.Page, theme: Dict[str, str], on_merge_complete: Optional[Callable] = None):
        self.page = page
        self.theme = theme
        self.on_merge_complete = on_merge_complete
        
        # State
        self.selected_files: List[Path] = []
        self.file_info: List[Dict[str, Any]] = []
        self.is_processing = False
        self.output_filename = "merged_document.pdf"
        
        # UI Components
        self.file_picker = None
        self.files_list_container = None
        self.merge_options_container = None
        self.progress_container = None
        self.results_container = None
        
        self._setup_ui()
        
        super().__init__(
            controls=self._build_layout(),
            spacing=24,
            expand=True
        )
    
    def _setup_ui(self):
        """Setup UI components"""
        # File picker
        self.file_picker = ft.FilePicker(
            on_result=self._on_files_selected
        )
        self.page.overlay.append(self.file_picker)
        
        # Files list container with scroll
        self.files_list_container = ft.Container(
            content=ft.Column([
                ft.Text("No hay archivos seleccionados",
                       size=16, color=self.theme.get('on_surface_variant', '#64748b'))
            ], scroll=ft.ScrollMode.AUTO),
            padding=20,
            border_radius=12,
            border=ft.border.all(1, self.theme.get('outline', '#e2e8f0')),
            bgcolor=self.theme.get('surface', '#ffffff'),
            height=300  # Increased height for better visibility
        )
        
        # Merge options container
        self.merge_options_container = ft.Container(
            content=ft.Column([
                ft.Text("Opciones de Fusión", size=16, weight=ft.FontWeight.W_600),
                ft.Row([
                    ft.Text("Nombre del archivo:", size=14),
                    ft.TextField(
                        value="merged_document.pdf",
                        width=300,
                        on_change=self._on_filename_changed,
                        bgcolor=self.theme.get('surface', '#ffffff'),
                        border_color=self.theme.get('outline', '#e2e8f0')
                    )
                ], spacing=12),
                ft.Container(height=16),
                ft.Row([
                    ft.ElevatedButton(
                        text="Fusionar PDFs",
                        icon=ft.Icons.MERGE,
                        on_click=self._start_merge,
                        disabled=True,
                        style=ft.ButtonStyle(
                            bgcolor="#2563eb",
                            color="white"
                        )
                    ),
                    ft.ElevatedButton(
                        text="Limpiar Lista",
                        icon=ft.Icons.CLEAR,
                        on_click=self._clear_files,
                        disabled=True,
                        style=ft.ButtonStyle(
                            bgcolor="#6b7280",
                            color="white"
                        )
                    )
                ], spacing=12)
            ]),
            visible=False,
            padding=20,
            border_radius=12,
            border=ft.border.all(1, self.theme.get('outline', '#e2e8f0')),
            bgcolor=self.theme.get('surface', '#ffffff')
        )
        
        # Progress container
        progress_bg = "#f0f9ff" if not self._is_dark_mode() else "#1e3a8a"
        progress_border = "#bae6fd" if not self._is_dark_mode() else "#3b82f6"

        self.progress_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.ProgressRing(width=24, height=24, color="#2563eb"),
                    ft.Text("Fusionando PDFs...", size=14, color="#2563eb")
                ], spacing=12),
                ft.Text("", size=12, color=self.theme.get('on_surface_variant', '#64748b'))
            ]),
            visible=False,
            padding=20,
            border_radius=12,
            bgcolor=progress_bg,
            border=ft.border.all(1, progress_border)
        )
        
        # Results container
        results_bg = "#ecfdf5" if not self._is_dark_mode() else "#064e3b"
        results_border = "#a7f3d0" if not self._is_dark_mode() else "#059669"

        self.results_container = ft.Container(
            content=ft.Column([]),
            visible=False,
            padding=20,
            border_radius=12,
            bgcolor=results_bg,
            border=ft.border.all(1, results_border)
        )
    
    def _build_layout(self):
        """Build the main layout"""
        return [
            # Header
            ft.Row([
                ft.Icon(ft.Icons.MERGE, color="#2563eb", size=24),
                ft.Text(
                    "Fusión de PDFs",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#2563eb"
                )
            ], spacing=12),
            
            # File selection
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.ElevatedButton(
                            text="Seleccionar PDFs",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=lambda _: self.file_picker.pick_files(
                                allowed_extensions=["pdf"],
                                allow_multiple=True,
                                dialog_title="Seleccionar PDFs para fusionar"
                            ),
                            style=ft.ButtonStyle(
                                bgcolor="#2563eb",
                                color="white",
                                padding=ft.padding.symmetric(horizontal=20, vertical=12)
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    
                    ft.Container(height=16),
                    
                    ft.Text(
                        "Selecciona múltiples archivos PDF para fusionar en un solo documento",
                        size=14,
                        color=self.theme.get('on_surface_variant', '#64748b'),
                        text_align=ft.TextAlign.CENTER
                    ),
                    
                    ft.Container(height=16),
                    self.files_list_container
                ]),
                padding=20,
                border_radius=12,
                border=ft.border.all(1, self.theme.get('outline', '#e2e8f0')),
                bgcolor=self.theme.get('surface_variant', '#f8fafc')
            ),
            
            # Merge options
            self.merge_options_container,
            
            # Progress
            self.progress_container,
            
            # Results
            self.results_container
        ]
    
    def _on_files_selected(self, e: ft.FilePickerResultEvent):
        """Handle PDF files selection"""
        if e.files:
            new_files = [Path(file.path) for file in e.files]
            self.selected_files.extend(new_files)
            self._analyze_files()
    
    def _analyze_files(self):
        """Analyze the selected PDF files"""
        self.file_info = []
        
        for file_path in self.selected_files:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    num_pages = len(pdf_reader.pages)
                    
                    # Get PDF metadata
                    metadata = pdf_reader.metadata
                    title = metadata.get('/Title', 'Sin título') if metadata else 'Sin título'
                    
                    file_info = {
                        'path': file_path,
                        'name': file_path.name,
                        'title': title,
                        'pages': num_pages,
                        'size': file_path.stat().st_size
                    }
                    self.file_info.append(file_info)
                    
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                # Add file with error info
                self.file_info.append({
                    'path': file_path,
                    'name': file_path.name,
                    'title': 'Error al leer archivo',
                    'pages': 0,
                    'size': file_path.stat().st_size,
                    'error': True
                })
        
        self._update_files_display()
    
    def _update_files_display(self):
        """Update the files list display"""
        if not self.file_info:
            self.files_list_container.content = ft.Column([
                ft.Text("No hay archivos seleccionados", 
                       size=16, color=self.theme.get('on_surface_variant', '#64748b'))
            ])
            self.merge_options_container.visible = False
        else:
            file_cards = []
            total_pages = 0
            
            for i, info in enumerate(self.file_info):
                if not info.get('error', False):
                    total_pages += info['pages']
                
                size_mb = info['size'] / (1024 * 1024)
                
                card = ft.Container(
                    content=ft.Row([
                        # File icon and info
                        ft.Row([
                            ft.Icon(
                                ft.Icons.PICTURE_AS_PDF, 
                                color="#dc2626" if not info.get('error', False) else "#6b7280", 
                                size=24
                            ),
                            ft.Column([
                                ft.Text(info['name'], size=14, weight=ft.FontWeight.W_600),
                                ft.Text(
                                    f"Páginas: {info['pages']} | Tamaño: {size_mb:.1f} MB" if not info.get('error', False) else "Error al leer archivo",
                                    size=12, 
                                    color="#dc2626" if info.get('error', False) else self.theme.get('on_surface_variant', '#64748b')
                                )
                            ], spacing=4, expand=True)
                        ], spacing=12, expand=True),
                        
                        # Move buttons
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.KEYBOARD_ARROW_UP,
                                tooltip="Mover arriba",
                                on_click=lambda e, idx=i: self._move_file_up(idx),
                                disabled=i == 0,
                                icon_size=16
                            ),
                            ft.IconButton(
                                icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                                tooltip="Mover abajo",
                                on_click=lambda e, idx=i: self._move_file_down(idx),
                                disabled=i == len(self.file_info) - 1,
                                icon_size=16
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Eliminar",
                                on_click=lambda e, idx=i: self._remove_file(idx),
                                icon_color="#dc2626",
                                icon_size=16
                            )
                        ], spacing=4)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=12,
                    border_radius=8,
                    border=ft.border.all(1, self.theme.get('outline', '#e2e8f0')),
                    bgcolor=self.theme.get('surface', '#ffffff')
                )
                file_cards.append(card)
            
            # Summary
            valid_files = len([f for f in self.file_info if not f.get('error', False)])
            summary = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO, color="#2563eb", size=20),
                    ft.Text(
                        f"Archivos: {valid_files} | Total de páginas: {total_pages}",
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color="#2563eb"
                    )
                ], spacing=8),
                padding=12,
                border_radius=8,
                bgcolor="#f0f9ff",
                border=ft.border.all(1, "#bae6fd")
            )
            
            self.files_list_container.content = ft.Column([
                ft.Text("Archivos seleccionados (orden de fusión):", 
                       size=14, weight=ft.FontWeight.W_600),
                ft.Container(height=8),
                *file_cards,
                ft.Container(height=12),
                summary
            ])
            
            self.merge_options_container.visible = valid_files > 1
            self._update_merge_button()
        
        self.page.update()
    
    def _move_file_up(self, index: int):
        """Move file up in the list"""
        if index > 0:
            self.file_info[index], self.file_info[index - 1] = self.file_info[index - 1], self.file_info[index]
            self.selected_files[index], self.selected_files[index - 1] = self.selected_files[index - 1], self.selected_files[index]
            self._update_files_display()
    
    def _move_file_down(self, index: int):
        """Move file down in the list"""
        if index < len(self.file_info) - 1:
            self.file_info[index], self.file_info[index + 1] = self.file_info[index + 1], self.file_info[index]
            self.selected_files[index], self.selected_files[index + 1] = self.selected_files[index + 1], self.selected_files[index]
            self._update_files_display()
    
    def _remove_file(self, index: int):
        """Remove file from the list"""
        self.file_info.pop(index)
        self.selected_files.pop(index)
        self._update_files_display()
    
    def _on_filename_changed(self, e):
        """Handle output filename change"""
        self.output_filename = e.control.value
        if not self.output_filename.endswith('.pdf'):
            self.output_filename += '.pdf'
    
    def _update_merge_button(self):
        """Update merge button state"""
        valid_files = len([f for f in self.file_info if not f.get('error', False)])
        
        if self.merge_options_container.content and hasattr(self.merge_options_container.content, 'controls'):
            for control in self.merge_options_container.content.controls:
                if isinstance(control, ft.Row):
                    for button in control.controls:
                        if isinstance(button, ft.ElevatedButton):
                            if "Fusionar" in button.text:
                                button.disabled = valid_files < 2 or self.is_processing
                            elif "Limpiar" in button.text:
                                button.disabled = valid_files == 0
        
        self.page.update()
    
    def _clear_files(self, e):
        """Clear all files"""
        self.selected_files.clear()
        self.file_info.clear()
        self._update_files_display()
    
    def _start_merge(self, e):
        """Start the merge operation"""
        valid_files = [f['path'] for f in self.file_info if not f.get('error', False)]
        
        if len(valid_files) < 2:
            return
        
        self.is_processing = True
        self.progress_container.visible = True
        self.results_container.visible = False
        self._update_merge_button()
        self.page.update()
        
        # Run merge operation in background thread
        threading.Thread(
            target=self._perform_merge,
            args=(valid_files,),
            daemon=True
        ).start()
    
    def _perform_merge(self, file_paths: List[Path]):
        """Perform the actual merge operation"""
        try:
            from core.pdf_processor import PDFProcessor
            from core.ghostscript_manager import GhostscriptManager
            from config.settings import DirectoryConfig

            # Setup processor
            dir_config = DirectoryConfig.get_default()
            output_dir = dir_config.output_dir / "merged"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Initialize Ghostscript manager with path detection
            from config.ghostscript_config import GhostscriptConfig
            from config.settings import DirectoryConfig

            # Get config directory
            dir_config = DirectoryConfig.get_default()
            config_dir = dir_config.config_dir

            # Initialize Ghostscript config
            gs_config = GhostscriptConfig(config_dir)
            gs_path = gs_config.auto_detect_ghostscript()

            if not gs_path:
                raise Exception("Ghostscript no encontrado. Por favor instala Ghostscript.")

            gs_manager = GhostscriptManager(gs_path)
            processor = PDFProcessor(gs_manager, output_dir)

            # Update progress
            self._update_progress("Iniciando fusión de PDFs...")

            # Merge PDFs
            result = processor.merge_pdfs(
                input_paths=file_paths,
                output_filename=self.output_filename,
                progress_callback=self._update_progress
            )

            # Update UI with results
            self._show_merge_results(result)

        except Exception as e:
            self._show_error(f"Error durante la fusión: {str(e)}")
        finally:
            self.is_processing = False
            self._update_merge_button()
    
    def _update_progress(self, message: str):
        """Update progress message"""
        if self.progress_container.content and hasattr(self.progress_container.content, 'controls'):
            progress_column = self.progress_container.content
            if len(progress_column.controls) > 1:
                progress_column.controls[1].value = message
                self.page.update()
    
    def _show_merge_results(self, result):
        """Show merge operation results"""
        self.progress_container.visible = False
        
        if result.success:
            self.results_container.content = ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="#059669", size=28),
                    ft.Text("Fusión Completada", size=18, weight=ft.FontWeight.BOLD, color="#059669")
                ], spacing=12),
                ft.Container(height=12),
                ft.Text(result.message, size=14),
                ft.Container(height=16),
                ft.Row([
                    ft.ElevatedButton(
                        text="Abrir Archivo",
                        icon=ft.Icons.OPEN_IN_NEW,
                        on_click=lambda _: self._open_result_file(result.output_path),
                        style=ft.ButtonStyle(bgcolor="#059669", color="white")
                    ),
                    ft.ElevatedButton(
                        text="Mostrar en Carpeta",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=lambda _: self._open_result_folder(result.output_path.parent),
                        style=ft.ButtonStyle(bgcolor="#3b82f6", color="white")
                    ),
                    ft.ElevatedButton(
                        text="Fusionar Más",
                        icon=ft.Icons.ADD,
                        on_click=self._reset_interface,
                        style=ft.ButtonStyle(bgcolor="#2563eb", color="white")
                    )
                ], spacing=12, alignment=ft.MainAxisAlignment.CENTER)
            ])
        else:
            self._show_error(result.message)
        
        self.results_container.visible = True
        self.page.update()
        
        if self.on_merge_complete:
            self.on_merge_complete(result)
    
    def _open_result_file(self, file_path: Path):
        """Open the result file"""
        import subprocess
        import sys
        
        try:
            if sys.platform == "win32":
                subprocess.run(["start", "", str(file_path)], shell=True)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(file_path)])
            else:
                subprocess.run(["xdg-open", str(file_path)])
        except Exception as e:
            print(f"Error opening file: {e}")
    
    def _open_result_folder(self, folder_path: Path):
        """Open the result folder"""
        import subprocess
        import sys
        
        try:
            if sys.platform == "win32":
                subprocess.run(["explorer", str(folder_path)])
            elif sys.platform == "darwin":
                subprocess.run(["open", str(folder_path)])
            else:
                subprocess.run(["xdg-open", str(folder_path)])
        except Exception as e:
            print(f"Error opening folder: {e}")
    
    def _reset_interface(self, e):
        """Reset the interface for new operation"""
        self.selected_files.clear()
        self.file_info.clear()
        self.output_filename = "merged_document.pdf"
        
        self.progress_container.visible = False
        self.results_container.visible = False
        
        self._update_files_display()
    
    def _show_error(self, message: str):
        """Show error message"""
        self.progress_container.visible = False
        self.results_container.content = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.ERROR, color="#dc2626", size=28),
                ft.Text("Error", size=18, weight=ft.FontWeight.BOLD, color="#dc2626")
            ], spacing=12),
            ft.Container(height=12),
            ft.Text(message, size=14, color="#dc2626"),
            ft.Container(height=16),
            ft.ElevatedButton(
                text="Intentar de Nuevo",
                icon=ft.Icons.REFRESH,
                on_click=self._reset_interface,
                style=ft.ButtonStyle(bgcolor="#dc2626", color="white")
            )
        ])
        self.results_container.visible = True
        self.page.update()

    def _is_dark_mode(self):
        """Check if current theme is dark mode"""
        return self.theme.get('background', '#ffffff') == '#0f172a'

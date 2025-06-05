"""
PDF Splitter Component for HYDRA21 PDF Compressor Pro
Provides PDF splitting functionality with page selection interface
"""

import flet as ft
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
import PyPDF2
import threading
import time

class PDFSplitter(ft.Column):
    """PDF Splitter component with page selection interface"""
    
    def __init__(self, page: ft.Page, theme: Dict[str, str], on_split_complete: Optional[Callable] = None):
        self.page = page
        self.theme = theme
        self.on_split_complete = on_split_complete
        
        # State
        self.selected_pdf: Optional[Path] = None
        self.pdf_info: Dict[str, Any] = {}
        self.selected_pages: List[int] = []
        self.is_processing = False
        
        # UI Components
        self.file_picker = None
        self.pdf_info_container = None
        self.page_selection_container = None
        self.split_options_container = None
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
            on_result=self._on_pdf_selected
        )
        self.page.overlay.append(self.file_picker)
        
        # PDF info container
        self.pdf_info_container = ft.Container(
            content=ft.Column([
                ft.Text("Selecciona un PDF para dividir", 
                       size=16, color=self.theme.get('on_surface_variant', '#64748b'))
            ]),
            padding=20,
            border_radius=12,
            border=ft.border.all(1, self.theme.get('outline', '#e2e8f0')),
            bgcolor=self.theme.get('surface', '#ffffff')
        )
        
        # Page selection container
        self.page_selection_container = ft.Container(
            content=ft.Column([
                ft.Text("Páginas del PDF", size=16, weight=ft.FontWeight.W_600),
                ft.Text("Selecciona las páginas que deseas extraer", size=14, color=self.theme.get('on_surface_variant', '#64748b'))
            ]),
            visible=False,
            padding=20,
            border_radius=12,
            border=ft.border.all(1, self.theme.get('outline', '#e2e8f0')),
            bgcolor=self.theme.get('surface', '#ffffff')
        )
        
        # Split options container
        self.split_options_container = ft.Container(
            content=ft.Column([
                ft.Text("Opciones de División", size=16, weight=ft.FontWeight.W_600),
                ft.Row([
                    ft.ElevatedButton(
                        text="Dividir Páginas Seleccionadas",
                        icon=ft.Icons.CONTENT_CUT,
                        on_click=self._split_selected_pages,
                        disabled=True,
                        style=ft.ButtonStyle(
                            bgcolor="#2563eb",
                            color="white"
                        )
                    ),
                    ft.ElevatedButton(
                        text="Dividir Todas las Páginas",
                        icon=ft.Icons.SPLITSCREEN,
                        on_click=self._split_all_pages,
                        disabled=True,
                        style=ft.ButtonStyle(
                            bgcolor="#059669",
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
                    ft.Text("Dividiendo PDF...", size=14, color="#2563eb")
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
                ft.Icon(ft.Icons.CONTENT_CUT, color="#2563eb", size=24),
                ft.Text(
                    "División de PDFs",
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
                            text="Seleccionar PDF",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=lambda _: self.file_picker.pick_files(
                                allowed_extensions=["pdf"],
                                dialog_title="Seleccionar PDF para dividir"
                            ),
                            style=ft.ButtonStyle(
                                bgcolor="#2563eb",
                                color="white",
                                padding=ft.padding.symmetric(horizontal=20, vertical=12)
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    
                    ft.Container(height=16),
                    self.pdf_info_container
                ]),
                padding=20,
                border_radius=12,
                border=ft.border.all(1, self.theme.get('outline', '#e2e8f0')),
                bgcolor=self.theme.get('surface_variant', '#f8fafc')
            ),
            
            # Page selection
            self.page_selection_container,
            
            # Split options
            self.split_options_container,
            
            # Progress
            self.progress_container,
            
            # Results
            self.results_container
        ]
    
    def _on_pdf_selected(self, e: ft.FilePickerResultEvent):
        """Handle PDF file selection"""
        if e.files:
            self.selected_pdf = Path(e.files[0].path)
            self._analyze_pdf()
    
    def _analyze_pdf(self):
        """Analyze the selected PDF and show page information"""
        if not self.selected_pdf or not self.selected_pdf.exists():
            return
        
        try:
            with open(self.selected_pdf, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                # Get PDF metadata
                metadata = pdf_reader.metadata
                title = metadata.get('/Title', 'Sin título') if metadata else 'Sin título'
                
                self.pdf_info = {
                    'title': title,
                    'num_pages': num_pages,
                    'file_size': self.selected_pdf.stat().st_size,
                    'file_name': self.selected_pdf.name
                }
                
                self._update_pdf_info_display()
                self._create_page_selection_interface()
                
        except Exception as e:
            self._show_error(f"Error al analizar el PDF: {str(e)}")
    
    def _update_pdf_info_display(self):
        """Update the PDF info display"""
        info = self.pdf_info
        file_size_mb = info['file_size'] / (1024 * 1024)
        
        self.pdf_info_container.content = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PICTURE_AS_PDF, color="#dc2626", size=32),
                ft.Column([
                    ft.Text(info['file_name'], size=16, weight=ft.FontWeight.W_600),
                    ft.Text(f"Páginas: {info['num_pages']} | Tamaño: {file_size_mb:.1f} MB", 
                           size=14, color=self.theme.get('on_surface_variant', '#64748b'))
                ], spacing=4, expand=True)
            ], spacing=12)
        ])
        
        self.page.update()
    
    def _create_page_selection_interface(self):
        """Create the page selection interface"""
        if not self.pdf_info:
            return
        
        num_pages = self.pdf_info['num_pages']
        page_buttons = []
        
        # Create page selection buttons (limit to reasonable number for UI)
        max_display_pages = min(num_pages, 50)  # Limit for UI performance
        
        for i in range(1, max_display_pages + 1):
            is_selected = i in self.selected_pages

            # Theme-aware colors
            if is_selected:
                text_color = "#ffffff"
                bg_color = "#2563eb"
                border_color = "#2563eb"
            else:
                text_color = self.theme.get('on_surface', '#1e293b') if not self._is_dark_mode() else "#e2e8f0"
                bg_color = self.theme.get('surface', '#ffffff') if not self._is_dark_mode() else "#374151"
                border_color = self.theme.get('outline', '#e2e8f0') if not self._is_dark_mode() else "#4b5563"

            page_buttons.append(
                ft.Container(
                    content=ft.Text(
                        str(i),
                        size=12,
                        text_align=ft.TextAlign.CENTER,
                        color=text_color,
                        weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL
                    ),
                    width=40,
                    height=40,
                    border_radius=8,
                    border=ft.border.all(2, border_color),
                    bgcolor=bg_color,
                    on_click=lambda e, page=i: self._toggle_page_selection(page),
                    alignment=ft.alignment.center
                )
            )
        
        # If there are more pages than we can display
        if num_pages > max_display_pages:
            page_buttons.append(
                ft.Text(f"... y {num_pages - max_display_pages} páginas más", 
                       size=12, color=self.theme.get('on_surface_variant', '#64748b'))
            )
        
        # Create rows of page buttons
        rows = []
        for i in range(0, len(page_buttons), 10):  # 10 buttons per row
            row_buttons = page_buttons[i:i+10]
            rows.append(ft.Row(row_buttons, spacing=8, wrap=True))
        
        self.page_selection_container.content = ft.Column([
            ft.Text("Páginas del PDF", size=16, weight=ft.FontWeight.W_600),
            ft.Text("Haz clic en las páginas que deseas extraer", 
                   size=14, color=self.theme.get('on_surface_variant', '#64748b')),
            ft.Container(height=12),
            ft.Container(
                content=ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO),
                height=200,
                padding=10,
                border_radius=8,
                border=ft.border.all(1, self.theme.get('outline', '#e2e8f0'))
            ),
            ft.Container(height=16),
            ft.Row([
                ft.TextButton("Seleccionar Todas", on_click=self._select_all_pages),
                ft.TextButton("Deseleccionar Todas", on_click=self._deselect_all_pages)
            ], spacing=12)
        ])
        
        self.page_selection_container.visible = True
        self.split_options_container.visible = True
        self.page.update()
    
    def _toggle_page_selection(self, page_num: int):
        """Toggle page selection"""
        if page_num in self.selected_pages:
            self.selected_pages.remove(page_num)
        else:
            self.selected_pages.append(page_num)
        
        self._update_page_buttons()
        self._update_split_buttons()
        self.page.update()
    
    def _update_page_buttons(self):
        """Update the visual state of page buttons"""
        # Regenerate the page selection display with current selection
        if self.pdf_info:
            self._create_page_selection_interface()
    
    def _update_split_buttons(self):
        """Update the state of split buttons"""
        has_selection = len(self.selected_pages) > 0
        has_pdf = self.selected_pdf is not None
        
        # Update button states in split_options_container
        if self.split_options_container.content and hasattr(self.split_options_container.content, 'controls'):
            for control in self.split_options_container.content.controls:
                if isinstance(control, ft.Row):
                    for button in control.controls:
                        if isinstance(button, ft.ElevatedButton):
                            if "Seleccionadas" in button.text:
                                button.disabled = not (has_selection and has_pdf)
                            else:
                                button.disabled = not has_pdf
        
        self.page.update()
    
    def _select_all_pages(self, e):
        """Select all pages"""
        if self.pdf_info:
            self.selected_pages = list(range(1, self.pdf_info['num_pages'] + 1))
            self._update_page_buttons()
            self._update_split_buttons()
    
    def _deselect_all_pages(self, e):
        """Deselect all pages"""
        self.selected_pages = []
        self._update_page_buttons()
        self._update_split_buttons()
    
    def _split_selected_pages(self, e):
        """Split selected pages"""
        if not self.selected_pages or not self.selected_pdf:
            return
        
        self._start_split_operation("selected", self.selected_pages)
    
    def _split_all_pages(self, e):
        """Split all pages"""
        if not self.selected_pdf:
            return
        
        self._start_split_operation("all", None)
    
    def _start_split_operation(self, mode: str, pages: Optional[List[int]]):
        """Start the split operation"""
        self.is_processing = True
        self.progress_container.visible = True
        self.results_container.visible = False
        self.page.update()
        
        # Run split operation in background thread
        threading.Thread(
            target=self._perform_split,
            args=(mode, pages),
            daemon=True
        ).start()
    
    def _perform_split(self, mode: str, pages: Optional[List[int]]):
        """Perform the actual split operation"""
        try:
            from core.pdf_processor import PDFProcessor
            from core.ghostscript_manager import GhostscriptManager
            from config.settings import DirectoryConfig

            # Setup processor
            dir_config = DirectoryConfig.get_default()
            output_dir = dir_config.output_dir / "split"
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
            self._update_progress("Iniciando división de PDF...")

            if mode == "all":
                # Split all pages
                result = processor.split_pdf(
                    input_path=self.selected_pdf,
                    progress_callback=self._update_progress
                )
            else:
                # Split selected pages using the new method
                result = processor.split_pdf_pages(
                    input_path=self.selected_pdf,
                    page_numbers=pages,
                    progress_callback=self._update_progress
                )

            # Update UI with results
            self._show_split_results(result)

        except Exception as e:
            self._show_error(f"Error durante la división: {str(e)}")
        finally:
            self.is_processing = False
    
    def _update_progress(self, message: str):
        """Update progress message"""
        if self.progress_container.content and hasattr(self.progress_container.content, 'controls'):
            progress_column = self.progress_container.content
            if len(progress_column.controls) > 1:
                progress_column.controls[1].value = message
                self.page.update()
    
    def _show_split_results(self, result):
        """Show split operation results"""
        self.progress_container.visible = False
        
        if result.success:
            self.results_container.content = ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color="#059669", size=28),
                    ft.Text("División Completada", size=18, weight=ft.FontWeight.BOLD, color="#059669")
                ], spacing=12),
                ft.Container(height=12),
                ft.Text(result.message, size=14),
                ft.Container(height=16),
                ft.Row([
                    ft.ElevatedButton(
                        text="Abrir Carpeta",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=lambda _: self._open_result_folder(result.output_path),
                        style=ft.ButtonStyle(bgcolor="#059669", color="white")
                    ),
                    ft.ElevatedButton(
                        text="Dividir Otro PDF",
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
        
        if self.on_split_complete:
            self.on_split_complete(result)
    
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
        self.selected_pdf = None
        self.pdf_info = {}
        self.selected_pages = []
        
        self.pdf_info_container.content = ft.Column([
            ft.Text("Selecciona un PDF para dividir", 
                   size=16, color=self.theme.get('on_surface_variant', '#64748b'))
        ])
        
        self.page_selection_container.visible = False
        self.split_options_container.visible = False
        self.progress_container.visible = False
        self.results_container.visible = False
        
        self.page.update()
    
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

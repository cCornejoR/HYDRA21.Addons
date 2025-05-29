# main.py - HYDRA21 PDF Compressor - Professional Compact UI Refactored
"""
Módulo principal refactorizado de HYDRA21 PDF Compressor.

Nuevas funcionalidades:
- Selección específica de páginas por archivo
- Mejor gestión de estado de botones
- UI/UX mejorada
- Integración mejorada de NotebookLM
"""

import flet as ft
import threading
import os
import webbrowser
import subprocess
import json
import glob
import sys
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import datetime
import tempfile
import shutil
import asyncio

# Importar módulos del proyecto
from themes import ThemeManager, ModernThemes, create_modern_button, create_modern_card
from settings import GS_PRESETS, DEFAULT_PRESET, CONFIG_FILE
from utils import FileUtils, GhostscriptUtils, ConfigManager
from compressor_logic import PDFCompressor, CompressionStats, BatchCompressionStats, BatchCompressionResult
from pdf_converter import PDFConverter, PDFConversionError
from up_to_notebooklm import subir_pdf_a_notebooklm

class FilePageConfig:
    """Configuración de páginas para un archivo específico"""
    def __init__(self, file_path: Path, page_ranges: List[Tuple[int, int]] = None, original_name: str = None):
        self.file_path = file_path
        self.page_ranges = page_ranges or []  # Lista de tuplas (inicio, fin)
        self.original_name = original_name or file_path.name
        self.process_entire_file = len(page_ranges) == 0 if page_ranges else True
    
    def get_display_name(self) -> str:
        """Obtener nombre para mostrar con información de páginas"""
        if self.process_entire_file:
            return f"{self.original_name} (completo)"
        else:
            ranges_str = ", ".join([f"{start}-{end}" if start != end else str(start) 
                                  for start, end in self.page_ranges])
            return f"{self.original_name} (págs: {ranges_str})"
    
    def has_page_selection(self) -> bool:
        """Verificar si tiene selección específica de páginas"""
        return not self.process_entire_file and len(self.page_ranges) > 0

class UIState:
    """Clase para manejar el estado de la UI"""
    def __init__(self):
        self.is_processing = False
        self.has_files = False
        self.show_preview = False
        self.show_results = False
        self.current_operation = None  # 'compress', 'export', 'preview', etc.
    
    def set_processing(self, operation: str = None):
        self.is_processing = True
        self.current_operation = operation
    
    def set_idle(self):
        self.is_processing = False
        self.current_operation = None
    
    def should_show_button(self, button_type: str) -> bool:
        """Determinar si un botón debe mostrarse según el estado actual"""
        if self.is_processing:
            if button_type in ['cancel', 'progress_info']:
                return True
            return False
        
        if button_type in ['compress', 'export_docx', 'preview'] and not self.has_files:
            return False
            
        return True
    
    def should_enable_button(self, button_type: str) -> bool:
        """Determinar si un botón debe estar habilitado"""
        if self.is_processing:
            return button_type in ['cancel']
        
        if button_type in ['compress', 'export_docx', 'preview']:
            return self.has_files
            
        return True

class HYDRA21_PDFCompressor:
    """Aplicación profesional de compresión PDF mejorada con UI moderna y compacta."""
    
    def __init__(self, page: ft.Page):
        """Inicializar la aplicación."""
        self.page = page
        self.theme_manager = ThemeManager()
        self.config_manager = ConfigManager()
        self.ui_state = UIState()
        
        # Configurar carpeta de salida
        documents_dir = Path.home() / "Documents"
        self.output_dir = documents_dir / "HYDRA21-PDFCompressor"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Limpiar directorio temporal al cerrar
        self.page.on_disconnect = lambda e: shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Inicializar utilidades
        self.pdf_compressor = PDFCompressor(output_dir=self.output_dir)
        self.file_utils = FileUtils()
        self.gs_utils = GhostscriptUtils()
        self.pdf_converter = PDFConverter()
        
        # Estado de archivos con configuración de páginas
        self.file_configs: List[FilePageConfig] = []
        self.selected_file_config: Optional[FilePageConfig] = None
        
        # Estados de resultados
        self.compression_stats: Optional[CompressionStats] = None
        self.batch_stats: Optional[BatchCompressionStats] = None
        
        # Configurar página
        self.setup_page()
        
        # Crear controles
        self.create_controls()
        
        # Verificar Ghostscript
        self.verify_ghostscript()
        
        # Construir UI
        self.build_ui()

    def setup_page(self):
        """Configurar propiedades de la página."""
        self.page.title = "HYDRA21 PDF Compressor"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.width = 900
        self.page.window.height = 1000
        self.page.window.resizable = True
        self.page.window.title_bar_hidden = False
        self.page.padding = 0
        self.page.on_file_picker_result = self.on_file_picker_result
        
        # Configurar icono
        self.configure_app_icon()


    def configure_app_icon(self):
        """Configurar icono de la aplicación"""
        try:
            icon_path = Path("assets/icons/logo32x32.ico")
            if icon_path.exists():
                self.page.window.icon = str(icon_path.absolute())
                return
            
            app_dir = Path(__file__).parent
            icon_path = app_dir / "assets" / "icons" / "logo32x32.ico"
            if icon_path.exists():
                self.page.window.icon = str(icon_path.absolute())
                return
                
        except Exception as e:
            print(f"Error configurando icono: {e}")

    async def apply_theme(self):
        """Aplicar tema actual a la página."""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        self.page.theme_mode = ft.ThemeMode.DARK if self.theme_manager.is_dark else ft.ThemeMode.LIGHT
        self.page.bgcolor = theme['background']
        await self.page.update_async()

    def create_controls(self):
        """Crear todos los controles de la UI"""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        
        # Header con toggle de tema
        self.header = self.create_header()
        
        # Drop zone mejorada
        self.drop_zone = self.create_drop_zone()
        
        # Lista de archivos mejorada
        self.files_list_container = ft.Container(
            content=ft.Column(spacing=8),
            padding=ft.padding.all(10),
            visible=False
        )
        
        # Selector de calidad
        self.quality_selector = self.create_quality_selector()
        
        # Botones principales con mejor gestión de estado
        self.create_action_buttons()
        
        # Controles de previsualización mejorados
        self.create_preview_controls()
        
        # Contenedores de progreso y resultados (eliminados)
        # self.progress_container = ft.Container(visible=False)
        # self.results_container = ft.Container(visible=False)
        # self.gs_status = ft.Container(visible=False)

    def create_header(self):
        """Crear header mejorado con información de estado"""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        
        # Toggle de tema
        theme_toggle = ft.IconButton(
            icon=ft.Icons.DARK_MODE if not self.theme_manager.is_dark else ft.Icons.LIGHT_MODE,
            icon_color=theme['on_surface'],
            tooltip="Cambiar tema",
            on_click=self.toggle_theme,
            icon_size=20,
            style=ft.ButtonStyle(
                shape=ft.CircleBorder(),
                bgcolor=theme['surface_variant'],
            )
        )
        
        # Indicador de estado
        self.status_text = ft.Text("Listo", size=12, color=theme['on_surface_variant'])
        self.progress_bar = ft.ProgressBar(value=0, visible=False, color=theme['primary'], bgcolor=theme['surface_variant'])

        self.status_indicator = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color=theme['success']),
                    self.status_text
                ], spacing=5),
                self.progress_bar
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.START),
            visible=True
        )
        
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.PICTURE_AS_PDF, color=theme['primary'], size=22),
                            bgcolor=theme['surface_variant'],
                            width=38,
                            height=38,
                            border_radius=10,
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text("HYDRA21 PDF Compressor", 
                                   size=18, 
                                   weight=ft.FontWeight.W_600, 
                                   color=theme['on_surface']),
                            self.status_indicator
                        ], spacing=2, tight=True)
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True
                ),
                theme_toggle
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=16, vertical=15),
            bgcolor=theme['surface'],
            border=ft.border.only(bottom=ft.BorderSide(1, theme['border']))
        )

    async def update_status_indicator(self, message: str, is_processing: bool = False, progress: Optional[float] = None):
        """Actualiza el indicador de estado en el header."""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        if is_processing:
            self.status_text.value = message
            self.status_text.color = theme['on_surface']
            self.status_indicator.content.controls[0].controls[0].visible = False # Hide the circle icon
            self.progress_bar.visible = True
            if progress is not None:
                self.progress_bar.value = progress
        else:
            self.status_text.value = message
            self.status_text.color = theme['success']
            self.status_indicator.content.controls[0].controls[0].visible = True # Show the circle icon
            self.status_indicator.content.controls[0].controls[0].content.color = theme['success'] # Set color to success
            self.progress_bar.visible = False
            self.progress_bar.value = 0
        await self.page.update_async()

    def create_drop_zone(self):
        """Crear zona de arrastrar y soltar mejorada"""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()

        self.drop_zone_content = ft.Column([
            ft.Container(
                content=ft.Icon(ft.Icons.CLOUD_UPLOAD, size=36, color=theme['on_surface_variant']),
                width=70,
                height=70,
                border_radius=35,
                bgcolor=theme['surface'],
                alignment=ft.alignment.center,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=8,
                    color=theme['shadow'],
                    offset=ft.Offset(0, 3)
                )
            ),
            ft.Text("Arrastra archivos PDF aquí",
                   size=16,
                   weight=ft.FontWeight.W_500,
                   color=theme['on_surface']),
            ft.Text("o haz clic para seleccionar", 
                   size=14, 
                   color=theme['on_surface_variant']),
            create_modern_button(
                text="Seleccionar archivos",
                icon=ft.Icons.FOLDER_OPEN,
                on_click=self.pick_files,
                style="primary",
                theme=theme
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)

        return ft.DragTarget(
            group="pdf_files",
            content=ft.Container(
                content=self.drop_zone_content,
                padding=ft.padding.symmetric(horizontal=20, vertical=25),
                border=ft.border.all(2, theme['border_variant']),
                border_radius=16,
                bgcolor=theme['surface_variant'],
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                alignment=ft.alignment.center,
                height=250
            ),
            on_will_accept=self.on_drag_will_accept,
            on_leave=self.on_drag_leave,
            on_accept=self.on_drag_accept
        )

    def create_action_buttons(self):
        """Crear botones de acción con mejor gestión de estado"""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        
        # Botón de compresión principal
        self.compress_button = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.COMPRESS, color="white", size=18),
                    ft.Text("Comprimir PDFs", size=15, weight=ft.FontWeight.W_600, color="white")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8
            ),
            height=50,
            bgcolor=theme['button_primary_bg'],
            border_radius=12,
            padding=ft.padding.all(12),
            alignment=ft.alignment.center,
            on_click=self.compress_pdfs,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=theme['shadow'],
                offset=ft.Offset(0, 3)
            ),
            disabled=True
        )
        
        # Botón de selección de documento mejorado
        self.select_document_button = create_modern_button(
            text="Configurar páginas",
            icon=ft.Icons.SETTINGS,
            on_click=self.show_document_selector,
            style="secondary",
            theme=theme
        )
        
        # Botones de exportación
        self.export_docx_button = create_modern_button(
            text="PDF a DOCX",
            icon=ft.Icons.FILE_DOWNLOAD_DONE,
            on_click=self.export_full_pdf_to_docx,
            style="secondary",
            theme=theme
        )
        
        self.export_page_docx_button = create_modern_button(
            text="Página a DOCX",
            icon=ft.Icons.FIND_IN_PAGE_OUTLINED,
            on_click=self.export_current_page_to_docx,
            style="secondary",
            theme=theme
        )

    def create_preview_controls(self):
        """Crear controles de previsualización mejorados"""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        
        self.page_number_input = ft.TextField(
            label="Página",
            value="1",
            width=120,
            text_align=ft.TextAlign.CENTER,
            dense=True,
            on_change=self.on_page_number_change,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.preview_button = create_modern_button(
            text="Previsualizar",
            icon=ft.Icons.IMAGE_SEARCH,
            on_click=self.preview_pdf_page,
            style="secondary",
            theme=theme
        )
        
        self.preview_image = ft.Image(
            src="",
            width=300,
            height=300,
            fit=ft.ImageFit.CONTAIN,
            visible=False
        )
        
        self.preview_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    self.page_number_input,
                    self.preview_button
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                ft.Container(height=10),
                self.preview_image
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(15),
            border_radius=12,
            bgcolor=theme['surface_variant'],
            visible=False
        )

    def create_quality_selector(self):
        """Crear selector de calidad mejorado"""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        
        self.quality_dropdown = ft.Dropdown(
            label="Calidad de compresión",
            value=DEFAULT_PRESET,
            options=[ft.dropdown.Option(key) for key in GS_PRESETS.keys()],
            filled=True,
            bgcolor=theme['surface'],
            border_color=theme['input_border'],
            border_radius=8,
            focused_border_color=theme['input_focused_border']
        )
        
        quality_info = [
            {"name": "Máxima Calidad", "desc": "Mejor para impresión", "icon": ft.Icons.PRINT},
            {"name": "Alta Calidad", "desc": "Equilibrio ideal", "icon": ft.Icons.HIGH_QUALITY},
            {"name": "Calidad Media", "desc": "Para documentos digitales", "icon": ft.Icons.TABLET},
            {"name": "Baja Calidad", "desc": "Máxima compresión", "icon": ft.Icons.COMPRESS}
        ]
        
        quality_grid = ft.GridView(
            expand=True,
            runs_count=2,
            max_extent=200,
            child_aspect_ratio=2.5,
            spacing=8,
            run_spacing=8
        )
        
        for item in quality_info:
            quality_grid.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(item["icon"], size=16, color=theme['primary']),
                        ft.Column([
                            ft.Text(item["name"], size=12, weight=ft.FontWeight.W_500),
                            ft.Text(item["desc"], size=10, color=theme['on_surface_variant'])
                        ], spacing=2, tight=True, expand=True)
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
                    padding=ft.padding.all(8),
                    border_radius=8,
                    bgcolor=theme['surface'],
                    height=50
                )
            )
        
        return create_modern_card(
            content=[
                ft.Row([
                    ft.Icon(ft.Icons.TUNE, size=18, color=theme['primary']),
                    ft.Text("Configuración", size=16, weight=ft.FontWeight.W_600)
                ], spacing=8),
                ft.Container(height=10),
                self.quality_dropdown,
                ft.Container(height=15),
                quality_grid
            ],
            theme=theme,
            padding=ft.padding.all(20)
        )
    async def show_document_selector(self, e):
        """Mostrar diálogo de selección de documento y páginas"""
        if not self.file_configs:
            await self.show_snackbar("Primero selecciona archivos PDF", error=True)
            return
        
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        
        # Lista de archivos disponibles
        file_options = []
        for i, config in enumerate(self.file_configs):
            file_size = await self.file_utils.get_file_size_async(config.file_path)
            file_options.append(
                ft.ListTile(
                    leading=ft.Radio(
                        value=str(i),
                    ),
                    title=ft.Text(config.original_name),
                    subtitle=ft.Text(f"Tamaño: {file_size}"),
                    on_click=lambda e, index=i: self.select_file_for_pages(index)
                )
            )
        
        # Controles de páginas
        self.page_start_input = ft.TextField(
            label="Página inicial",
            value="1",
            width=120,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.page_end_input = ft.TextField(
            label="Página final",
            value="",
            width=120,
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="Vacío = hasta el final"
        )
        
        self.selected_file_radio = ft.RadioGroup(
            content=ft.Column(file_options, spacing=5),
            value=str(0) if not self.selected_file_config else 
                  str(self.file_configs.index(self.selected_file_config))
        )
        
        async def close_dialog(e):
            dialog.open = False
            await self.page.update_async()
        
        async def apply_selection(e):
            try:
                selected_index = int(self.selected_file_radio.value) if self.selected_file_radio.value else 0
                self.selected_file_config = self.file_configs[selected_index]
                
                start_page = int(self.page_start_input.value) if self.page_start_input.value else 1
                end_page = int(self.page_end_input.value) if self.page_end_input.value else None
                
                if end_page and end_page < start_page:
                    await self.show_snackbar("La página final debe ser mayor que la inicial", error=True)
                    return
                
                # Actualizar configuración
                if start_page == 1 and not end_page:
                    self.selected_file_config.process_entire_file = True
                    self.selected_file_config.page_ranges = []
                else:
                    self.selected_file_config.process_entire_file = False
                    self.selected_file_config.page_ranges = [(start_page, end_page or start_page)]
                
                await self.update_files_display()
                await self.show_snackbar(f"Configuración aplicada: {self.selected_file_config.get_display_name()}")
                await close_dialog(e)
                
            except ValueError:
                await self.show_snackbar("Por favor ingresa números válidos para las páginas", error=True)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Configurar procesamiento de páginas"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Selecciona el archivo:", weight=ft.FontWeight.W_500),
                    self.selected_file_radio,
                    ft.Divider(height=20),
                    ft.Text("Rango de páginas:", weight=ft.FontWeight.W_500),
                    ft.Row([
                        self.page_start_input,
                        ft.Text("-"),
                        self.page_end_input
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=10, tight=True),
                width=400,
                height=300
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.TextButton("Aplicar", on_click=apply_selection)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog = dialog
        dialog.open = True
        await self.page.update_async()

    async def update_status_indicator(self, message: str, is_processing: bool = False, progress: Optional[float] = None):
        """Update status indicator in header"""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        
        if is_processing:
            icon = ft.Icons.HOURGLASS_EMPTY
            color = theme['warning']
        elif message == "Listo":
            icon = ft.Icons.CHECK_CIRCLE
            color = theme['success']
        elif "Error" in message:
            icon = ft.Icons.ERROR
            color = theme['error']
        else:
            icon = ft.Icons.INFO
            color = theme['primary']
        
        self.status_text.value = message
        self.status_text.color = theme['on_surface'] if is_processing else color
        self.status_indicator.content.controls[0].controls[0].content.color = color
        self.status_indicator.content.controls[0].controls[0].visible = not is_processing
        self.progress_bar.visible = is_processing
        if progress is not None:
            self.progress_bar.value = progress
        
        await self.page.update_async()

    async def update_ui_state(self):
        """Update state of all UI elements"""
        self.ui_state.has_files = len(self.file_configs) > 0
        
        # Update button visibility and state
        self.compress_button.disabled = not self.ui_state.should_enable_button('compress')
        self.select_document_button.disabled = not self.ui_state.should_enable_button('compress')
        self.export_docx_button.disabled = not self.ui_state.should_enable_button('export_docx')
        self.export_page_docx_button.disabled = not self.ui_state.should_enable_button('export_docx')
        self.preview_button.disabled = not self.ui_state.should_enable_button('preview')
        
        # Update container visibility
        self.files_list_container.visible = self.ui_state.has_files
        self.preview_container.visible = self.ui_state.has_files and self.ui_state.show_preview
        
        # Update compression button text
        files_count = len(self.file_configs)
        button_text = "Comprimir PDFs" if files_count != 1 else "Comprimir PDF"
        if files_count > 1:
            button_text = f"Comprimir {files_count} PDFs"
        
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        self.compress_button.content = ft.Row([
            ft.Icon(ft.Icons.COMPRESS, color="white", size=18),
            ft.Text(button_text, size=15, weight=ft.FontWeight.W_600, color="white")
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8)
        
        await self.page.update_async()

    async def on_file_picker_result(self, e: ft.FilePickerResultEvent):
        """Handle file picker result"""
        if e.files:
            await self.handle_selected_files(e.files)

    async def handle_selected_files(self, files):
        """Process selected files"""
        for file in files:
            file_path = Path(file.path)
            if file_path.suffix.lower() == '.pdf':
                config = FilePageConfig(file_path, original_name=file.name)
                if config not in [fc.file_path for fc in self.file_configs]:
                    self.file_configs.append(config)
            else:
                await self.show_snackbar(f"Archivo no válido: {file.name}", error=True)
        
        await self.update_files_display()
        await self.update_ui_state()

    async def handle_dropped_files(self, dropped_files):
        """Handle dropped files"""
        for f_info in dropped_files:
            if f_info.name.lower().endswith(".pdf"):
                temp_file_path = Path(f_info.path)
                config = FilePageConfig(temp_file_path, original_name=f_info.name)
                self.file_configs.append(config)
            else:
                await self.show_snackbar(f"Archivo no válido: {f_info.name}", error=True)
        
        await self.update_files_display()
        await self.update_ui_state()

    async def update_files_display(self):
        """Update files display"""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        self.files_list_container.content.controls.clear()
        
        if not self.file_configs:
            self.files_list_container.visible = False
            return
        
        # List header
        header = ft.Container(
            content=ft.Row([
                ft.Text(f"{len(self.file_configs)} archivo(s) seleccionado(s)",
                       size=14, weight=ft.FontWeight.W_500),
                ft.Row([
                    self.select_document_button,
                    ft.TextButton("Limpiar todo", on_click=self.clear_all_files)
                ], spacing=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(vertical=10)
        )
        
        self.files_list_container.content.controls.append(header)
        
        # Files list
        for i, config in enumerate(self.file_configs):
            file_card = await self.create_file_card(config, i)
            self.files_list_container.content.controls.append(file_card)
        
        self.files_list_container.visible = True
        await self.page.update_async()

    async def create_file_card(self, config: FilePageConfig, index: int):
        """Create improved file card"""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        
        file_size = await self.file_utils.get_file_size_async(config.file_path)
        is_configured = config.has_page_selection()
        
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.PICTURE_AS_PDF,
                        color=theme['primary'] if not is_configured else theme['warning'],
                        size=24
                    ),
                    width=40,
                    height=40,
                    alignment=ft.alignment.center,
                    border_radius=8,
                    bgcolor=theme['surface_variant']
                ),
                ft.Column([
                    ft.Text(config.get_display_name(),
                           size=14, weight=ft.FontWeight.W_500,
                           overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"Tamaño: {file_size}",
                           size=12, color=theme['on_surface_variant'])
                ], spacing=2, expand=True, tight=True),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=theme['on_surface_variant'],
                    icon_size=18,
                    on_click=lambda _: self.remove_file_config(index),
                    tooltip="Remover archivo"
                )
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(12),
            border_radius=8,
            bgcolor=theme['surface'],
            border=ft.border.all(1, theme['warning'] if is_configured else theme['border']),
            margin=ft.margin.symmetric(vertical=2)
        )

    async def remove_file_config(self, index: int):
        """Remove file configuration"""
        if 0 <= index < len(self.file_configs):
            removed_config = self.file_configs.pop(index)
            if self.selected_file_config == removed_config:
                self.selected_file_config = None
            await self.update_files_display()
            await self.update_ui_state()

    async def clear_all_files(self, e):
        """Clear all files"""
        self.file_configs.clear()
        self.selected_file_config = None
        await self.update_files_display()
        await self.update_ui_state()
        self.results_container.visible = False
        self.preview_container.visible = False
        await self.page.update_async()

    # Drag and drop methods
    async def on_drag_will_accept(self, e):
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        e.control.content.border = ft.border.all(2, theme['primary'])
        await e.control.update_async()

    async def on_drag_leave(self, e):
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        e.control.content.border = ft.border.all(2, theme['border_variant'])
        await e.control.update_async()

    async def on_drag_accept(self, e):
        if e.files:
            await self.handle_dropped_files(e.files)
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        e.control.content.border = ft.border.all(2, theme['border_variant'])
        await e.control.update_async()

    async def pick_files(self, e):
        """Open file picker"""
        file_picker = ft.FilePicker(
            on_result=self.on_file_picker_result
        )
        self.page.overlay.append(file_picker)
        await self.page.update_async()
        
        file_picker.pick_files(
            dialog_title="Seleccionar archivos PDF",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"],
            allow_multiple=True
        )

    async def toggle_theme(self, e):
        """Change theme"""
        self.theme_manager.toggle_theme()

        await self.apply_theme()
        await self.refresh_ui()

    async def refresh_ui(self):
        """Refresh UI with new theme"""
        self.create_controls()
        self.build_ui()

    def verify_ghostscript(self):
        """Verify Ghostscript availability"""
        if not self.gs_utils.is_available():
            self.show_error("Ghostscript no está disponible. Por favor instálalo para usar la aplicación.")

    async def show_error(self, message: str):
        """Show error dialog"""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()
        
        async def close_dialog(e):
            dialog.open = False
            await self.page.update_async()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Error", color=theme['error']),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dialog)]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        await self.page.update_async()

    async def show_snackbar(self, message: str, error: bool = False, duration: int = 3000):
        """Show snackbar message"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.ERROR if error else None),
            duration=duration
        )
        self.page.snack_bar.open = True
        await self.page.update_async()

    async def on_page_number_change(self, e):
        """Handle page number change"""
        await self.update_ui_state()

    async def build_ui(self):
        """Build user interface"""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()

        # Footer
        footer = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=theme['on_surface_variant']),
                    ft.Text(f"HYDRA²¹ PDF Compressor v2.0 © {datetime.date.today().year}", 
                           size=11, color=theme['on_surface_variant'])
                ], spacing=5)
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor=theme['surface'],
            border=ft.border.only(top=ft.BorderSide(1, theme['border']))
        )

        # Main layout
        main_content = ft.Column([
            ft.Row([
                ft.Container(content=self.drop_zone, expand=2, padding=ft.padding.only(right=8)),
                ft.Container(content=self.quality_selector, expand=1, padding=ft.padding.only(left=8))
            ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.START),
            
            self.files_list_container,
            self.preview_container,
            
            ft.Row([
                self.compress_button,
                self.export_docx_button,
                self.export_page_docx_button
            ], spacing=12, alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.page.controls = [
            self.header,
            ft.Container(
                content=main_content,
                expand=True,
                padding=ft.padding.symmetric(horizontal=20, vertical=15)
            ),
            footer
        ]
        
        await self.update_ui_state()
        await self.page.update_async()

    async def show_compression_results_modal(self, batch_result: BatchCompressionResult):
        """Show compression results modal"""
        await self.apply_theme()
        theme = self.theme_manager.get_theme()

        modal_content = ft.Column(
            [
                ft.Text("Resultados de Compresión", size=20, weight=ft.FontWeight.BOLD, color=theme['on_surface']),
                ft.Divider(),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

        for stats in batch_result.file_stats:
            original_size_mb = stats.original_size / (1024 * 1024)
            compressed_size_mb = stats.compressed_size / (1024 * 1024)
            reduction_percent = (1 - (compressed_size_mb / original_size_mb)) * 100 if original_size_mb > 0 else 0

            modal_content.controls.append(
                ft.Column(
                    [
                        ft.Text(f"Archivo: {stats.file_path.name}", size=16, weight=ft.FontWeight.W_500, color=theme['on_surface']),
                        ft.Text(f"Tamaño Original: {original_size_mb:.2f} MB", size=14, color=theme['on_surface_variant']),
                        ft.Text(f"Tamaño Comprimido: {compressed_size_mb:.2f} MB", size=14, color=theme['on_surface_variant']),
                        ft.Text(f"Reducción: {reduction_percent:.2f}%", size=14, color=theme['on_surface_variant']),
                        ft.Divider(height=5)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=5
                )
            )
        
        modal_buttons = ft.Row(
            [
                create_modern_button(
                    text="Abrir Carpeta",
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=lambda e: self.file_utils.open_folder(str(self.output_dir)),
                    style="secondary",
                    theme=theme
                ),
                create_modern_button(
                    text="Comprimir Más Archivos",
                    icon=ft.Icons.ADD_CIRCLE,
                    on_click=lambda e: self.close_modal_and_reset(e),
                    style="primary",
                    theme=theme
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15
        )

        self.page.dialog = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                content=ft.Column(
                    [modal_content, modal_buttons],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                padding=20,
                width=400,
                height=500,
                bgcolor=theme['surface'],
                border_radius=15,
            ),
            on_dismiss=lambda e: print("Modal dismissed!")
        )
        self.page.dialog.open = True
        await self.page.update_async()

    async def close_modal_and_reset(self, e):
        """Close modal and reset UI for new compression"""
        self.page.dialog.open = False
        await self.page.update_async()
        await self.reset_ui_for_new_compression()

    async def reset_ui_for_new_compression(self):
        """Reset UI state for new compression"""
        self.file_configs = []
        self.selected_file_config = None
        self.compression_stats = None
        self.batch_stats = None
        self.ui_state.set_idle()
        await self.update_status_indicator("Listo", False)
        await self.update_ui_state()
        await self.page.update_async()

    async def compress_pdfs(self, e):
        """Compress PDFs with specific logic"""
        if not self.file_configs:
            return
        
        self.ui_state.set_processing('compress')
        await self.update_status_indicator("Compressing...", True)
        await self.update_ui_state()
        await self.page.update_async()

        try:
            pdf_compressor = PDFCompressor(output_dir=self.output_dir)
            quality_preset = self.quality_dropdown.value or DEFAULT_PRESET

            compression_jobs = []
            for fc in self.file_configs:
                if fc.has_page_selection():
                    for start, end in fc.page_ranges:
                        compression_jobs.append({
                            'path': fc.file_path,
                            'page_range': (start, end)
                        })
                else:
                    compression_jobs.append({
                        'path': fc.file_path,
                        'page_range': None
                    })

            batch_result = await pdf_compressor.compress_batch_async(
                compression_jobs=compression_jobs,
                quality_preset=quality_preset,
                progress_callback=self.update_compression_progress
            )

            if batch_result.success:
                self.ui_state.set_idle()
                await self.update_status_indicator("Compression completed", False)
                await self.show_compression_results_modal(batch_result)
            else:
                self.ui_state.set_idle()
                await self.update_status_indicator("Compression error", False)
                await self.show_snackbar(f"Error during compression: {batch_result.error_message}", error=True)

        except Exception as ex:
            self.ui_state.set_idle()
            await self.update_status_indicator("Compression error", False)
            await self.show_snackbar(f"Error during compression: {str(ex)}", error=True)
        finally:
            await self.page.update_async()

    async def update_compression_progress(self, current: int, total: int, filename: str):
        """Update compression progress indicator"""
        message = f"Compressing {filename}... ({current}/{total})"
        progress = current / total if total > 0 else 0
        await self.update_status_indicator(message, True, progress)

    def export_full_pdf_to_docx(self, e):
        """Exportar PDF completo a DOCX"""
        if not self.file_configs:
            return
        
        self.ui_state.set_processing('export')
        self.update_status_indicator("Exportando...", True)
        self.update_ui_state()
        
        # TODO: Implementar exportación
        self.show_snackbar("Función de exportación en desarrollo")

    def export_current_page_to_docx(self, e):
        """Exportar página actual a DOCX"""
        if not self.file_configs:
            return
        
        # TODO: Implementar exportación de página
        self.show_snackbar("Función de exportación de página en desarrollo")

    def preview_pdf_page(self, e):
        """Previsualizar página PDF"""
        if not self.file_configs:
            return
        
        # TODO: Implementar previsualización
        self.show_snackbar("Función de previsualización en desarrollo")

def main(page: ft.Page):
    """Función principal de la aplicación"""
    app = HYDRA21_PDFCompressor(page)

if __name__ == "__main__":
    ft.app(target=main)
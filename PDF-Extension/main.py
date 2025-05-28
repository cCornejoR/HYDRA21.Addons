# main_flet.py - HYDRA21 PDF Compressor - Professional Compact UI
import flet as ft
import threading
import os
import webbrowser
import subprocess
import json
import glob
import sys
from pathlib import Path
from typing import Optional
import datetime

# Importar módulos del proyecto
from themes import ThemeManager, ModernThemes, create_modern_button, create_modern_card
from settings import GS_PRESETS, DEFAULT_PRESET, CONFIG_FILE
from utils import FileUtils, GhostscriptUtils, ConfigManager
from compressor_logic import PDFCompressor, CompressionStats, BatchCompressionStats, BatchCompressionResult

class HYDRA21_PDFCompressor:
    """Aplicación profesional de compresión PDF con UI moderna y compacta"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.theme_manager = ThemeManager()
        self.config_manager = ConfigManager()
        
        # Configurar carpeta de salida por defecto en Documents/HYDRA21-PDFCompressor
        documents_dir = Path.home() / "Documents"
        self.output_dir = documents_dir / "HYDRA21-PDFCompressor"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar compresor con la carpeta configurada
        self.pdf_compressor = PDFCompressor(output_dir=self.output_dir)
        self.file_utils = FileUtils()
        self.gs_utils = GhostscriptUtils()
        
        # Estado de la aplicación
        self.selected_files: list[Path] = []
        self.is_processing = False
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
        """Configurar propiedades de la página"""
        self.page.title = "HYDRA21 PDF Compressor"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.width = 640
        self.page.window.height = 720
        self.page.window.resizable = True
        self.page.window.title_bar_hidden = False
        self.page.padding = 0

        # Deshabilitar redimensionar y maximizar
        self.page.window_resizable = False
        self.page.window_maximizable = False
        self.page.window_fullscreen = False

        # Capturar eventos de ventana para evitar "escapes"
        def on_window_event(e: ft.WindowEvent):
            if e.data == "maximize" or e.data == "resize":
                # rehacer el tamaño fijo
                self.page.window_width = 640
                self.page.window_height = 720
                self.page.update()
        
        self.page.on_window_event = on_window_event
        
        # Configurar icono de la aplicación
        self.configure_app_icon()
        
        self.apply_theme()
    
    def apply_theme(self):
        """Aplicar tema actual a la página"""
        theme = self.theme_manager.get_theme()
        self.page.theme_mode = ft.ThemeMode.DARK if self.theme_manager.is_dark else ft.ThemeMode.LIGHT
        self.page.bgcolor = theme['background']
        self.page.update()
    
    def configure_app_icon(self):
        """Configurar icono de la aplicación para desarrollo y builds"""
        try:
            # Intentar primero con la ruta relativa para desarrollo
            icon_path = Path("assets/icons/logo32x32.ico")
            
            if icon_path.exists():
                self.page.window.icon = str(icon_path.absolute())
                print(f"Icono configurado desde: {icon_path}")
                return
            
            # Si no existe, intentar desde el directorio de la aplicación
            app_dir = Path(__file__).parent
            icon_path = app_dir / "assets" / "icons" / "logo32x32.ico"
            
            if icon_path.exists():
                self.page.window.icon = str(icon_path.absolute())
                print(f"Icono configurado desde directorio de app: {icon_path}")
                return
            
            # Como fallback, usar el icono de 256x256 si está disponible
            icon_path_fallback = app_dir / "assets" / "icons" / "logo256x256.ico"
            if icon_path_fallback.exists():
                self.page.window.icon = str(icon_path_fallback.absolute())
                print(f"Icono configurado (fallback): {icon_path_fallback}")
                return
            
            print("Advertencia: No se pudo encontrar el icono de la aplicación")
            
        except Exception as e:
            print(f"Error configurando icono: {e}")
    
    def create_controls(self):
        """Crear todos los controles de la UI"""
        theme = self.theme_manager.get_theme()
        
        # Header con toggle de tema
        self.header = self.create_header()
        
        # Drop zone para archivos
        self.drop_zone = self.create_drop_zone()
        
        # Información del archivo seleccionado - dos columnas
        self.files_list_container = ft.Column(spacing=10)
        self.files_list_container_right = ft.Column(spacing=10)
        
        # Selector de calidad
        self.quality_selector = self.create_quality_selector()
        
        # Botón de compresión mejorado
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
            )
        )
        self.compress_button.disabled = True
        
        # Indicador de progreso
        self.progress_container = ft.Container(visible=False)
        
        # Resultados de compresión
        self.results_container = ft.Container(visible=False)
        
        # Estado de Ghostscript
        self.gs_status = ft.Container(visible=False)
    
    def create_header(self):
        """Crear header con logo y toggle de tema"""
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
                        ft.Text("HYDRA21 PDF Compressor", 
                               size=18, 
                               weight=ft.FontWeight.W_600, 
                               color=theme['on_surface'])
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True
                ),
                theme_toggle
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=16, vertical=15),
            bgcolor=theme['surface'],
            border=ft.border.only(bottom=ft.BorderSide(1, theme['border']))
        )
    
    def create_drop_zone(self):
        """Crear zona de arrastrar y soltar"""
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
                    blur_radius=5,
                    color=theme['shadow'],
                    offset=ft.Offset(0, 2)
                )
            ),
            ft.Text("Arrastra archivos PDF aquí", 
                   size=16, 
                   weight=ft.FontWeight.W_500, 
                   color=theme['on_surface']),
            ft.Text("o", size=14, color=theme['on_surface_variant']),
            create_modern_button(
                text="Seleccionar archivos",
                icon=ft.Icons.FOLDER_OPEN,
                on_click=self.pick_file,
                style="primary",
                theme=theme
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        
        return ft.Container(
            content=self.drop_zone_content,
            padding=ft.padding.symmetric(horizontal=16, vertical=20),
            border=ft.border.all(1, theme['border_variant']),
            border_radius=16,
            bgcolor=theme['surface_variant'],
            margin=ft.margin.all(4),
            on_click=self.pick_file,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )
    
    def create_quality_selector(self):
        """Crear selector de calidad de compresión"""
        theme = self.theme_manager.get_theme()
        
        self.quality_dropdown = ft.Dropdown(
            label="Calidad de compresión",
            value=DEFAULT_PRESET,
            options=[ft.dropdown.Option(key) for key in GS_PRESETS.keys()],
            filled=True,
            bgcolor=theme['input_bg'],
            border_color=theme['input_border'],
            border_radius=8,
            focused_border_color=theme['input_focused_border'],
            label_style=ft.TextStyle(color=theme['on_surface_variant'], size=14),
            text_style=ft.TextStyle(color=theme['on_surface'], weight=ft.FontWeight.W_500)
        )
        
        quality_info = [
            {"name": "Máxima Calidad", "desc": "Mejor para impresión profesional", "icon": ft.Icons.PRINT_ROUNDED},
            {"name": "Alta Calidad", "desc": "Equilibrio entre calidad y tamaño", "icon": ft.Icons.HIGH_QUALITY_ROUNDED},
            {"name": "Calidad Media", "desc": "Ideal para documentos digitales", "icon": ft.Icons.TABLET_ROUNDED},
            {"name": "Baja Calidad", "desc": "Máxima compresión", "icon": ft.Icons.COMPRESS_ROUNDED}
        ]
        
        quality_items = []
        for item in quality_info:
            quality_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(item["icon"], size=16, color=theme['on_surface']),
                            width=24,
                            height=24,
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text(item["name"], 
                                  size=13, 
                                  weight=ft.FontWeight.W_500, 
                                  color=theme['on_surface']),
                            ft.Text(item["desc"], 
                                  size=11, 
                                  color=theme['on_surface_variant'])
                        ], spacing=1, tight=True)
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START),
                    padding=ft.padding.only(bottom=7)
                )
            )
        
        return create_modern_card(
            content=[
                ft.Row([
                    ft.Icon(ft.Icons.TUNE_ROUNDED, size=18, color=theme['primary']),
                    ft.Text("Configuración", size=16, weight=ft.FontWeight.W_600, color=theme['on_surface'])
                ], spacing=8),
                ft.Container(height=8),
                self.quality_dropdown,
                ft.Container(height=10),
                ft.Column(quality_items, spacing=5, tight=True)
            ],
            theme=theme
        )
    
    def create_file_info_card(self, file_path: Path, on_remove=None):
        """Crear tarjeta con información del archivo y botón de eliminar"""
        theme = self.theme_manager.get_theme()
        
        file_size = self.file_utils.get_file_size(file_path)
        
        card_content = [
            ft.Row([
                ft.Icon(ft.Icons.DESCRIPTION, color=theme['primary'], size=20),
                ft.Column([
                    ft.Text(file_path.name,
                           size=14,
                           weight=ft.FontWeight.W_500,
                           color=theme['on_surface'],
                           overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"Tamaño: {file_size}",
                           size=12,
                           color=theme['on_surface_variant'])
                ], spacing=4, expand=True),
                ft.IconButton(
                    icon="close",
                    icon_color=theme['on_surface_variant'],
                    icon_size=20,
                    on_click=on_remove,
                    tooltip="Quitar archivo"
                )
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        ]
        
        return create_modern_card(
            content=card_content,
            theme=theme,
            padding=ft.padding.symmetric(horizontal=16, vertical=12)
        )
    
    def create_progress_indicator(self, is_batch=False, current_file="", progress=None):
        """Crear indicador de progreso"""
        theme = self.theme_manager.get_theme()
        
        if is_batch and progress:
            current, total = progress
            progress_text = f"Procesando archivo {current} de {total}"
            detail_text = f"Archivo actual: {current_file}" if current_file else "Preparando..."
        else:
            progress_text = "Comprimiendo PDF..."
            detail_text = "Este proceso puede tomar unos momentos."
        
        return create_modern_card(
            content=[
                ft.Row([
                    ft.ProgressRing(width=32, height=32, stroke_width=3, color=theme['primary']),
                    ft.Column([
                        ft.Text(progress_text, 
                               size=16,
                               weight=ft.FontWeight.W_500,
                               color=theme['on_surface']),
                        ft.Text(detail_text, 
                               size=13,
                               color=theme['on_surface_variant'])
                    ], spacing=4, expand=True)
                ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ],
            theme=theme,
            padding=ft.padding.all(20)
        )
    
    def create_results_card(self, stats: CompressionStats):
        """Crear tarjeta con resultados de compresión"""
        theme = self.theme_manager.get_theme()
        
        reduction_percent = ((stats.original_size - stats.compressed_size) / stats.original_size) * 100
        
        return create_modern_card(
            content=[
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=theme['success'], size=20),
                    ft.Text("Compresión completada", 
                           size=16, 
                           weight=ft.FontWeight.W_600, 
                           color=theme['on_surface'])
                ], spacing=8),
                ft.Column([
                    ft.Row([
                        ft.Text("Tamaño original:", size=12, color=theme['on_surface_variant']),
                        ft.Text(stats.original_size_str, size=12, weight=ft.FontWeight.W_500, color=theme['on_surface'])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.Text("Tamaño comprimido:", size=12, color=theme['on_surface_variant']),
                        ft.Text(stats.compressed_size_str, size=12, weight=ft.FontWeight.W_500, color=theme['on_surface'])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.Text("Reducción:", size=12, color=theme['on_surface_variant']),
                        ft.Text(f"{reduction_percent:.1f}%", size=12, weight=ft.FontWeight.W_500, color=theme['success'])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=4),
                ft.Row([
                    create_modern_button(
                        text="Abrir archivo",
                        icon=ft.Icons.OPEN_IN_NEW,
                        on_click=lambda _: self.open_output_file(stats.output_path),
                        style="primary",
                        theme=theme
                    ),
                    create_modern_button(
                        text="Abrir carpeta",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=lambda _: self.open_output_folder(stats.output_path),
                        style="secondary",
                        theme=theme
                    )
                ], spacing=12)
            ],
            theme=theme
        )
    
    def create_batch_results_card(self, batch_stats: BatchCompressionStats):
        """Crear tarjeta con resultados de compresión por lotes"""
        theme = self.theme_manager.get_theme()
        
        content = [
            ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=theme['success'], size=20),
                ft.Text("Compresión por lotes completada", 
                       size=16, 
                       weight=ft.FontWeight.W_600, 
                       color=theme['on_surface'])
            ], spacing=8),
            ft.Column([
                ft.Row([
                    ft.Text("Archivos procesados:", size=12, color=theme['on_surface_variant']),
                    ft.Text(f"{batch_stats.successful_files}/{batch_stats.total_files}", 
                           size=12, weight=ft.FontWeight.W_500, color=theme['on_surface'])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Tamaño original total:", size=12, color=theme['on_surface_variant']),
                    ft.Text(batch_stats.total_original_size_str, 
                           size=12, weight=ft.FontWeight.W_500, color=theme['on_surface'])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Tamaño comprimido total:", size=12, color=theme['on_surface_variant']),
                    ft.Text(batch_stats.total_compressed_size_str, 
                           size=12, weight=ft.FontWeight.W_500, color=theme['on_surface'])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Reducción total:", size=12, color=theme['on_surface_variant']),
                    ft.Text(f"{batch_stats.total_reduction_percent:.1f}%", 
                           size=12, weight=ft.FontWeight.W_500, color=theme['success'])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=4)
        ]
        
        # Añadir lista de errores si los hay
        if batch_stats.failed_files_list:
            content.append(ft.Container(height=8))
            content.append(ft.Text("Archivos con errores:", 
                                  size=12, 
                                  weight=ft.FontWeight.W_500,
                                  color=theme['error']))
            for error in batch_stats.failed_files_list[:3]:  # Mostrar máximo 3 errores
                content.append(ft.Text(f"• {error}", 
                                     size=11, 
                                     color=theme['on_surface_variant']))
            if len(batch_stats.failed_files_list) > 3:
                content.append(ft.Text(f"... y {len(batch_stats.failed_files_list) - 3} más", 
                                     size=11, 
                                     color=theme['on_surface_variant']))
        
        # Botones de acción
        content.append(ft.Container(height=8))
        content.append(ft.Row([
            create_modern_button(
                text="Abrir carpeta",
                icon=ft.Icons.FOLDER_OPEN,
                on_click=lambda _: self.open_output_folder(self.output_dir),
                style="primary",
                theme=theme
            ),
            create_modern_button(
                text="Nueva compresión",
                icon=ft.Icons.REFRESH,
                on_click=lambda _: self.reset_ui(),
                style="secondary",
                theme=theme
            )
        ], spacing=12))
        
        return create_modern_card(content=content, theme=theme)


    def build_ui(self):
        theme = self.theme_manager.get_theme()

        footer = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=14, color=theme['on_surface_variant']),
                            ft.Text(f"Un addon de HYDRA²¹ v1.0.0 © {datetime.date.today().year}", size=11, color=theme['on_surface_variant'])
                        ],
                        spacing=5
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor=theme['surface'],
            border=ft.border.only(top=ft.BorderSide(1, theme['border']))
        )

        # Altura corregida de contenedores principales
        fixed_height = 290

        main_row = ft.Row(
            [
                ft.Container(content=self.drop_zone, width=300, height=fixed_height, padding=ft.padding.only(right=4)),
                ft.Container(content=self.quality_selector, width=300, height=fixed_height, padding=ft.padding.only(left=4)),
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Contenedor de archivos (ya vienen llenos desde update_files_list)
        files_section = ft.Container(
            content=ft.Column([
                # Encabezado
                ft.Container(
                    content=ft.Row([
                        ft.Text(
                            f"{len(self.selected_files)} archivo{'s' if len(self.selected_files) != 1 else ''} seleccionado{'s' if len(self.selected_files) != 1 else ''}",
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=theme['on_surface']
                        ),
                        ft.TextButton(
                            "Limpiar todo",
                            on_click=lambda _: self.clear_files_list(),
                            style=ft.ButtonStyle(
                                color=theme['primary'],
                                text_style=ft.TextStyle(size=12)
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6)
                ),

                # Las columnas reales, sin alterar sus contenidos
                ft.Row([
                    ft.Container(content=self.files_list_container, expand=True, padding=ft.padding.symmetric(horizontal=6)),
                    ft.Container(content=self.files_list_container_right, expand=True, padding=ft.padding.symmetric(horizontal=6))
                ])
            ]),
            padding=ft.padding.only(top=10)
        )

        self.page.controls = [
            self.header,
            ft.Container(
                content=ft.Column([
                    main_row,
                    files_section,
                    ft.Container(
                        content=self.compress_button,
                        padding=ft.padding.symmetric(horizontal=16),
                        margin=ft.margin.only(top=15, bottom=10),
                        alignment=ft.alignment.center
                    ),
                    ft.Container(content=self.progress_container, alignment=ft.alignment.center, padding=ft.padding.symmetric(horizontal=16, vertical=10)),
                    self.results_container,
                    self.gs_status,
                    ft.Container(height=1, expand=True)
                ],
                    spacing=15,
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.ADAPTIVE
                ),
                expand=True,
                padding=ft.padding.symmetric(horizontal=8, vertical=10)
            ),
            footer
        ]

        self.page.update()


    def toggle_theme(self, e):
        """Alternar entre tema claro y oscuro"""
        self.theme_manager.toggle_theme()
        self.apply_theme()
        self.refresh_ui()
    
    def refresh_ui(self):
        """Refrescar la UI con el nuevo tema"""
        # Recrear controles con el nuevo tema
        self.create_controls()
        self.build_ui()
    
    def pick_file(self, e):
        """Abrir selector de archivos"""
        def file_picker_result(e: ft.FilePickerResultEvent):
            if e.files:
                for file in e.files:
                    file_path = Path(file.path)
                    if file_path.suffix.lower() == '.pdf':
                        self.add_file_to_list(file_path)
                    else:
                        self.show_error(f"Archivo no válido: {file_path.name}. Por favor selecciona solo archivos PDF.")
        
        file_picker = ft.FilePicker(on_result=file_picker_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        file_picker.pick_files(
            dialog_title="Seleccionar archivos PDF",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"],
            allow_multiple=True
        )
    
    def compress_pdfs(self, e):
        """Comprimir archivos PDF (individual o por lotes)"""
        if not self.selected_files or self.is_processing:
            return
        
        self.is_processing = True
        self.compress_button.disabled = True
        
        # Mostrar progreso
        is_batch = len(self.selected_files) > 1
        self.progress_container.content = self.create_progress_indicator(is_batch=is_batch)
        self.progress_container.visible = True
        self.results_container.visible = False
        self.page.update()
        
        # Ejecutar compresión en hilo separado
        if is_batch:
            threading.Thread(target=self._compress_batch_thread, daemon=True).start()
        else:
            threading.Thread(target=self._compress_single_thread, daemon=True).start()
    
    def _compress_single_thread(self):
        """Ejecutar compresión de un solo archivo en hilo separado"""
        try:
            quality_preset = self.quality_dropdown.value
            
            result = self.pdf_compressor.compress(
                input_path=self.selected_files[0],
                quality_preset=quality_preset
            )
            
            if result.success:
                self.compression_stats = result.stats
                self.page.run_thread(self.show_compression_results)
            else:
                self.page.run_thread(lambda: self.show_error(result.error_message))
                
        except Exception as e:
            self.page.run_thread(lambda: self.show_error(f"Error durante la compresión: {str(e)}"))
        finally:
            self.is_processing = False
            self.page.run_thread(self.hide_progress)
            self.page.run_thread(self.update_compress_button)
    
    def _compress_batch_thread(self):
        """Ejecutar compresión por lotes en hilo separado"""
        try:
            quality_preset = self.quality_dropdown.value
            
            def progress_callback(current, total, filename):
                """Callback para actualizar progreso"""
                self.page.run_thread(lambda: self.update_batch_progress(current, total, filename))
            
            result = self.pdf_compressor.compress_batch(
                input_paths=self.selected_files,
                quality_preset=quality_preset,
                progress_callback=progress_callback
            )
            
            if result.success:
                self.batch_stats = result.batch_stats
                self.page.run_thread(self.show_batch_results)
            else:
                self.page.run_thread(lambda: self.show_error(result.error_message))
                
        except Exception as e:
            self.page.run_thread(lambda: self.show_error(f"Error durante la compresión por lotes: {str(e)}"))
        finally:
            self.is_processing = False
            self.page.run_thread(self.hide_progress)
            self.page.run_thread(self.update_compress_button)
    
    def update_batch_progress(self, current, total, filename):
        """Actualizar progreso de compresión por lotes"""
        if self.progress_container.visible:
            self.progress_container.content = self.create_progress_indicator(
                is_batch=True, 
                current_file=filename, 
                progress=(current, total)
            )
            self.page.update()
    
    def show_compression_results(self):
        """Mostrar resultados de compresión"""
        if self.compression_stats:
            self.results_container.content = self.create_results_card(self.compression_stats)
            self.results_container.visible = True
            self.page.update()
    
    def show_batch_results(self):
        """Mostrar resultados de compresión por lotes"""
        if self.batch_stats:
            self.results_container.content = self.create_batch_results_card(self.batch_stats)
            self.results_container.visible = True
            self.page.update()
    
    def hide_progress(self):
        """Ocultar indicador de progreso"""
        self.progress_container.visible = False
        self.page.update()
    
    def show_error(self, message: str):
        """Mostrar mensaje de error"""
        theme = self.theme_manager.get_theme()
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Error", color=theme['error']),
            content=ft.Text(message, color=theme['on_surface']),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def verify_ghostscript(self):
        """Verificar disponibilidad de Ghostscript"""
        if not self.gs_utils.is_available():
            # Si no tenemos create_gs_status_error, usamos show_error temporalmente
            self.show_error("Ghostscript no está disponible. Por favor instálalo para usar la aplicación.")
    
    def open_output_file(self, file_path: Path):
        """Abrir archivo de salida"""
        try:
            os.startfile(str(file_path))
        except Exception as e:
            self.show_error(f"Error al abrir el archivo: {str(e)}")
    
    def open_output_folder(self, file_path):
        """Abrir carpeta de salida"""
        try:
            if isinstance(file_path, Path):
                folder_path = file_path if file_path.is_dir() else file_path.parent
            else:
                folder_path = Path(file_path)
            os.startfile(str(folder_path))
        except Exception as e:
            self.show_error(f"Error al abrir la carpeta: {str(e)}")
    
    def update_compress_button(self):
        """Actualizar el estado del botón de compresión según archivos seleccionados"""
        files_count = len(self.selected_files)
        self.compress_button.disabled = files_count == 0 or self.is_processing
        
        # Actualizar texto del botón
        if files_count == 0:
            button_text = "Comprimir PDFs"
        elif files_count == 1:
            button_text = "Comprimir PDF"
        else:
            button_text = f"Comprimir {files_count} PDFs"
        
        # Actualizar contenido del botón
        theme = self.theme_manager.get_theme()
        self.compress_button.content = ft.Row(
            [
                ft.Icon(ft.Icons.COMPRESS, color="white", size=18),
                ft.Text(button_text, size=15, weight=ft.FontWeight.W_600, color="white")
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8
        )
        
        # Actualizar colores según el tema
        self.compress_button.bgcolor = theme['button_primary_bg']
        
        self.page.update()
    
    def add_file_to_list(self, file_path: Path):
        """Añadir archivo a la lista de archivos seleccionados"""
        if file_path not in self.selected_files:
            self.selected_files.append(file_path)
            self.update_files_list()
            self.update_compress_button()
    
    def remove_file_from_list(self, file_path: Path):
        """Eliminar archivo de la lista"""
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            self.update_files_list()
            self.update_compress_button()
    
    def clear_files_list(self):
        """Limpiar la lista de archivos"""
        self.selected_files.clear()
        self.update_files_list()
        self.update_compress_button()
    
    def update_files_list(self):
        """Actualizar la UI de la lista de archivos en dos columnas"""
        # Limpiar ambas columnas
        self.files_list_container.controls.clear()
        self.files_list_container_right.controls.clear()
        
        if self.selected_files:
            theme = self.theme_manager.get_theme()
                       
            # Distribuir archivos en dos columnas de manera equilibrada
            for i, file_path in enumerate(self.selected_files):
                file_card = self.create_file_info_card(
                    file_path, 
                    on_remove=lambda _, fp=file_path: self.remove_file_from_list(fp)
                )
                file_container = ft.Container(
                    content=file_card,
                    margin=ft.margin.symmetric(horizontal=8, vertical=4)
                )
                
                # Alternar entre columnas: pares en izquierda, impares en derecha
                if i % 2 == 0:
                    self.files_list_container.controls.append(file_container)
                else:
                    self.files_list_container_right.controls.append(file_container)
        
        self.page.update()
    
    def reset_ui(self):
        """Resetear la interfaz para una nueva compresión"""
        # Limpiar archivos seleccionados
        self.clear_files_list()
        
        # Ocultar resultados y progreso
        self.results_container.visible = False
        self.progress_container.visible = False
        
        # Resetear estadísticas
        self.compression_stats = None
        self.batch_stats = None
        self.is_processing = False
        
        # Actualizar botón de compresión
        self.update_compress_button()
        
        # Actualizar página
        self.page.update()

def main(page: ft.Page):
    """Función principal de la aplicación"""
    app = HYDRA21_PDFCompressor(page)

if __name__ == "__main__":
    ft.app(target=main)

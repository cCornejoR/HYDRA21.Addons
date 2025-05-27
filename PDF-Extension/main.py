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
import datetime # Moved import datetime to the top

# Importar módulos del proyecto
from themes import ThemeManager, ModernThemes, create_modern_button, create_modern_card
from settings import GS_PRESETS, DEFAULT_PRESET, CONFIG_FILE
from utils import FileUtils, GhostscriptUtils, ConfigManager
from compressor_logic import PDFCompressor, CompressionStats

class HYDRA21_PDFCompressor:
    """Aplicación profesional de compresión PDF con UI moderna y compacta"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.theme_manager = ThemeManager()
        self.config_manager = ConfigManager()
        self.pdf_compressor = PDFCompressor()
        self.file_utils = FileUtils()
        self.gs_utils = GhostscriptUtils()
        
        # Estado de la aplicación
        self.selected_file: Optional[Path] = None
        self.is_processing = False
        self.compression_stats: Optional[CompressionStats] = None
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
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
        self.page.window_width = 200
        self.page.window_height = 850
        self.page.window_min_width = 200
        self.page.window_min_height = 850
        self.page.window_max_width = 200
        self.page.window_max_height = 680

        # Deshabilitar redimensionar y maximizar
        self.page.window_resizable = False
        self.page.window_maximizable = False
        self.page.window_fullscreen = False

        # Capturar eventos de ventana para evitar “escapes”
        def on_window_event(e: ft.WindowEvent):
            if e.data == "maximize" or e.data == "resize":
                # rehacer el tamaño fijo
                self.page.window_width = 450
                self.page.window_height = 680
                self.page.update()

        self.page.on_window_event = on_window_event
        
        # Configurar icono
        icon_path = Path("assets/icons/logo32x32.ico")
        if icon_path.exists():
            self.page.window_icon = str(icon_path.absolute())
        
        self.apply_theme()
    
    def apply_theme(self):
        """Aplicar tema actual a la página"""
        theme = self.theme_manager.get_theme()
        self.page.theme_mode = ft.ThemeMode.DARK if self.theme_manager.is_dark else ft.ThemeMode.LIGHT
        self.page.bgcolor = theme['background']
        self.page.update()
    
    def create_controls(self):
        """Crear todos los controles de la UI"""
        theme = self.theme_manager.get_theme()
        
        # Header con toggle de tema
        self.header = self.create_header()
        
        # Drop zone para archivos
        self.drop_zone = self.create_drop_zone()
        
        # Información del archivo seleccionado
        self.file_info = ft.Container(visible=False)
        
        # Selector de calidad
        self.quality_selector = self.create_quality_selector()
        
        # Botón de compresión mejorado
        self.compress_button = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.COMPRESS, color="white", size=18),
                    ft.Text("Comprimir PDF", size=15, weight=ft.FontWeight.W_600, color="white")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8
            ),
            width=410,
            height=50,
            bgcolor=theme['button_primary_bg'],
            border_radius=12,
            padding=ft.padding.all(12),
            alignment=ft.alignment.center,
            on_click=self.compress_pdf,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=5,
                color=theme['shadow'],
                offset=ft.Offset(0, 2)
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
            ft.Text("Arrastra un archivo PDF aquí", 
                   size=16, 
                   weight=ft.FontWeight.W_500, 
                   color=theme['on_surface']),
            ft.Text("o", size=14, color=theme['on_surface_variant']),
            create_modern_button(
                text="Seleccionar archivo",
                icon=ft.Icons.FOLDER_OPEN,
                on_click=self.pick_file,
                style="primary",
                theme=theme
            )
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15)
        
        return ft.Container(
            content=self.drop_zone_content,
            padding=ft.padding.symmetric(horizontal=30, vertical=35),
            border=ft.border.all(1, theme['border_variant']),
            border_radius=16,
            bgcolor=theme['surface_variant'],
            margin=ft.margin.only(left=16, right=16, top=20, bottom=10),
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
    
    def create_file_info_card(self, file_path: Path):
        """Crear tarjeta con información del archivo"""
        theme = self.theme_manager.get_theme()
        
        file_size = self.file_utils.get_file_size(file_path)
        
        return create_modern_card(
            content=[
                ft.Row([
                    ft.Icon(ft.Icons.DESCRIPTION, color=theme['primary'], size=20),
                    ft.Text("Archivo seleccionado", 
                           size=16, 
                           weight=ft.FontWeight.W_600, 
                           color=theme['on_surface'])
                ], spacing=8),
                ft.Text(file_path.name, 
                       size=14, 
                       weight=ft.FontWeight.W_500, 
                       color=theme['on_surface']),
                ft.Text(f"Tamaño: {file_size}", 
                       size=12, 
                       color=theme['on_surface_variant'])
            ],
            theme=theme
        )
    
    def create_progress_indicator(self):
        """Crear indicador de progreso"""
        theme = self.theme_manager.get_theme()
        
        return create_modern_card(
            content=[
                ft.Row([
                    ft.ProgressRing(width=32, height=32, stroke_width=3, color=theme['primary']), # Aumentar tamaño y grosor
                    ft.Text("Comprimiendo PDF...", 
                           size=16, # Aumentar tamaño de fuente
                           weight=ft.FontWeight.W_500, # Ajustar peso de fuente
                           color=theme['on_surface'])
                ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER), # Aumentar espaciado y centrar verticalmente
                ft.Container(height=4), # Pequeño espacio
                ft.Text("Este proceso puede tomar unos momentos.", 
                       size=13, # Aumentar tamaño de fuente 
                       color=theme['on_surface_variant'])
            ],
            theme=theme,
            padding=ft.padding.all(20) # Aumentar padding general de la tarjeta
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
    
    def create_gs_status_error(self):
        """Crear tarjeta de error de Ghostscript"""
        theme = self.theme_manager.get_theme()
        
        return create_modern_card(
            content=[
                ft.Row([
                    ft.Icon(ft.Icons.ERROR, color=theme['error'], size=20),
                    ft.Text("Ghostscript no encontrado", 
                           size=16, 
                           weight=ft.FontWeight.W_600, 
                           color=theme['on_surface'])
                ], spacing=8),
                ft.Text("Se requiere Ghostscript para comprimir archivos PDF. "
                       "Por favor, instala Ghostscript e intenta nuevamente.", 
                       size=12, 
                       color=theme['on_surface_variant']),
                create_modern_button(
                    text="Descargar Ghostscript",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda _: self.open_ghostscript_download(),
                    style="primary",
                    theme=theme
                )
            ],
            theme=theme
        )
    
    def build_ui(self):
        """Construir la interfaz de usuario"""
        theme = self.theme_manager.get_theme()
        
        # Footer con información
        footer = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=14, color=theme['on_surface_variant']),
                            ft.Text(f"Un addon de HYDRA²¹ v1.0.0 © {datetime.date.today().year}", size=11, color=theme['on_surface_variant']) # Año dinámico
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
        
        self.page.controls = [
            self.header,
            ft.Container(
                content=ft.Column(
                    [
                        self.drop_zone,
                        self.file_info,
                        self.quality_selector,
                        ft.Container(
                            content=self.compress_button,
                            padding=ft.padding.symmetric(horizontal=16),
                            margin=ft.margin.only(top=10, bottom=10), # Ajustar margen
                            alignment=ft.alignment.center
                        ),
                        # Asegurar que el contenedor de progreso tenga espacio y sea visible
                        ft.Container( 
                            content=self.progress_container,
                            alignment=ft.alignment.center,
                            padding=ft.padding.symmetric(horizontal=16, vertical=10) # Añadir padding
                        ),
                        self.results_container,
                        self.gs_status,
                        ft.Container(height=1, expand=True)  # Spacer para empujar el footer al fondo
                    ],
                    spacing=15,
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, # Centrar elementos horizontalmente
                    scroll=ft.ScrollMode.ADAPTIVE  # <<< Habilitar autoscroll
                ),
                expand=True,
                padding=ft.padding.only(bottom=10)
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
        
        # Restaurar estado si hay archivo seleccionado
        if self.selected_file:
            self.show_file_info(self.selected_file)
    
    def pick_file(self, e):
        """Abrir selector de archivos"""
        def file_picker_result(e: ft.FilePickerResultEvent):
            if e.files:
                file_path = Path(e.files[0].path)
                if file_path.suffix.lower() == '.pdf':
                    self.select_file(file_path)
                else:
                    self.show_error("Por favor selecciona un archivo PDF válido")
        
        file_picker = ft.FilePicker(on_result=file_picker_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        file_picker.pick_files(
            dialog_title="Seleccionar archivo PDF",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"]
        )
    
    def select_file(self, file_path: Path):
        """Seleccionar archivo PDF"""
        self.selected_file = file_path
        self.show_file_info(file_path)
        self.compress_button.disabled = False
        self.page.update()
    
    def show_file_info(self, file_path: Path):
        """Mostrar información del archivo seleccionado"""
        self.file_info.content = self.create_file_info_card(file_path)
        self.file_info.visible = True
        
        # Ocultar drop zone y mostrar solo un botón pequeño
        theme = self.theme_manager.get_theme()
        self.drop_zone.content = ft.Container(
            content=create_modern_button(
                text="Cambiar archivo",
                icon=ft.Icons.SWAP_HORIZ,
                on_click=self.pick_file,
                style="secondary",
                theme=theme
            ),
            padding=ft.padding.all(12)
        )
        
        self.page.update()
    
    def compress_pdf(self, e):
        """Comprimir archivo PDF"""
        if not self.selected_file or self.is_processing:
            return
        
        self.is_processing = True
        self.compress_button.disabled = True
        
        # Mostrar progreso
        self.progress_container.content = self.create_progress_indicator()
        self.progress_container.visible = True
        self.results_container.visible = False
        self.page.update()
        
        # Ejecutar compresión en hilo separado
        threading.Thread(target=self._compress_pdf_thread, daemon=True).start()
    
    def _compress_pdf_thread(self):
        """Ejecutar compresión en hilo separado"""
        try:
            quality_preset = self.quality_dropdown.value
            
            result = self.pdf_compressor.compress(
                input_path=self.selected_file,
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
            self.compress_button.disabled = False
            self.page.run_thread(self.hide_progress)
    
    def show_compression_results(self):
        """Mostrar resultados de compresión"""
        if self.compression_stats:
            self.results_container.content = self.create_results_card(self.compression_stats)
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
            self.gs_status.content = self.create_gs_status_error()
            self.gs_status.visible = True
            self.compress_button.disabled = True
            self.page.update()
    
    def open_output_file(self, file_path: Path):
        """Abrir archivo de salida"""
        try:
            os.startfile(str(file_path))
        except Exception as e:
            self.show_error(f"Error al abrir el archivo: {str(e)}")
    
    def open_output_folder(self, file_path: Path):
        """Abrir carpeta de salida"""
        try:
            os.startfile(str(file_path.parent))
        except Exception as e:
            self.show_error(f"Error al abrir la carpeta: {str(e)}")
    
    def open_ghostscript_download(self):
        """Abrir página de descarga de Ghostscript"""
        webbrowser.open("https://www.ghostscript.com/download/gsdnld.html")

def main(page: ft.Page):
    """Función principal de la aplicación"""
    app = HYDRA21_PDFCompressor(page)

if __name__ == "__main__":
    ft.app(target=main)
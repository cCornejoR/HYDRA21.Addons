"""
HYDRA21 Orthophoto Processor Pro - Processing Options Component
Professional processing options and configuration interface
"""

import flet as ft
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path

from config.settings import SUPPORTED_OUTPUT_FORMATS, COMPRESSION_PRESETS, DirectoryConfig
from config.orthophoto_config import EXPORT_PROFILES, RESAMPLING_METHODS
from config.user_settings import UserSettings

class ProcessingOptions(ft.Column):
    """Professional processing options configuration"""

    def __init__(
        self,
        theme: Dict[str, str],
        on_process_start: Optional[Callable] = None,
        page: Optional[ft.Page] = None
    ):
        self.theme = theme
        self.on_process_start = on_process_start
        self.page = page

        # Initialize user settings
        self.user_settings = UserSettings(DirectoryConfig.get_config_dir())

        # State - Load from saved settings
        self.selected_files: List[Path] = []
        saved_options = self.user_settings.get_processing_options()
        self.current_options = {
            "output_format": "GeoTIFF",
            "compression": saved_options.get("compression", "lossless"),
            "quality": saved_options.get("quality", None),
            "export_profile": saved_options.get("export_profile", "gis_analysis"),
            "preserve_crs": saved_options.get("preserve_crs", True),
            "create_overviews": saved_options.get("create_overviews", True),
            "resampling_method": saved_options.get("resampling_method", "bilinear"),
            "output_directory": saved_options.get("output_directory", "./output")
        }
        
        # Components
        self.format_dropdown = None
        self.compression_dropdown = None
        self.quality_slider = None
        self.profile_dropdown = None
        self.preserve_crs_checkbox = None
        self.overviews_checkbox = None
        self.resampling_dropdown = None
        self.output_dir_field = None
        
        self._setup_ui()
        
        super().__init__(
            controls=self._build_layout(),
            spacing=24,
            expand=True
        )
    
    def _setup_ui(self):
        """Setup UI components"""
        # Output format dropdown
        self.format_dropdown = ft.Dropdown(
            label="Formato de salida",
            options=[
                ft.dropdown.Option(key, value["description"])
                for key, value in SUPPORTED_OUTPUT_FORMATS.items()
            ],
            value="GeoTIFF",
            on_change=self._on_format_change,
            width=300
        )
        
        # Compression dropdown
        self.compression_dropdown = ft.Dropdown(
            label="Compresión",
            options=[
                ft.dropdown.Option(key, value["name"])
                for key, value in COMPRESSION_PRESETS.items()
            ],
            value="lossless",
            on_change=self._on_compression_change,
            width=300
        )
        
        # Quality slider
        self.quality_slider = ft.Slider(
            min=1,
            max=100,
            value=85,
            divisions=99,
            label="Calidad: {value}%",
            on_change=self._on_quality_change,
            visible=False,
            width=300
        )
        
        # Export profile dropdown
        self.profile_dropdown = ft.Dropdown(
            label="Perfil de exportación",
            options=[
                ft.dropdown.Option(key, value["name"])
                for key, value in EXPORT_PROFILES.items()
            ],
            value="gis_analysis",
            on_change=self._on_profile_change,
            width=300
        )
        
        # Resampling method dropdown
        self.resampling_dropdown = ft.Dropdown(
            label="Método de remuestreo",
            options=[
                ft.dropdown.Option(key, value["name"])
                for key, value in RESAMPLING_METHODS.items()
            ],
            value="bilinear",
            on_change=self._on_resampling_change,
            width=300
        )
        
        # Checkboxes
        self.preserve_crs_checkbox = ft.Checkbox(
            label="Preservar sistema de coordenadas original",
            value=True,
            on_change=self._on_preserve_crs_change
        )
        
        self.overviews_checkbox = ft.Checkbox(
            label="Crear overviews (pirámides)",
            value=True,
            on_change=self._on_overviews_change
        )
        
        # Output directory field - Load saved directory
        saved_output_dir = self.user_settings.get_output_directory()
        self.output_dir_field = ft.TextField(
            label="Directorio de salida",
            value=saved_output_dir,
            expand=True,
            read_only=True
        )
        # Update current options with saved directory
        self.current_options["output_directory"] = saved_output_dir

        # Directory picker
        self.directory_picker = ft.FilePicker(on_result=self._on_directory_selected)

        # Add to page overlay if page is available
        if self.page:
            self.page.overlay.append(self.directory_picker)
    
    def _build_layout(self) -> List[ft.Control]:
        """Build the options layout"""
        return [
            # Header
            ft.Text(
                "⚙️ Opciones de Procesamiento",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=self.theme['on_surface']
            ),
            
            # Format and compression section
            self._create_section(
                "Formato y Compresión",
                [
                    ft.Row([
                        self.format_dropdown,
                        self.compression_dropdown
                    ], spacing=16),
                    self.quality_slider,
                    self._create_compression_info()
                ]
            ),
            
            # Processing options section
            self._create_section(
                "Opciones de Procesamiento",
                [
                    ft.Row([
                        self.profile_dropdown,
                        self.resampling_dropdown
                    ], spacing=16),
                    ft.Column([
                        self.preserve_crs_checkbox,
                        self.overviews_checkbox
                    ], spacing=8)
                ]
            ),
            
            # Output section
            self._create_section(
                "Salida",
                [
                    ft.Row([
                        self.output_dir_field,
                        ft.ElevatedButton(
                            "Cambiar",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=self._select_output_dir
                        )
                    ], spacing=8)
                ]
            ),
            
            # Action buttons
            ft.Row([
                ft.ElevatedButton(
                    text="Procesar Archivos",
                    icon=ft.Icons.PLAY_ARROW,
                    bgcolor=self.theme['primary'],
                    color=self.theme['on_primary'],
                    width=200,
                    height=45,
                    on_click=self._start_processing,
                    disabled=len(self.selected_files) == 0
                ),
                ft.ElevatedButton(
                    text="Restablecer",
                    icon=ft.Icons.REFRESH,
                    bgcolor=self.theme['surface_variant'],
                    color=self.theme['on_surface'],
                    width=120,
                    height=45,
                    on_click=self._reset_options
                )
            ], spacing=16)
        ]
    
    def _create_section(self, title: str, content: List[ft.Control]) -> ft.Container:
        """Create a section container"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    title,
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=self.theme['on_surface']
                ),
                ft.Column(content, spacing=12)
            ], spacing=16),
            padding=ft.padding.all(20),
            bgcolor=self.theme['surface_variant'],
            border_radius=12,
            border=ft.border.all(1, self.theme['border'])
        )
    
    def _create_compression_info(self) -> ft.Container:
        """Create compression information display"""
        preset_key = self.compression_dropdown.value
        if preset_key in COMPRESSION_PRESETS:
            preset = COMPRESSION_PRESETS[preset_key]
            info_text = preset["description"]
            
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=self.theme['info'], size=16),
                    ft.Text(
                        info_text,
                        size=12,
                        color=self.theme['on_surface_variant']
                    )
                ], spacing=8),
                padding=ft.padding.all(12),
                bgcolor=self.theme['info_container'],
                border_radius=6,
                border=ft.border.all(1, self.theme['info'])
            )
        
        return ft.Container()
    
    def _on_format_change(self, e):
        """Handle format change"""
        self.current_options["output_format"] = e.control.value
        self._update_compression_options()
    
    def _on_compression_change(self, e):
        """Handle compression change"""
        preset_key = e.control.value
        self.current_options["compression"] = preset_key
        
        # Update quality slider visibility
        if preset_key in ["medium", "low"]:
            self.quality_slider.visible = True
            preset = COMPRESSION_PRESETS[preset_key]
            self.quality_slider.value = preset.get("quality", 85)
            self.current_options["quality"] = preset.get("quality", 85)
        else:
            self.quality_slider.visible = False
            self.current_options["quality"] = None
        
        self._update_layout()
    
    def _on_quality_change(self, e):
        """Handle quality change"""
        self.current_options["quality"] = int(e.control.value)
    
    def _on_profile_change(self, e):
        """Handle profile change"""
        self.current_options["export_profile"] = e.control.value
        
        # Update other options based on profile
        if e.control.value in EXPORT_PROFILES:
            profile = EXPORT_PROFILES[e.control.value]
            
            # Update format if specified in profile
            if "format" in profile:
                format_map = {
                    "GTiff": "GeoTIFF",
                    "JPEG": "JPEG",
                    "PNG": "PNG"
                }
                if profile["format"] in format_map:
                    self.format_dropdown.value = format_map[profile["format"]]
                    self.current_options["output_format"] = format_map[profile["format"]]
            
            # Update compression
            if "compression" in profile:
                compression_map = {
                    "LZW": "lossless",
                    "DEFLATE": "lossless",
                    "JPEG": "medium"
                }
                if profile["compression"] in compression_map:
                    self.compression_dropdown.value = compression_map[profile["compression"]]
                    self.current_options["compression"] = compression_map[profile["compression"]]
        
        self._update_layout()
    
    def _on_resampling_change(self, e):
        """Handle resampling method change"""
        self.current_options["resampling_method"] = e.control.value
    
    def _on_preserve_crs_change(self, e):
        """Handle preserve CRS change"""
        self.current_options["preserve_crs"] = e.control.value
    
    def _on_overviews_change(self, e):
        """Handle overviews change"""
        self.current_options["create_overviews"] = e.control.value
    
    def _update_compression_options(self):
        """Update compression options based on format"""
        format_name = self.current_options["output_format"]
        
        # Update compression dropdown options based on format
        if format_name == "JPEG":
            self.compression_dropdown.options = [
                ft.dropdown.Option("medium", "JPEG Estándar"),
                ft.dropdown.Option("low", "JPEG Comprimido")
            ]
            self.compression_dropdown.value = "medium"
        elif format_name == "PNG":
            self.compression_dropdown.options = [
                ft.dropdown.Option("lossless", "PNG Sin pérdida")
            ]
            self.compression_dropdown.value = "lossless"
        else:  # GeoTIFF
            self.compression_dropdown.options = [
                ft.dropdown.Option(key, value["name"])
                for key, value in COMPRESSION_PRESETS.items()
            ]
            self.compression_dropdown.value = "lossless"
        
        self.current_options["compression"] = self.compression_dropdown.value
        self._update_layout()
    
    def _select_output_dir(self, e):
        """Select output directory"""
        if hasattr(self, 'directory_picker'):
            self.directory_picker.get_directory_path(dialog_title="Seleccionar directorio de salida")

    def _on_directory_selected(self, e: ft.FilePickerResultEvent):
        """Handle directory selection"""
        if e.path:
            self.output_dir_field.value = e.path
            self.current_options["output_directory"] = e.path

            # Save to user settings
            self.user_settings.set_output_directory(e.path)
            print(f"✅ Carpeta de salida guardada: {e.path}")

            if hasattr(self, 'page') and self.page:
                self.page.update()
    
    def _start_processing(self, e):
        """Start processing with current options"""
        if self.on_process_start:
            self.on_process_start(self.current_options.copy())
    
    def _reset_options(self, e):
        """Reset options to defaults"""
        self.current_options = {
            "output_format": "GeoTIFF",
            "compression": "LZW",
            "quality": None,
            "export_profile": "gis_analysis",
            "preserve_crs": True,
            "create_overviews": True,
            "resampling_method": "bilinear"
        }
        
        # Update UI components
        self.format_dropdown.value = "GeoTIFF"
        self.compression_dropdown.value = "lossless"
        self.quality_slider.value = 85
        self.quality_slider.visible = False
        self.profile_dropdown.value = "gis_analysis"
        self.resampling_dropdown.value = "bilinear"
        self.preserve_crs_checkbox.value = True
        self.overviews_checkbox.value = True
        
        self._update_layout()
    
    def _update_layout(self):
        """Update the layout"""
        try:
            # Rebuild compression info - find the format section and update it
            for i, control in enumerate(self.controls):
                if isinstance(control, ft.Container):
                    # Check if this is the format and compression section
                    if hasattr(control, 'content') and isinstance(control.content, ft.Column):
                        column_controls = control.content.controls
                        if len(column_controls) > 1:
                            section_content = column_controls[1]
                            if isinstance(section_content, ft.Column) and len(section_content.controls) >= 3:
                                # Update the compression info (third item)
                                section_content.controls[2] = self._create_compression_info()
                                break
        except (IndexError, AttributeError) as e:
            print(f"Layout update error: {e}")

        # Update page if available
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def set_files(self, files: List[Path]):
        """Set selected files"""
        self.selected_files = files
        
        # Update process button state
        for control in self.controls:
            if isinstance(control, ft.Row):
                for button in control.controls:
                    if isinstance(button, ft.ElevatedButton) and "Procesar" in button.text:
                        button.disabled = len(files) == 0
    
    def get_options(self) -> Dict[str, Any]:
        """Get current processing options"""
        return self.current_options.copy()
    
    def set_theme(self, new_theme: Dict[str, str]):
        """Update theme"""
        self.theme = new_theme
        # Theme updates would be applied to all components here

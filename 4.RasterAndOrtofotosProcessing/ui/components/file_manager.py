"""
HYDRA21 Orthophoto Processor Pro - File Manager Component
Professional file selection and management interface
"""

import flet as ft
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import os

from config.settings import SUPPORTED_INPUT_FORMATS
from core.orthophoto_engine import OrthophotoProcessor

class FileManager(ft.Column):
    """Professional file manager with drag-and-drop and batch selection"""
    
    def __init__(
        self,
        page: ft.Page,
        theme: Dict[str, str],
        on_files_selected: Optional[Callable] = None
    ):
        self.page = page
        self.theme = theme
        self.on_files_selected = on_files_selected
        
        # State
        self.selected_files: List[Path] = []
        self.file_info: List[Dict[str, Any]] = []
        
        # Components
        self.file_picker = None
        self.files_list = None
        self.selection_info = None
        self.processor = OrthophotoProcessor()
        
        self._setup_ui()
        
        super().__init__(
            controls=self._build_layout(),
            spacing=16,
            expand=True
        )
    
    def _setup_ui(self):
        """Setup UI components"""
        # File picker
        self.file_picker = ft.FilePicker(on_result=self._on_files_picked)
        self.page.overlay.append(self.file_picker)
        
        # Selection info
        self.selection_info = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, color=self.theme['info'], size=20),
                ft.Text(
                    "Selecciona archivos de ortofoto para procesar",
                    size=14,
                    color=self.theme['on_surface_variant']
                )
            ], spacing=8),
            padding=ft.padding.all(16),
            bgcolor=self.theme['info_container'],
            border_radius=8,
            border=ft.border.all(1, self.theme['info'])
        )
        
        # Files list
        self.files_list = ft.Column(
            controls=[],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def _build_layout(self) -> List[ft.Control]:
        """Build the file manager layout"""
        return [
            # Header
            ft.Row([
                ft.Text(
                    "📁 Gestión de Archivos",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=self.theme['on_surface']
                ),
                ft.Row([
                    self._create_select_button(),
                    self._create_clear_button()
                ], spacing=8)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            # Selection info
            self.selection_info,
            
            # Files list container
            ft.Container(
                content=self.files_list,
                bgcolor=self.theme['surface'],
                border_radius=12,
                border=ft.border.all(1, self.theme['border']),
                padding=ft.padding.all(16),
                height=300,
                expand=True
            )
        ]
    
    def _create_select_button(self) -> ft.ElevatedButton:
        """Create file selection button"""
        return ft.ElevatedButton(
            text="Seleccionar Archivos",
            icon=ft.Icons.UPLOAD_FILE,
            bgcolor=self.theme['primary'],
            color=self.theme['on_primary'],
            on_click=self._select_files
        )
    
    def _create_clear_button(self) -> ft.ElevatedButton:
        """Create clear selection button"""
        return ft.ElevatedButton(
            text="Limpiar",
            icon=ft.Icons.CLEAR,
            bgcolor=self.theme['surface_variant'],
            color=self.theme['on_surface'],
            on_click=self._clear_selection
        )
    
    def _select_files(self, e):
        """Open file picker"""
        # Get file extensions for picker
        extensions = [ext.lstrip('.') for ext in SUPPORTED_INPUT_FORMATS]
        
        self.file_picker.pick_files(
            dialog_title="Seleccionar archivos de ortofoto",
            allow_multiple=True,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=extensions
        )
    
    def _clear_selection(self, e):
        """Clear file selection"""
        self.selected_files.clear()
        self.file_info.clear()
        self._update_files_display()
        self._update_selection_info()
        
        if self.on_files_selected:
            self.on_files_selected(self.selected_files)
    
    def _on_files_picked(self, e: ft.FilePickerResultEvent):
        """Handle file picker result"""
        if e.files:
            # Convert to Path objects and filter valid files
            new_files = []
            for file in e.files:
                file_path = Path(file.path)
                if file_path.suffix.lower() in SUPPORTED_INPUT_FORMATS:
                    new_files.append(file_path)
            
            # Add to selection (avoid duplicates)
            for file_path in new_files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
            
            # Get file information
            self._load_file_info()
            
            # Update display
            self._update_files_display()
            self._update_selection_info()
            
            # Notify callback
            if self.on_files_selected:
                self.on_files_selected(self.selected_files)
    
    def _load_file_info(self):
        """Load information for selected files"""
        self.file_info.clear()
        
        for file_path in self.selected_files:
            try:
                # Get basic file info
                stat = file_path.stat()
                info = {
                    "path": file_path,
                    "name": file_path.name,
                    "size": stat.st_size,
                    "size_mb": stat.st_size / (1024 * 1024),
                    "extension": file_path.suffix.upper(),
                    "valid": True,
                    "error": None
                }
                
                # Try to get geospatial info
                geo_info = self.processor.get_file_info(file_path)
                if "error" not in geo_info:
                    info.update(geo_info)
                else:
                    info["geo_error"] = geo_info["error"]
                
                self.file_info.append(info)
                
            except Exception as e:
                self.file_info.append({
                    "path": file_path,
                    "name": file_path.name,
                    "valid": False,
                    "error": str(e)
                })
    
    def _update_files_display(self):
        """Update the files list display"""
        self.files_list.controls.clear()
        
        if not self.selected_files:
            # Show empty state
            self.files_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            ft.Icons.FOLDER_OPEN,
                            size=48,
                            color=self.theme['on_surface_variant']
                        ),
                        ft.Text(
                            "No hay archivos seleccionados",
                            size=16,
                            color=self.theme['on_surface_variant'],
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            "Haz clic en 'Seleccionar Archivos' para comenzar",
                            size=12,
                            color=self.theme['on_surface_variant'],
                            text_align=ft.TextAlign.CENTER
                        )
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8),
                    alignment=ft.alignment.center,
                    expand=True
                )
            )
        else:
            # Show file list
            for i, info in enumerate(self.file_info):
                self.files_list.controls.append(
                    self._create_file_item(info, i)
                )
    
    def _create_file_item(self, info: Dict[str, Any], index: int) -> ft.Container:
        """Create a file item display"""
        # Determine icon and color based on file type and validity
        if not info.get("valid", True):
            icon = ft.Icons.ERROR
            icon_color = self.theme['error']
        elif info["extension"] in [".TIF", ".TIFF"]:
            icon = ft.Icons.MAP
            icon_color = self.theme['primary']
        elif info["extension"] == ".ECW":
            icon = ft.Icons.COMPRESS
            icon_color = self.theme['secondary']
        else:
            icon = ft.Icons.INSERT_DRIVE_FILE
            icon_color = self.theme['on_surface_variant']
        
        # Create file details
        details = []
        details.append(f"{info['extension']} • {info['size_mb']:.1f} MB")
        
        if "width" in info and "height" in info:
            details.append(f"{info['width']} × {info['height']} px")
        
        if "crs" in info:
            details.append(f"CRS: {info['crs']}")
        
        if info.get("error"):
            details.append(f"Error: {info['error']}")
        
        # Create remove button
        remove_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_color=self.theme['error'],
            tooltip="Remover archivo",
            on_click=lambda e, idx=index: self._remove_file(idx)
        )
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=icon_color, size=24),
                ft.Column([
                    ft.Text(
                        info["name"],
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.theme['on_surface']
                    ),
                    ft.Text(
                        " • ".join(details),
                        size=12,
                        color=self.theme['on_surface_variant']
                    )
                ], spacing=2, expand=True),
                remove_button
            ], spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(12),
            bgcolor=self.theme['surface_variant'],
            border_radius=8,
            border=ft.border.all(1, self.theme['border'])
        )
    
    def _remove_file(self, index: int):
        """Remove file from selection"""
        if 0 <= index < len(self.selected_files):
            self.selected_files.pop(index)
            self.file_info.pop(index)
            
            self._update_files_display()
            self._update_selection_info()
            
            if self.on_files_selected:
                self.on_files_selected(self.selected_files)
    
    def _update_selection_info(self):
        """Update selection information display"""
        if not self.selected_files:
            self.selection_info.content = ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, color=self.theme['info'], size=20),
                ft.Text(
                    "Selecciona archivos de ortofoto para procesar",
                    size=14,
                    color=self.theme['on_surface_variant']
                )
            ], spacing=8)
            self.selection_info.bgcolor = self.theme['info_container']
            self.selection_info.border = ft.border.all(1, self.theme['info'])
        else:
            total_size = sum(info.get("size", 0) for info in self.file_info)
            total_size_mb = total_size / (1024 * 1024)
            
            self.selection_info.content = ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=self.theme['success'], size=20),
                ft.Text(
                    f"{len(self.selected_files)} archivo(s) seleccionado(s) • {total_size_mb:.1f} MB total",
                    size=14,
                    color=self.theme['on_surface']
                )
            ], spacing=8)
            self.selection_info.bgcolor = self.theme['success_container']
            self.selection_info.border = ft.border.all(1, self.theme['success'])
    
    def get_selected_files(self) -> List[Path]:
        """Get list of selected files"""
        return self.selected_files.copy()
    
    def get_file_info(self) -> List[Dict[str, Any]]:
        """Get file information list"""
        return self.file_info.copy()
    
    def set_theme(self, new_theme: Dict[str, str]):
        """Update theme"""
        self.theme = new_theme
        self._update_files_display()
        self._update_selection_info()

"""
File selection components for HYDRA21 PDF Compressor
Provides file picker dialogs and file management UI
"""

import flet as ft
from pathlib import Path
from typing import List, Optional, Callable, Dict
from core.file_manager import FileManager, FileInfo
from ui.themes.modern_components import create_modern_button, create_modern_card, create_file_info_card

class FileSelector(ft.Column):
    """File selection component with validation and preview"""
        
    def __init__(
        self,
        theme: Dict[str, str],
        file_manager: FileManager,
        on_files_selected: Optional[Callable[[List[Path]], None]] = None,
        allow_multiple: bool = True,
        max_files: int = 100
    ):
        super().__init__()
        self.theme = theme
        self.file_manager = file_manager
        self.on_files_selected = on_files_selected
        self.allow_multiple = allow_multiple
        self.max_files = max_files

        self.selected_files: List[FileInfo] = []

        # Create file picker
        self.file_picker = ft.FilePicker(
            on_result=self._on_file_picker_result
        )

        # Files container
        self.files_container = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            height=300
        )

        # Selection info
        self.selection_info = ft.Text(
            "No hay archivos seleccionados",
            size=14,
            color=self.theme['on_surface_variant']
        )

        # Build the component
        self.spacing = 16
        self.controls = [
            self.file_picker,
            # File picker button
            ft.Row([
                create_modern_button(
                    text="Seleccionar Archivos PDF" if self.allow_multiple else "Seleccionar Archivo PDF",
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=self._open_file_picker,
                    style="primary",
                    theme=self.theme
                ),
                create_modern_button(
                    text="Limpiar Selección",
                    icon=ft.Icons.CLEAR,
                    on_click=self._clear_selection,
                    style="secondary",
                    theme=self.theme
                )
            ], spacing=12),

            # Selection info
            self.selection_info,

            # Files list
            create_modern_card(
                content=[
                    ft.Text(
                        "Archivos Seleccionados",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=self.theme['on_surface']
                    ),
                    self.files_container
                ],
                theme=self.theme,
                padding=ft.padding.all(16)
            )
        ]
    
    def _open_file_picker(self, _):
        """Open file picker dialog"""
        self.file_picker.pick_files(
            dialog_title="Seleccionar archivos PDF",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"],
            allow_multiple=self.allow_multiple
        )
    
    def _on_file_picker_result(self, e: ft.FilePickerResultEvent):
        """Handle file picker result"""
        if e.files:
            # Convert to Path objects
            file_paths = [Path(f.path) for f in e.files]
            
            # Limit number of files
            if len(file_paths) > self.max_files:
                self._show_error(f"Demasiados archivos seleccionados. Máximo: {self.max_files}")
                return
            
            # Validate files
            valid_files, invalid_files = self.file_manager.validate_files(file_paths)
            
            # Update selected files
            if self.allow_multiple:
                # Add to existing selection (avoid duplicates)
                existing_paths = {f.path for f in self.selected_files}
                new_files = [f for f in valid_files if f.path not in existing_paths]
                self.selected_files.extend(new_files)
            else:
                # Replace selection
                self.selected_files = valid_files[:1] if valid_files else []
            
            # Show warnings for invalid files
            if invalid_files:
                invalid_names = [f.name for f in invalid_files]
                self._show_warning(f"Archivos inválidos ignorados: {', '.join(invalid_names)}")
            
            # Update UI
            self._update_files_display()
            self._update_selection_info()
            
            # Notify parent
            if self.on_files_selected and self.selected_files:
                valid_paths = [f.path for f in self.selected_files]
                self.on_files_selected(valid_paths)
    
    def _clear_selection(self, _):
        """Clear file selection"""
        self.selected_files.clear()
        self._update_files_display()
        self._update_selection_info()
        
        if self.on_files_selected:
            self.on_files_selected([])
    
    def _remove_file(self, file_info: FileInfo):
        """Remove specific file from selection"""
        if file_info in self.selected_files:
            self.selected_files.remove(file_info)
            self._update_files_display()
            self._update_selection_info()
            
            if self.on_files_selected:
                valid_paths = [f.path for f in self.selected_files]
                self.on_files_selected(valid_paths)
    
    def _update_files_display(self):
        """Update the files display"""
        self.files_container.controls.clear()
        
        if not self.selected_files:
            self.files_container.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay archivos seleccionados",
                        size=14,
                        color=self.theme['on_surface_variant'],
                        text_align=ft.TextAlign.CENTER
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.all(20)
                )
            )
        else:
            for file_info in self.selected_files:
                file_card = self._create_file_card(file_info)
                self.files_container.controls.append(file_card)
        
        self.update()
    
    def _create_file_card(self, file_info: FileInfo) -> ft.Container:
        """Create a card for displaying file information"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.PICTURE_AS_PDF,
                    color=self.theme['primary'],
                    size=24
                ),
                ft.Column([
                    ft.Text(
                        file_info.name,
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.theme['on_surface'],
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    ft.Text(
                        f"{file_info.size_formatted} • {file_info.path.parent}",
                        size=12,
                        color=self.theme['on_surface_variant'],
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                ], spacing=2, expand=True),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=self.theme['error'],
                    icon_size=20,
                    tooltip="Remover archivo",
                    on_click=lambda _, f=file_info: self._remove_file(f)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=self.theme['surface_variant'],
            border_radius=8,
            padding=ft.padding.all(12),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )
    
    def _update_selection_info(self):
        """Update selection information text"""
        if not self.selected_files:
            self.selection_info.value = "No hay archivos seleccionados"
            self.selection_info.color = self.theme['on_surface_variant']
        else:
            total_size = sum(f.size for f in self.selected_files)
            size_formatted = self.file_manager.format_file_size(total_size)
            
            if len(self.selected_files) == 1:
                self.selection_info.value = f"1 archivo seleccionado ({size_formatted})"
            else:
                self.selection_info.value = f"{len(self.selected_files)} archivos seleccionados ({size_formatted})"
            
            self.selection_info.color = self.theme['on_surface']
        
        self.update()
    
    def _show_error(self, message: str):
        """Show error message"""
        if self.page:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=self.theme['error']
                )
            )
    
    def _show_warning(self, message: str):
        """Show warning message"""
        if self.page:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=self.theme['warning']
                )
            )
    
    def get_selected_files(self) -> List[Path]:
        """Get list of selected file paths"""
        return [f.path for f in self.selected_files]
    
    def set_files(self, file_paths: List[Path]):
        """Set files programmatically"""
        if file_paths:
            valid_files, invalid_files = self.file_manager.validate_files(file_paths)
            self.selected_files = valid_files
            self._update_files_display()
            self._update_selection_info()
            
            if self.on_files_selected:
                valid_paths = [f.path for f in self.selected_files]
                self.on_files_selected(valid_paths)
    
    def clear_files(self):
        """Clear all selected files"""
        self._clear_selection(None)

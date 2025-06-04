"""
Progress display components for HYDRA21 PDF Compressor
Provides progress indicators, spinners, and status updates
"""

import flet as ft
import time
import threading
from typing import Dict, Optional, Callable
from ui.themes.modern_components import create_modern_card, create_progress_indicator

class ProgressDisplay(ft.Container):
    """Progress display component with spinner and progress bar"""
    
    def __init__(
        self,
        theme: Dict[str, str],
        show_spinner: bool = True,
        show_progress_bar: bool = True,
        show_details: bool = True
    ):
        self.theme = theme
        self.show_spinner = show_spinner
        self.show_progress_bar = show_progress_bar
        self.show_details = show_details

        self.is_visible = False
        self.current_progress = 0.0
        self.current_message = ""
        self.current_details = ""

        # Build UI components
        self._build_components()

        # Initialize container
        super().__init__(
            content=self.progress_container,
            visible=False,
            animate_opacity=300
        )

    def _build_components(self):
        """Build the progress display components"""
        # Spinner
        self.spinner = ft.ProgressRing(
            width=40,
            height=40,
            stroke_width=4,
            color=self.theme['primary'],
            visible=self.show_spinner
        )

        # Progress bar
        self.progress_bar = ft.ProgressBar(
            width=400,
            height=8,
            color=self.theme['primary'],
            bgcolor=self.theme.get('surface_variant', '#f1f5f9'),
            value=0,
            visible=self.show_progress_bar
        )

        # Progress percentage text
        self.progress_text = ft.Text(
            "0%",
            size=14,
            weight=ft.FontWeight.W_500,
            color=self.theme['on_surface'],
            visible=self.show_progress_bar
        )

        # Message text
        self.message_text = ft.Text(
            "",
            size=16,
            color=self.theme['on_surface'],
            text_align=ft.TextAlign.CENTER,
            weight=ft.FontWeight.W_500
        )

        # Details text
        self.details_text = ft.Text(
            "",
            size=12,
            color=self.theme['on_surface_variant'],
            text_align=ft.TextAlign.CENTER,
            visible=self.show_details
        )

        # Progress container
        progress_content = []

        if self.show_spinner:
            progress_content.append(self.spinner)

        if self.show_progress_bar:
            progress_content.extend([
                ft.Row([
                    self.progress_bar,
                    self.progress_text
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
            ])

        progress_content.extend([
            self.message_text,
            self.details_text if self.show_details else ft.Container()
        ])

        self.progress_container = ft.Column(
            progress_content,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16
        )
    
    def show_progress(
        self,
        message: str = "Procesando...",
        progress: Optional[float] = None,
        details: str = ""
    ):
        """
        Show progress indicator
        
        Args:
            message: Main progress message
            progress: Progress percentage (0-100) or None for indeterminate
            details: Additional details text
        """
        self.current_message = message
        self.current_details = details
        
        if progress is not None:
            self.current_progress = max(0, min(100, progress))
        
        # Update UI components
        self.message_text.value = message
        
        if self.show_details:
            self.details_text.value = details
        
        if self.show_progress_bar and progress is not None:
            self.progress_bar.value = self.current_progress / 100
            self.progress_text.value = f"{self.current_progress:.1f}%"
        
        # Show container
        if not self.is_visible:
            self.visible = True
            self.is_visible = True

        self.update()
    
    def update_progress(
        self,
        progress: float,
        message: Optional[str] = None,
        details: Optional[str] = None
    ):
        """
        Update progress value and optional message
        
        Args:
            progress: Progress percentage (0-100)
            message: Optional new message
            details: Optional new details
        """
        self.current_progress = max(0, min(100, progress))
        
        if message is not None:
            self.current_message = message
            self.message_text.value = message
        
        if details is not None:
            self.current_details = details
            if self.show_details:
                self.details_text.value = details
        
        if self.show_progress_bar:
            self.progress_bar.value = self.current_progress / 100
            self.progress_text.value = f"{self.current_progress:.1f}%"
        
        self.update()
    
    def hide_progress(self):
        """Hide progress indicator"""
        self.visible = False
        self.is_visible = False
        self.current_progress = 0.0
        self.current_message = ""
        self.current_details = ""
        self.update()
    
    def set_indeterminate(self, message: str = "Procesando..."):
        """Set progress to indeterminate mode"""
        self.show_progress(message=message, progress=None)
    
    def set_complete(self, message: str = "Completado", details: str = ""):
        """Set progress to complete state"""
        self.show_progress(message=message, progress=100, details=details)

class BatchProgressDisplay(ft.Container):
    """Enhanced progress display for batch operations"""
    
    def __init__(self, theme: Dict[str, str]):
        self.theme = theme

        self.is_visible = False
        self.current_file = 0
        self.total_files = 0
        self.current_filename = ""
        self.current_operation = ""
        self.overall_progress = 0.0

        # Build UI components
        self._build_components()

        # Initialize container
        super().__init__(
            content=self.progress_container,
            visible=False,
            animate_opacity=300
        )

    def _build_components(self):
        """Build the batch progress display"""
        # Spinner
        self.spinner = ft.ProgressRing(
            width=40,
            height=40,
            stroke_width=4,
            color=self.theme['primary']
        )
        
        # Overall progress
        self.overall_progress_bar = ft.ProgressBar(
            width=400,
            height=10,
            color=self.theme['primary'],
            bgcolor=self.theme.get('surface_variant', '#f1f5f9'),
            value=0
        )
        
        # File progress (for individual file operations)
        self.file_progress_bar = ft.ProgressBar(
            width=400,
            height=6,
            color=self.theme['secondary'],
            bgcolor=self.theme.get('surface_variant', '#f1f5f9'),
            value=0
        )
        
        # Text components
        self.overall_text = ft.Text(
            "",
            size=16,
            weight=ft.FontWeight.W_600,
            color=self.theme['on_surface'],
            text_align=ft.TextAlign.CENTER
        )
        
        self.current_file_text = ft.Text(
            "",
            size=14,
            color=self.theme['on_surface'],
            text_align=ft.TextAlign.CENTER,
            overflow=ft.TextOverflow.ELLIPSIS
        )
        
        self.operation_text = ft.Text(
            "",
            size=12,
            color=self.theme['on_surface_variant'],
            text_align=ft.TextAlign.CENTER
        )
        
        # Progress container
        self.progress_container = create_modern_card([
            ft.Column([
                self.spinner,
                ft.Container(height=16),
                self.overall_text,
                ft.Row([
                    self.overall_progress_bar,
                    ft.Text(
                        "0%",
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.theme['on_surface']
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
                ft.Container(height=8),
                self.current_file_text,
                self.operation_text,
                ft.Container(height=8),
                self.file_progress_bar
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
        ], theme=self.theme)
    
    def show_batch_progress(
        self,
        current_file: int,
        total_files: int,
        filename: str,
        operation: str = "Procesando"
    ):
        """
        Show batch progress
        
        Args:
            current_file: Current file number (1-based)
            total_files: Total number of files
            filename: Current filename being processed
            operation: Current operation description
        """
        self.current_file = current_file
        self.total_files = total_files
        self.current_filename = filename
        self.current_operation = operation
        
        # Calculate overall progress
        if total_files > 0:
            self.overall_progress = (current_file / total_files) * 100
        else:
            self.overall_progress = 0
        
        # Update UI
        self.overall_text.value = f"Procesando archivo {current_file} de {total_files}"
        self.current_file_text.value = f"📄 {filename}"
        self.operation_text.value = operation
        
        # Update progress bars
        self.overall_progress_bar.value = self.overall_progress / 100
        
        # Update percentage text
        percentage_text = self.overall_progress_bar.parent.controls[1]
        percentage_text.value = f"{self.overall_progress:.0f}%"
        
        # Show container
        if not self.is_visible:
            self.visible = True
            self.is_visible = True

        self.update()
    
    def update_file_progress(self, file_progress: float):
        """
        Update progress for current file
        
        Args:
            file_progress: Progress for current file (0-100)
        """
        if self.file_progress_bar:
            self.file_progress_bar.value = max(0, min(100, file_progress)) / 100
            self.update()
    
    def hide_progress(self):
        """Hide batch progress display"""
        self.visible = False
        self.is_visible = False
        self.current_file = 0
        self.total_files = 0
        self.current_filename = ""
        self.current_operation = ""
        self.overall_progress = 0.0
        self.update()
    
    def set_complete(self, message: str = "Procesamiento completado"):
        """Set batch progress to complete state"""
        self.overall_text.value = message
        self.current_file_text.value = "✅ Todos los archivos procesados"
        self.operation_text.value = ""
        self.overall_progress_bar.value = 1.0
        self.file_progress_bar.value = 1.0
        
        # Update percentage text
        percentage_text = self.overall_progress_bar.parent.controls[1]
        percentage_text.value = "100%"
        
        # Hide spinner
        self.spinner.visible = False
        
        self.update()
    
    def set_error(self, message: str = "Error en el procesamiento"):
        """Set batch progress to error state"""
        self.overall_text.value = message
        self.overall_text.color = self.theme['error']
        self.current_file_text.value = "❌ Procesamiento interrumpido"
        self.operation_text.value = ""
        
        # Hide spinner
        self.spinner.visible = False
        
        self.update()

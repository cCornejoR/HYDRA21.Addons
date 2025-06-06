"""
HYDRA21 Orthophoto Processor Pro - Progress Display Components
Professional progress indicators and statistics display
"""

import flet as ft
import time
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta

class ProgressDisplay(ft.Column):
    """Professional progress display with spinner, progress bar, and statistics"""
    
    def __init__(
        self,
        theme: Dict[str, str],
        show_spinner: bool = True,
        show_progress_bar: bool = True,
        show_details: bool = True,
        show_statistics: bool = True
    ):
        self.theme = theme
        self.show_spinner = show_spinner
        self.show_progress_bar = show_progress_bar
        self.show_details = show_details
        self.show_statistics = show_statistics
        
        # State
        self.current_progress = 0
        self.current_message = ""
        self.current_details = ""
        self.start_time = None
        self.statistics = {}
        
        # Build components
        self._build_components()
        
        super().__init__(
            controls=self._build_layout(),
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
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

        # ETA text
        self.eta_text = ft.Text(
            "",
            size=12,
            color=self.theme['on_surface_variant'],
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

        # Statistics container
        self.statistics_container = ft.Container(
            content=ft.Column([], spacing=8),
            visible=self.show_statistics,
            padding=ft.padding.all(16),
            bgcolor=self.theme['surface_variant'],
            border_radius=8,
            border=ft.border.all(1, self.theme['border'])
        )
    
    def _build_layout(self) -> List[ft.Control]:
        """Build the layout"""
        layout = []
        
        # Spinner and message row
        if self.show_spinner:
            layout.append(
                ft.Row([
                    self.spinner,
                    ft.Column([
                        self.message_text,
                        self.details_text
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=16)
            )
        else:
            layout.append(self.message_text)
            if self.show_details:
                layout.append(self.details_text)
        
        # Progress bar and percentage
        if self.show_progress_bar:
            layout.append(
                ft.Column([
                    self.progress_bar,
                    ft.Row([
                        self.progress_text,
                        self.eta_text
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        
        # Statistics
        if self.show_statistics:
            layout.append(self.statistics_container)
        
        return layout
    
    def show_progress(
        self,
        message: str = "Procesando...",
        progress: Optional[float] = None,
        details: str = ""
    ):
        """
        Show progress indicator with enhanced features

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

            # Calculate and show estimated time remaining
            if self.start_time and progress > 0:
                elapsed = time.time() - self.start_time
                estimated_total = elapsed * (100 / progress)
                remaining = estimated_total - elapsed

                if remaining > 0:
                    if remaining < 60:
                        eta_text = f"ETA: {remaining:.0f}s"
                    elif remaining < 3600:
                        eta_text = f"ETA: {remaining/60:.1f}m"
                    else:
                        eta_text = f"ETA: {remaining/3600:.1f}h"

                    self.eta_text.value = eta_text
        
        # Update visibility
        self.visible = True
        self.spinner.visible = self.show_spinner
        
        # Start timing if not already started
        if self.start_time is None:
            self.start_time = time.time()
    
    def update_statistics(self, stats: Dict[str, Any]):
        """Update processing statistics"""
        self.statistics.update(stats)
        
        if self.show_statistics:
            self._update_statistics_display()
    
    def _update_statistics_display(self):
        """Update the statistics display"""
        stats_controls = []
        
        # Processing time
        if self.start_time:
            if isinstance(self.start_time, float):
                # start_time is a timestamp
                elapsed_seconds = time.time() - self.start_time
                elapsed = timedelta(seconds=elapsed_seconds)
            else:
                # start_time is a datetime
                elapsed = datetime.now() - self.start_time
            stats_controls.append(
                self._create_stat_row("⏱️ Tiempo transcurrido", self._format_duration(elapsed))
            )
        
        # File information
        if "current_file" in self.statistics:
            stats_controls.append(
                self._create_stat_row("📁 Archivo actual", self.statistics["current_file"])
            )
        
        if "files_processed" in self.statistics and "total_files" in self.statistics:
            stats_controls.append(
                self._create_stat_row(
                    "📊 Progreso de archivos", 
                    f"{self.statistics['files_processed']}/{self.statistics['total_files']}"
                )
            )
        
        # Compression ratio
        if "compression_ratio" in self.statistics:
            ratio = self.statistics["compression_ratio"]
            stats_controls.append(
                self._create_stat_row("🗜️ Ratio de compresión", f"{ratio:.1f}%")
            )
        
        # File sizes
        if "original_size" in self.statistics and "compressed_size" in self.statistics:
            original = self.statistics["original_size"]
            compressed = self.statistics["compressed_size"]
            stats_controls.append(
                self._create_stat_row(
                    "📏 Tamaño original", 
                    self._format_file_size(original)
                )
            )
            stats_controls.append(
                self._create_stat_row(
                    "📦 Tamaño comprimido", 
                    self._format_file_size(compressed)
                )
            )
        
        # Processing speed
        if "processing_speed" in self.statistics:
            speed = self.statistics["processing_speed"]
            stats_controls.append(
                self._create_stat_row("⚡ Velocidad", f"{speed:.1f} MB/s")
            )
        
        # Update container
        self.statistics_container.content.controls = stats_controls
    
    def _create_stat_row(self, label: str, value: str) -> ft.Row:
        """Create a statistics row"""
        return ft.Row([
            ft.Text(
                label,
                size=12,
                color=self.theme['on_surface_variant'],
                weight=ft.FontWeight.W_500,
                expand=True
            ),
            ft.Text(
                value,
                size=12,
                color=self.theme['on_surface'],
                weight=ft.FontWeight.W_600
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration for display"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size for display"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def hide_progress(self):
        """Hide progress indicator"""
        self.visible = False
        self.spinner.visible = False
        self.start_time = None
        self.statistics.clear()
    
    def reset(self):
        """Reset progress display"""
        self.current_progress = 0
        self.current_message = ""
        self.current_details = ""
        self.start_time = None
        self.statistics.clear()
        
        self.progress_bar.value = 0
        self.progress_text.value = "0%"
        self.eta_text.value = ""
        self.message_text.value = ""
        self.details_text.value = ""
        self.statistics_container.content.controls.clear()
        
        self.hide_progress()
    
    def set_theme(self, new_theme: Dict[str, str]):
        """Update theme"""
        self.theme = new_theme
        
        # Update component colors
        self.spinner.color = self.theme['primary']
        self.progress_bar.color = self.theme['primary']
        self.progress_bar.bgcolor = self.theme.get('surface_variant', '#f1f5f9')
        self.progress_text.color = self.theme['on_surface']
        self.eta_text.color = self.theme['on_surface_variant']
        self.message_text.color = self.theme['on_surface']
        self.details_text.color = self.theme['on_surface_variant']
        
        # Update statistics container
        self.statistics_container.bgcolor = self.theme['surface_variant']
        self.statistics_container.border = ft.border.all(1, self.theme['border'])
        
        # Refresh statistics display
        if self.statistics:
            self._update_statistics_display()

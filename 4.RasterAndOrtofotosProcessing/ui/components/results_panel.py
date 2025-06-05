"""
HYDRA21 Orthophoto Processor Pro - Results Panel Component
Professional results display with statistics and file access
"""

import flet as ft
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class ResultsPanel(ft.Column):
    """Professional results panel with comprehensive statistics and file access"""
    
    def __init__(self, page: ft.Page, theme: Dict[str, str]):
        self.page = page
        self.theme = theme
        
        # State
        self.processing_results = None
        self.output_directory = None
        
        super().__init__(
            controls=self._build_layout(),
            spacing=24,
            expand=True
        )
    
    def _build_layout(self) -> List[ft.Control]:
        """Build the results panel layout"""
        if not self.processing_results:
            return self._build_empty_state()
        
        return [
            # Header
            self._create_header(),
            
            # Summary statistics
            self._create_summary_stats(),
            
            # Processed files list
            self._create_files_list(),
            
            # Action buttons
            self._create_action_buttons()
        ]
    
    def _build_empty_state(self) -> List[ft.Control]:
        """Build empty state when no results available"""
        return [
            ft.Container(
                content=ft.Column([
                    ft.Icon(
                        ft.Icons.ASSESSMENT,
                        size=64,
                        color=self.theme['on_surface_variant']
                    ),
                    ft.Text(
                        "No hay resultados disponibles",
                        size=20,
                        weight=ft.FontWeight.W_500,
                        color=self.theme['on_surface_variant'],
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Los resultados del procesamiento aparecerán aquí una vez completado",
                        size=14,
                        color=self.theme['on_surface_variant'],
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
    
    def _create_header(self) -> ft.Row:
        """Create results header"""
        success_count = len(self.processing_results.get("processed_files", []))
        failed_count = len(self.processing_results.get("failed_files", []))
        
        if failed_count == 0:
            status_icon = ft.Icons.CHECK_CIRCLE
            status_color = self.theme['success']
            status_text = "Procesamiento completado exitosamente"
        elif success_count == 0:
            status_icon = ft.Icons.ERROR
            status_color = self.theme['error']
            status_text = "Procesamiento falló"
        else:
            status_icon = ft.Icons.WARNING
            status_color = self.theme['warning']
            status_text = "Procesamiento completado con errores"
        
        return ft.Row([
            ft.Row([
                ft.Icon(status_icon, color=status_color, size=24),
                ft.Text(
                    "📊 Resultados del Procesamiento",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=self.theme['on_surface']
                )
            ], spacing=8),
            ft.Container(
                content=ft.Text(
                    status_text,
                    size=14,
                    color=status_color,
                    weight=ft.FontWeight.W_500
                ),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                bgcolor=self._get_status_container_color(status_color),
                border_radius=16,
                border=ft.border.all(1, status_color)
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    def _create_summary_stats(self) -> ft.Container:
        """Create summary statistics"""
        stats = self.processing_results
        
        # Calculate statistics
        total_files = len(stats.get("processed_files", [])) + len(stats.get("failed_files", []))
        success_count = len(stats.get("processed_files", []))
        success_rate = (success_count / total_files * 100) if total_files > 0 else 0
        
        original_size = stats.get("total_original_size", 0)
        compressed_size = stats.get("total_compressed_size", 0)
        compression_ratio = stats.get("compression_ratio", 0)
        processing_time = stats.get("processing_time", 0)
        
        # Create stat cards
        stat_cards = [
            self._create_stat_card(
                "📁 Archivos Procesados",
                f"{success_count}/{total_files}",
                f"{success_rate:.1f}% éxito",
                self.theme['primary']
            ),
            self._create_stat_card(
                "📏 Tamaño Original",
                self._format_file_size(original_size),
                "Total de entrada",
                self.theme['info']
            ),
            self._create_stat_card(
                "📦 Tamaño Comprimido",
                self._format_file_size(compressed_size),
                f"{compression_ratio:.1f}% reducción",
                self.theme['success']
            ),
            self._create_stat_card(
                "⏱️ Tiempo de Procesamiento",
                self._format_duration(processing_time),
                f"{self._calculate_speed(original_size, processing_time):.1f} MB/s",
                self.theme['secondary']
            )
        ]
        
        return ft.Container(
            content=ft.Row(
                stat_cards,
                spacing=16,
                alignment=ft.MainAxisAlignment.SPACE_AROUND
            ),
            padding=ft.padding.all(20),
            bgcolor=self.theme['surface_variant'],
            border_radius=12,
            border=ft.border.all(1, self.theme['border'])
        )
    
    def _create_stat_card(
        self,
        title: str,
        value: str,
        subtitle: str,
        color: str
    ) -> ft.Container:
        """Create a statistics card"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    title,
                    size=12,
                    color=self.theme['on_surface_variant'],
                    weight=ft.FontWeight.W_500
                ),
                ft.Text(
                    value,
                    size=18,
                    color=color,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    subtitle,
                    size=11,
                    color=self.theme['on_surface_variant']
                )
            ],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(16),
            bgcolor=self.theme['surface'],
            border_radius=8,
            border=ft.border.all(1, color),
            width=180
        )
    
    def _create_files_list(self) -> ft.Container:
        """Create processed files list"""
        processed_files = self.processing_results.get("processed_files", [])
        failed_files = self.processing_results.get("failed_files", [])
        
        files_content = []
        
        # Successful files
        if processed_files:
            files_content.append(
                ft.Text(
                    f"✅ Archivos procesados exitosamente ({len(processed_files)})",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=self.theme['success']
                )
            )
            
            for file_result in processed_files:
                files_content.append(
                    self._create_file_result_item(file_result, True)
                )
        
        # Failed files
        if failed_files:
            if processed_files:
                files_content.append(ft.Divider(height=20))
            
            files_content.append(
                ft.Text(
                    f"❌ Archivos con errores ({len(failed_files)})",
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=self.theme['error']
                )
            )
            
            for file_error in failed_files:
                files_content.append(
                    self._create_file_error_item(file_error)
                )
        
        return ft.Container(
            content=ft.Column(
                files_content,
                spacing=12,
                scroll=ft.ScrollMode.AUTO
            ),
            padding=ft.padding.all(20),
            bgcolor=self.theme['surface'],
            border_radius=12,
            border=ft.border.all(1, self.theme['border']),
            height=300,
            expand=True
        )
    
    def _create_file_result_item(self, file_result: Dict[str, Any], success: bool) -> ft.Container:
        """Create a file result item"""
        input_file = Path(file_result["input_file"])
        output_file = Path(file_result["output_file"])
        
        # File info
        original_size = file_result.get("original_size", 0)
        compressed_size = file_result.get("compressed_size", 0)
        compression_ratio = file_result.get("compression_ratio", 0)
        processing_time = file_result.get("processing_time", 0)
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE if success else ft.Icons.ERROR,
                    color=self.theme['success'] if success else self.theme['error'],
                    size=20
                ),
                ft.Column([
                    ft.Text(
                        input_file.name,
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.theme['on_surface']
                    ),
                    ft.Text(
                        f"{self._format_file_size(original_size)} → {self._format_file_size(compressed_size)} "
                        f"({compression_ratio:.1f}% reducción) • {processing_time:.1f}s",
                        size=12,
                        color=self.theme['on_surface_variant']
                    )
                ], spacing=2, expand=True),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.FOLDER_OPEN,
                        tooltip="Abrir carpeta",
                        icon_color=self.theme['primary'],
                        on_click=lambda e, path=output_file.parent: self._open_folder(path)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.OPEN_IN_NEW,
                        tooltip="Abrir archivo",
                        icon_color=self.theme['secondary'],
                        on_click=lambda e, path=output_file: self._open_file(path)
                    )
                ], spacing=0)
            ], spacing=12),
            padding=ft.padding.all(12),
            bgcolor=self.theme['surface_variant'],
            border_radius=8,
            border=ft.border.all(1, self.theme['border'])
        )
    
    def _create_file_error_item(self, file_error: Dict[str, Any]) -> ft.Container:
        """Create a file error item"""
        file_path = Path(file_error["file"])
        error_message = file_error["error"]
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR, color=self.theme['error'], size=20),
                ft.Column([
                    ft.Text(
                        file_path.name,
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.theme['on_surface']
                    ),
                    ft.Text(
                        f"Error: {error_message}",
                        size=12,
                        color=self.theme['error']
                    )
                ], spacing=2, expand=True)
            ], spacing=12),
            padding=ft.padding.all(12),
            bgcolor=self.theme['error_container'],
            border_radius=8,
            border=ft.border.all(1, self.theme['error'])
        )
    
    def _create_action_buttons(self) -> ft.Row:
        """Create action buttons"""
        return ft.Row([
            ft.ElevatedButton(
                text="Abrir Carpeta de Salida",
                icon=ft.Icons.FOLDER_OPEN,
                bgcolor=self.theme['primary'],
                color=self.theme['on_primary'],
                width=200,
                height=45,
                on_click=lambda e: self._open_folder(self.output_directory) if self.output_directory else None
            ),
            ft.ElevatedButton(
                text="Nuevo Procesamiento",
                icon=ft.Icons.REFRESH,
                bgcolor=self.theme['secondary'],
                color=self.theme['on_primary'],
                width=180,
                height=45,
                on_click=self._start_new_processing
            ),
            ft.ElevatedButton(
                text="Exportar Reporte",
                icon=ft.Icons.DOWNLOAD,
                bgcolor=self.theme['surface_variant'],
                color=self.theme['on_surface'],
                width=150,
                height=45,
                on_click=self._export_report
            )
        ], spacing=16)
    
    def _open_folder(self, folder_path: Path):
        """Open folder in file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(folder_path))
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', str(folder_path)])
        except Exception as e:
            print(f"Error opening folder: {e}")
    
    def _open_file(self, file_path: Path):
        """Open file with default application"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(file_path))
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', str(file_path)])
        except Exception as e:
            print(f"Error opening file: {e}")
    
    def _start_new_processing(self, e):
        """Start new processing session"""
        # TODO: Reset application state and return to files tab
        pass
    
    def _export_report(self, e):
        """Export processing report"""
        # TODO: Implement report export
        pass
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size for display"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration for display"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def _calculate_speed(self, size_bytes: int, time_seconds: float) -> float:
        """Calculate processing speed in MB/s"""
        if time_seconds > 0:
            return (size_bytes / (1024 * 1024)) / time_seconds
        return 0
    
    def _get_status_container_color(self, status_color: str) -> str:
        """Get container color for status"""
        if status_color == self.theme['success']:
            return self.theme['success_container']
        elif status_color == self.theme['error']:
            return self.theme['error_container']
        elif status_color == self.theme['warning']:
            return self.theme['warning_container']
        else:
            return self.theme['info_container']
    
    def set_results(self, results: Dict[str, Any], output_dir: Path):
        """Set processing results"""
        self.processing_results = results
        self.output_directory = output_dir
        
        # Rebuild layout
        self.controls.clear()
        self.controls.extend(self._build_layout())
    
    def set_theme(self, new_theme: Dict[str, str]):
        """Update theme"""
        self.theme = new_theme
        
        # Rebuild layout with new theme
        if self.processing_results:
            self.controls.clear()
            self.controls.extend(self._build_layout())

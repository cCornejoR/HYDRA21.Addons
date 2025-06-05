"""
Statistics display panel for HYDRA21 PDF Compressor
Shows detailed statistics and results after processing operations
"""

import flet as ft
from pathlib import Path
from typing import Dict, List, Optional, Any
from core.pdf_processor import ProcessingStats
from core.ghostscript_manager import OperationResult
from core.file_manager import FileManager
from ui.themes.modern_components import create_modern_card, create_modern_button, create_status_chip
from utils.helpers import format_duration

class StatisticsPanel(ft.Container):
    """Statistics display panel for processing results"""
    
    def __init__(
        self,
        theme: Dict[str, str],
        file_manager: FileManager,
        on_open_file: Optional[callable] = None,
        on_open_folder: Optional[callable] = None
    ):
        self.theme = theme
        self.file_manager = file_manager
        self.on_open_file = on_open_file
        self.on_open_folder = on_open_folder

        self.is_visible = False

        # Initialize with default content
        super().__init__(
            content=ft.Column([
                ft.Text(
                    "Estadísticas de Procesamiento",
                    size=20,
                    weight=ft.FontWeight.W_600,
                    color=self.theme['on_surface']
                )
            ], spacing=16),
            visible=False,
            animate_opacity=300
        )
    
    def show_compression_stats(self, stats: ProcessingStats):
        """
        Show compression statistics
        
        Args:
            stats: ProcessingStats object with compression results
        """
        self._clear_content()
        
        # Overall statistics
        overall_stats = self._create_overall_stats_card(stats)
        
        # Individual file results
        if stats.individual_results:
            individual_results = self._create_individual_results_section(stats.individual_results)
        else:
            individual_results = ft.Container()
        
        # Failed files section
        failed_section = ft.Container()
        if stats.failed_files_list:
            failed_section = self._create_failed_files_section(stats.failed_files_list)
        
        # Action buttons
        action_buttons = self._create_action_buttons(stats)
        
        # Update container content
        self.content = ft.Column([
            ft.Text(
                "📊 Estadísticas de Compresión",
                size=20,
                weight=ft.FontWeight.W_600,
                color=self.theme['on_surface']
            ),
            overall_stats,
            individual_results,
            failed_section,
            action_buttons
        ], spacing=16, scroll=ft.ScrollMode.AUTO)

        self._show()
    
    def show_single_operation_stats(self, result: OperationResult, operation_type: str = "compresión"):
        """
        Show statistics for single operation
        
        Args:
            result: OperationResult from the operation
            operation_type: Type of operation (compresión, fusión, división)
        """
        self._clear_content()
        
        # Operation icon
        operation_icons = {
            "compresión": "📦",
            "fusión": "🔗",
            "división": "✂️"
        }
        icon = operation_icons.get(operation_type, "📄")
        
        # Create single operation stats
        stats_content = []
        
        if result.success:
            # Success stats
            stats_rows = []
            
            if result.original_size and result.final_size:
                # Size information
                original_size_str = self.file_manager.format_file_size(result.original_size)
                final_size_str = self.file_manager.format_file_size(result.final_size)
                reduction = result.original_size - result.final_size
                reduction_str = self.file_manager.format_file_size(reduction)
                compression_ratio = (reduction / result.original_size) * 100 if result.original_size > 0 else 0
                
                stats_rows.extend([
                    self._create_stat_row("Tamaño Original", original_size_str),
                    self._create_stat_row("Tamaño Final", final_size_str),
                    self._create_stat_row("Reducción", f"{reduction_str} ({compression_ratio:.1f}%)"),
                ])
            
            if result.processing_time:
                stats_rows.append(
                    self._create_stat_row("Tiempo de Procesamiento", format_duration(result.processing_time))
                )
            
            if result.output_path:
                stats_rows.append(
                    self._create_stat_row("Archivo de Salida", str(result.output_path.name))
                )
            
            stats_content.append(
                create_modern_card([
                    ft.Row([
                        create_status_chip("Exitoso", "success", self.theme, ft.Icons.CHECK_CIRCLE),
                        ft.Text(
                            result.message,
                            size=16,
                            weight=ft.FontWeight.W_500,
                            color=self.theme['on_surface'],
                            expand=True
                        )
                    ]),
                    ft.Divider(color=self.theme['border']),
                    ft.Column(stats_rows, spacing=8)
                ], self.theme)
            )
            
            # Action buttons for successful operation
            if result.output_path:
                action_buttons = ft.Row([
                    create_modern_button(
                        text="Abrir Archivo",
                        icon=ft.Icons.OPEN_IN_NEW,
                        on_click=lambda e: self._open_file(result.output_path),
                        style="primary",
                        theme=self.theme
                    ),
                    create_modern_button(
                        text="Abrir Carpeta",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=lambda e: self._open_folder(result.output_path.parent),
                        style="secondary",
                        theme=self.theme
                    )
                ], spacing=12)
                
                stats_content.append(action_buttons)
        
        else:
            # Error stats
            stats_content.append(
                create_modern_card([
                    ft.Row([
                        create_status_chip("Error", "error", self.theme, ft.Icons.ERROR),
                        ft.Text(
                            "Operación Fallida",
                            size=16,
                            weight=ft.FontWeight.W_500,
                            color=self.theme['error'],
                            expand=True
                        )
                    ]),
                    ft.Divider(color=self.theme['border']),
                    ft.Text(
                        result.message,
                        size=14,
                        color=self.theme['on_surface']
                    )
                ], self.theme)
            )
        
        # Update container content
        self.content = ft.Column([
            ft.Text(
                f"{icon} Resultado de {operation_type.title()}",
                size=20,
                weight=ft.FontWeight.W_600,
                color=self.theme['on_surface']
            ),
            *stats_content
        ], spacing=16)

        self._show()
    
    def _create_overall_stats_card(self, stats: ProcessingStats) -> ft.Container:
        """Create overall statistics card"""
        return create_modern_card([
            ft.Text(
                "Resumen General",
                size=16,
                weight=ft.FontWeight.W_600,
                color=self.theme['on_surface']
            ),
            ft.Row([
                self._create_metric_card("Archivos Procesados", f"{stats.processed_files}/{stats.total_files}"),
                self._create_metric_card("Tasa de Éxito", f"{stats.success_rate:.1f}%"),
                self._create_metric_card("Tiempo Total", format_duration(stats.total_processing_time))
            ], spacing=12),
            ft.Divider(color=self.theme['border']),
            ft.Column([
                self._create_stat_row("Tamaño Original Total", self.file_manager.format_file_size(stats.total_original_size)),
                self._create_stat_row("Tamaño Final Total", self.file_manager.format_file_size(stats.total_final_size)),
                self._create_stat_row("Reducción Total", f"{self.file_manager.format_file_size(stats.size_reduction)} ({stats.compression_ratio:.1f}%)"),
                self._create_stat_row("Tiempo Promedio por Archivo", format_duration(stats.total_processing_time / max(stats.processed_files, 1)))
            ], spacing=8)
        ], self.theme)
    
    def _create_individual_results_section(self, results: List[OperationResult]) -> ft.Container:
        """Create individual results section"""
        results_list = []
        
        for i, result in enumerate(results, 1):
            if result.success and result.output_path:
                original_size_str = self.file_manager.format_file_size(result.original_size or 0)
                final_size_str = self.file_manager.format_file_size(result.final_size or 0)
                
                if result.original_size and result.final_size:
                    reduction = result.original_size - result.final_size
                    compression_ratio = (reduction / result.original_size) * 100
                    reduction_text = f"{compression_ratio:.1f}% reducción"
                else:
                    reduction_text = "N/A"
                
                result_card = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PICTURE_AS_PDF, color=self.theme['primary'], size=20),
                        ft.Column([
                            ft.Text(
                                result.output_path.name,
                                size=14,
                                weight=ft.FontWeight.W_500,
                                color=self.theme['on_surface']
                            ),
                            ft.Text(
                                f"{original_size_str} → {final_size_str} ({reduction_text})",
                                size=12,
                                color=self.theme['on_surface_variant']
                            )
                        ], spacing=2, expand=True),
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.OPEN_IN_NEW,
                                icon_color=self.theme['primary'],
                                icon_size=20,
                                tooltip="Abrir archivo",
                                on_click=lambda e, path=result.output_path: self._open_file(path)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.FOLDER_OPEN,
                                icon_color=self.theme['secondary'],
                                icon_size=20,
                                tooltip="Abrir carpeta",
                                on_click=lambda e, path=result.output_path.parent: self._open_folder(path)
                            )
                        ], spacing=0)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=self.theme['surface_variant'],
                    border_radius=8,
                    padding=ft.padding.all(12)
                )
                
                results_list.append(result_card)
        
        if results_list:
            return create_modern_card([
                ft.Text(
                    f"Archivos Procesados ({len(results_list)})",
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=self.theme['on_surface']
                ),
                ft.Column(results_list, spacing=8, scroll=ft.ScrollMode.AUTO, height=200)
            ], self.theme)
        else:
            return ft.Container()
    
    def _create_failed_files_section(self, failed_files: List[str]) -> ft.Container:
        """Create failed files section"""
        failed_list = []
        
        for failed_file in failed_files:
            failed_card = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ERROR, color=self.theme['error'], size=20),
                    ft.Text(
                        failed_file,
                        size=14,
                        color=self.theme['on_surface'],
                        expand=True,
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                ]),
                bgcolor=self.theme['error_container'],
                border_radius=8,
                padding=ft.padding.all(12)
            )
            failed_list.append(failed_card)
        
        return create_modern_card([
            ft.Text(
                f"Archivos con Errores ({len(failed_files)})",
                size=16,
                weight=ft.FontWeight.W_600,
                color=self.theme['error']
            ),
            ft.Column(failed_list, spacing=8, scroll=ft.ScrollMode.AUTO, height=150)
        ], self.theme)
    
    def _create_action_buttons(self, stats: ProcessingStats) -> ft.Container:
        """Create action buttons section"""
        buttons = []
        
        if stats.processed_files > 0:
            # Get output directory from first successful result
            output_dir = None
            for result in stats.individual_results:
                if result.success and result.output_path:
                    output_dir = result.output_path.parent
                    break
            
            if output_dir:
                buttons.append(
                    create_modern_button(
                        text="Abrir Carpeta de Salida",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=lambda e: self._open_folder(output_dir),
                        style="primary",
                        theme=self.theme
                    )
                )
        
        buttons.append(
            create_modern_button(
                text="Cerrar Estadísticas",
                icon=ft.Icons.CLOSE,
                on_click=lambda e: self.hide(),
                style="secondary",
                theme=self.theme
            )
        )
        
        return ft.Row(buttons, spacing=12, alignment=ft.MainAxisAlignment.CENTER)
    
    def _create_metric_card(self, title: str, value: str) -> ft.Container:
        """Create a metric card"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    value,
                    size=20,
                    weight=ft.FontWeight.W_700,
                    color=self.theme['primary']
                ),
                ft.Text(
                    title,
                    size=12,
                    color=self.theme['on_surface_variant']
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            bgcolor=self.theme['surface_variant'],
            border_radius=8,
            padding=ft.padding.all(16),
            expand=True
        )
    
    def _create_stat_row(self, label: str, value: str) -> ft.Row:
        """Create a statistics row"""
        return ft.Row([
            ft.Text(
                label,
                size=14,
                color=self.theme['on_surface_variant'],
                expand=True
            ),
            ft.Text(
                value,
                size=14,
                weight=ft.FontWeight.W_500,
                color=self.theme['on_surface']
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    def _open_file(self, file_path: Path):
        """Open file with default application"""
        if self.on_open_file:
            self.on_open_file(file_path)
        else:
            self.file_manager.open_file(file_path)
    
    def _open_folder(self, folder_path: Path):
        """Open folder in file explorer"""
        if self.on_open_folder:
            self.on_open_folder(folder_path)
        else:
            self.file_manager.open_folder(folder_path)
    
    def _clear_content(self):
        """Clear container content"""
        self.content = ft.Column([])

    def _show(self):
        """Show the statistics panel"""
        self.visible = True
        self.is_visible = True
        self.update()

    def hide(self):
        """Hide the statistics panel"""
        self.visible = False
        self.is_visible = False
        self.update()
    
    def is_shown(self) -> bool:
        """Check if panel is currently shown"""
        return self.is_visible

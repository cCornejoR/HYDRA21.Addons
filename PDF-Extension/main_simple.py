"""
HYDRA21 PDF Compressor Pro - Versión Simplificada
Aplicación funcional sin componentes complejos que causan errores
"""

import flet as ft
import sys
import os
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main(page: ft.Page):
    """Aplicación principal simplificada"""
    
    # Configurar página
    page.title = "HYDRA21 PDF Compressor Pro v3.0.0"
    page.window_width = 1000
    page.window_height = 700
    page.window_center = True
    page.window_resizable = True
    
    # Tema azul (preferencia del usuario)
    page.theme = ft.Theme(
        use_material3=True,
        color_scheme_seed="#2563eb"
    )
    
    # Variables de estado
    selected_files = []
    current_operation = "compress"
    
    # Crear componentes principales
    def create_header():
        """Crear header de la aplicación"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PICTURE_AS_PDF, size=40, color="#2563eb"),
                ft.Column([
                    ft.Text(
                        "HYDRA21 PDF Compressor Pro",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color="#2563eb"
                    ),
                    ft.Text(
                        "Procesamiento profesional de archivos PDF",
                        size=14,
                        color="#64748b"
                    )
                ], spacing=2),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.HELP_OUTLINE,
                        tooltip="Ayuda",
                        icon_color="#6b7280",
                        on_click=lambda _: show_help()
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        tooltip="Configuración",
                        icon_color="#6b7280",
                        on_click=lambda _: show_settings()
                    )
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(20),
            bgcolor="#f8fafc",
            border_radius=12,
            margin=ft.margin.all(10),
            border=ft.border.all(1, "#e2e8f0")
        )
    
    def create_file_selector():
        """Crear selector de archivos simplificado"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "📁 Selección de Archivos",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color="#374151"
                ),
                ft.Container(height=10),
                ft.Row([
                    ft.ElevatedButton(
                        text="Seleccionar Archivos PDF",
                        icon=ft.Icons.FOLDER_OPEN,
                        bgcolor="#2563eb",
                        color="white",
                        on_click=lambda _: select_files()
                    ),
                    ft.ElevatedButton(
                        text="Limpiar Selección",
                        icon=ft.Icons.CLEAR,
                        bgcolor="#6b7280",
                        color="white",
                        on_click=lambda _: clear_files()
                    )
                ], spacing=12),
                ft.Container(height=10),
                ft.Text(
                    "No hay archivos seleccionados",
                    size=14,
                    color="#6b7280"
                )
            ]),
            padding=ft.padding.all(20),
            bgcolor="white",
            border_radius=12,
            margin=ft.margin.all(10),
            border=ft.border.all(1, "#e2e8f0")
        )
    
    def create_operations_panel():
        """Crear panel de operaciones"""
        return ft.Container(
            content=ft.Tabs(
                selected_index=0,
                on_change=lambda e: change_operation(e),
                tabs=[
                    ft.Tab(
                        text="Comprimir",
                        icon=ft.Icons.COMPRESS,
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("🗜️ Compresión de PDFs", size=16, weight=ft.FontWeight.W_600),
                                ft.Text("Reduce el tamaño de tus archivos PDF manteniendo la calidad."),
                                ft.Container(height=15),
                                ft.Dropdown(
                                    label="Calidad de compresión",
                                    options=[
                                        ft.dropdown.Option("high", "Alta calidad (menos compresión)"),
                                        ft.dropdown.Option("medium", "Calidad media (compresión balanceada)"),
                                        ft.dropdown.Option("low", "Baja calidad (máxima compresión)")
                                    ],
                                    value="medium",
                                    width=400
                                ),
                                ft.Container(height=15),
                                ft.ElevatedButton(
                                    text="Comprimir PDFs",
                                    icon=ft.Icons.PLAY_ARROW,
                                    bgcolor="#10b981",
                                    color="white",
                                    on_click=lambda _: start_compression()
                                )
                            ], spacing=8),
                            padding=ft.padding.all(20)
                        )
                    ),
                    ft.Tab(
                        text="Fusionar",
                        icon=ft.Icons.MERGE,
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("🔗 Fusión de PDFs", size=16, weight=ft.FontWeight.W_600),
                                ft.Text("Combina múltiples archivos PDF en uno solo."),
                                ft.Container(height=15),
                                ft.TextField(
                                    label="Nombre del archivo fusionado",
                                    value="documento_fusionado.pdf",
                                    width=400
                                ),
                                ft.Container(height=15),
                                ft.ElevatedButton(
                                    text="Fusionar PDFs",
                                    icon=ft.Icons.PLAY_ARROW,
                                    bgcolor="#10b981",
                                    color="white",
                                    on_click=lambda _: start_merge()
                                )
                            ], spacing=8),
                            padding=ft.padding.all(20)
                        )
                    ),
                    ft.Tab(
                        text="Dividir",
                        icon=ft.Icons.CONTENT_CUT,
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("✂️ División de PDFs", size=16, weight=ft.FontWeight.W_600),
                                ft.Text("Extrae páginas específicas de un archivo PDF."),
                                ft.Container(height=15),
                                ft.Row([
                                    ft.TextField(
                                        label="Página inicial",
                                        value="1",
                                        width=150
                                    ),
                                    ft.TextField(
                                        label="Página final",
                                        hint_text="Opcional (todas)",
                                        width=150
                                    )
                                ], spacing=12),
                                ft.Container(height=15),
                                ft.ElevatedButton(
                                    text="Dividir PDF",
                                    icon=ft.Icons.PLAY_ARROW,
                                    bgcolor="#10b981",
                                    color="white",
                                    on_click=lambda _: start_split()
                                )
                            ], spacing=8),
                            padding=ft.padding.all(20)
                        )
                    )
                ]
            ),
            bgcolor="white",
            border_radius=12,
            margin=ft.margin.all(10),
            border=ft.border.all(1, "#e2e8f0")
        )
    
    def create_status_panel():
        """Crear panel de estado"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "📊 Estado de la Aplicación",
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color="#374151"
                ),
                ft.Container(height=10),
                ft.Text(
                    "✅ Aplicación lista para usar",
                    size=14,
                    color="#10b981"
                ),
                ft.Text(
                    "💡 Selecciona archivos PDF y elige una operación para comenzar",
                    size=12,
                    color="#6b7280"
                )
            ]),
            padding=ft.padding.all(20),
            bgcolor="#f0fdf4",
            border_radius=12,
            margin=ft.margin.all(10),
            border=ft.border.all(1, "#bbf7d0")
        )
    
    # Funciones de eventos
    def select_files():
        """Simular selección de archivos"""
        show_message("📁 Función de selección de archivos (simulada)")
        # Aquí iría la lógica real de selección de archivos
    
    def clear_files():
        """Limpiar archivos seleccionados"""
        global selected_files
        selected_files = []
        show_message("🗑️ Selección limpiada")
    
    def change_operation(e):
        """Cambiar operación actual"""
        global current_operation
        operations = ["compress", "merge", "split"]
        current_operation = operations[e.control.selected_index]
        show_message(f"🔄 Operación cambiada a: {current_operation}")
    
    def start_compression():
        """Iniciar compresión"""
        show_message("🗜️ Iniciando compresión de PDFs...")
        # Aquí iría la lógica real de compresión
    
    def start_merge():
        """Iniciar fusión"""
        show_message("🔗 Iniciando fusión de PDFs...")
        # Aquí iría la lógica real de fusión
    
    def start_split():
        """Iniciar división"""
        show_message("✂️ Iniciando división de PDF...")
        # Aquí iría la lógica real de división
    
    def show_help():
        """Mostrar ayuda"""
        show_message("❓ Ayuda: Esta es una versión simplificada de HYDRA21 PDF Compressor")
    
    def show_settings():
        """Mostrar configuración"""
        show_message("⚙️ Configuración: Funcionalidad en desarrollo")
    
    def show_message(message: str):
        """Mostrar mensaje en snackbar"""
        try:
            # Método compatible con diferentes versiones de Flet
            snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor="#2563eb"
            )
            page.snack_bar = snack_bar
            snack_bar.open = True
            page.update()
        except Exception as e:
            # Fallback: mostrar en consola
            print(f"💬 {message}")
            print(f"Debug: {e}")
    
    # Construir interfaz
    page.add(
        ft.Column([
            create_header(),
            create_file_selector(),
            create_operations_panel(),
            create_status_panel()
        ], expand=True, scroll=ft.ScrollMode.AUTO)
    )

def run_app():
    """Ejecutar la aplicación"""
    try:
        print("🚀 Iniciando HYDRA21 PDF Compressor Pro (Versión Simplificada)...")
        print("📁 Directorio de trabajo:", current_dir)
        
        ft.app(
            target=main,
            view=ft.AppView.FLET_APP
        )
        
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario")
    except Exception as e:
        print(f"Error crítico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_app()

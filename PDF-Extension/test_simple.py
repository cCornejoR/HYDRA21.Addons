"""
Test simple de la aplicación PDF-Extension
Prueba la interfaz básica sin componentes complejos
"""

import flet as ft

def main(page: ft.Page):
    """Aplicación de prueba simple"""
    
    # Configurar página
    page.title = "HYDRA21 PDF Compressor Pro - Test"
    page.window_width = 800
    page.window_height = 600
    page.window_center = True
    
    # Tema azul
    page.theme = ft.Theme(
        use_material3=True,
        color_scheme_seed="#2563eb"
    )
    
    # Contenido de prueba
    page.add(
        ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PICTURE_AS_PDF, size=32, color="#2563eb"),
                    ft.Text(
                        "HYDRA21 PDF Compressor Pro",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color="#2563eb"
                    )
                ], spacing=12),
                padding=ft.padding.all(20),
                bgcolor="#f8fafc",
                border_radius=12,
                margin=ft.margin.all(10)
            ),
            
            # Tabs de operaciones
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(
                        text="Comprimir",
                        icon=ft.Icons.COMPRESS,
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("🗜️ Compresión de PDFs", size=18, weight=ft.FontWeight.W_600),
                                ft.Text("Reduce el tamaño de tus archivos PDF manteniendo la calidad."),
                                ft.Container(height=20),
                                ft.ElevatedButton(
                                    text="Seleccionar Archivos PDF",
                                    icon=ft.Icons.FOLDER_OPEN,
                                    bgcolor="#2563eb",
                                    color="white",
                                    on_click=lambda _: show_message("Función de selección de archivos")
                                ),
                                ft.Container(height=10),
                                ft.Dropdown(
                                    label="Calidad de compresión",
                                    options=[
                                        ft.dropdown.Option("high", "Alta calidad"),
                                        ft.dropdown.Option("medium", "Calidad media"),
                                        ft.dropdown.Option("low", "Baja calidad")
                                    ],
                                    value="medium",
                                    width=300
                                )
                            ], spacing=10),
                            padding=ft.padding.all(20)
                        )
                    ),
                    ft.Tab(
                        text="Fusionar",
                        icon=ft.Icons.MERGE,
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("🔗 Fusión de PDFs", size=18, weight=ft.FontWeight.W_600),
                                ft.Text("Combina múltiples archivos PDF en uno solo."),
                                ft.Container(height=20),
                                ft.ElevatedButton(
                                    text="Seleccionar Múltiples PDFs",
                                    icon=ft.Icons.FOLDER_OPEN,
                                    bgcolor="#2563eb",
                                    color="white",
                                    on_click=lambda _: show_message("Función de fusión de archivos")
                                )
                            ], spacing=10),
                            padding=ft.padding.all(20)
                        )
                    ),
                    ft.Tab(
                        text="Dividir",
                        icon=ft.Icons.CONTENT_CUT,
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("✂️ División de PDFs", size=18, weight=ft.FontWeight.W_600),
                                ft.Text("Extrae páginas específicas de un archivo PDF."),
                                ft.Container(height=20),
                                ft.ElevatedButton(
                                    text="Seleccionar PDF",
                                    icon=ft.Icons.FOLDER_OPEN,
                                    bgcolor="#2563eb",
                                    color="white",
                                    on_click=lambda _: show_message("Función de división de archivos")
                                ),
                                ft.Container(height=10),
                                ft.Row([
                                    ft.TextField(
                                        label="Página inicial",
                                        value="1",
                                        width=120
                                    ),
                                    ft.TextField(
                                        label="Página final",
                                        hint_text="Opcional",
                                        width=120
                                    )
                                ], spacing=10)
                            ], spacing=10),
                            padding=ft.padding.all(20)
                        )
                    )
                ],
                expand=True
            ),
            
            # Botones de acción
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(
                        text="Procesar",
                        icon=ft.Icons.PLAY_ARROW,
                        bgcolor="#10b981",
                        color="white",
                        on_click=lambda _: show_message("Iniciando procesamiento...")
                    ),
                    ft.ElevatedButton(
                        text="Limpiar",
                        icon=ft.Icons.CLEAR,
                        bgcolor="#6b7280",
                        color="white",
                        on_click=lambda _: show_message("Limpiando selección...")
                    ),
                    ft.ElevatedButton(
                        text="Configuración",
                        icon=ft.Icons.SETTINGS,
                        bgcolor="#8b5cf6",
                        color="white",
                        on_click=lambda _: show_message("Abriendo configuración...")
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
                padding=ft.padding.all(20)
            ),
            
            # Estado
            ft.Container(
                content=ft.Text(
                    "✅ Aplicación lista para usar",
                    size=14,
                    color="#10b981",
                    text_align=ft.TextAlign.CENTER
                ),
                padding=ft.padding.all(10),
                bgcolor="#f0fdf4",
                border_radius=8,
                margin=ft.margin.symmetric(horizontal=10)
            )
        ], expand=True)
    )
    
    def show_message(message: str):
        """Mostrar mensaje de prueba"""
        page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor="#2563eb"
            )
        )

if __name__ == "__main__":
    print("🧪 Ejecutando prueba simple de la interfaz...")
    ft.app(target=main, view=ft.AppView.FLET_APP)

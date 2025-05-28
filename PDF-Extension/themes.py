# themes.py - Sistema de temas moderno para HYDRA21 PDF Compressor
import flet as ft

class ModernThemes:
    """Sistema de temas minimalista blanco y negro"""
    
    @staticmethod
    def get_light_theme():
        """Tema claro - minimalista blanco"""
        return {
            # Colores principales
            'primary': '#000000',
            'primary_variant': '#333333',
            'secondary': '#666666',
            
            # Colores de superficie
            'background': '#ffffff',
            'surface': '#f8f9fa',
            'surface_variant': '#f1f3f4',
            
            # Colores de texto
            'on_background': '#000000',
            'on_surface': '#202124',
            'on_surface_variant': '#5f6368',
            
            # Estados
            'success': '#000000',
            'success_bg': '#f0f0f0',
            'error': '#000000',
            'error_bg': '#f5f5f5',
            'warning': '#333333',
            'warning_bg': '#f9f9f9',
            
            # Bordes y divisores
            'border': '#e0e0e0',
            'border_variant': '#dadce0',
            'divider': '#f0f0f0',
            
            # Efectos
            'shadow': '#00000010',
            'hover': '#f5f5f5',
            'pressed': '#e8e8e8',
            
            # Específicos para componentes
            'card_bg': '#ffffff',
            'card_border': '#e8eaed',
            'button_primary_bg': '#000000',
            'button_primary_text': '#ffffff',
            'button_secondary_bg': '#f8f9fa',
            'button_secondary_text': '#000000',
            'input_bg': '#ffffff',
            'input_border': '#dadce0',
            'input_focused_border': '#000000',
        }
    @staticmethod
    def get_dark_theme():
        """Tema oscuro - minimalista negro"""
        return {
            # Colores principales
            'primary': '#4285f4',
            'primary_variant': '#3367d6',
            'secondary': '#9aa0a6',
            
            # Colores de superficie
            'background': '#121212',
            'surface': '#1e1e1e',
            'surface_variant': '#2d2d2d',
            
            # Colores de texto
            'on_background': '#ffffff',
            'on_surface': '#ffffff',
            'on_surface_variant': '#b3b3b3',
            
            # Estados
            'success': '#34a853',
            'success_bg': '#1a2e1a',
            'error': '#ea4335',
            'error_bg': '#2e1a1a',
            'warning': '#fbbc04',
            'warning_bg': '#2e2a1a',
            
            # Bordes y divisores
            'border': '#404040',
            'border_variant': '#333333',
            'divider': '#333333',
            
            # Efectos
            'shadow': '#00000050',
            'hover': '#333333',
            'pressed': '#404040',
            
            # Específicos para componentes
            'card_bg': '#1e1e1e',
            'card_border': '#333333',
            'button_primary_bg': '#4285f4',
            'button_primary_text': '#ffffff',
            'button_secondary_bg': '#333333',
            'button_secondary_text': '#ffffff',
            'input_bg': '#2d2d2d',
            'input_border': '#404040',
            'input_focused_border': '#4285f4',
        }

class ThemeManager:
    """Gestor de temas para la aplicación"""
    
    def __init__(self):
        self.is_dark = False
        self.current_theme = ModernThemes.get_light_theme()
    
    def toggle_theme(self):
        """Alternar entre tema claro y oscuro"""
        self.is_dark = not self.is_dark
        self.current_theme = ModernThemes.get_dark_theme() if self.is_dark else ModernThemes.get_light_theme()
        return self.current_theme
    
    def get_theme(self):
        """Obtener tema actual"""
        return self.current_theme
    
    def set_dark_theme(self, is_dark: bool):
        """Establecer tema específico"""
        self.is_dark = is_dark
        self.current_theme = ModernThemes.get_dark_theme() if is_dark else ModernThemes.get_light_theme()
        return self.current_theme

def create_modern_button(text: str, icon: str = None, on_click=None, 
                        style: str = "primary", width=None, height=48, theme=None, small=False):
    """Crear botón moderno minimalista"""
    if not theme:
        theme = ModernThemes.get_light_theme()
    
    # Determinar estilo
    if style == "primary":
        bg_color = theme['button_primary_bg']
        text_color = theme['button_primary_text']
        border_color = theme['button_primary_bg']
    elif style == "secondary":
        bg_color = theme['button_secondary_bg']
        text_color = theme['button_secondary_text']
        border_color = theme['border']
    else:  # outline
        bg_color = "transparent"
        text_color = theme['on_surface']
        border_color = theme['border']
    
    # Tamaño según si es pequeño o normal
    text_size = 12 if small else 14
    icon_size = 16 if small else 20
    padding_h = 8 if small else 16
    padding_v = 6 if small else 12
    button_height = 32 if small else height
    spacing = 4 if small else 8
    
    # Contenido del botón
    content = []
    if icon:
        content.append(ft.Icon(icon, color=text_color, size=icon_size))
    content.append(ft.Text(text, color=text_color, size=text_size, weight=ft.FontWeight.W_500))
    
    return ft.Container(
        content=ft.Row(
            content,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=spacing,
        ),
        bgcolor=bg_color,
        border=ft.border.all(1, border_color),
        border_radius=8,
        padding=ft.padding.symmetric(horizontal=padding_h, vertical=padding_v),
        width=width,
        height=button_height,
        on_click=on_click,
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
    )

def create_modern_card(content: list, theme=None, padding=None, margin=None, border_radius=None, width=None, height=None):
    """Crear tarjeta moderna minimalista"""
    if not theme:
        theme = ModernThemes.get_light_theme()
    
    # Usar valores por defecto si no se especifican
    card_padding = padding if padding is not None else ft.padding.all(16)
    card_margin = margin if margin is not None else ft.margin.all(0) 
    card_border_radius = border_radius if border_radius is not None else 12

    return ft.Container(
        content=ft.Column(
            content,
            spacing=10,
            tight=True
        ),
        padding=card_padding,
        margin=card_margin,
        bgcolor=theme['card_bg'],
        border=ft.border.all(1, theme['card_border']),
        border_radius=card_border_radius,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=theme['shadow'],
            offset=ft.Offset(0, 2)
        ),
        width=width,
        height=height
    )

def create_drop_zone(on_click=None, theme=None):
    """Crear zona de arrastre minimalista"""
    if not theme:
        theme = ModernThemes.get_light_theme()
    
    return ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Icon(
                    "upload_file_outlined",
                    size=48,
                    color=theme['on_surface_variant']
                ),
                margin=ft.margin.only(bottom=16)
            ),
            ft.Text(
                "Selecciona o arrastra tu archivo PDF",
                size=16,
                weight=ft.FontWeight.W_500,
                color=theme['on_surface'],
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                "Formatos soportados: PDF",
                size=14,
                color=theme['on_surface_variant'],
                text_align=ft.TextAlign.CENTER
            )
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8),
        border=ft.border.all(2, theme['border_variant']),
        border_radius=12,
        padding=48,
        bgcolor=theme['surface'],
        on_click=on_click,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    )

def create_file_info_card(file_name: str = "", file_size: str = "", 
                         on_remove=None, theme=None):
    """Crear tarjeta de información de archivo"""
    if not theme:
        theme = ModernThemes.get_light_theme()
    
    return ft.Container(
        content=ft.Row([
            # Icono del archivo
            ft.Container(
                content=ft.Icon("description", color=theme['on_surface'], size=24),
                bgcolor=theme['surface_variant'],
                border_radius=8,
                padding=12,
                width=48,
                height=48
            ),
            # Información del archivo
            ft.Column([
                ft.Text(
                    file_name,
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=theme['on_surface'],
                    overflow=ft.TextOverflow.ELLIPSIS
                ),
                ft.Text(
                    file_size,
                    size=12,
                    color=theme['on_surface_variant']
                )
            ], spacing=4, expand=True),
            # Botón de eliminar
            ft.IconButton(
                icon="close",
                icon_color=theme['on_surface_variant'],
                icon_size=20,
                on_click=on_remove,
                tooltip="Quitar archivo"
            )
        ], spacing=12),
        bgcolor=theme['surface'],
        border=ft.border.all(1, theme['border']),
        border_radius=8,
        padding=16,
        animate_opacity=ft.Animation(200)
    )

def create_progress_indicator(theme=None):
    """Crear indicador de progreso moderno"""
    if not theme:
        theme = ModernThemes.get_light_theme()
    
    return ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.ProgressRing(
                    width=48,
                    height=48,
                    stroke_width=4,
                    color=theme['primary']
                ),
                alignment=ft.alignment.center,
                margin=ft.margin.only(bottom=16)
            ),
            ft.Text(
                "Procesando archivo...",
                size=16,
                weight=ft.FontWeight.W_500,
                color=theme['on_surface'],
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                "Este proceso puede tomar unos momentos",
                size=14,
                color=theme['on_surface_variant'],
                text_align=ft.TextAlign.CENTER
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8),
        padding=32,
        alignment=ft.alignment.center
    )

def create_header(title="HYDRA21", subtitle="PDF Compressor", 
                 on_help_click=None, theme=None):
    """Crear header moderno"""
    if not theme:
        theme = ModernThemes.get_light_theme()
    
    return ft.Container(
        content=ft.Row([
            # Título
            ft.Column([
                ft.Text(
                    title,
                    size=24,
                    weight=ft.FontWeight.W700,
                    color=theme['on_surface']
                ),
                ft.Text(
                    subtitle,
                    size=14,
                    color=theme['on_surface_variant']
                )
            ], spacing=4),
            # Spacer
            ft.Container(expand=True),
            # Botón de ayuda
            ft.IconButton(
                icon="help_outline",
                icon_color=theme['on_surface_variant'],
                icon_size=24,
                on_click=on_help_click,
                tooltip="Ayuda"
            )
        ]),
        padding=ft.padding.all(24),
        border=ft.border.only(bottom=ft.BorderSide(1, theme['divider']))
    )
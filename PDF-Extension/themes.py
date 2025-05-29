# themes_improved.py - Sistema de temas mejorado para HYDRA21 PDF Compressor
"""
Sistema de temas mejorado con:
- Más colores y variantes
- Componentes modernos mejorados
- Animaciones y efectos visuales
- Mejor accesibilidad
"""

import flet as ft
from typing import Dict, Any, Optional, List

class ModernThemes:
    """Temas modernos mejorados para la aplicación"""
    
    LIGHT_THEME = {
        # Colores principales
        'primary': '#2563eb',           # Azul moderno
        'primary_variant': '#1d4ed8',   
        'secondary': '#7c3aed',         # Púrpura
        'accent': '#059669',            # Verde esmeralda
        
        # Fondos
        'background': '#f8fafc',        # Gris muy claro
        'surface': '#ffffff',           # Blanco puro
        'surface_variant': '#f1f5f9',   # Gris claro
        'surface_container': '#e2e8f0', # Gris medio claro
        
        # Textos
        'on_surface': '#0f172a',        # Negro suave
        'on_surface_variant': '#64748b', # Gris medio
        'on_primary': '#ffffff',        # Blanco
        'on_background': '#1e293b',     # Gris oscuro suave
        
        # Estados
        'success': '#059669',           # Verde
        'warning': '#f59e0b',           # Ámbar
        'error': '#dc2626',             # Rojo
        'info': '#3b82f6',              # Azul
        
        # Contenedores de estado
        'success_container': '#ecfdf5',
        'warning_container': '#fffbeb',
        'error_container': '#fef2f2',
        'info_container': '#eff6ff',
        
        # Bordes y divisores
        'border': '#e2e8f0',
        'border_variant': '#cbd5e1',
        'divider': '#e2e8f0',
        
        # Botones
        'button_primary_bg': '#2563eb',
        'button_primary_hover': '#1d4ed8',
        'button_secondary_bg': '#f1f5f9',
        'button_secondary_hover': '#e2e8f0',
        
        # Inputs
        'input_border': '#d1d5db',
        'input_focused_border': '#2563eb',
        'input_bg': '#ffffff',
        
        # Sombras
        'shadow': 'rgba(0, 0, 0, 0.1)',
        'shadow_elevated': 'rgba(0, 0, 0, 0.15)',
        
        # Overlays
        'overlay_light': 'rgba(255, 255, 255, 0.8)',
        'overlay_dark': 'rgba(0, 0, 0, 0.3)',
    }
    
    DARK_THEME = {
        # Colores principales
        'primary': '#3b82f6',           
        'primary_variant': '#2563eb',   
        'secondary': '#8b5cf6',         
        'accent': '#10b981',            
        
        # Fondos
        'background': '#0f172a',        # Azul muy oscuro
        'surface': '#1e293b',           # Azul oscuro
        'surface_variant': '#334155',   # Azul gris
        'surface_container': '#475569', # Azul gris claro
        
        # Textos
        'on_surface': '#f1f5f9',        # Blanco suave
        'on_surface_variant': '#94a3b8', # Gris claro
        'on_primary': '#ffffff',        # Blanco
        'on_background': '#e2e8f0',     # Gris muy claro
        
        # Estados
        'success': '#10b981',           
        'warning': '#fbbf24',           
        'error': '#ef4444',             
        'info': '#3b82f6',              
        
        # Contenedores de estado
        'success_container': '#064e3b',
        'warning_container': '#92400e',
        'error_container': '#991b1b',
        'info_container': '#1e3a8a',
        
        # Bordes y divisores
        'border': '#334155',
        'border_variant': '#475569',
        'divider': '#334155',
        
        # Botones
        'button_primary_bg': '#3b82f6',
        'button_primary_hover': '#2563eb',
        'button_secondary_bg': '#334155',
        'button_secondary_hover': '#475569',
        
        # Inputs
        'input_border': '#475569',
        'input_focused_border': '#3b82f6',
        'input_bg': '#1e293b',
        
        # Sombras
        'shadow': 'rgba(0, 0, 0, 0.3)',
        'shadow_elevated': 'rgba(0, 0, 0, 0.5)',
        
        # Overlays
        'overlay_light': 'rgba(255, 255, 255, 0.1)',
        'overlay_dark': 'rgba(0, 0, 0, 0.6)',
    }

class ThemeManager:
    """Gestor de temas mejorado"""
    
    def __init__(self):
        self.is_dark = False
        self._listeners = []
    
    def get_theme(self) -> Dict[str, str]:
        """Obtener tema actual"""
        return ModernThemes.DARK_THEME if self.is_dark else ModernThemes.LIGHT_THEME
    
    def toggle_theme(self):
        """Cambiar entre tema claro y oscuro"""
        self.is_dark = not self.is_dark
        self._notify_listeners()
    
    def set_theme(self, is_dark: bool):
        """Establecer tema específico"""
        if self.is_dark != is_dark:
            self.is_dark = is_dark
            self._notify_listeners()
    
    def add_listener(self, callback):
        """Agregar listener para cambios de tema"""
        self._listeners.append(callback)
    
    def remove_listener(self, callback):
        """Remover listener"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self):
        """Notificar cambios de tema"""
        for callback in self._listeners:
            try:
                callback(self.get_theme())
            except Exception as e:
                print(f"Error in theme listener: {e}")

def create_modern_button(
    text: str,
    icon: Optional[str] = None,
    on_click=None,
    style: str = "primary",
    theme: Dict[str, str] = None,
    disabled: bool = False,
    width: Optional[float] = None,
    height: float = 45
) -> ft.Container:
    """Crear botón moderno mejorado con animaciones"""
    
    if theme is None:
        theme = ModernThemes.LIGHT_THEME
    
    # Configurar estilos según el tipo
    if style == "primary":
        bg_color = theme['button_primary_bg']
        text_color = theme['on_primary']
        hover_color = theme['button_primary_hover']
        border_color = None
    elif style == "secondary":
        bg_color = theme['button_secondary_bg']
        text_color = theme['on_surface']
        hover_color = theme['button_secondary_hover']
        border_color = theme['border']
    elif style == "accent":
        bg_color = theme['accent']
        text_color = theme['on_primary']
        hover_color = theme['primary']
        border_color = None
    else:  # outline
        bg_color = "transparent"
        text_color = theme['primary']
        hover_color = theme['surface_variant']
        border_color = theme['primary']
    
    # Si está deshabilitado
    if disabled:
        bg_color = theme['surface_variant']
        text_color = theme['on_surface_variant']
        border_color = theme['border_variant']
    
    # Crear contenido del botón
    button_content = []
    
    if icon:
        button_content.append(
            ft.Icon(icon, color=text_color, size=18)
        )
    
    button_content.append(
        ft.Text(
            text,
            size=14,
            weight=ft.FontWeight.W_500,
            color=text_color
        )
    )
    
    # Crear botón con animaciones
    button = ft.Container(
        content=ft.Row(
            button_content,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            tight=True
        ),
        bgcolor=bg_color,
        border=ft.border.all(1, border_color) if border_color else None,
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        alignment=ft.alignment.center,
        on_click=on_click if not disabled else None,
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=4 if style == "primary" else 2,
            color=theme['shadow'],
            offset=ft.Offset(0, 2)
        ) if not disabled else None,
        height=height,
        width=width,
        tooltip=text if len(text) > 15 else None
    )
    
    return button

def create_modern_card(
    content: list,
    theme: Dict[str, str] = None,
    padding: ft.Padding = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    elevation: int = 1
) -> ft.Container:
    """Crear tarjeta moderna mejorada"""
    
    if theme is None:
        theme = ModernThemes.LIGHT_THEME
    
    if padding is None:
        padding = ft.padding.all(20)
    
    # Configurar sombra según elevación
    if elevation == 0:
        shadow = None
    elif elevation == 1:
        shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=6,
            color=theme['shadow'],
            offset=ft.Offset(0, 2)
        )
    else:  # elevation >= 2
        shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=12,
            color=theme['shadow_elevated'],
            offset=ft.Offset(0, 4)
        )
    
    return ft.Container(
        content=ft.Column(
            content,
            spacing=8,
            tight=True
        ),
        bgcolor=theme['surface'],
        border_radius=12,
        padding=padding,
        shadow=shadow,
        border=ft.border.all(1, theme['border']),
        width=width,
        height=height,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    )

def create_modern_input(
    label: str,
    value: str = "",
    hint_text: str = "",
    prefix_icon: Optional[str] = None,
    suffix_icon: Optional[str] = None,
    on_change=None,
    multiline: bool = False,
    password: bool = False,
    theme: Dict[str, str] = None,
    width: Optional[float] = None
) -> ft.TextField:
    """Crear campo de entrada moderno"""
    
    if theme is None:
        theme = ModernThemes.LIGHT_THEME
    
    return ft.TextField(
        label=label,
        value=value,
        hint_text=hint_text,
        prefix_icon=prefix_icon,
        suffix_icon=suffix_icon,
        on_change=on_change,
        multiline=multiline,
        password=password,
        filled=True,
        bgcolor=theme['input_bg'],
        border_color=theme['input_border'],
        focused_border_color=theme['input_focused_border'],
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        label_style=ft.TextStyle(
            color=theme['on_surface_variant'],
            size=14
        ),
        text_style=ft.TextStyle(
            color=theme['on_surface'],
            size=14
        ),
        width=width
    )

def create_modern_dropdown(
    label: str,
    options: list,
    value: Optional[str] = None,
    on_change=None,
    theme: Dict[str, str] = None,
    width: Optional[float] = None
) -> ft.Dropdown:
    """Crear dropdown moderno"""
    
    if theme is None:
        theme = ModernThemes.LIGHT_THEME
    
    return ft.Dropdown(
        label=label,
        value=value,
        options=[ft.dropdown.Option(opt) if isinstance(opt, str) else opt for opt in options],
        on_change=on_change,
        filled=True,
        bgcolor=theme['input_bg'],
        border_color=theme['input_border'],
        focused_border_color=theme['input_focused_border'],
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=8),
        label_style=ft.TextStyle(
            color=theme['on_surface_variant'],
            size=14
        ),
        text_style=ft.TextStyle(
            color=theme['on_surface'],
            size=14,
            weight=ft.FontWeight.W_500
        ),
        width=width
    )

def create_status_chip(
    text: str,
    status: str = "info",  # info, success, warning, error
    theme: Dict[str, str] = None,
    icon: Optional[str] = None
) -> ft.Container:
    """Crear chip de estado moderno"""
    
    if theme is None:
        theme = ModernThemes.LIGHT_THEME
    
    # Configurar colores según estado
    status_colors = {
        'info': (theme['info'], theme['info_container'], theme['on_primary']),
        'success': (theme['success'], theme['success_container'], theme['on_primary']),
        'warning': (theme['warning'], theme['warning_container'], theme['on_primary']),
        'error': (theme['error'], theme['error_container'], theme['on_primary'])
    }
    
    bg_color, container_color, text_color = status_colors.get(status, status_colors['info'])
    
    content = []
    if icon:
        content.append(ft.Icon(icon, color=text_color, size=16))
    content.append(ft.Text(text, color=text_color, size=12, weight=ft.FontWeight.W_500))
    
    return ft.Container(
        content=ft.Row(
            content,
            spacing=4,
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER
        ),
        bgcolor=bg_color,
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
    )

def create_loading_overlay(
    message: str = "Cargando...",
    theme: Dict[str, str] = None
) -> ft.Container:
    """Crear overlay de carga moderno"""
    
    if theme is None:
        theme = ModernThemes.LIGHT_THEME
    
    return ft.Container(
        content=ft.Column([
            ft.ProgressRing(
                width=50,
                height=50,
                stroke_width=4,
                color=theme['primary']
            ),
            ft.Container(height=20),
            ft.Text(
                message,
                size=16,
                color=theme['on_surface'],
                text_align=ft.TextAlign.CENTER
            )
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=theme['overlay_light'],
        alignment=ft.alignment.center,
        expand=True,
        animate_opacity=300
    )

def create_modern_dialog(
    title: str,
    content: ft.Control,
    actions: List[ft.Control] = None,
    theme: Dict[str, str] = None,
    width: float = 400
) -> ft.AlertDialog:
    """Crear diálogo moderno"""
    
    if theme is None:
        theme = ModernThemes.LIGHT_THEME
    
    return ft.AlertDialog(
        title=ft.Text(
            title,
            size=18,
            weight=ft.FontWeight.W_600,
            color=theme['on_surface']
        ),
        content=ft.Container(
            content=content,
            width=width,
            padding=ft.padding.symmetric(vertical=10)
        ),
        actions=actions or [],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=theme['surface'],
        title_padding=ft.padding.all(20),
        content_padding=ft.padding.symmetric(horizontal=20, vertical=10),
        actions_padding=ft.padding.all(20),
        shape=ft.RoundedRectangleBorder(radius=12),
        modal=True
    )

def create_animated_icon_button(
    icon: str,
    on_click=None,
    tooltip: str = "",
    theme: Dict[str, str] = None,
    size: float = 24
) -> ft.IconButton:
    """Crear botón de icono animado"""
    
    if theme is None:
        theme = ModernThemes.LIGHT_THEME
    
    return ft.IconButton(
        icon=icon,
        icon_color=theme['on_surface'],
        icon_size=size,
        tooltip=tooltip,
        on_click=on_click,
        style=ft.ButtonStyle(
            shape=ft.CircleBorder(),
            bgcolor=theme['surface_variant'],
            overlay_color={
                ft.MaterialState.HOVERED: theme['overlay_light'],
                ft.MaterialState.PRESSED: theme['overlay_dark']
            },
            animation_duration=150
        )
    )

# Función para aplicar tema global a la página
def apply_global_theme(page: ft.Page, theme_manager: ThemeManager):
    """Aplicar tema global a la página"""
    theme = theme_manager.get_theme()
    
    page.theme_mode = ft.ThemeMode.DARK if theme_manager.is_dark else ft.ThemeMode.LIGHT
    page.bgcolor = theme['background']
    
    # Configurar tema personalizado si es necesario
    if hasattr(page, 'theme'):
        page.theme = ft.Theme(
            color_scheme_seed=theme['primary'],
            use_material3=True
        )
    
    page.update()

# Constantes para animaciones
ANIMATION_DURATIONS = {
    'fast': 150,
    'normal': 300,
    'slow': 500
}

ANIMATION_CURVES = {
    'ease': ft.AnimationCurve.EASE,
    'ease_in': ft.AnimationCurve.EASE_IN,
    'ease_out': ft.AnimationCurve.EASE_OUT,
    'ease_in_out': ft.AnimationCurve.EASE_IN_OUT,
    'bounce': ft.AnimationCurve.BOUNCE_OUT
}
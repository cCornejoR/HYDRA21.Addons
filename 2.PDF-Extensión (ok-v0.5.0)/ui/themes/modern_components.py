"""
Modern UI components for HYDRA21 PDF Compressor
Creates consistent, modern UI elements without shadows (per user preference)
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any

def create_modern_button(
    text: str,
    icon: Optional[str] = None,
    on_click: Optional[Callable] = None,
    style: str = "primary",
    theme: Dict[str, str] = None,
    disabled: bool = False,
    width: Optional[float] = None,
    height: float = 45
) -> ft.Container:
    """Create modern button without shadows"""
    
    if theme is None:
        # Default light theme colors
        theme = {
            'button_primary_bg': '#2563eb',
            'button_primary_hover': '#1d4ed8',
            'button_secondary_bg': '#f1f5f9',
            'button_secondary_hover': '#e2e8f0',
            'on_primary': '#ffffff',
            'on_surface': '#0f172a',
            'primary': '#2563eb',
            'surface_variant': '#f1f5f9',
            'border': '#e2e8f0'
        }
    
    # Configure style colors
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
        bg_color = theme.get('accent', theme['primary'])
        text_color = theme['on_primary']
        hover_color = theme['button_primary_hover']
        border_color = None
    else:  # outline
        bg_color = "transparent"
        text_color = theme['primary']
        hover_color = theme['surface_variant']
        border_color = theme['primary']
    
    # Handle disabled state
    if disabled:
        bg_color = theme['surface_variant']
        text_color = theme.get('on_surface_variant', theme['on_surface'])
        border_color = theme.get('border_variant', theme['border'])
    
    # Create button content
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
    
    return ft.Container(
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
        height=height,
        width=width,
        tooltip=text if len(text) > 15 else None
    )

def create_modern_card(
    content: List[ft.Control],
    theme: Dict[str, str] = None,
    padding: ft.Padding = None,
    width: Optional[float] = None,
    height: Optional[float] = None
) -> ft.Container:
    """Create modern card without shadows"""
    
    if theme is None:
        theme = {
            'surface': '#ffffff',
            'border': '#e2e8f0'
        }
    
    if padding is None:
        padding = ft.padding.all(20)
    
    return ft.Container(
        content=ft.Column(
            content,
            spacing=12,
            tight=True
        ),
        bgcolor=theme['surface'],
        border_radius=12,
        padding=padding,
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
    on_change: Optional[Callable] = None,
    multiline: bool = False,
    password: bool = False,
    theme: Dict[str, str] = None,
    width: Optional[float] = None
) -> ft.TextField:
    """Create modern input field"""
    
    if theme is None:
        theme = {
            'input_bg': '#ffffff',
            'input_border': '#d1d5db',
            'input_focused_border': '#2563eb',
            'on_surface_variant': '#64748b',
            'on_surface': '#0f172a'
        }
    
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
    options: List[ft.dropdown.Option],
    value: Optional[str] = None,
    on_change: Optional[Callable] = None,
    theme: Dict[str, str] = None,
    width: Optional[float] = None
) -> ft.Dropdown:
    """Create modern dropdown"""
    
    if theme is None:
        theme = {
            'input_bg': '#ffffff',
            'input_border': '#d1d5db',
            'input_focused_border': '#2563eb',
            'on_surface_variant': '#64748b',
            'on_surface': '#0f172a'
        }
    
    return ft.Dropdown(
        label=label,
        value=value,
        options=options,
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
    status: str = "info",
    theme: Dict[str, str] = None,
    icon: Optional[str] = None
) -> ft.Container:
    """Create status chip"""
    
    if theme is None:
        theme = {
            'info': '#3b82f6',
            'success': '#059669',
            'warning': '#f59e0b',
            'error': '#dc2626',
            'on_primary': '#ffffff'
        }
    
    # Get status color
    status_colors = {
        'info': theme['info'],
        'success': theme['success'],
        'warning': theme['warning'],
        'error': theme['error']
    }
    
    bg_color = status_colors.get(status, theme['info'])
    text_color = theme['on_primary']
    
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

def create_progress_indicator(
    message: str = "Procesando...",
    progress: Optional[float] = None,
    theme: Dict[str, str] = None,
    show_spinner: bool = True
) -> ft.Container:
    """Create progress indicator with spinner and/or progress bar"""
    
    if theme is None:
        theme = {
            'primary': '#2563eb',
            'on_surface': '#0f172a',
            'surface': '#ffffff'
        }
    
    content = []
    
    if show_spinner:
        content.append(
            ft.ProgressRing(
                width=40,
                height=40,
                stroke_width=4,
                color=theme['primary']
            )
        )
    
    if progress is not None:
        content.append(
            ft.ProgressBar(
                value=progress / 100 if progress > 1 else progress,
                width=300,
                height=8,
                color=theme['primary'],
                bgcolor=theme.get('surface_variant', '#f1f5f9')
            )
        )
        content.append(
            ft.Text(
                f"{progress:.1f}%" if progress > 1 else f"{progress * 100:.1f}%",
                size=14,
                color=theme['on_surface'],
                weight=ft.FontWeight.W_500
            )
        )
    
    content.append(
        ft.Text(
            message,
            size=16,
            color=theme['on_surface'],
            text_align=ft.TextAlign.CENTER
        )
    )
    
    return ft.Container(
        content=ft.Column(
            content,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.all(20)
    )

def create_file_info_card(
    filename: str,
    file_path: str,
    file_size: str,
    theme: Dict[str, str] = None,
    status: str = "info",
    additional_info: Optional[str] = None
) -> ft.Container:
    """Create file information card"""
    
    if theme is None:
        theme = {
            'surface': '#ffffff',
            'border': '#e2e8f0',
            'on_surface': '#0f172a',
            'on_surface_variant': '#64748b'
        }
    
    content = [
        ft.Row([
            ft.Icon(ft.Icons.PICTURE_AS_PDF, color=theme.get('primary', '#2563eb'), size=24),
            ft.Column([
                ft.Text(
                    filename,
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=theme['on_surface']
                ),
                ft.Text(
                    file_size,
                    size=12,
                    color=theme['on_surface_variant']
                )
            ], spacing=2, expand=True),
            create_status_chip("", status, theme)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Text(
            file_path,
            size=11,
            color=theme['on_surface_variant'],
            overflow=ft.TextOverflow.ELLIPSIS
        )
    ]
    
    if additional_info:
        content.append(
            ft.Text(
                additional_info,
                size=12,
                color=theme['on_surface_variant']
            )
        )
    
    return create_modern_card(content, theme, ft.padding.all(16))

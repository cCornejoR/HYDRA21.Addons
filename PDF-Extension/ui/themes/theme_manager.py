"""
Theme management for HYDRA21 PDF Compressor
Handles light/dark theme switching with blue color scheme
"""

import flet as ft
import json
from pathlib import Path
from typing import Dict, List, Callable, Optional
from config.settings import THEME_CONFIG

class ThemeManager:
    """Manages application themes and theme switching"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_file = config_dir / "theme_config.json"
        self._is_dark = False
        self._listeners: List[Callable] = []
        self._load_theme_preference()
    
    def _load_theme_preference(self):
        """Load theme preference from configuration file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self._is_dark = config.get('is_dark', False)
            except Exception as e:
                print(f"Error loading theme preference: {e}")
                self._is_dark = False
    
    def _save_theme_preference(self):
        """Save theme preference to configuration file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            config = {'is_dark': self._is_dark}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving theme preference: {e}")
    
    @property
    def is_dark(self) -> bool:
        """Check if dark theme is active"""
        return self._is_dark
    
    @property
    def theme_name(self) -> str:
        """Get current theme name"""
        return "dark" if self._is_dark else "light"
    
    def get_theme(self) -> Dict[str, str]:
        """Get current theme colors"""
        return THEME_CONFIG["dark" if self._is_dark else "light"]
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self._is_dark = not self._is_dark
        self._save_theme_preference()
        self._notify_listeners()
    
    def set_theme(self, is_dark: bool):
        """Set specific theme"""
        if self._is_dark != is_dark:
            self._is_dark = is_dark
            self._save_theme_preference()
            self._notify_listeners()
    
    def add_listener(self, callback: Callable[[Dict[str, str]], None]):
        """Add theme change listener"""
        self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable[[Dict[str, str]], None]):
        """Remove theme change listener"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self):
        """Notify all listeners of theme change"""
        theme = self.get_theme()
        for callback in self._listeners:
            try:
                callback(theme)
            except Exception as e:
                print(f"Error in theme listener: {e}")
    
    def apply_to_page(self, page: ft.Page):
        """Apply current theme to Flet page"""
        theme = self.get_theme()
        
        # Set theme mode
        page.theme_mode = ft.ThemeMode.DARK if self._is_dark else ft.ThemeMode.LIGHT
        
        # Set background color
        page.bgcolor = theme['background']
        
        # Configure custom theme with blue color scheme
        page.theme = ft.Theme(
            color_scheme_seed=theme['primary'],
            use_material3=True
        )
        
        # Update page
        page.update()
    
    def get_color(self, color_key: str) -> str:
        """Get specific color from current theme"""
        theme = self.get_theme()
        return theme.get(color_key, theme.get('primary', '#2563eb'))
    
    def get_text_color(self, surface_type: str = 'surface') -> str:
        """Get appropriate text color for surface type"""
        theme = self.get_theme()
        if surface_type == 'primary':
            return theme['on_primary']
        elif surface_type == 'background':
            return theme['on_background']
        else:
            return theme['on_surface']
    
    def get_status_colors(self, status: str) -> Dict[str, str]:
        """Get colors for status indicators"""
        theme = self.get_theme()
        
        status_map = {
            'success': {
                'color': theme['success'],
                'container': theme['success_container'],
                'text': theme['on_primary']
            },
            'warning': {
                'color': theme['warning'],
                'container': theme['warning_container'],
                'text': theme['on_primary']
            },
            'error': {
                'color': theme['error'],
                'container': theme['error_container'],
                'text': theme['on_primary']
            },
            'info': {
                'color': theme['info'],
                'container': theme['info_container'],
                'text': theme['on_primary']
            }
        }
        
        return status_map.get(status, status_map['info'])
    
    def create_theme_toggle_button(self, on_click: Optional[Callable] = None) -> ft.IconButton:
        """Create theme toggle button"""
        def handle_toggle(e):
            self.toggle_theme()
            if on_click:
                on_click(e)
        
        theme = self.get_theme()
        
        return ft.IconButton(
            icon=ft.Icons.DARK_MODE if not self._is_dark else ft.Icons.LIGHT_MODE,
            icon_color=theme['on_surface'],
            tooltip="Cambiar tema" if not self._is_dark else "Cambiar a tema claro",
            on_click=handle_toggle,
            style=ft.ButtonStyle(
                shape=ft.CircleBorder(),
                bgcolor=theme['surface_variant']
            )
        )
    
    def get_theme_info(self) -> Dict:
        """Get current theme information"""
        return {
            "is_dark": self._is_dark,
            "theme_name": self.theme_name,
            "primary_color": self.get_color('primary'),
            "background_color": self.get_color('background'),
            "surface_color": self.get_color('surface')
        }

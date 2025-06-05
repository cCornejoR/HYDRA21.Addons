"""
Tabbed Interface Component for HYDRA21 PDF Compressor Pro
Organizes different PDF operations in tabs
"""

import flet as ft
from typing import Dict, List, Optional, Callable, Any

class TabbedInterface(ft.Column):
    """Tabbed interface for organizing PDF operations"""
    
    def __init__(self, page: ft.Page, theme: Dict[str, str]):
        self.page = page
        self.theme = theme
        self.current_tab = 0
        
        # Tab definitions
        self.tabs = [
            {
                'id': 'compress',
                'title': 'Comprimir',
                'icon': ft.Icons.COMPRESS,
                'content': None
            },
            {
                'id': 'split',
                'title': 'Dividir',
                'icon': ft.Icons.CONTENT_CUT,
                'content': None
            },
            {
                'id': 'merge',
                'title': 'Fusionar',
                'icon': ft.Icons.MERGE,
                'content': None
            }
        ]
        
        # UI Components
        self.tab_bar = None
        self.content_container = None
        
        self._setup_ui()
        
        super().__init__(
            controls=self._build_layout(),
            spacing=0,
            expand=True
        )
    
    def _setup_ui(self):
        """Setup UI components"""
        # Create tab bar
        tab_buttons = []
        for i, tab in enumerate(self.tabs):
            is_active = i == self.current_tab

            tab_buttons.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            tab['icon'],
                            size=20,
                            color=self._get_tab_color(i)
                        ),
                        ft.Text(
                            tab['title'],
                            size=14,
                            weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_500,
                            color=self._get_tab_color(i)
                        )
                    ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(horizontal=24, vertical=14),
                    border_radius=ft.border_radius.only(top_left=12, top_right=12),
                    bgcolor=self._get_tab_bg_color(i),
                    border=ft.border.only(
                        left=ft.BorderSide(1, self._get_tab_border_color(i)),
                        right=ft.BorderSide(1, self._get_tab_border_color(i)),
                        top=ft.BorderSide(1, self._get_tab_border_color(i)),
                        bottom=ft.BorderSide(
                            3 if is_active else 1,
                            self.theme.get('primary', '#2563eb') if is_active else "transparent"
                        )
                    ),
                    on_click=lambda e, tab_index=i: self._switch_tab(tab_index),
                    expand=True,
                    # Add hover effect
                    on_hover=lambda e, tab_index=i: self._on_tab_hover(e, tab_index)
                )
            )
        
        self.tab_bar = ft.Row(
            controls=tab_buttons,
            spacing=0,
            alignment=ft.MainAxisAlignment.START
        )
        
        # Content container
        self.content_container = ft.Container(
            content=ft.Column([
                ft.Text("Selecciona una pestaña para comenzar",
                       size=16, color=self.theme.get('on_surface_variant', '#64748b'))
            ]),
            padding=32,
            expand=True,
            bgcolor=self.theme.get('surface', '#ffffff'),
            border=ft.border.all(1, self.theme.get('outline', '#e2e8f0')),
            border_radius=ft.border_radius.only(
                top_right=12, bottom_left=12, bottom_right=12
            )
        )
    
    def _build_layout(self):
        """Build the main layout"""
        return [
            # Tab bar
            ft.Container(
                content=self.tab_bar,
                bgcolor=self.theme.get('surface_variant', '#f8fafc'),
                padding=ft.padding.only(left=0, right=0, top=0, bottom=0)
            ),
            
            # Content area
            self.content_container
        ]
    
    def _get_tab_color(self, tab_index: int) -> str:
        """Get tab text/icon color"""
        if tab_index == self.current_tab:
            return self.theme.get('primary', '#2563eb')
        return self.theme.get('on_surface_variant', '#64748b')

    def _get_tab_bg_color(self, tab_index: int) -> str:
        """Get tab background color"""
        if tab_index == self.current_tab:
            return self.theme.get('surface', '#ffffff')
        return self.theme.get('surface_variant', '#f8fafc')

    def _get_tab_border_color(self, tab_index: int) -> str:
        """Get tab border color"""
        if tab_index == self.current_tab:
            return self.theme.get('outline', '#e2e8f0')
        return "transparent"

    def _get_tab_hover_color(self, tab_index: int) -> str:
        """Get tab hover background color"""
        if tab_index == self.current_tab:
            return self.theme.get('surface', '#ffffff')
        # Lighter version of surface_variant for hover
        if 'surface_variant' in self.theme:
            base_color = self.theme['surface_variant']
            if base_color == '#f8fafc':  # Light mode
                return '#f1f5f9'
            else:  # Dark mode
                return '#475569'
        return self.theme.get('surface_variant', '#f8fafc')
    
    def _switch_tab(self, tab_index: int):
        """Switch to a different tab"""
        if tab_index == self.current_tab:
            return

        self.current_tab = tab_index
        self._update_tab_appearance()
        self._update_content()

    def _on_tab_hover(self, e, tab_index: int):
        """Handle tab hover effect"""
        if tab_index == self.current_tab:
            return

        # Only apply hover effect to inactive tabs
        if hasattr(e, 'data') and e.data == "true":  # Mouse enter
            if self.tab_bar and hasattr(self.tab_bar, 'controls'):
                tab_container = self.tab_bar.controls[tab_index]
                if isinstance(tab_container, ft.Container):
                    tab_container.bgcolor = self._get_tab_hover_color(tab_index)
                    self.page.update()
        else:  # Mouse leave
            if self.tab_bar and hasattr(self.tab_bar, 'controls'):
                tab_container = self.tab_bar.controls[tab_index]
                if isinstance(tab_container, ft.Container):
                    tab_container.bgcolor = self._get_tab_bg_color(tab_index)
                    self.page.update()
    
    def _update_tab_appearance(self):
        """Update the visual appearance of tabs"""
        if not self.tab_bar or not hasattr(self.tab_bar, 'controls'):
            return

        for i, tab_container in enumerate(self.tab_bar.controls):
            if isinstance(tab_container, ft.Container):
                is_active = i == self.current_tab

                # Update colors
                tab_container.bgcolor = self._get_tab_bg_color(i)
                tab_container.border = ft.border.only(
                    left=ft.BorderSide(1, self._get_tab_border_color(i)),
                    right=ft.BorderSide(1, self._get_tab_border_color(i)),
                    top=ft.BorderSide(1, self._get_tab_border_color(i)),
                    bottom=ft.BorderSide(
                        3 if is_active else 1,
                        self.theme.get('primary', '#2563eb') if is_active else "transparent"
                    )
                )

                # Update content colors
                if hasattr(tab_container.content, 'controls'):
                    row = tab_container.content
                    for control in row.controls:
                        if isinstance(control, ft.Icon):
                            control.color = self._get_tab_color(i)
                        elif isinstance(control, ft.Text):
                            control.color = self._get_tab_color(i)
                            control.weight = ft.FontWeight.W_600 if is_active else ft.FontWeight.W_500

        if self.page:
            self.page.update()
    
    def _update_content(self):
        """Update the content area based on current tab"""
        try:
            current_tab_data = self.tabs[self.current_tab]

            if current_tab_data['content']:
                self.content_container.content = current_tab_data['content']
            else:
                # Show placeholder content
                self.content_container.content = ft.Column([
                    ft.Row([
                        ft.Icon(current_tab_data['icon'], size=48, color="#2563eb"),
                        ft.Column([
                            ft.Text(
                                f"Funcionalidad de {current_tab_data['title']}",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color="#2563eb"
                            ),
                            ft.Text(
                                "Esta funcionalidad se está cargando...",
                                size=14,
                                color=self.theme.get('on_surface_variant', '#64748b')
                            )
                        ], spacing=4, expand=True)
                    ], spacing=16, alignment=ft.MainAxisAlignment.CENTER),

                    ft.Container(height=32),

                    ft.Container(
                        content=ft.ProgressRing(width=32, height=32, color="#2563eb"),
                        alignment=ft.alignment.center
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16)

            if self.page:
                self.page.update()
        except Exception as e:
            print(f"Error updating tab content: {e}")
    
    def set_tab_content(self, tab_id: str, content: ft.Control):
        """Set content for a specific tab"""
        for tab in self.tabs:
            if tab['id'] == tab_id:
                tab['content'] = content
                
                # If this is the current tab, update the display
                if self.tabs[self.current_tab]['id'] == tab_id:
                    self._update_content()
                break
    
    def get_current_tab_id(self) -> str:
        """Get the ID of the current tab"""
        return self.tabs[self.current_tab]['id']
    
    def switch_to_tab(self, tab_id: str):
        """Switch to a tab by ID"""
        for i, tab in enumerate(self.tabs):
            if tab['id'] == tab_id:
                self._switch_tab(i)
                break
    
    def add_tab(self, tab_id: str, title: str, icon: str, content: Optional[ft.Control] = None):
        """Add a new tab"""
        new_tab = {
            'id': tab_id,
            'title': title,
            'icon': icon,
            'content': content
        }
        self.tabs.append(new_tab)
        self._rebuild_tab_bar()
    
    def remove_tab(self, tab_id: str):
        """Remove a tab"""
        for i, tab in enumerate(self.tabs):
            if tab['id'] == tab_id:
                self.tabs.pop(i)
                
                # Adjust current tab if necessary
                if self.current_tab >= len(self.tabs):
                    self.current_tab = len(self.tabs) - 1
                elif self.current_tab > i:
                    self.current_tab -= 1
                
                self._rebuild_tab_bar()
                self._update_content()
                break
    
    def _rebuild_tab_bar(self):
        """Rebuild the tab bar after adding/removing tabs"""
        self._setup_ui()
        
        # Update the layout
        if hasattr(self, 'controls') and len(self.controls) >= 2:
            self.controls[0].content = self.tab_bar
            self.controls[1] = self.content_container
        
        self.page.update()
    
    def set_theme(self, new_theme: Dict[str, str]):
        """Update the theme"""
        self.theme = new_theme
        self._update_tab_appearance()
        
        # Update content container
        self.content_container.bgcolor = self.theme.get('surface', '#ffffff')
        self.content_container.border = ft.border.all(1, self.theme.get('outline', '#e2e8f0'))
        
        self.page.update()
    
    def get_tab_count(self) -> int:
        """Get the number of tabs"""
        return len(self.tabs)
    
    def is_tab_active(self, tab_id: str) -> bool:
        """Check if a tab is currently active"""
        return self.tabs[self.current_tab]['id'] == tab_id

"""
Tutorial modal component for HYDRA21 PDF Compressor
Provides setup guidance and Ghostscript configuration help
"""

import flet as ft
from pathlib import Path
from typing import Dict, Optional, Callable, List
from config.ghostscript_config import GhostscriptConfig
from ui.themes.modern_components import create_modern_button, create_modern_card, create_modern_input, create_status_chip

class TutorialModal(ft.Container):
    """Tutorial modal for first-time setup and Ghostscript configuration"""
    
    def __init__(
        self,
        theme: Dict[str, str],
        gs_config: GhostscriptConfig,
        on_setup_complete: Optional[Callable] = None
    ):
        self.theme = theme
        self.gs_config = gs_config
        self.on_setup_complete = on_setup_complete

        self.current_step = 0
        self.total_steps = 4

        # UI components
        self.step_content = None
        self.step_indicator = None
        self.navigation_buttons = None
        self.gs_path_input = None
        self.status_text = None
        self.auto_detect_button = None
        self.verify_button = None

        # Build the modal
        self._build_modal()

        # Initialize container
        super().__init__(
            content=self.modal_content,
            alignment=ft.alignment.center,
            bgcolor=self.theme['overlay_dark'],
            expand=True,
            visible=False,
            animate_opacity=300
        )

    def _build_modal(self):
        """Build the tutorial modal"""
        # Step indicator
        self.step_indicator = ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER
        )

        # Step content container
        self.step_content = ft.Container(
            content=ft.Column([]),
            height=400,
            padding=ft.padding.all(20)
        )

        # Navigation buttons
        self.navigation_buttons = ft.Row([
            create_modern_button(
                text="Anterior",
                icon=ft.Icons.ARROW_BACK,
                on_click=self._previous_step,
                style="secondary",
                theme=self.theme
            ),
            create_modern_button(
                text="Siguiente",
                icon=ft.Icons.ARROW_FORWARD,
                on_click=self._next_step,
                style="primary",
                theme=self.theme
            ),
            create_modern_button(
                text="Finalizar",
                icon=ft.Icons.CHECK,
                on_click=self._finish_setup,
                style="primary",
                theme=self.theme
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Modal content
        self.modal_content = ft.Container(
            content=ft.Column([
                # Header
                ft.Row([
                    ft.Text(
                        "🚀 Configuración Inicial - HYDRA21 PDF Compressor",
                        size=20,
                        weight=ft.FontWeight.W_600,
                        color=self.theme['on_surface']
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=self.theme['on_surface_variant'],
                        on_click=self._close_modal
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Divider(color=self.theme['border']),

                # Step indicator
                self.step_indicator,

                # Step content
                self.step_content,

                ft.Divider(color=self.theme['border']),

                # Navigation
                self.navigation_buttons

            ], spacing=16),
            width=600,
            bgcolor=self.theme['surface'],
            border_radius=12,
            padding=ft.padding.all(24),
            border=ft.border.all(1, self.theme['border'])
        )

        # Initialize first step
        self._update_step_indicator()
        self._show_step(0)
    
    def show(self):
        """Show the tutorial modal"""
        self.visible = True
        self.current_step = 0
        self._update_step_indicator()
        self._show_step(0)
        self.update()

    def hide(self):
        """Hide the tutorial modal"""
        self.visible = False
        self.update()
    
    def _close_modal(self, e):
        """Close modal without completing setup"""
        self.hide()
    
    def _update_step_indicator(self):
        """Update step indicator dots"""
        if not self.theme:
            return

        self.step_indicator.controls.clear()

        for i in range(self.total_steps):
            if i == self.current_step:
                # Current step
                dot = ft.Container(
                    width=12,
                    height=12,
                    bgcolor=self.theme.get('primary', '#2563eb'),
                    border_radius=6
                )
            elif i < self.current_step:
                # Completed step
                dot = ft.Container(
                    content=ft.Icon(ft.Icons.CHECK, size=12, color=self.theme.get('on_primary', 'white')),
                    width=12,
                    height=12,
                    bgcolor=self.theme.get('success', '#10b981'),
                    border_radius=6
                )
            else:
                # Future step
                dot = ft.Container(
                    width=12,
                    height=12,
                    bgcolor=self.theme.get('surface_variant', '#f1f5f9'),
                    border_radius=6,
                    border=ft.border.all(1, self.theme.get('border', '#e2e8f0'))
                )

            self.step_indicator.controls.append(dot)
    
    def _show_step(self, step: int):
        """Show specific step content"""
        if step == 0:
            self._show_welcome_step()
        elif step == 1:
            self._show_ghostscript_info_step()
        elif step == 2:
            self._show_ghostscript_setup_step()
        elif step == 3:
            self._show_completion_step()
        
        self._update_navigation_buttons()
    
    def _show_welcome_step(self):
        """Show welcome step"""
        self.step_content.content = ft.Column([
            ft.Text(
                "¡Bienvenido a HYDRA21 PDF Compressor Pro!",
                size=24,
                weight=ft.FontWeight.W_700,
                color=self.theme['primary'],
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=20),
            ft.Text(
                "Esta aplicación te permite comprimir, fusionar y dividir archivos PDF de manera profesional.",
                size=16,
                color=self.theme['on_surface'],
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=20),
            create_modern_card([
                ft.Text(
                    "Características principales:",
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=self.theme['on_surface']
                ),
                ft.Column([
                    self._create_feature_item("📦", "Compresión de PDFs con múltiples niveles de calidad"),
                    self._create_feature_item("🔗", "Fusión de múltiples PDFs en un solo archivo"),
                    self._create_feature_item("✂️", "División de PDFs por páginas o rangos"),
                    self._create_feature_item("⚡", "Procesamiento por lotes para múltiples archivos"),
                    self._create_feature_item("📊", "Estadísticas detalladas de compresión"),
                    self._create_feature_item("🎨", "Interfaz moderna con tema claro/oscuro")
                ], spacing=8)
            ], self.theme),
            ft.Container(height=20),
            ft.Text(
                "Para comenzar, necesitamos configurar Ghostscript, el motor que procesa los PDFs.",
                size=14,
                color=self.theme['on_surface_variant'],
                text_align=ft.TextAlign.CENTER
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def _show_ghostscript_info_step(self):
        """Show Ghostscript information step"""
        self.step_content.content = ft.Column([
            ft.Text(
                "¿Qué es Ghostscript?",
                size=20,
                weight=ft.FontWeight.W_600,
                color=self.theme['on_surface'],
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=16),
            ft.Text(
                "Ghostscript es un intérprete de PostScript y PDF de código abierto que utilizamos para procesar archivos PDF.",
                size=14,
                color=self.theme['on_surface'],
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=20),
            create_modern_card([
                ft.Text(
                    "Opciones de instalación:",
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=self.theme['on_surface']
                ),
                ft.Column([
                    self._create_option_item(
                        "🔍 Detección Automática",
                        "Si ya tienes Ghostscript instalado, intentaremos detectarlo automáticamente."
                    ),
                    self._create_option_item(
                        "📥 Descarga Manual",
                        "Si no tienes Ghostscript, puedes descargarlo desde: https://www.ghostscript.com/download/gsdnld.html"
                    ),
                    self._create_option_item(
                        "📂 Ruta Personalizada",
                        "Si tienes Ghostscript en una ubicación específica, puedes especificar la ruta manualmente."
                    )
                ], spacing=12)
            ], self.theme),
            ft.Container(height=20),
            ft.Text(
                "En el siguiente paso configuraremos Ghostscript para tu sistema.",
                size=14,
                color=self.theme['info'],
                text_align=ft.TextAlign.CENTER
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def _show_ghostscript_setup_step(self):
        """Show Ghostscript setup step"""
        # Ghostscript path input
        self.gs_path_input = create_modern_input(
            label="Ruta de Ghostscript (opcional)",
            hint_text="Deja vacío para detección automática",
            theme=self.theme,
            width=400
        )
        
        # Status text
        self.status_text = ft.Text(
            "",
            size=14,
            text_align=ft.TextAlign.CENTER
        )
        
        # Auto-detect button
        self.auto_detect_button = create_modern_button(
            text="Detectar Automáticamente",
            icon=ft.Icons.SEARCH,
            on_click=self._auto_detect_ghostscript,
            style="primary",
            theme=self.theme
        )
        
        # Verify button
        self.verify_button = create_modern_button(
            text="Verificar Configuración",
            icon=ft.Icons.CHECK_CIRCLE,
            on_click=self._verify_ghostscript,
            style="secondary",
            theme=self.theme
        )
        
        # File picker button
        file_picker_button = create_modern_button(
            text="Buscar Archivo",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self._browse_ghostscript,
            style="secondary",
            theme=self.theme
        )
        
        self.step_content.content = ft.Column([
            ft.Text(
                "Configuración de Ghostscript",
                size=20,
                weight=ft.FontWeight.W_600,
                color=self.theme['on_surface'],
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=16),
            
            # Current status
            self._get_current_gs_status(),
            
            ft.Container(height=20),
            
            # Configuration options
            create_modern_card([
                ft.Text(
                    "Opciones de configuración:",
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=self.theme['on_surface']
                ),
                ft.Row([
                    self.auto_detect_button,
                    file_picker_button
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
                
                ft.Text(
                    "O especifica la ruta manualmente:",
                    size=14,
                    color=self.theme['on_surface_variant'],
                    text_align=ft.TextAlign.CENTER
                ),
                
                self.gs_path_input,
                
                ft.Row([
                    self.verify_button
                ], alignment=ft.MainAxisAlignment.CENTER),
                
                self.status_text
            ], self.theme)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Auto-detect on first load
        self._auto_detect_ghostscript(None)
    
    def _show_completion_step(self):
        """Show completion step"""
        gs_info = self.gs_config.get_ghostscript_info()
        
        if gs_info['verified']:
            # Success completion
            self.step_content.content = ft.Column([
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE,
                    size=64,
                    color=self.theme['success']
                ),
                ft.Text(
                    "¡Configuración Completada!",
                    size=24,
                    weight=ft.FontWeight.W_700,
                    color=self.theme['success'],
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=16),
                ft.Text(
                    "HYDRA21 PDF Compressor está listo para usar.",
                    size=16,
                    color=self.theme['on_surface'],
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                create_modern_card([
                    ft.Text(
                        "Configuración de Ghostscript:",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=self.theme['on_surface']
                    ),
                    ft.Column([
                        self._create_info_row("Ruta", gs_info['path']),
                        self._create_info_row("Versión", gs_info['version'] or "Detectada"),
                        self._create_info_row("Estado", "✅ Verificado y funcionando")
                    ], spacing=8)
                ], self.theme),
                ft.Container(height=20),
                ft.Text(
                    "Ya puedes comenzar a comprimir, fusionar y dividir tus archivos PDF.",
                    size=14,
                    color=self.theme['on_surface_variant'],
                    text_align=ft.TextAlign.CENTER
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        else:
            # Error completion
            self.step_content.content = ft.Column([
                ft.Icon(
                    ft.Icons.WARNING,
                    size=64,
                    color=self.theme['warning']
                ),
                ft.Text(
                    "Configuración Incompleta",
                    size=24,
                    weight=ft.FontWeight.W_700,
                    color=self.theme['warning'],
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=16),
                ft.Text(
                    "Ghostscript no está configurado correctamente.",
                    size=16,
                    color=self.theme['on_surface'],
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                create_modern_card([
                    ft.Text(
                        "Para continuar:",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=self.theme['on_surface']
                    ),
                    ft.Column([
                        ft.Text("1. Descarga Ghostscript desde: https://www.ghostscript.com/download/gsdnld.html"),
                        ft.Text("2. Instálalo en tu sistema"),
                        ft.Text("3. Vuelve al paso anterior para configurarlo"),
                        ft.Text("4. O especifica la ruta manualmente si ya está instalado")
                    ], spacing=8)
                ], self.theme),
                ft.Container(height=20),
                ft.Text(
                    "Puedes cerrar este tutorial y configurar Ghostscript más tarde desde el menú de configuración.",
                    size=14,
                    color=self.theme['on_surface_variant'],
                    text_align=ft.TextAlign.CENTER
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def _get_current_gs_status(self) -> ft.Container:
        """Get current Ghostscript status display"""
        gs_info = self.gs_config.get_ghostscript_info()
        
        if gs_info['verified']:
            status_chip = create_status_chip("Configurado", "success", self.theme, ft.Icons.CHECK_CIRCLE)
            message = f"Ghostscript está configurado y funcionando correctamente."
            details = f"Ruta: {gs_info['path']}"
        elif gs_info['configured']:
            status_chip = create_status_chip("Error", "error", self.theme, ft.Icons.ERROR)
            message = f"Ghostscript configurado pero no funciona correctamente."
            details = f"Error: {gs_info['message']}"
        else:
            status_chip = create_status_chip("No Configurado", "warning", self.theme, ft.Icons.WARNING)
            message = "Ghostscript no está configurado."
            details = "Necesitas configurar Ghostscript para usar la aplicación."
        
        return create_modern_card([
            ft.Row([
                status_chip,
                ft.Column([
                    ft.Text(
                        message,
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.theme['on_surface']
                    ),
                    ft.Text(
                        details,
                        size=12,
                        color=self.theme['on_surface_variant']
                    )
                ], spacing=4, expand=True)
            ])
        ], self.theme)
    
    def _create_feature_item(self, icon: str, text: str) -> ft.Row:
        """Create a feature list item"""
        return ft.Row([
            ft.Text(icon, size=16),
            ft.Text(text, size=14, color=self.theme['on_surface'], expand=True)
        ], spacing=12)
    
    def _create_option_item(self, title: str, description: str) -> ft.Column:
        """Create an option item"""
        return ft.Column([
            ft.Text(
                title,
                size=14,
                weight=ft.FontWeight.W_600,
                color=self.theme['on_surface']
            ),
            ft.Text(
                description,
                size=12,
                color=self.theme['on_surface_variant']
            )
        ], spacing=4)
    
    def _create_info_row(self, label: str, value: str) -> ft.Row:
        """Create an info row"""
        return ft.Row([
            ft.Text(
                f"{label}:",
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
        ])
    
    def _auto_detect_ghostscript(self, e):
        """Auto-detect Ghostscript installation"""
        self.status_text.value = "🔍 Detectando Ghostscript..."
        self.status_text.color = self.theme['info']
        self.update()
        
        success, message = self.gs_config.setup_ghostscript()
        
        if success:
            self.status_text.value = f"✅ {message}"
            self.status_text.color = self.theme['success']
            gs_info = self.gs_config.get_ghostscript_info()
            if gs_info['path']:
                self.gs_path_input.value = gs_info['path']
        else:
            self.status_text.value = f"❌ {message}"
            self.status_text.color = self.theme['error']
        
        self.update()
    
    def _verify_ghostscript(self, e):
        """Verify Ghostscript configuration"""
        custom_path = self.gs_path_input.value.strip() if self.gs_path_input.value else None
        
        self.status_text.value = "🔍 Verificando configuración..."
        self.status_text.color = self.theme['info']
        self.update()
        
        if custom_path:
            success, message = self.gs_config.setup_ghostscript(custom_path)
        else:
            is_valid, message = self.gs_config.verify_ghostscript()
            success = is_valid
        
        if success:
            self.status_text.value = f"✅ {message}"
            self.status_text.color = self.theme['success']
        else:
            self.status_text.value = f"❌ {message}"
            self.status_text.color = self.theme['error']
        
        self.update()
    
    def _browse_ghostscript(self, e):
        """Browse for Ghostscript executable"""
        # This would open a file picker in a real implementation
        # For now, show common paths
        common_paths = self.gs_config.get_common_paths()
        
        if common_paths:
            # Show first common path as example
            self.gs_path_input.value = common_paths[0]
            self.status_text.value = "💡 Ruta de ejemplo cargada. Verifica si es correcta."
            self.status_text.color = self.theme['info']
            self.update()
    
    def _previous_step(self, e):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_step_indicator()
            self._show_step(self.current_step)
            self.update()
    
    def _next_step(self, e):
        """Go to next step"""
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self._update_step_indicator()
            self._show_step(self.current_step)
            self.update()
    
    def _finish_setup(self, e):
        """Finish setup and close modal"""
        if self.on_setup_complete:
            self.on_setup_complete()
        self.hide()
    
    def _update_navigation_buttons(self):
        """Update navigation button visibility"""
        prev_button, next_button, finish_button = self.navigation_buttons.controls
        
        # Previous button
        prev_button.visible = self.current_step > 0
        
        # Next/Finish buttons
        if self.current_step < self.total_steps - 1:
            next_button.visible = True
            finish_button.visible = False
        else:
            next_button.visible = False
            finish_button.visible = True

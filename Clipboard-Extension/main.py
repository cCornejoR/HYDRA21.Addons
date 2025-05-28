import flet as ft
import pyperclip
import threading
import time
import json
import datetime
import sys
import os
from typing import List, Dict # Added

# Función para obtener la ruta de los assets
def resource_path(relative_path):
    """ Obtener la ruta absoluta al recurso, funciona para desarrollo y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ClipboardManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.max_clips = 50
        self.clips: List[Dict] = [] # Corrected type hint
        self.monitoring = False
        self.last_clipboard_content = ""
        self.theme_icon_button = ft.IconButton(
            ft.Icons.LIGHT_MODE, # Corrected
            tooltip="Cambiar tema",
            on_click=self.toggle_theme,
            icon_size=20,
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.WHITE, # Corrected
                shape=ft.RoundedRectangleBorder(radius=8),
            )
        )
        
        # Configurar la página
        self.setup_page()
        
        # Cargar clips guardados
        self.load_clips()
        
        # Crear la interfaz
        self.create_ui()
        
        # Iniciar monitoreo del portapapeles
        self.start_monitoring()
    
    def setup_page(self):
        self.page.title = "Clipboard Manager Addon"
        self.page.window.icon = resource_path("assets/icons/logo_clipboard.ico")
        
        # Cargar preferencia de tema
        saved_theme = self.page.client_storage.get("theme_mode")
        if saved_theme == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_icon_button.icon = ft.Icons.DARK_MODE # Corrected
            self.theme_icon_button.style.color = ft.Colors.WHITE # Corrected
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT # Predeterminado a claro
            self.theme_icon_button.icon = ft.Icons.LIGHT_MODE # Corrected
            self.theme_icon_button.style.color = ft.Colors.BLACK # Corrected

        self.page.window.width = 500
        self.page.window.height = 800
        self.page.window.resizable = True
        self.page.window.title_bar_hidden = False
        self.page.padding = 0
        
        # Configurar atajos de teclado
        self.page.on_keyboard_event = self.on_keyboard
    
    def create_ui(self):
        # Header compacto y moderno
        self.counter_text = ft.Text(
            f"{len(self.clips)}/50",
            size=12,
            color=ft.Colors.GREY_600, # Corrected
            weight=ft.FontWeight.W_500
        )
        
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.CONTENT_PASTE_ROUNDED, size=24), # Corrected
                    ft.Text("Clips", size=18, weight=ft.FontWeight.W_600),
                ], spacing=8),
                
                ft.Row([
                    self.counter_text,
                    self.theme_icon_button,
                    ft.IconButton(
                        icon=ft.Icons.REFRESH_ROUNDED, # Corrected
                        tooltip="Capturar (Ctrl+Shift+V)",
                        on_click=self.capture_clipboard,
                        icon_size=20,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                        )
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_SWEEP_ROUNDED, # Corrected
                        tooltip="Limpiar todo (Ctrl+Shift+C)",
                        on_click=self.clear_all,
                        icon_size=20,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                        )
                    ),
                ], spacing=4),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.OUTLINE if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_200)),
        )
        
        # Lista de clips con diseño moderno
        self.clips_list = ft.ListView(
            expand=True,
            spacing=1,
            padding=ft.padding.all(0),
        )
        
        # Panel de información minimalista
        shortcuts_info = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.KEYBOARD_ROUNDED, size=16, color=ft.Colors.GREY_500), # Corrected
                    ft.Text("Ctrl+Shift+V: Capturar  •  Ctrl+Shift+C: Limpiar", 
                           size=11, color=ft.Colors.GREY_600), # Corrected
                ], spacing=6),
            ]),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            border=ft.border.only(top=ft.BorderSide(1, ft.Colors.OUTLINE if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_200)),
        )
        
        # Layout principal
        self.page.add(
            ft.Column([
                header,
                ft.Container(
                    content=self.clips_list,
                    expand=True,
                ),
                shortcuts_info
            ], spacing=0, expand=True)
        )
        
        # Actualizar la lista
        self.update_clips_display()
    
    def load_clips(self):
        """Cargar clips desde el storage"""
        try:
            stored_clips = self.page.client_storage.get("clipboard_clips")
            if stored_clips:
                self.clips = json.loads(stored_clips)
        except Exception as e:
            print(f"Error loading clips: {e}")
            self.clips = []
    
    def save_clips(self):
        """Guardar clips al storage"""
        try:
            self.page.client_storage.set("clipboard_clips", json.dumps(self.clips))
        except Exception as e:
            print(f"Error saving clips: {e}")
    
    def add_clip(self, content: str):
        """Agregar un nuevo clip al historial"""
        if not content.strip():
            return
            
        # Evitar duplicados recientes
        if self.clips and self.clips[0].get("content") == content:
            return
        
        # Crear nuevo clip
        new_clip = {
            "content": content,
            "timestamp": datetime.datetime.now().isoformat(),
            "preview": content.replace('\\n', ' ').replace('\\t', ' ')[:80] + "..." if len(content) > 80 else content.replace('\\n', ' ').replace('\\t', ' ')
        }
        
        # Agregar al inicio de la lista
        self.clips.insert(0, new_clip)
        
        # Mantener solo los últimos 50
        if len(self.clips) > self.max_clips:
            self.clips = self.clips[:self.max_clips]
        
        # Guardar y actualizar
        self.save_clips()
        self.update_clips_display()
    
    def capture_clipboard(self, e=None):
        """Capturar contenido actual del portapapeles"""
        try:
            # Usar solo pyperclip que es más confiable
            content = pyperclip.paste()
            
            if content and content.strip():
                self.add_clip(content)
                self.show_snackbar("📋 Clip capturado", ft.Colors.GREEN_600) # Corrected
            else:
                self.show_snackbar("⚠️ Portapapeles vacío", ft.Colors.ORANGE_600) # Corrected
                
        except Exception as e:
            print(f"Clipboard error: {e}")
            self.show_snackbar("❌ Error de acceso", ft.Colors.RED_600) # Corrected
    
    def copy_to_clipboard(self, content: str):
        """Copiar contenido al portapapeles"""
        try:
            # Usar solo pyperclip que es más confiable
            pyperclip.copy(content)
            self.show_snackbar("✅ Copiado", ft.Colors.GREEN_600) # Corrected
        except Exception as e:
            print(f"Copy error: {e}")
            self.show_snackbar("❌ Error al copiar", ft.Colors.RED_600) # Corrected
    
    def delete_clip(self, index: int):
        """Eliminar un clip específico"""
        if 0 <= index < len(self.clips):
            self.clips.pop(index)
            self.save_clips()
            self.update_clips_display()
            self.show_snackbar("🗑️ Eliminado", ft.Colors.BLUE_600) # Corrected
    
    def clear_all(self, e=None):
        """Limpiar todo el historial"""
        self.clips = []
        self.save_clips()
        self.update_clips_display()
        self.show_snackbar("🧹 Historial limpio", ft.Colors.BLUE_600) # Corrected
    
    def update_clips_display(self):
        """Actualizar la visualización de clips"""
        self.clips_list.controls.clear()
        
        # Actualizar contador
        self.counter_text.value = f"{len(self.clips)}/50"
        
        if not self.clips:
            # Estado vacío elegante
            self.clips_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX_ROUNDED, size=48), # Corrected
                        ft.Text("Sin clips guardados", 
                               size=16,
                               weight=ft.FontWeight.W_500,
                               text_align=ft.TextAlign.CENTER),
                        ft.Text("Usa Ctrl+Shift+V para empezar", 
                               size=12,
                               text_align=ft.TextAlign.CENTER),
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8),
                    padding=60,
                    alignment=ft.alignment.center,
                )
            )
        else:
            for i, clip in enumerate(self.clips):
                # Formatear timestamp compacto
                try:
                    timestamp = datetime.datetime.fromisoformat(clip["timestamp"])
                    if timestamp.date() == datetime.date.today():
                        time_str = timestamp.strftime("%H:%M")
                    else:
                        time_str = timestamp.strftime("%d/%m %H:%M")
                except:
                    time_str = "Ahora"                  # Card moderno y compacto
                is_dark = self.page.theme_mode == ft.ThemeMode.DARK
                card_bgcolor = ft.Colors.SURFACE if is_dark else ft.Colors.WHITE
                text_color = ft.Colors.ON_SURFACE if is_dark else ft.Colors.GREY_800
                secondary_text_color = ft.Colors.ON_SURFACE if is_dark else ft.Colors.GREY_500
                icon_button_bgcolor = ft.Colors.PRIMARY_CONTAINER if is_dark else ft.Colors.INDIGO_50
                icon_button_color = ft.Colors.ON_PRIMARY_CONTAINER if is_dark else ft.Colors.INDIGO_600
                delete_button_bgcolor = ft.Colors.ERROR_CONTAINER if is_dark else ft.Colors.RED_50
                delete_button_color = ft.Colors.ON_ERROR_CONTAINER if is_dark else ft.Colors.RED_400
                number_bg_color = ft.Colors.PRIMARY_CONTAINER if is_dark else ft.Colors.INDIGO_400
                number_text_color = ft.Colors.ON_PRIMARY_CONTAINER if is_dark else ft.Colors.WHITE


                clip_card = ft.Container(
                    content=ft.Row([
                        # Número y contenido
                        ft.Column([
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(str(i+1), 
                                                   size=10, 
                                                   color=number_text_color,
                                                   weight=ft.FontWeight.W_600),
                                    width=20,
                                    height=20,
                                    bgcolor=number_bg_color,
                                    border_radius=10,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Text(time_str, 
                                       size=10, 
                                       color=secondary_text_color,
                                       weight=ft.FontWeight.W_500),
                            ], spacing=8),
                            

                            ft.Container(
                                content=ft.Text(
                                    clip["preview"],
                                    size=13,
                                    color=text_color,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    weight=ft.FontWeight.W_400,
                                ),
                                padding=ft.padding.only(top=4),
                                width=350,  # Ancho fijo para compatibilidad
                            ),
                        ], spacing=4, expand=True),
                        
                        # Botones de acción compactos
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.CONTENT_COPY_ROUNDED, # Corrected
                                tooltip="Copiar",
                                on_click=lambda e, content=clip["content"]: self.copy_to_clipboard(content),
                                icon_size=16,
                                style=ft.ButtonStyle(
                                    color=icon_button_color,
                                    bgcolor=icon_button_bgcolor,
                                    shape=ft.CircleBorder(),
                                ),
                                width=32,
                                height=32,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED, # Corrected
                                tooltip="Eliminar",
                                on_click=lambda e, idx=i: self.delete_clip(idx),
                                icon_size=16,
                                style=ft.ButtonStyle(
                                    color=delete_button_color,
                                    bgcolor=delete_button_bgcolor,
                                    shape=ft.CircleBorder(),
                                ),
                                width=32,
                                height=32,
                            ),
                        ], spacing=10),
                    ], spacing=12),
                    
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    bgcolor=card_bgcolor,
                    border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.OUTLINE if is_dark else ft.Colors.GREY_100)),
                    ink=True,
                    on_click=lambda e, content=clip["content"]: self.copy_to_clipboard(content),
                )
                
                self.clips_list.controls.append(clip_card)
        
        self.page.update()
    
    def show_snackbar(self, message: str, color: str):
        """Mostrar mensaje de notificación"""
        try:            # Usar colores de tema para snackbar si es posible
            is_dark = self.page.theme_mode == ft.ThemeMode.DARK
            text_color_snackbar = ft.Colors.WHITE
            bgcolor_snackbar = color # Mantener el color pasado para mensajes de éxito/error

            # Ajustar colores comunes para mejor contraste en tema oscuro
            if is_dark:
                if color == ft.Colors.GREEN_600:
                    bgcolor_snackbar = ft.Colors.GREEN_600
                elif color == ft.Colors.ORANGE_600:
                    bgcolor_snackbar = ft.Colors.ORANGE_600
                elif color == ft.Colors.RED_600:
                    bgcolor_snackbar = ft.Colors.ERROR
                    text_color_snackbar = ft.Colors.ON_ERROR
                elif color == ft.Colors.BLUE_600:
                    bgcolor_snackbar = ft.Colors.BLUE_600

            snackbar = ft.SnackBar(
                content=ft.Text(message, 
                               color=text_color_snackbar,
                               size=13,
                               weight=ft.FontWeight.W_500),
                bgcolor=bgcolor_snackbar,
                duration=1500,
                behavior=ft.SnackBarBehavior.FLOATING,
                margin=ft.margin.all(20),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
            )
            self.page.snack_bar = snackbar
            snackbar.open = True
            self.page.update()
        except Exception as e:
            print(f"Snackbar error: {e}")
    
    def on_keyboard(self, e: ft.KeyboardEvent):
        """Manejar atajos de teclado"""
        if e.ctrl and e.shift:
            if e.key == "V":  # Ctrl+Shift+V: Capturar
                self.capture_clipboard()
            elif e.key == "C":  # Ctrl+Shift+C: Limpiar
                self.clear_all()
    
    def start_monitoring(self):
        """Iniciar monitoreo automático del portapapeles"""
        def monitor():
            while True:
                try:
                    # Usar solo pyperclip que es más confiable
                    current_content = pyperclip.paste()
                    
                    if (current_content and 
                        current_content != self.last_clipboard_content and
                        len(current_content.strip()) > 0 and
                        len(current_content) < 10000):  # Limitar tamaño
                        
                        self.last_clipboard_content = current_content
                        # Actualizar UI de forma segura
                        try:
                            self.page.run_thread(lambda: self.add_clip(current_content))
                        except:
                            # Fallback si run_thread no existe
                            self.add_clip(current_content)
                    
                    time.sleep(1)  # Verificar cada segundo
                except Exception as e:
                    print(f"Monitor error: {e}")
                    time.sleep(3)
        
        # Ejecutar en thread separado
        self.monitoring = True
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def toggle_theme(self, e):
        current_theme = self.page.theme_mode
        if current_theme == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_icon_button.icon = ft.Icons.DARK_MODE # Corrected
            self.theme_icon_button.style.color = ft.Colors.WHITE # Corrected
            self.page.client_storage.set("theme_mode", "dark")
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_icon_button.icon = ft.Icons.LIGHT_MODE # Corrected
            self.theme_icon_button.style.color = ft.Colors.BLACK # Corrected
            self.page.client_storage.set("theme_mode", "light")
        
        # Actualizar colores de elementos que no se adaptan automáticamente
        # Esto es crucial si algunos colores se establecieron explícitamente
        # y no usan el sistema de temas de Flet (ej. ft.Colors.PRIMARY)
        self.update_ui_colors_for_theme()
        self.page.update()    

    def update_ui_colors_for_theme(self):
        """Actualizar colores de elementos que no se adaptan automáticamente"""
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        
        # self.page.controls[0] is the main ft.Column of the page
        main_column = self.page.controls[0]

        # Header Container is the first control in the main_column
        header_container = main_column.controls[0]
        header_container.bgcolor = ft.Colors.SURFACE if is_dark else ft.Colors.WHITE
        header_container.border = ft.border.only(bottom=ft.BorderSide(1, ft.Colors.OUTLINE if is_dark else ft.Colors.GREY_200))
        
        # Header's content is an ft.Row
        header_content_row = header_container.content
        
        # First item in header_content_row is another ft.Row for Icon and "Clips" Text
        header_title_row = header_content_row.controls[0]
        header_title_row.controls[0].color = ft.Colors.PRIMARY if is_dark else ft.Colors.INDIGO_600
        header_title_row.controls[1].color = ft.Colors.PRIMARY if is_dark else ft.Colors.INDIGO_600
        
        # Update counter_text color (it's an instance variable, so directly accessible)
        self.counter_text.color = ft.Colors.ON_SURFACE if is_dark else ft.Colors.GREY_600

        # Second item in header_content_row is an ft.Row for action buttons
        header_actions_row = header_content_row.controls[1]
        # Order: self.counter_text (already handled), self.theme_icon_button, refresh_button, clear_all_button
        # Note: self.counter_text is the first element in this row in create_ui,
        # self.theme_icon_button is the second.
        # So, refresh_button is at index 2, clear_all_button is at index 3.
        refresh_button = header_actions_row.controls[2] 
        clear_all_button = header_actions_row.controls[3]
        
        refresh_button.style.color = ft.Colors.PRIMARY if is_dark else ft.Colors.INDIGO_600
        refresh_button.style.bgcolor = ft.Colors.PRIMARY_CONTAINER if is_dark else ft.Colors.INDIGO_50

        clear_all_button.style.color = ft.Colors.ERROR if is_dark else ft.Colors.RED_600
        clear_all_button.style.bgcolor = ft.Colors.ERROR_CONTAINER if is_dark else ft.Colors.RED_50

        # Container for clips_list is the second control in the main_column
        clips_list_container = main_column.controls[1]
        clips_list_container.bgcolor = ft.Colors.SURFACE if is_dark else ft.Colors.GREY_50
        
        # shortcuts_info Container is the third control in the main_column
        shortcuts_container = main_column.controls[2]
        shortcuts_container.bgcolor = ft.Colors.SURFACE if is_dark else ft.Colors.GREY_50
        shortcuts_container.border = ft.border.only(top=ft.BorderSide(1, ft.Colors.OUTLINE if is_dark else ft.Colors.GREY_200))
        
        # shortcuts_container.content is an ft.Column, its first control is an ft.Row
        shortcuts_text_row = shortcuts_container.content.controls[0]
        shortcuts_text_row.controls[0].color = ft.Colors.ON_SURFACE if is_dark else ft.Colors.GREY_500
        shortcuts_text_row.controls[1].color = ft.Colors.ON_SURFACE if is_dark else ft.Colors.GREY_600

        # Actualizar los clips existentes para reflejar el nuevo tema
        self.update_clips_display() # Esto ya maneja los colores de los cards
        # self.page.update() # This will be called by toggle_theme

def main(page: ft.Page):
    # Configurar assets_dir para PyInstaller
    page.assets_dir = resource_path("assets")
    
    # Add page close handler to prevent threading errors
    def on_window_event(e):
        if e.data == "close":
            page.window_destroy()
    
    page.window_prevent_close = True
    page.on_window_event = on_window_event
    
    app = ClipboardManager(page)
    page.update()

if __name__ == "__main__":
    try:
        ft.app(target=main, assets_dir=resource_path("assets"))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        # Ensure clean exit
        import sys
        sys.exit(0)
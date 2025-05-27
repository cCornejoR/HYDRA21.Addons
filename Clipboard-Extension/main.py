import flet as ft
import json
import datetime
import threading
import time
import pyperclip
from typing import List, Dict

class ClipboardManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.max_clips = 50
        self.clips: List[Dict] = []
        self.monitoring = False
        self.last_clipboard_content = ""
        
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
        self.page.theme_mode = ft.ThemeMode.LIGHT
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
            color=ft.Colors.GREY_600,
            weight=ft.FontWeight.W_500
        )
        
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.CONTENT_PASTE_ROUNDED, size=24, color=ft.Colors.INDIGO_600),
                    ft.Text("Clips", size=18, weight=ft.FontWeight.W_600, color=ft.Colors.INDIGO_600),
                ], spacing=8),
                
                ft.Row([
                    self.counter_text,
                    ft.IconButton(
                        icon=ft.Icons.REFRESH_ROUNDED,
                        tooltip="Capturar (Ctrl+Shift+V)",
                        on_click=self.capture_clipboard,
                        icon_size=20,
                        style=ft.ButtonStyle(
                            color=ft.Colors.INDIGO_600,
                            bgcolor=ft.Colors.INDIGO_50,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        )
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_SWEEP_ROUNDED,
                        tooltip="Limpiar todo (Ctrl+Shift+C)",
                        on_click=self.clear_all,
                        icon_size=20,
                        style=ft.ButtonStyle(
                            color=ft.Colors.RED_600,
                            bgcolor=ft.Colors.RED_50,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        )
                    ),
                ], spacing=4),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
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
                    ft.Icon(ft.Icons.KEYBOARD_ROUNDED, size=16, color=ft.Colors.GREY_500),
                    ft.Text("Ctrl+Shift+V: Capturar  •  Ctrl+Shift+C: Limpiar", 
                           size=11, color=ft.Colors.GREY_600),
                ], spacing=6),
            ]),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            bgcolor=ft.Colors.GREY_50,
            border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_200)),
        )
        
        # Layout principal
        self.page.add(
            ft.Column([
                header,
                ft.Container(
                    content=self.clips_list,
                    expand=True,
                    bgcolor=ft.Colors.GREY_50,
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
            "preview": content.replace('\n', ' ').replace('\t', ' ')[:80] + "..." if len(content) > 80 else content.replace('\n', ' ').replace('\t', ' ')
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
                self.show_snackbar("📋 Clip capturado", ft.Colors.GREEN_600)
            else:
                self.show_snackbar("⚠️ Portapapeles vacío", ft.Colors.ORANGE_600)
                
        except Exception as e:
            print(f"Clipboard error: {e}")
            self.show_snackbar("❌ Error de acceso", ft.Colors.RED_600)
    
    def copy_to_clipboard(self, content: str):
        """Copiar contenido al portapapeles"""
        try:
            # Usar solo pyperclip que es más confiable
            pyperclip.copy(content)
            self.show_snackbar("✅ Copiado", ft.Colors.GREEN_600)
        except Exception as e:
            print(f"Copy error: {e}")
            self.show_snackbar("❌ Error al copiar", ft.Colors.RED_600)
    
    def delete_clip(self, index: int):
        """Eliminar un clip específico"""
        if 0 <= index < len(self.clips):
            self.clips.pop(index)
            self.save_clips()
            self.update_clips_display()
            self.show_snackbar("🗑️ Eliminado", ft.Colors.BLUE_600)
    
    def clear_all(self, e=None):
        """Limpiar todo el historial"""
        self.clips = []
        self.save_clips()
        self.update_clips_display()
        self.show_snackbar("🧹 Historial limpio", ft.Colors.BLUE_600)
    
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
                        ft.Icon(ft.Icons.INBOX_ROUNDED, size=48, color=ft.Colors.GREY_300),
                        ft.Text("Sin clips guardados", 
                               size=16,
                               color=ft.Colors.GREY_500,
                               weight=ft.FontWeight.W_500,
                               text_align=ft.TextAlign.CENTER),
                        ft.Text("Usa Ctrl+Shift+V para empezar", 
                               size=12,
                               color=ft.Colors.GREY_400,
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
                    time_str = "Ahora"
                
                # Card moderno y compacto
                clip_card = ft.Container(
                    content=ft.Row([
                        # Número y contenido
                        ft.Column([
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(str(i+1), 
                                                   size=10, 
                                                   color=ft.Colors.WHITE,
                                                   weight=ft.FontWeight.W_600),
                                    width=20,
                                    height=20,
                                    bgcolor=ft.Colors.INDIGO_400,
                                    border_radius=10,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Text(time_str, 
                                       size=10, 
                                       color=ft.Colors.GREY_500,
                                       weight=ft.FontWeight.W_500),
                            ], spacing=8),
                            
                            ft.Container(
                                content=ft.Text(
                                    clip["preview"],
                                    size=13,
                                    color=ft.Colors.GREY_800,
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
                                icon=ft.Icons.CONTENT_COPY_ROUNDED,
                                tooltip="Copiar",
                                on_click=lambda e, content=clip["content"]: self.copy_to_clipboard(content),
                                icon_size=16,
                                style=ft.ButtonStyle(
                                    color=ft.Colors.INDIGO_600,
                                    bgcolor=ft.Colors.INDIGO_50,
                                    shape=ft.CircleBorder(),
                                ),
                                width=32,
                                height=32,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                tooltip="Eliminar",
                                on_click=lambda e, idx=i: self.delete_clip(idx),
                                icon_size=16,
                                style=ft.ButtonStyle(
                                    color=ft.Colors.RED_400,
                                    bgcolor=ft.Colors.RED_50,
                                    shape=ft.CircleBorder(),
                                ),
                                width=32,
                                height=32,
                            ),
                        ], spacing=0),
                    ], spacing=12),
                    
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
                    ink=True,
                    on_click=lambda e, content=clip["content"]: self.copy_to_clipboard(content),
                )
                
                self.clips_list.controls.append(clip_card)
        
        self.page.update()
    
    def show_snackbar(self, message: str, color: str):
        """Mostrar mensaje de notificación"""
        try:
            snackbar = ft.SnackBar(
                content=ft.Text(message, 
                               color=ft.Colors.WHITE,
                               size=13,
                               weight=ft.FontWeight.W_500),
                bgcolor=color,
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

def main(page: ft.Page):
    app = ClipboardManager(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
import flet as ft
import google.generativeai as genai
import PyPDF2
import io
import base64
from datetime import datetime
import json
import asyncio
import os
from typing import Optional, List, Dict
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Configuración de Gemini
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")  # Usar variable de entorno
genai.configure(api_key=API_KEY)

# Modelos
MODEL_GENERAL = genai.GenerativeModel("gemini-1.5-flash")  # Modelo disponible
MODEL_TTS = "models/gemini-2.0-flash-preview-tts"  # Para futuro uso

# Idiomas disponibles
LANGUAGES = {
    "es": "Español",
    "en": "Inglés",
    "fr": "Francés",
    "de": "Alemán",
    "it": "Italiano",
    "pt": "Portugués",
    "ja": "Japonés",
    "ko": "Coreano",
    "zh": "Chino",
    "ru": "Ruso"
}

class PaperTranslatorApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Paper Translator AI"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = "#f0f4f8"
        self.page.padding = 0
        self.page.window.width = 500
        self.page.window.height = 800
        self.page.window.resizable = True
        self.page.window.center = True
        
        # Variables de estado
        self.paper_text = ""
        self.translated_text = ""
        self.summary = ""
        self.chat_history = []
        self.source_lang = "en"
        self.target_lang = "es"
        self.file_name = ""
        
        # Configurar tema azul
        self.primary_color = "#1976d2"
        self.secondary_color = "#2196f3"
        self.accent_color = "#03a9f4"
        self.light_blue = "#e3f2fd"
        self.dark_blue = "#0d47a1"
        
        self.setup_ui()
        
    def show_snackbar(self, message: str, bgcolor: str = None):
        """Mostrar snackbar con mensaje"""
        snack = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=bgcolor or self.primary_color,
            duration=3000
        )
        self.page.snack_bar = snack
        self.page.snack_bar.open = True
        self.page.update()
        
    def setup_ui(self):
        # Header compacto
        self.header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.TRANSLATE, color="white", size=24),
                ft.Text(
                    "Paper Translator AI",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="white"
                ),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.HELP_OUTLINE,
                        icon_color="white",
                        icon_size=20,
                        tooltip="Ayuda",
                        on_click=self.show_help
                    ),
                    ft.IconButton(
                        icon=ft.Icons.INFO_OUTLINE,
                        icon_color="white",
                        icon_size=20,
                        tooltip="Acerca de",
                        on_click=self.show_about
                    ),
                ], tight=True)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor=self.primary_color,
            border_radius=ft.border_radius.only(bottom_left=15, bottom_right=15),
        )
        
        # Área de carga de archivo más compacta
        self.file_picker = ft.FilePicker(on_result=self.file_picked)
        self.page.overlay.append(self.file_picker)
        
        self.file_name_text = ft.Text("", size=12, color=self.dark_blue, visible=False)
        
        self.upload_area = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CLOUD_UPLOAD, size=40, color=self.primary_color),
                ft.Text("Arrastra tu PDF aquí o haz clic", 
                       size=14, color=self.primary_color, text_align=ft.TextAlign.CENTER),
                ft.ElevatedButton(
                    "Seleccionar Archivo",
                    icon=ft.Icons.FOLDER_OPEN,
                    bgcolor=self.secondary_color,
                    color="white",
                    height=35,
                    on_click=lambda _: self.file_picker.pick_files(
                        allowed_extensions=["pdf"]
                    )
                ),
                self.file_name_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            padding=20,
            bgcolor=self.light_blue,
            border_radius=10,
            border=ft.border.all(2, self.accent_color),
            on_click=lambda _: self.file_picker.pick_files(allowed_extensions=["pdf"]),
            height=150        )
        
        # Selectores de idioma más compactos
        self.source_lang_dropdown = ft.Dropdown(
            label="Idioma original",
            width=150,
            value="en",
            options=[ft.dropdown.Option(key, text) for key, text in LANGUAGES.items()],
            on_change=self.on_source_lang_change,
            bgcolor="white",
            border_color=self.primary_color,
            focused_border_color=self.accent_color,
            label_style=ft.TextStyle(color=self.primary_color, size=12),
            text_size=13
        )        
        self.target_lang_dropdown = ft.Dropdown(
            label="Traducir a",
            width=150,
            value="es",
            options=[ft.dropdown.Option(key, text) for key, text in LANGUAGES.items()],
            on_change=self.on_target_lang_change,
            bgcolor="white",
            border_color=self.primary_color,
            focused_border_color=self.accent_color,
            label_style=ft.TextStyle(color=self.primary_color, size=12),
            text_size=13
        )
        
        self.translate_button = ft.ElevatedButton(
            "Traducir",
            icon=ft.Icons.TRANSLATE,
            bgcolor=self.primary_color,
            color="white",
            on_click=self.translate_paper,
            disabled=True,
            height=45,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            )
        )
        
        # Tabs más compactas
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            height=45,
            tabs=[                ft.Tab(
                    text="Traducción",
                    icon=ft.Icons.TRANSLATE,
                ),
                ft.Tab(
                    text="Resumen",
                    icon=ft.Icons.SUMMARIZE,
                ),
                ft.Tab(
                    text="Chat",
                    icon=ft.Icons.CHAT,
                ),
                ft.Tab(
                    text="Infografía",
                    icon=ft.Icons.IMAGE,
                ),
            ],
            on_change=self.on_tab_change,
        )
        
        # Contenido de traducción
        self.translation_content = ft.Container(
            content=ft.Column([
                ft.Text("Texto traducido aparecerá aquí", 
                       size=13, color=self.dark_blue, italic=True),
            ], scroll=ft.ScrollMode.AUTO),
            padding=15,
            bgcolor="white",
            border_radius=8,
            expand=True,
        )
        
        # Contenido de resumen
        self.summary_content = ft.Container(
            content=ft.Column([
                ft.Text("El resumen aparecerá aquí", 
                       size=13, color=self.dark_blue, italic=True),
            ], scroll=ft.ScrollMode.AUTO),
            padding=15,
            bgcolor="white",
            border_radius=8,
            expand=True,
        )
        
        # Contenido de chat
        self.chat_messages = ft.ListView(
            expand=True,
            spacing=8,
            padding=ft.padding.all(10),
            auto_scroll=True,
        )
        
        self.chat_input = ft.TextField(
            hint_text="Escribe tu pregunta sobre el paper...",
            border_radius=20,
            filled=True,
            expand=True,
            bgcolor="white",
            border_color=self.primary_color,
            focused_border_color=self.accent_color,
            on_submit=self.send_chat_message,
            height=45,
            text_size=13
        )
        
        self.chat_content = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=self.chat_messages,
                    expand=True,
                    bgcolor=self.light_blue,
                    border_radius=8,
                ),
                ft.Row([
                    self.chat_input,                    ft.IconButton(
                        icon=ft.Icons.SEND,
                        bgcolor=self.primary_color,
                        icon_color="white",
                        icon_size=20,
                        on_click=self.send_chat_message
                    )
                ], spacing=5)
            ], spacing=10),
            expand=True,
        )
        
        # Contenido de infografía
        self.infographic_image = ft.Image(visible=False, fit=ft.ImageFit.CONTAIN)
        
        self.infographic_content = ft.Container(
            content=ft.Column([
                ft.Text("La infografía aparecerá aquí", 
                       size=13, color=self.dark_blue, italic=True),                ft.ElevatedButton(
                    "Generar Infografía",
                    icon=ft.Icons.AUTO_GRAPH,
                    bgcolor=self.secondary_color,
                    color="white",
                    on_click=self.generate_infographic,
                    height=40,
                ),
                self.infographic_image,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=15,
            bgcolor="white",
            border_radius=8,
            expand=True,
        )        
        # Botón de texto a voz
        self.tts_button = ft.IconButton(
            icon=ft.Icons.VOLUME_UP,
            bgcolor=self.accent_color,
            icon_color="white",
            icon_size=20,
            tooltip="Escuchar resumen",
            on_click=self.text_to_speech
        )
        
        # Progress bar
        self.progress_bar = ft.ProgressBar(
            width=300,
            color=self.primary_color,
            bgcolor=self.light_blue,
            visible=False,
            height=3
        )
        
        # Contenedor principal de contenido
        self.content_container = ft.Container(
            expand=True,
            content=ft.Stack([
                self.translation_content,
                self.summary_content,
                self.chat_content,
                self.infographic_content,
            ])
        )
        
        # Layout principal responsivo
        self.main_content = ft.Column([
            self.header,
            ft.Container(
                content=ft.Column([
                    self.upload_area,
                    ft.ResponsiveRow([
                        ft.Column(col={"sm": 12, "md": 5}, controls=[self.source_lang_dropdown]),                        ft.Column(col={"sm": 12, "md": 2}, controls=[
                            ft.Icon(ft.Icons.ARROW_FORWARD, color=self.primary_color, size=20)
                        ]),
                        ft.Column(col={"sm": 12, "md": 5}, controls=[self.target_lang_dropdown]),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    self.translate_button,
                    self.progress_bar,
                    self.tabs,
                    self.content_container,
                    ft.Row([
                        self.tts_button,
                    ], alignment=ft.MainAxisAlignment.END)
                ], spacing=10),
                padding=15,
                expand=True
            )
        ], spacing=0, expand=True)
        
        # Agregar al page
        self.page.add(self.main_content)
        self.update_tab_content()
        
    def file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            self.file_name = file.name
            
            try:
                # Leer el PDF
                with open(file.path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    self.paper_text = text
                
                # Actualizar UI
                self.file_name_text.value = f"📄 {self.file_name}"
                self.file_name_text.visible = True
                self.translate_button.disabled = False
                self.page.update()
                
                self.show_snackbar(f"Archivo cargado: {self.file_name}", ft.Colors.GREEN_400)
            except Exception as ex:
                self.show_snackbar(f"Error al leer el archivo: {str(ex)}", ft.Colors.RED_400)
            
    async def translate_paper(self, e):
        if not self.paper_text:
            self.show_snackbar("Por favor, carga un archivo PDF primero", ft.Colors.ORANGE_400)
            return
            
        # Verificar API key
        if API_KEY == "YOUR_API_KEY_HERE":
            self.show_snackbar("Por favor, configura tu API key de Gemini", ft.Colors.RED_400)
            return
            
        self.progress_bar.visible = True
        self.translate_button.disabled = True
        self.page.update()
        
        try:
            # Traducir el paper (limitamos a 3000 caracteres para el ejemplo)
            text_chunk = self.paper_text[:9000]
            
            prompt = f"""
            Traduce el siguiente texto académico del {LANGUAGES[self.source_lang]} al {LANGUAGES[self.target_lang]}.
            Mantén el formato y la estructura del documento.
            Preserva los términos técnicos cuando sea apropiado.
            
            Texto:
            {text_chunk}
            """
            
            response = await asyncio.to_thread(MODEL_GENERAL.generate_content, prompt)
            self.translated_text = response.text
            
            # Generar resumen
            summary_prompt = f"""
            Genera un resumen ejecutivo en {LANGUAGES[self.target_lang]} del siguiente paper académico.
            El resumen debe incluir:
            - Objetivo principal
            - Metodología
            - Resultados clave
            - Conclusiones
            
            Texto:
            {text_chunk}
            """
            
            summary_response = await asyncio.to_thread(MODEL_GENERAL.generate_content, summary_prompt)
            self.summary = summary_response.text
            
            # Actualizar UI
            self.translation_content.content = ft.Column([
                ft.Text("Traducción completa:", size=16, weight=ft.FontWeight.BOLD, color=self.dark_blue),
                ft.Text(self.translated_text, size=13, selectable=True),
            ], scroll=ft.ScrollMode.AUTO)
            
            self.summary_content.content = ft.Column([
                ft.Text("Resumen ejecutivo:", size=16, weight=ft.FontWeight.BOLD, color=self.dark_blue),
                ft.Text(self.summary, size=13, selectable=True),
            ], scroll=ft.ScrollMode.AUTO)
            
            self.show_snackbar("Traducción completada exitosamente", ft.Colors.GREEN_400)
            
        except Exception as ex:
            error_msg = str(ex)
            if "API_KEY_INVALID" in error_msg:
                self.show_snackbar("API key inválida. Por favor, verifica tu configuración", ft.Colors.RED_400)
            else:
                self.show_snackbar(f"Error: {error_msg[:100]}...", ft.Colors.RED_400)
        finally:
            self.progress_bar.visible = False
            self.translate_button.disabled = False
            self.page.update()
            
    async def send_chat_message(self, e):
        if not self.chat_input.value or not self.paper_text:
            return
            
        user_message = self.chat_input.value
        self.chat_input.value = ""
        
        # Agregar mensaje del usuario
        user_bubble = self.create_chat_bubble(user_message, is_user=True)
        self.chat_messages.controls.append(user_bubble)
        self.page.update()
        
        try:
            # Generar respuesta
            prompt = f"""
            Basándote en el siguiente paper académico, responde la pregunta del usuario en {LANGUAGES[self.target_lang]}.
            Sé preciso y cita información específica del paper cuando sea relevante.
            
            Paper:
            {self.paper_text[:2000]}
            
            Pregunta del usuario: {user_message}
            """
            
            response = await asyncio.to_thread(MODEL_GENERAL.generate_content, prompt)
            
            # Agregar respuesta del bot
            bot_bubble = self.create_chat_bubble(response.text, is_user=False)
            self.chat_messages.controls.append(bot_bubble)
            
        except Exception as ex:
            error_bubble = self.create_chat_bubble(f"Error: {str(ex)[:100]}...", is_user=False)
            self.chat_messages.controls.append(error_bubble)
            
        self.page.update()
        
    def create_chat_bubble(self, message: str, is_user: bool):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(message, size=13, color="white" if is_user else self.dark_blue),
                    padding=12,
                    bgcolor=self.primary_color if is_user else "white",
                    border_radius=ft.border_radius.only(
                        top_left=15,
                        top_right=15,
                        bottom_left=15 if not is_user else 3,
                        bottom_right=3 if not is_user else 15
                    ),
                    max_width=300,
                ),
            ], alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START),
            margin=ft.margin.only(left=40 if is_user else 0, right=0 if is_user else 40),
        )
        
    async def generate_infographic(self, e):
        if not self.summary:
            self.show_snackbar("Primero debes traducir el paper", ft.Colors.ORANGE_400)
            return
            
        try:
            # Extraer puntos clave del resumen
            extract_prompt = f"""
            Del siguiente resumen, extrae exactamente 4 puntos clave en formato JSON.
            Cada punto debe tener un título corto (máximo 3 palabras) y una descripción breve (máximo 15 palabras).
            
            Formato esperado:
            {{
                "puntos": [
                    {{"titulo": "...", "descripcion": "..."}},
                    {{"titulo": "...", "descripcion": "..."}},
                    {{"titulo": "...", "descripcion": "..."}},
                    {{"titulo": "...", "descripcion": "..."}}
                ]
            }}
            
            Resumen:
            {self.summary}
            """
            
            response = await asyncio.to_thread(MODEL_GENERAL.generate_content, extract_prompt)
            
            # Parsear respuesta
            try:
                # Limpiar respuesta para obtener solo JSON
                json_str = response.text.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0]
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0]
                    
                data = json.loads(json_str)
                puntos = data.get("puntos", [])[:4]
            except:
                # Fallback si falla el parsing
                puntos = [
                    {"titulo": "Objetivo", "descripcion": "Objetivo principal del estudio"},
                    {"titulo": "Método", "descripcion": "Metodología empleada"},
                    {"titulo": "Resultados", "descripcion": "Hallazgos principales"},
                    {"titulo": "Conclusión", "descripcion": "Conclusiones del estudio"}
                ]
            
            # Crear infografía
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('#f0f4f8')
            ax.set_facecolor('#f0f4f8')
            
            # Título
            ax.text(0.5, 0.95, 'RESUMEN DEL PAPER', 
                   ha='center', va='top', fontsize=20, fontweight='bold',
                   color='#1976d2', transform=ax.transAxes)
            
            # Crear cajas para cada punto
            positions = [(0.25, 0.7), (0.75, 0.7), (0.25, 0.3), (0.75, 0.3)]
            colors = ['#1976d2', '#2196f3', '#03a9f4', '#0288d1']
            
            for i, (punto, pos, color) in enumerate(zip(puntos, positions, colors)):
                # Caja principal
                box = FancyBboxPatch(
                    (pos[0] - 0.18, pos[1] - 0.12), 0.36, 0.2,
                    boxstyle="round,pad=0.02",
                    facecolor=color,
                    edgecolor='none',
                    transform=ax.transAxes,
                    alpha=0.9
                )
                ax.add_patch(box)
                
                # Número
                circle = plt.Circle((pos[0] - 0.13, pos[1] + 0.05), 0.03, 
                                  color='white', transform=ax.transAxes)
                ax.add_patch(circle)
                ax.text(pos[0] - 0.13, pos[1] + 0.05, str(i+1), 
                       ha='center', va='center', fontsize=12, fontweight='bold',
                       color=color, transform=ax.transAxes)
                
                # Título
                ax.text(pos[0], pos[1] + 0.05, punto.get('titulo', ''), 
                       ha='center', va='center', fontsize=14, fontweight='bold',
                       color='white', transform=ax.transAxes)
                
                # Descripción
                ax.text(pos[0], pos[1] - 0.03, punto.get('descripcion', ''), 
                       ha='center', va='center', fontsize=10,
                       color='white', transform=ax.transAxes, wrap=True)
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Guardar como imagen
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            plt.close()
            
            # Convertir a base64
            img_base64 = base64.b64encode(buf.read()).decode()
            
            # Mostrar infografía
            self.infographic_image.src_base64 = img_base64
            self.infographic_image.visible = True
            
            self.infographic_content.content = ft.Column([
                self.infographic_image,                ft.ElevatedButton(
                    "Descargar Infografía",
                    icon=ft.Icons.DOWNLOAD,
                    bgcolor=self.secondary_color,
                    color="white",
                    height=40,
                    on_click=lambda _: self.download_infographic(img_base64)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
            
            self.page.update()
            self.show_snackbar("Infografía generada exitosamente", ft.Colors.GREEN_400)
            
        except Exception as ex:
            self.show_snackbar(f"Error generando infografía: {str(ex)[:100]}...", ft.Colors.RED_400)
            
    async def text_to_speech(self, e):
        if not self.summary:
            self.show_snackbar("No hay resumen para convertir a voz", ft.Colors.ORANGE_400)
            return
            
        try:
            # Aquí iría la implementación real de TTS con Gemini
            # Por ahora mostramos un mensaje
            self.show_snackbar("Función TTS en desarrollo", ft.Colors.BLUE_400)
        except Exception as ex:
            self.show_snackbar(f"Error: {str(ex)}", ft.Colors.RED_400)
            
    def download_infographic(self, img_base64):
        # Implementar descarga real
        self.show_snackbar("Infografía lista para descargar", ft.Colors.GREEN_400)
        
    def on_tab_change(self, e):
        self.update_tab_content()
        
    def update_tab_content(self):
        # Mostrar/ocultar contenido según tab seleccionada
        tab_index = self.tabs.selected_index
        self.translation_content.visible = tab_index == 0
        self.summary_content.visible = tab_index == 1
        self.chat_content.visible = tab_index == 2
        self.infographic_content.visible = tab_index == 3
        self.page.update()
        
    def on_source_lang_change(self, e):
        self.source_lang = e.control.value
        
    def on_target_lang_change(self, e):
        self.target_lang = e.control.value
        
    def show_help(self, e):
        help_dialog = ft.AlertDialog(
            title=ft.Text("Ayuda", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📄 Carga un archivo PDF", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("Selecciona o arrastra tu paper académico en formato PDF.", size=12),
                    ft.Text("\n🌐 Selecciona idiomas", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("Elige el idioma original y al que deseas traducir.", size=12),
                    ft.Text("\n🔄 Traduce", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("Haz clic en 'Traducir' para comenzar.", size=12),
                    ft.Text("\n💬 Chatea", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("Haz preguntas sobre el contenido del paper.", size=12),
                    ft.Text("\n📊 Genera infografía", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("Crea una visualización de los puntos clave.", size=12),
                ], scroll=ft.ScrollMode.AUTO),
                width=350,
                height=300,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self.close_dialog())
            ]
        )
        self.page.dialog = help_dialog
        help_dialog.open = True
        self.page.update()
        
    def show_about(self, e):
        about_dialog = ft.AlertDialog(
            title=ft.Text("Acerca de", size=18, weight=ft.FontWeight.BOLD),            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.TRANSLATE, size=50, color=self.primary_color),
                    ft.Text("Paper Translator AI", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("Versión 1.0.0", size=12),
                    ft.Text("\nTraducción inteligente de papers académicos", size=12),
                    ft.Text("Powered by Google Gemini AI", size=11, italic=True),
                    ft.Text("\n© 2025 - Todos los derechos reservados", size=11),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=280,
            ),            actions=[
                ft.TextButton("Cerrar", on_click=lambda _: self.close_dialog())
            ]
        )
        self.page.dialog = about_dialog
        about_dialog.open = True
        self.page.update()
        
    def close_dialog(self):
        self.page.dialog.open = False
        self.page.update()

def main(page: ft.Page):
    # Add page close handler to prevent threading errors
    def on_window_event(e):
        if e.data == "close":
            page.window_destroy()
    
    page.window_prevent_close = True
    page.on_window_event = on_window_event
    
    app = PaperTranslatorApp(page)

if __name__ == "__main__":
    try:
        ft.app(target=main)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        # Ensure clean exit
        import sys
        sys.exit(0)
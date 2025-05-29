"""
Paper Translator AI - Aplicación para traducir papers académicos
Versión mejorada y simplificada
"""

import os
import io
import base64
import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
import threading

# Flet imports
import flet as ft

# Google AI imports
import google.generativeai as genai

# PDF processing imports
try:
    import PyPDF2
    import pdfplumber
except ImportError:
    print("Instalando dependencias de PDF...")
    os.system("pip install PyPDF2 pdfplumber")
    import PyPDF2
    import pdfplumber

# Text-to-speech imports
try:
    import pyttsx3
except ImportError:
    print("Instalando pyttsx3...")
    os.system("pip install pyttsx3")
    import pyttsx3

# Matplotlib for infographics
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import FancyBboxPatch
    import numpy as np
except ImportError:
    print("Instalando matplotlib...")
    os.system("pip install matplotlib")
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import FancyBboxPatch
    import numpy as np

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de Gemini
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
genai.configure(api_key=API_KEY)

# Modelo
MODEL_GENERAL = genai.GenerativeModel("gemini-1.5-flash")

# Idiomas disponibles
LANGUAGES = {
    "auto": "🌐 Detectar idioma",
    "es": "🇪🇸 Español",
    "en": "🇺🇸 Inglés", 
    "fr": "🇫🇷 Francés",
    "de": "🇩🇪 Alemán",
    "it": "🇮🇹 Italiano",
    "pt": "🇵🇹 Portugués",
    "ja": "🇯🇵 Japonés",
    "ko": "🇰🇷 Coreano",
    "zh": "🇨🇳 Chino",
    "ru": "🇷🇺 Ruso"
}

def with_opacity(opacity: float, color: str) -> str:
    """Helper function para colores con opacidad"""
    if color.startswith("#"):
        color = color[1:]
    
    if len(color) == 3:
        color = ''.join([c*2 for c in color])
    
    try:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16) 
        b = int(color[4:6], 16)
        a = int(opacity * 255)
        return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
    except:
        return "#80808080"

class AppTheme:
    """Tema de la aplicación"""
    PRIMARY = "#2563eb"      # Blue-600
    SECONDARY = "#059669"    # Emerald-600
    BACKGROUND = "#f8fafc"   # Slate-50
    SURFACE = "#ffffff"      # White
    ERROR = "#dc2626"        # Red-600
    SUCCESS = "#16a34a"      # Green-600
    WARNING = "#d97706"      # Amber-600
    ON_PRIMARY = "#ffffff"   # White
    ON_SURFACE = "#1e293b"   # Slate-800
    OUTLINE = "#cbd5e1"      # Slate-300

class PaperTranslatorApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "📄 Paper Translator AI"
        self.page.theme = ft.Theme(
            color_scheme_seed=AppTheme.PRIMARY,
            use_material3=True,
        )
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = AppTheme.BACKGROUND
        self.page.padding = 0
        self.page.window.width = 900
        self.page.window.height = 700
        self.page.window.min_width = 800
        self.page.window.min_height = 600
        self.page.window.resizable = True
        self.page.window.center = True
          # Variables de estado
        self.paper_text = ""
        self.translated_text = ""
        self.summary = ""
        self.chat_history = []
        self.source_lang = "auto"
        self.target_lang = "es"
        self.file_name = ""
        self.tts_engine = None
        self.current_dialog = None  # Para controlar modales
        
        # Crear botón de traducir
        self.translate_button = ft.ElevatedButton(
            text="🔄 Traducir",
            bgcolor=AppTheme.PRIMARY,
            color=AppTheme.ON_PRIMARY,
            disabled=True,
            on_click=self.translate_paper
        )
        
        # Inicializar TTS
        self.init_tts()
        self.setup_ui()
        
    def init_tts(self):
        """Inicializar motor de texto a voz"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
        except Exception as e:
            logger.error(f"Error inicializando TTS: {e}")
            self.tts_engine = None

    def show_snackbar(self, message: str, color: str = None):
        """Mostrar mensaje emergente"""
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.colors.WHITE),
            bgcolor=color or AppTheme.PRIMARY,
            duration=3000,
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()

    def close_dialog(self, e=None):
        """Cerrar modal actual correctamente"""
        if self.current_dialog:
            self.current_dialog.open = False
            self.page.update()
            self.current_dialog = None

    def setup_ui(self):
        """Configurar interfaz simplificada"""
        # File picker
        self.file_picker = ft.FilePicker(on_result=self.file_picked)
        self.page.overlay.append(self.file_picker)

        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Text("📄", size=30),
                ft.Text("Paper Translator AI", 
                       size=24, 
                       weight=ft.FontWeight.BOLD, 
                       color=AppTheme.ON_SURFACE),
                ft.Row([
                    ft.TextButton("❓ Ayuda", on_click=self.show_help),
                    ft.TextButton("ℹ️ Acerca de", on_click=self.show_about),
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=20,
            bgcolor=AppTheme.SURFACE,
            border=ft.border.only(bottom=ft.BorderSide(1, AppTheme.OUTLINE))
        )

        # Área de carga de archivo
        self.upload_btn = ft.ElevatedButton(
            text="📁 Seleccionar PDF",
            bgcolor=AppTheme.PRIMARY,
            color=AppTheme.ON_PRIMARY,
            width=200,
            height=50,
            on_click=lambda _: self.file_picker.pick_files(
                dialog_title="Seleccionar PDF",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"]
            )
        )

        self.file_info = ft.Text("", visible=False, size=14)

        # Selectores de idioma
        lang_row = ft.Row([
            ft.Dropdown(
                label="Idioma origen",
                options=[ft.dropdown.Option(key=k, text=v) for k, v in LANGUAGES.items()],
                value="auto",
                on_change=self.on_source_lang_change,
                width=200,
            ),
            ft.Text("→", size=20, color=AppTheme.PRIMARY),
            ft.Dropdown(
                label="Idioma destino",
                options=[ft.dropdown.Option(key=k, text=v) for k, v in LANGUAGES.items() if k != "auto"],
                value="es",
                on_change=self.on_target_lang_change,
                width=200,
            ),            self.translate_button  # Se creará abajo
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

        # Barra de progreso
        self.progress_bar = ft.ProgressBar(
            value=0,
            width=500,
            color=AppTheme.PRIMARY,
            visible=False
        )

        self.status_text = ft.Text(
            "Selecciona un archivo PDF para comenzar",
            size=14,
            color=AppTheme.ON_SURFACE,
            text_align=ft.TextAlign.CENTER
        )

        # Pestañas principales
        self.tabs = ft.Tabs(
            selected_index=0,
            indicator_color=AppTheme.PRIMARY,
            label_color=AppTheme.PRIMARY,
            tabs=[
                ft.Tab(
                    text="📄 Original",
                    content=self.create_text_tab("original")
                ),
                ft.Tab(
                    text="🔄 Traducción", 
                    content=self.create_text_tab("translation")
                ),
                ft.Tab(
                    text="💬 Chat",
                    content=self.create_chat_tab()
                ),
                ft.Tab(
                    text="📋 Resumen",
                    content=self.create_text_tab("summary")
                ),
                ft.Tab(
                    text="📊 Infografía",
                    content=self.create_infographic_tab()
                )
            ],
            expand=True
        )

        # Layout principal
        main_content = ft.Column([
            header,
            ft.Container(
                content=ft.Column([
                    self.upload_btn,
                    self.file_info,
                    lang_row,
                    self.progress_bar,
                    self.status_text
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                padding=20,
                bgcolor=AppTheme.SURFACE,
                border=ft.border.only(bottom=ft.BorderSide(1, AppTheme.OUTLINE))
            ),
            ft.Container(
                content=self.tabs,
                expand=True,
                padding=10
            )
        ], spacing=0, expand=True)

        self.page.add(main_content)
        self.page.update()

    def create_text_tab(self, tab_type):
        """Crear pestaña de texto genérica"""
        if tab_type == "original":
            title = "Texto Original"
            placeholder = "El texto original aparecerá aquí..."
            actions = []
        elif tab_type == "translation":
            title = "Traducción"
            placeholder = "La traducción aparecerá aquí..."
            actions = [ft.TextButton("🔊 Escuchar", on_click=self.text_to_speech)]
        elif tab_type == "summary":
            title = "Resumen Ejecutivo"
            placeholder = "El resumen se generará automáticamente..."
            actions = []

        content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                    *actions
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.Text(
                        placeholder,
                        size=14,
                        selectable=True
                    ),
                    bgcolor=AppTheme.SURFACE,
                    padding=15,
                    border_radius=10,
                    border=ft.border.all(1, AppTheme.OUTLINE),
                    expand=True
                )
            ], spacing=10, expand=True),
            padding=10
        )

        # Guardar referencias
        if tab_type == "original":
            self.original_text = content.content.controls[1].content
        elif tab_type == "translation":
            self.translation_text = content.content.controls[1].content
        elif tab_type == "summary":
            self.summary_text = content.content.controls[1].content

        return content

    def create_chat_tab(self):
        """Crear pestaña de chat"""
        self.chat_list = ft.ListView(
            spacing=10,
            padding=10,
            auto_scroll=True,
            expand=True
        )

        self.chat_input = ft.TextField(
            hint_text="Escribe tu pregunta sobre el paper...",
            expand=True,
            on_submit=self.send_chat_message,
            border_color=AppTheme.OUTLINE
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("Chat con el Paper", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.chat_list,
                    bgcolor=AppTheme.SURFACE,
                    border_radius=10,
                    border=ft.border.all(1, AppTheme.OUTLINE),
                    height=300,
                    padding=5
                ),
                ft.Row([
                    self.chat_input,
                    ft.TextButton("📤", on_click=self.send_chat_message)
                ], spacing=10)
            ], spacing=10, expand=True),
            padding=10
        )

    def create_infographic_tab(self):
        """Crear pestaña de infografía"""
        self.infographic_container = ft.Container(
            content=ft.Text(
                "Haz clic en 'Generar' para crear una infografía del paper",
                size=14,
                text_align=ft.TextAlign.CENTER
            ),
            bgcolor=AppTheme.SURFACE,
            padding=20,
            border_radius=10,
            border=ft.border.all(1, AppTheme.OUTLINE),
            expand=True,
            alignment=ft.alignment.center
        )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Infografía", size=18, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        text="📊 Generar",
                        on_click=self.generate_infographic,
                        bgcolor=AppTheme.SECONDARY,
                        color=AppTheme.ON_PRIMARY
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.infographic_container
            ], spacing=10, expand=True),
            padding=10
        )

    def file_picked(self, e: ft.FilePickerResultEvent):
        """Manejar selección de archivo"""
        if not e.files:
            return
            
        file = e.files[0]
        self.file_name = file.name
        
        # Mostrar info del archivo
        self.file_info.value = f"📄 {file.name} ({file.size / 1024:.1f} KB)"
        self.file_info.visible = True
          # Habilitar botón traducir
        self.translate_button.disabled = False
        
        self.status_text.value = "¡Archivo cargado! Listo para traducir."
        
        # Leer PDF
        try:
            with open(file.path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                self.paper_text = text
                self.original_text.value = text
                
        except Exception as error:
            self.show_snackbar(f"Error al leer PDF: {str(error)}", AppTheme.ERROR)
            logger.error(f"Error reading PDF: {error}")
        
        self.page.update()

    async def translate_paper(self, e):
        """Traducir el paper"""
        if not self.paper_text:
            self.show_snackbar("Selecciona un archivo PDF primero", AppTheme.ERROR)
            return
        
        self.progress_bar.visible = True
        self.progress_bar.value = 0
        self.status_text.value = "Traduciendo..."
        self.page.update()
        
        try:
            # Dividir en chunks
            chunk_size = 3000
            chunks = [self.paper_text[i:i+chunk_size] for i in range(0, len(self.paper_text), chunk_size)]
            translated_chunks = []
            
            for i, chunk in enumerate(chunks):
                self.progress_bar.value = (i + 1) / len(chunks) * 0.8
                self.page.update()
                
                prompt = f"""
                Traduce el siguiente texto académico del {LANGUAGES.get(self.source_lang, 'idioma detectado')} al {LANGUAGES[self.target_lang]}.
                Mantén el formato y términos técnicos.
                
                Texto: {chunk}
                """
                
                response = await asyncio.to_thread(MODEL_GENERAL.generate_content, prompt)
                translated_chunks.append(response.text)
                await asyncio.sleep(0.5)
            
            self.translated_text = "\n".join(translated_chunks)
            self.translation_text.value = self.translated_text
            
            # Generar resumen
            self.progress_bar.value = 0.9
            self.status_text.value = "Generando resumen..."
            self.page.update()
            
            await self.generate_summary()
            
            self.progress_bar.value = 1.0
            self.status_text.value = "✅ ¡Traducción completada!"
            self.show_snackbar("Traducción completada exitosamente", AppTheme.SUCCESS)
            
            # Cambiar a pestaña traducción
            self.tabs.selected_index = 1
            
        except Exception as error:
            self.show_snackbar(f"Error: {str(error)}", AppTheme.ERROR)
            logger.error(f"Translation error: {error}")
        finally:
            self.progress_bar.visible = False
            self.page.update()

    async def generate_summary(self):
        """Generar resumen"""
        try:
            prompt = f"""
            Genera un resumen ejecutivo del siguiente paper:
            1. Objetivos principales
            2. Metodología
            3. Resultados clave
            4. Conclusiones
            5. Implicaciones
            
            Paper: {self.translated_text[:4000]}
            """
            
            response = await asyncio.to_thread(MODEL_GENERAL.generate_content, prompt)
            self.summary = response.text
            self.summary_text.value = self.summary
            
        except Exception as error:
            logger.error(f"Summary error: {error}")

    async def send_chat_message(self, e):
        """Enviar mensaje de chat"""
        if not self.translated_text:
            self.show_snackbar("Traduce un paper primero", AppTheme.ERROR)
            return
        
        message = self.chat_input.value.strip()
        if not message:
            return
        
        self.chat_input.value = ""
        
        # Agregar mensaje usuario
        user_bubble = self.create_chat_bubble(message, True)
        self.chat_list.controls.append(user_bubble)
        
        # Indicador de escritura
        typing = ft.Container(
            content=ft.Text("💭 AI está pensando...", size=12, italic=True),
            padding=10
        )
        self.chat_list.controls.append(typing)
        self.page.update()
        
        try:
            prompt = f"""
            Responde la pregunta sobre este paper académico:
            
            Paper: {self.translated_text[:3000]}
            
            Pregunta: {message}
            
            Responde de manera clara y académica.
            """
            
            response = await asyncio.to_thread(MODEL_GENERAL.generate_content, prompt)
            
            # Remover indicador
            self.chat_list.controls.remove(typing)
            
            # Agregar respuesta
            ai_bubble = self.create_chat_bubble(response.text, False)
            self.chat_list.controls.append(ai_bubble)
            
        except Exception as error:
            self.chat_list.controls.remove(typing)
            error_bubble = self.create_chat_bubble(f"Error: {str(error)}", False)
            self.chat_list.controls.append(error_bubble)
        
        self.page.update()

    def create_chat_bubble(self, message, is_user):
        """Crear burbuja de chat"""
        return ft.Container(
            content=ft.Column([
                ft.Text("Tú" if is_user else "🤖 AI", size=10, weight=ft.FontWeight.BOLD),
                ft.Text(message, size=14, selectable=True)
            ], spacing=5),
            bgcolor=with_opacity(0.1, AppTheme.PRIMARY if is_user else AppTheme.SECONDARY),
            padding=10,
            border_radius=10,
            margin=ft.margin.only(
                left=50 if is_user else 0,
                right=0 if is_user else 50,
                bottom=10
            )
        )

    async def generate_infographic(self, e):
        """Generar infografía"""
        if not self.translated_text:
            self.show_snackbar("Traduce un paper primero", AppTheme.ERROR)
            return
        
        self.infographic_container.content = ft.Column([
            ft.Text("⏳", size=50),
            ft.Text("Generando infografía...", size=16)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
        
        try:
            # Crear infografía simple
            img_base64 = await self.create_simple_infographic()
            
            self.infographic_container.content = ft.Column([
                ft.Image(src_base64=img_base64, width=500, height=600, fit=ft.ImageFit.CONTAIN),
                ft.ElevatedButton(
                    text="💾 Descargar",
                    on_click=lambda _: self.download_infographic(img_base64),
                    bgcolor=AppTheme.SECONDARY
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
            
            self.show_snackbar("Infografía generada", AppTheme.SUCCESS)
            
        except Exception as error:
            self.infographic_container.content = ft.Text(
                f"Error: {str(error)}", 
                color=AppTheme.ERROR
            )
        
        self.page.update()

    async def create_simple_infographic(self):
        """Crear infografía simple"""
        def create_plot():
            fig, ax = plt.subplots(figsize=(8, 10))
            fig.patch.set_facecolor('white')
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 12)
            ax.axis('off')
            
            # Título
            ax.text(5, 11, "📄 Paper Summary", fontsize=20, fontweight='bold', ha='center')
            
            # Contenido simplificado
            content = [
                "📋 Resumen del Paper",
                f"📄 Archivo: {self.file_name[:30]}...",
                f"🌐 Traducido a: {LANGUAGES[self.target_lang]}",
                "✅ Procesado con IA"
            ]
            
            for i, text in enumerate(content):
                ax.text(1, 9-i*1.5, text, fontsize=12, ha='left')
            
            # Guardar como base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return img_base64
        
        return await asyncio.to_thread(create_plot)

    def download_infographic(self, img_base64):
        """Descargar infografía"""
        try:
            img_data = base64.b64decode(img_base64)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"infografia_{timestamp}.png"
            
            with open(filename, 'wb') as f:
                f.write(img_data)
            
            self.show_snackbar(f"Guardado como {filename}", AppTheme.SUCCESS)
            
        except Exception as error:
            self.show_snackbar(f"Error al guardar: {str(error)}", AppTheme.ERROR)

    def text_to_speech(self, e):
        """Leer texto en voz alta"""
        if not self.translated_text:
            self.show_snackbar("No hay texto para leer", AppTheme.ERROR)
            return
        
        if not self.tts_engine:
            self.show_snackbar("TTS no disponible", AppTheme.ERROR)
            return
        
        try:
            text_to_read = self.translated_text[:500] + "..."
            
            def speak():
                self.tts_engine.say(text_to_read)
                self.tts_engine.runAndWait()
            
            threading.Thread(target=speak, daemon=True).start()
            self.show_snackbar("🔊 Reproduciendo audio...", AppTheme.SUCCESS)
            
        except Exception as error:
            self.show_snackbar(f"Error TTS: {str(error)}", AppTheme.ERROR)

    def on_source_lang_change(self, e):
        """Cambio idioma origen"""
        self.source_lang = e.control.value

    def on_target_lang_change(self, e):
        """Cambio idioma destino"""
        self.target_lang = e.control.value

    def show_help(self, e):
        """Mostrar ayuda con modal que se cierra correctamente"""
        self.current_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("❓ Ayuda - Paper Translator AI"),
            content=ft.Text("""
📋 Cómo usar la aplicación:

1. 📁 Selecciona un archivo PDF
2. 🌐 Elige idiomas origen y destino  
3. 🔄 Haz clic en 'Traducir'
4. 💬 Usa el chat para preguntas
5. 📋 Revisa el resumen automático
6. 📊 Genera infografías

💡 Consejos:
• PDFs con texto seleccionable funcionan mejor
• La traducción puede tomar varios minutos
• El chat usa IA para responder sobre el contenido
            """, size=14),
            actions=[
                ft.TextButton("✅ Entendido", on_click=self.close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(self.current_dialog)
        self.current_dialog.open = True
        self.page.update()

    def show_about(self, e):
        """Mostrar información con modal que se cierra correctamente"""
        self.current_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("ℹ️ Acerca de Paper Translator AI"),
            content=ft.Text("""
📄 Paper Translator AI v2.0

Una aplicación moderna para traducir papers académicos.

✨ Características:
• 🤖 Traducción con Gemini AI
• 💬 Chat inteligente
• 📝 Resúmenes automáticos
• 📊 Infografías visuales
• 🔊 Texto a voz

🛠️ Tecnologías:
• Flet (Flutter para Python)
• Google Gemini AI
• PyPDF2 & pdfplumber
• Matplotlib
• pyttsx3

© 2024 Paper Translator AI - Versión Mejorada
            """, size=14),
            actions=[
                ft.TextButton("🚀 ¡Genial!", on_click=self.close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(self.current_dialog)
        self.current_dialog.open = True
        self.page.update()

def main(page: ft.Page):
    """Función principal"""
    app = PaperTranslatorApp(page)

if __name__ == "__main__":
    ft.app(target=main)

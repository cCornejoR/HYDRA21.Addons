# settings.py - Configuraciones mejoradas para HYDRA21 PDF Compressor
import os
from pathlib import Path

# Configuraciones de Ghostscript
GS_PRESETS = {
    "Máxima Calidad": "/prepress",
    "Alta Calidad": "/printer", 
    "Calidad Media": "/ebook",
    "Baja Calidad": "/screen"
}

# Configuración por defecto
DEFAULT_PRESET = "Calidad Media"

# Archivos de configuración
CONFIG_FILE = "gs_config.json"
LOG_FILE = "compressor.log"

# Rutas
OUTPUT_DIR = "output"
TEMP_DIR = "temp"
ASSETS_DIR = "assets"

# Configuraciones de UI - Colores
class Colors:
    # Paleta principal
    PRIMARY = "#6366f1"
    PRIMARY_DARK = "#4f46e5"
    PRIMARY_LIGHT = "#a5b4fc"
    
    SECONDARY = "#8b5cf6"
    SECONDARY_DARK = "#7c3aed"
    SECONDARY_LIGHT = "#c4b5fd"
    
    # Estados
    SUCCESS = "#10b981"
    SUCCESS_DARK = "#059669"
    SUCCESS_LIGHT = "#6ee7b7"
    
    WARNING = "#f59e0b"
    WARNING_DARK = "#d97706"
    WARNING_LIGHT = "#fcd34d"
    
    ERROR = "#ef4444"
    ERROR_DARK = "#dc2626"
    ERROR_LIGHT = "#fca5a5"
    
    INFO = "#3b82f6"
    INFO_DARK = "#2563eb"
    INFO_LIGHT = "#93c5fd"
    
    # Neutros
    BACKGROUND_LIGHT = "#f8fafc"
    BACKGROUND_DARK = "#0f172a"
    
    SURFACE_LIGHT = "#ffffff"
    SURFACE_DARK = "#1e293b"
    
    TEXT_PRIMARY_LIGHT = "#1e293b"
    TEXT_PRIMARY_DARK = "#f1f5f9"
    
    TEXT_SECONDARY_LIGHT = "#64748b"
    TEXT_SECONDARY_DARK = "#94a3b8"
    
    BORDER_LIGHT = "#e2e8f0"
    BORDER_DARK = "#334155"

# Configuraciones de UI - Tipografía
class Typography:
    FONT_FAMILY = "Segoe UI"
    
    # Tamaños
    SIZE_XS = 12
    SIZE_SM = 14
    SIZE_BASE = 16
    SIZE_LG = 18
    SIZE_XL = 20
    SIZE_2XL = 24
    SIZE_3XL = 30
    SIZE_4XL = 36
    
    # Pesos
    WEIGHT_NORMAL = "normal"
    WEIGHT_MEDIUM = "w500"
    WEIGHT_SEMIBOLD = "w600"
    WEIGHT_BOLD = "bold"

# Configuraciones de UI - Espaciado
class Spacing:
    XS = 4
    SM = 8
    BASE = 12
    MD = 16
    LG = 20
    XL = 24
    XXL = 32
    XXXL = 48

# Configuraciones de UI - Bordes
class Borders:
    RADIUS_SM = 6
    RADIUS_BASE = 8
    RADIUS_MD = 12
    RADIUS_LG = 16
    RADIUS_XL = 20
    RADIUS_FULL = 9999

# Configuraciones de UI - Sombras
class Shadows:
    SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    BASE = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)"
    MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

# Configuraciones de animación
class Animations:
    DURATION_FAST = 150
    DURATION_BASE = 200
    DURATION_SLOW = 300
    
    EASING_LINEAR = "linear"
    EASING_EASE = "ease"
    EASING_EASE_IN = "ease-in"
    EASING_EASE_OUT = "ease-out"
    EASING_EASE_IN_OUT = "ease-in-out"

# Configuraciones de la aplicación
class App:
    NAME = "HYDRA21 PDF Compressor"
    VERSION = "2.0.0"
    AUTHOR = "HYDRA21"
    DESCRIPTION = "Compresor de PDF profesional con interfaz moderna"
    
    # Ventana
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 900
    WINDOW_MIN_WIDTH = 600
    WINDOW_MIN_HEIGHT = 700
    
    # Archivos soportados
    SUPPORTED_EXTENSIONS = [".pdf"]
    MAX_FILE_SIZE_MB = 500

# Configuraciones de Ghostscript específicas
class Ghostscript:
    # Rutas comunes de Ghostscript en Windows
    WINDOWS_PATHS = [
        r"C:\Program Files\gs\gs*\bin\gswin64c.exe",
        r"C:\Program Files (x86)\gs\gs*\bin\gswin32c.exe",
        r"C:\gs\gs*\bin\gswin64c.exe",
        r"C:\gs\gs*\bin\gswin32c.exe"
    ]
    
    # Comandos para diferentes sistemas
    UNIX_COMMAND = "gs"
    
    # Parámetros base
    BASE_PARAMS = [
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH"
    ]
    
    # Timeout para verificación
    VERIFICATION_TIMEOUT = 5
    
    # Texto esperado en la salida de version
    VERSION_KEYWORDS = ["GPL Ghostscript", "Artifex Ghostscript"]

# Configuraciones de logging
class Logging:
    LEVEL = "INFO"
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    BACKUP_COUNT = 3

# Configuraciones de rendimiento
class Performance:
    THREAD_TIMEOUT = 30
    MAX_CONCURRENT_COMPRESSIONS = 1
    CLEANUP_TEMP_ON_EXIT = True

# Mensajes de la aplicación
class Messages:
    # Éxito
    SUCCESS_COMPRESSION = "¡PDF comprimido exitosamente!"
    SUCCESS_GS_CONFIGURED = "Ghostscript configurado correctamente"
    
    # Errores
    ERROR_NO_FILE = "Por favor selecciona un archivo PDF"
    ERROR_GS_NOT_FOUND = "Ghostscript no encontrado en el sistema"
    ERROR_GS_NOT_VERIFIED = "Ghostscript no está verificado"
    ERROR_COMPRESSION_FAILED = "Error al comprimir el PDF"
    ERROR_FILE_TOO_LARGE = f"El archivo es demasiado grande (máximo {App.MAX_FILE_SIZE_MB}MB)"
    ERROR_INVALID_FILE = "El archivo seleccionado no es un PDF válido"
    
    # Información
    INFO_DETECTING_GS = "Detectando Ghostscript..."
    INFO_COMPRESSING = "Comprimiendo PDF..."
    INFO_VERIFYING_GS = "Verificando Ghostscript..."
    
    # Warnings
    WARNING_GS_NOT_OPTIMAL = "Ghostscript encontrado pero puede no ser la versión óptima"

# Funciones utilitarias
def ensure_directories():
    """Crear directorios necesarios si no existen"""
    directories = [OUTPUT_DIR, TEMP_DIR, ASSETS_DIR]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def get_config_path() -> Path:
    """Obtener ruta del archivo de configuración"""
    return Path.cwd() / CONFIG_FILE

def get_log_path() -> Path:
    """Obtener ruta del archivo de log"""
    return Path.cwd() / LOG_FILE

def is_debug_mode() -> bool:
    """Verificar si está en modo debug"""
    return os.getenv("DEBUG", "false").lower() == "true"

# Configuración inicial
def init_settings():
    """Inicializar configuraciones"""
    ensure_directories()
    
    # Configurar logging si es necesario
    if is_debug_mode():
        import logging
        logging.basicConfig(
            level=getattr(logging, Logging.LEVEL),
            format=Logging.FORMAT,
            handlers=[
                logging.FileHandler(get_log_path()),
                logging.StreamHandler()
            ]
        )

# Ejecutar inicialización al importar
init_settings()
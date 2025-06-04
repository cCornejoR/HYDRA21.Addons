"""
Configuration settings for HYDRA21 PDF Compressor - PROGRAMA_OK
Complete PDF processing application with modern UI
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Application Information
APP_NAME = "HYDRA21 PDF Compressor Pro"
APP_VERSION = "3.0.0"
APP_AUTHOR = "HYDRA21"
APP_DESCRIPTION = "Professional PDF processing tool with modern interface"

# Window Configuration
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 700
WINDOW_MIN_HEIGHT = 500

# File Configuration
SUPPORTED_EXTENSIONS = [".pdf"]
MAX_FILE_SIZE_MB = 1000  # 1GB max file size
MAX_BATCH_FILES = 100

# Ghostscript Quality Presets
GS_QUALITY_PRESETS = {
    "high": {
        "name": "Alta Calidad",
        "setting": "/prepress",
        "description": "Máxima calidad para impresión profesional"
    },
    "medium": {
        "name": "Calidad Media", 
        "setting": "/ebook",
        "description": "Balance entre calidad y tamaño de archivo"
    },
    "low": {
        "name": "Baja Calidad",
        "setting": "/screen",
        "description": "Máxima compresión para visualización en pantalla"
    }
}

DEFAULT_QUALITY = "medium"

# Directory Configuration
@dataclass
class DirectoryConfig:
    """Configuration for application directories"""
    output_dir: Path
    temp_dir: Path
    config_dir: Path
    
    @classmethod
    def get_default(cls) -> 'DirectoryConfig':
        """Get default directory configuration"""
        home = Path.home()
        base_dir = home / "Documents" / "HYDRA21-PDFCompressor-Pro"
        
        return cls(
            output_dir=base_dir / "output",
            temp_dir=base_dir / "temp", 
            config_dir=base_dir / "config"
        )
    
    def ensure_directories(self):
        """Create directories if they don't exist"""
        for directory in [self.output_dir, self.temp_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)

# Theme Configuration
THEME_CONFIG = {
    "light": {
        # Primary colors (blue scheme)
        "primary": "#2563eb",
        "primary_variant": "#1d4ed8",
        "primary_light": "#60a5fa",
        
        # Secondary colors
        "secondary": "#7c3aed",
        "secondary_variant": "#6d28d9",
        "accent": "#059669",
        
        # Background colors
        "background": "#f8fafc",
        "surface": "#ffffff",
        "surface_variant": "#f1f5f9",
        "surface_container": "#e2e8f0",
        
        # Text colors
        "on_surface": "#0f172a",
        "on_surface_variant": "#64748b",
        "on_primary": "#ffffff",
        "on_background": "#1e293b",
        
        # Status colors
        "success": "#059669",
        "warning": "#f59e0b", 
        "error": "#dc2626",
        "info": "#3b82f6",
        
        # Status containers
        "success_container": "#ecfdf5",
        "warning_container": "#fffbeb",
        "error_container": "#fef2f2",
        "info_container": "#eff6ff",
        
        # Borders and dividers
        "border": "#e2e8f0",
        "border_variant": "#cbd5e1",
        "divider": "#e2e8f0",
        
        # Buttons
        "button_primary_bg": "#2563eb",
        "button_primary_hover": "#1d4ed8",
        "button_secondary_bg": "#f1f5f9",
        "button_secondary_hover": "#e2e8f0",
        
        # Inputs
        "input_border": "#d1d5db",
        "input_focused_border": "#2563eb",
        "input_bg": "#ffffff",
        
        # Overlays (no shadows per user preference)
        "overlay_light": "rgba(255, 255, 255, 0.8)",
        "overlay_dark": "rgba(0, 0, 0, 0.3)",
    },
    "dark": {
        # Primary colors (blue scheme)
        "primary": "#3b82f6",
        "primary_variant": "#2563eb",
        "primary_light": "#93c5fd",
        
        # Secondary colors
        "secondary": "#8b5cf6",
        "secondary_variant": "#7c3aed",
        "accent": "#10b981",
        
        # Background colors
        "background": "#0f172a",
        "surface": "#1e293b",
        "surface_variant": "#334155",
        "surface_container": "#475569",
        
        # Text colors
        "on_surface": "#f1f5f9",
        "on_surface_variant": "#94a3b8",
        "on_primary": "#ffffff",
        "on_background": "#e2e8f0",
        
        # Status colors
        "success": "#10b981",
        "warning": "#fbbf24",
        "error": "#ef4444",
        "info": "#3b82f6",
        
        # Status containers
        "success_container": "#064e3b",
        "warning_container": "#92400e",
        "error_container": "#991b1b",
        "info_container": "#1e3a8a",
        
        # Borders and dividers
        "border": "#334155",
        "border_variant": "#475569",
        "divider": "#334155",
        
        # Buttons
        "button_primary_bg": "#3b82f6",
        "button_primary_hover": "#2563eb",
        "button_secondary_bg": "#334155",
        "button_secondary_hover": "#475569",
        
        # Inputs
        "input_border": "#475569",
        "input_focused_border": "#3b82f6",
        "input_bg": "#1e293b",
        
        # Overlays
        "overlay_light": "rgba(255, 255, 255, 0.1)",
        "overlay_dark": "rgba(0, 0, 0, 0.6)",
    }
}

# Animation Configuration
ANIMATION_CONFIG = {
    "duration_fast": 150,
    "duration_normal": 300,
    "duration_slow": 500,
    "easing_ease_out": "ease-out",
    "easing_ease_in_out": "ease-in-out"
}

# Progress Configuration
PROGRESS_CONFIG = {
    "update_interval": 100,  # milliseconds
    "spinner_size": 40,
    "progress_bar_height": 8
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    "rotation": "10 MB",
    "retention": "1 week"
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "max_concurrent_operations": 1,
    "operation_timeout": 300,  # 5 minutes
    "cleanup_temp_on_exit": True
}

# Messages
MESSAGES = {
    # Success messages
    "success_compression": "¡PDF comprimido exitosamente!",
    "success_merge": "¡PDFs fusionados exitosamente!",
    "success_split": "¡PDF dividido exitosamente!",
    "success_batch": "¡Procesamiento por lotes completado!",
    
    # Error messages
    "error_no_file": "Por favor selecciona al menos un archivo PDF",
    "error_gs_not_found": "Ghostscript no encontrado. Por favor configúralo en el tutorial.",
    "error_file_too_large": f"El archivo es demasiado grande (máximo {MAX_FILE_SIZE_MB}MB)",
    "error_invalid_file": "El archivo seleccionado no es un PDF válido",
    "error_operation_failed": "La operación falló. Revisa los detalles del error.",
    
    # Info messages
    "info_processing": "Procesando archivo...",
    "info_detecting_gs": "Detectando Ghostscript...",
    "info_batch_processing": "Procesando archivos por lotes...",
    
    # Tutorial messages
    "tutorial_welcome": "¡Bienvenido a HYDRA21 PDF Compressor Pro!",
    "tutorial_gs_setup": "Configuremos Ghostscript para comenzar",
}

def get_app_config() -> Dict:
    """Get complete application configuration"""
    return {
        "app": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "author": APP_AUTHOR,
            "description": APP_DESCRIPTION
        },
        "window": {
            "width": WINDOW_WIDTH,
            "height": WINDOW_HEIGHT,
            "min_width": WINDOW_MIN_WIDTH,
            "min_height": WINDOW_MIN_HEIGHT
        },
        "files": {
            "supported_extensions": SUPPORTED_EXTENSIONS,
            "max_file_size_mb": MAX_FILE_SIZE_MB,
            "max_batch_files": MAX_BATCH_FILES
        },
        "ghostscript": {
            "quality_presets": GS_QUALITY_PRESETS,
            "default_quality": DEFAULT_QUALITY
        },
        "theme": THEME_CONFIG,
        "animation": ANIMATION_CONFIG,
        "progress": PROGRESS_CONFIG,
        "logging": LOGGING_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "messages": MESSAGES
    }

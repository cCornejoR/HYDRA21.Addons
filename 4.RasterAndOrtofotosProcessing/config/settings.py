"""
HYDRA21 Orthophoto Processor Pro - Configuration Settings
Professional orthophoto processing application configuration
"""

import os
from pathlib import Path
from typing import Dict, List, Any

# Application Information
APP_NAME = "HYDRA21 Orthophoto Processor Pro"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Professional orthophoto processing with geospatial data preservation"

# Directory Configuration
class DirectoryConfig:
    """Directory configuration for the application"""
    
    @staticmethod
    def get_app_dir() -> Path:
        """Get application directory"""
        return Path(__file__).parent.parent
    
    @staticmethod
    def get_output_dir() -> Path:
        """Get output directory for processed files"""
        output_dir = DirectoryConfig.get_app_dir() / "output"
        output_dir.mkdir(exist_ok=True)
        return output_dir
    
    @staticmethod
    def get_temp_dir() -> Path:
        """Get temporary directory for processing"""
        temp_dir = DirectoryConfig.get_app_dir() / "temp"
        temp_dir.mkdir(exist_ok=True)
        return temp_dir
    
    @staticmethod
    def get_config_dir() -> Path:
        """Get configuration directory"""
        config_dir = DirectoryConfig.get_app_dir() / "config"
        config_dir.mkdir(exist_ok=True)
        return config_dir

# Supported File Formats
SUPPORTED_INPUT_FORMATS = [
    ".tif", ".tiff",  # GeoTIFF files
    ".ecw",           # ECW compressed files
    ".jp2",           # JPEG 2000
    ".img",           # ERDAS IMAGINE
    ".bil", ".bip", ".bsq",  # ENVI formats
]

SUPPORTED_OUTPUT_FORMATS = {
    "GeoTIFF": {
        "extension": ".tif",
        "driver": "GTiff",
        "description": "GeoTIFF with georeferenciation",
        "compression_options": ["LZW", "DEFLATE", "JPEG", "PACKBITS"]
    },
    "JPEG": {
        "extension": ".jpg",
        "driver": "JPEG",
        "description": "JPEG with world file",
        "compression_options": ["JPEG"]
    },
    "PNG": {
        "extension": ".png",
        "driver": "PNG",
        "description": "PNG with world file",
        "compression_options": ["DEFLATE"]
    },
    "ECW": {
        "extension": ".ecw",
        "driver": "ECW",
        "description": "Enhanced Compression Wavelet",
        "compression_options": ["ECW"]
    }
}

# Theme Configuration - Blue Color Scheme
THEME_CONFIG = {
    "light": {
        # Primary colors (blue scheme) - Improved for light mode
        "primary": "#1d4ed8",
        "primary_variant": "#1e40af",
        "primary_light": "#3b82f6",

        # Secondary colors
        "secondary": "#7c3aed",
        "secondary_variant": "#6d28d9",
        "accent": "#059669",

        # Background colors - Better contrast
        "background": "#f8fafc",
        "surface": "#ffffff",
        "surface_variant": "#f1f5f9",
        "surface_container": "#e2e8f0",

        # Text colors - Improved readability
        "on_surface": "#0f172a",
        "on_surface_variant": "#475569",
        "on_primary": "#ffffff",
        "on_background": "#1e293b",

        # Status colors
        "success": "#059669",
        "warning": "#d97706",
        "error": "#dc2626",
        "info": "#1d4ed8",

        # Status containers - Better visibility
        "success_container": "#ecfdf5",
        "warning_container": "#fef3c7",
        "error_container": "#fef2f2",
        "info_container": "#dbeafe",

        # Borders and dividers - More visible
        "border": "#d1d5db",
        "border_variant": "#9ca3af",
        "divider": "#d1d5db",

        # Buttons - Better contrast
        "button_primary_bg": "#1d4ed8",
        "button_primary_hover": "#1e40af",
        "button_secondary_bg": "#f3f4f6",
        "button_secondary_hover": "#e5e7eb",

        # Inputs - Better visibility
        "input_border": "#9ca3af",
        "input_focused_border": "#1d4ed8",
        "input_bg": "#ffffff",

        # Overlays
        "overlay_light": "rgba(255, 255, 255, 0.95)",
        "overlay_dark": "rgba(0, 0, 0, 0.5)",
    },
    
    "dark": {
        # Primary colors (blue scheme) - Improved for dark mode
        "primary": "#60a5fa",
        "primary_variant": "#3b82f6",
        "primary_light": "#93c5fd",

        # Secondary colors
        "secondary": "#a78bfa",
        "secondary_variant": "#8b5cf6",
        "accent": "#34d399",

        # Background colors - Better contrast
        "background": "#0f172a",
        "surface": "#1e293b",
        "surface_variant": "#334155",
        "surface_container": "#475569",

        # Text colors - Improved readability
        "on_surface": "#f8fafc",
        "on_surface_variant": "#cbd5e1",
        "on_primary": "#0f172a",
        "on_background": "#f1f5f9",

        # Status colors - Better visibility in dark mode
        "success": "#34d399",
        "warning": "#fbbf24",
        "error": "#f87171",
        "info": "#60a5fa",

        # Status containers - Improved contrast
        "success_container": "#064e3b",
        "warning_container": "#92400e",
        "error_container": "#991b1b",
        "info_container": "#1e3a8a",

        # Borders and dividers - Better visibility
        "border": "#475569",
        "border_variant": "#64748b",
        "divider": "#475569",

        # Buttons - Improved contrast
        "button_primary_bg": "#60a5fa",
        "button_primary_hover": "#3b82f6",
        "button_secondary_bg": "#475569",
        "button_secondary_hover": "#64748b",

        # Inputs - Better visibility
        "input_border": "#64748b",
        "input_focused_border": "#60a5fa",
        "input_bg": "#334155",

        # Overlays
        "overlay_light": "rgba(255, 255, 255, 0.1)",
        "overlay_dark": "rgba(0, 0, 0, 0.7)",
    }
}

# Processing Configuration
PROCESSING_CONFIG = {
    "max_memory_usage": 0.8,  # 80% of available memory
    "chunk_size": 1024,       # Processing chunk size in MB
    "max_workers": 4,         # Maximum number of worker threads
    "progress_update_interval": 0.1,  # Progress update interval in seconds
}

# Compression Quality Presets
COMPRESSION_PRESETS = {
    "lossless": {
        "name": "Sin pérdida",
        "description": "Máxima calidad, mayor tamaño",
        "compression": "LZW",
        "quality": None,
        "predictor": 2
    },
    "high": {
        "name": "Alta calidad",
        "description": "Excelente calidad, tamaño moderado",
        "compression": "DEFLATE",
        "quality": 95,
        "predictor": 2
    },
    "medium": {
        "name": "Calidad media",
        "description": "Buena calidad, tamaño reducido",
        "compression": "JPEG",
        "quality": 85,
        "predictor": None
    },
    "low": {
        "name": "Calidad básica",
        "description": "Calidad aceptable, tamaño mínimo",
        "compression": "JPEG",
        "quality": 70,
        "predictor": None
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

def get_app_config() -> Dict[str, Any]:
    """Get complete application configuration"""
    return {
        "app_info": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "description": APP_DESCRIPTION
        },
        "directories": {
            "app_dir": str(DirectoryConfig.get_app_dir()),
            "output_dir": str(DirectoryConfig.get_output_dir()),
            "temp_dir": str(DirectoryConfig.get_temp_dir()),
            "config_dir": str(DirectoryConfig.get_config_dir())
        },
        "formats": {
            "input": SUPPORTED_INPUT_FORMATS,
            "output": SUPPORTED_OUTPUT_FORMATS
        },
        "themes": THEME_CONFIG,
        "processing": PROCESSING_CONFIG,
        "compression": COMPRESSION_PRESETS,
        "animation": ANIMATION_CONFIG,
        "progress": PROGRESS_CONFIG
    }

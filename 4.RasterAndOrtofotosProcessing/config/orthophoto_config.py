"""
HYDRA21 Orthophoto Processor Pro - Geospatial Configuration
Configuration for geospatial data processing and orthophoto handling
"""

from typing import Dict, List, Tuple, Optional
import os

# GDAL Configuration
GDAL_CONFIG = {
    "GDAL_CACHEMAX": "512",  # Cache size in MB
    "GDAL_NUM_THREADS": "ALL_CPUS",
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "VSI_CACHE": "TRUE",
    "VSI_CACHE_SIZE": "25000000",  # 25MB
    "GDAL_HTTP_TIMEOUT": "30",
    "GDAL_HTTP_CONNECTTIMEOUT": "10"
}

# Coordinate Reference Systems (CRS) commonly used in orthophotos
COMMON_CRS = {
    "EPSG:4326": {
        "name": "WGS 84",
        "description": "World Geodetic System 1984",
        "type": "Geographic"
    },
    "EPSG:3857": {
        "name": "Web Mercator",
        "description": "WGS 84 / Pseudo-Mercator",
        "type": "Projected"
    },
    "EPSG:32717": {
        "name": "UTM Zone 17S",
        "description": "WGS 84 / UTM zone 17S",
        "type": "Projected"
    },
    "EPSG:32718": {
        "name": "UTM Zone 18S",
        "description": "WGS 84 / UTM zone 18S",
        "type": "Projected"
    },
    "EPSG:25830": {
        "name": "ETRS89 UTM 30N",
        "description": "ETRS89 / UTM zone 30N",
        "type": "Projected"
    },
    "EPSG:2154": {
        "name": "RGF93 Lambert 93",
        "description": "Réseau Géodésique Français 1993",
        "type": "Projected"
    }
}

# Resampling methods for orthophoto processing
RESAMPLING_METHODS = {
    "nearest": {
        "name": "Vecino más cercano",
        "description": "Rápido, preserva valores originales",
        "use_case": "Datos categóricos, mapas de clasificación"
    },
    "bilinear": {
        "name": "Bilineal",
        "description": "Suavizado moderado, buena velocidad",
        "use_case": "Imágenes continuas, ortofotografías"
    },
    "cubic": {
        "name": "Cúbico",
        "description": "Suavizado alto, mejor calidad visual",
        "use_case": "Visualización, ampliación de imágenes"
    },
    "lanczos": {
        "name": "Lanczos",
        "description": "Máxima calidad, más lento",
        "use_case": "Procesamiento de alta calidad"
    }
}

# Compression options for different output formats
COMPRESSION_OPTIONS = {
    "GTiff": {
        "LZW": {
            "name": "LZW",
            "description": "Sin pérdida, buena compresión",
            "options": {"COMPRESS": "LZW", "PREDICTOR": "2"}
        },
        "DEFLATE": {
            "name": "DEFLATE",
            "description": "Sin pérdida, compresión rápida",
            "options": {"COMPRESS": "DEFLATE", "PREDICTOR": "2"}
        },
        "JPEG": {
            "name": "JPEG",
            "description": "Con pérdida, alta compresión",
            "options": {"COMPRESS": "JPEG", "JPEG_QUALITY": "85"}
        },
        "PACKBITS": {
            "name": "PACKBITS",
            "description": "Sin pérdida, compresión básica",
            "options": {"COMPRESS": "PACKBITS"}
        }
    },
    "JPEG": {
        "JPEG": {
            "name": "JPEG",
            "description": "Estándar JPEG con calidad ajustable",
            "options": {"QUALITY": "85"}
        }
    },
    "PNG": {
        "DEFLATE": {
            "name": "PNG",
            "description": "Sin pérdida con transparencia",
            "options": {"COMPRESS": "DEFLATE"}
        }
    }
}

# Tile configuration for large orthophoto processing
TILE_CONFIG = {
    "default_tile_size": 512,  # pixels
    "overlap": 64,             # pixels overlap between tiles
    "max_tile_size": 2048,     # maximum tile size
    "min_tile_size": 256       # minimum tile size
}

# Memory management configuration
MEMORY_CONFIG = {
    "max_memory_usage": 0.75,    # 75% of available memory
    "chunk_size_mb": 256,        # Processing chunk size in MB
    "cache_size_mb": 128,        # Cache size for intermediate results
    "gc_threshold": 0.85         # Garbage collection threshold
}

# Quality assessment parameters
QUALITY_METRICS = {
    "compression_ratio_threshold": 0.1,  # Minimum compression ratio
    "max_acceptable_loss": 0.05,         # Maximum acceptable quality loss
    "histogram_bins": 256,               # Bins for histogram analysis
    "sample_size": 1000                  # Sample size for quality assessment
}

# Export profiles for different use cases
EXPORT_PROFILES = {
    "web_mapping": {
        "name": "Mapas Web",
        "description": "Optimizado para visualización web",
        "format": "GTiff",
        "compression": "JPEG",
        "quality": 80,
        "tile_size": 256,
        "overview_levels": [2, 4, 8, 16],
        "crs": "EPSG:3857"
    },
    "gis_analysis": {
        "name": "Análisis GIS",
        "description": "Máxima precisión para análisis",
        "format": "GTiff",
        "compression": "LZW",
        "quality": None,
        "tile_size": 512,
        "overview_levels": [2, 4, 8],
        "preserve_crs": True
    },
    "archive": {
        "name": "Archivo",
        "description": "Almacenamiento a largo plazo",
        "format": "GTiff",
        "compression": "DEFLATE",
        "quality": None,
        "tile_size": 1024,
        "overview_levels": [2, 4, 8, 16, 32],
        "preserve_crs": True
    },
    "visualization": {
        "name": "Visualización",
        "description": "Optimizado para presentación",
        "format": "JPEG",
        "compression": "JPEG",
        "quality": 90,
        "tile_size": None,
        "overview_levels": [],
        "world_file": True
    }
}

# Processing pipeline configuration
PIPELINE_CONFIG = {
    "validate_input": True,
    "create_overviews": True,
    "calculate_statistics": True,
    "preserve_metadata": True,
    "create_world_file": True,
    "verify_output": True
}

# Error handling configuration
ERROR_CONFIG = {
    "max_retries": 3,
    "retry_delay": 1.0,  # seconds
    "continue_on_error": False,
    "log_errors": True,
    "create_error_report": True
}

def get_gdal_options(format_name: str, compression: str, quality: Optional[int] = None) -> Dict[str, str]:
    """Get GDAL creation options for specific format and compression"""
    options = {}
    
    if format_name in COMPRESSION_OPTIONS:
        if compression in COMPRESSION_OPTIONS[format_name]:
            options.update(COMPRESSION_OPTIONS[format_name][compression]["options"])
    
    # Add quality if specified and supported
    if quality is not None:
        if "JPEG_QUALITY" in options:
            options["JPEG_QUALITY"] = str(quality)
        elif "QUALITY" in options:
            options["QUALITY"] = str(quality)
    
    return options

def get_export_profile(profile_name: str) -> Dict:
    """Get export profile configuration"""
    return EXPORT_PROFILES.get(profile_name, EXPORT_PROFILES["gis_analysis"])

def configure_gdal_environment():
    """Configure GDAL environment variables"""
    for key, value in GDAL_CONFIG.items():
        os.environ[key] = value

def get_processing_config() -> Dict:
    """Get complete processing configuration"""
    return {
        "gdal": GDAL_CONFIG,
        "crs": COMMON_CRS,
        "resampling": RESAMPLING_METHODS,
        "compression": COMPRESSION_OPTIONS,
        "tiles": TILE_CONFIG,
        "memory": MEMORY_CONFIG,
        "quality": QUALITY_METRICS,
        "export_profiles": EXPORT_PROFILES,
        "pipeline": PIPELINE_CONFIG,
        "error_handling": ERROR_CONFIG
    }

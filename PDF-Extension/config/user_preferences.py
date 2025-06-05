"""
User Preferences Manager for HYDRA21 PDF Compressor Pro
Handles user settings, theme preferences, and application state
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class UserPreferences:
    """User preferences data class"""
    theme_mode: str = "light"  # "light" or "dark"
    default_quality: str = "medium"  # "high", "medium", "low"
    auto_open_results: bool = True
    show_compression_stats: bool = True
    remember_window_size: bool = True
    window_width: int = 1200
    window_height: int = 800
    last_output_directory: Optional[str] = None
    ghostscript_path: Optional[str] = None
    max_history_entries: int = 50
    auto_detect_ghostscript: bool = True
    show_tooltips: bool = True
    enable_keyboard_shortcuts: bool = True
    compression_timeout: int = 300  # seconds
    batch_size_limit: int = 100
    language: str = "es"  # "es", "en"

class PreferencesManager:
    """Manages user preferences and settings"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.preferences_file = config_dir / "user_preferences.json"
        self.preferences = UserPreferences()
        self.load_preferences()
    
    def load_preferences(self) -> UserPreferences:
        """Load preferences from file"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Update preferences with loaded data
                for key, value in data.items():
                    if hasattr(self.preferences, key):
                        setattr(self.preferences, key, value)
                
                print(f"✅ Preferencias cargadas desde: {self.preferences_file}")
            else:
                print("📝 Usando preferencias por defecto")
                self.save_preferences()  # Create default file
                
        except Exception as e:
            print(f"⚠️ Error cargando preferencias: {e}")
            self.preferences = UserPreferences()  # Reset to defaults
        
        return self.preferences
    
    def save_preferences(self) -> bool:
        """Save preferences to file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.preferences), f, indent=2, ensure_ascii=False)
            
            print(f"💾 Preferencias guardadas en: {self.preferences_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando preferencias: {e}")
            return False
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a specific preference value"""
        return getattr(self.preferences, key, default)
    
    def set_preference(self, key: str, value: Any) -> bool:
        """Set a specific preference value"""
        try:
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
                return self.save_preferences()
            else:
                print(f"⚠️ Preferencia desconocida: {key}")
                return False
        except Exception as e:
            print(f"❌ Error estableciendo preferencia {key}: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all preferences to default values"""
        try:
            self.preferences = UserPreferences()
            return self.save_preferences()
        except Exception as e:
            print(f"❌ Error reseteando preferencias: {e}")
            return False
    
    def export_preferences(self, export_path: Path) -> bool:
        """Export preferences to a file"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.preferences), f, indent=2, ensure_ascii=False)
            
            print(f"📤 Preferencias exportadas a: {export_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando preferencias: {e}")
            return False
    
    def import_preferences(self, import_path: Path) -> bool:
        """Import preferences from a file"""
        try:
            if not import_path.exists():
                print(f"❌ Archivo no encontrado: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate and update preferences
            for key, value in data.items():
                if hasattr(self.preferences, key):
                    setattr(self.preferences, key, value)
            
            success = self.save_preferences()
            if success:
                print(f"📥 Preferencias importadas desde: {import_path}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error importando preferencias: {e}")
            return False
    
    def get_theme_colors(self) -> Dict[str, str]:
        """Get theme colors based on current theme mode"""
        if self.preferences.theme_mode == "dark":
            return {
                "primary": "#3b82f6",
                "background": "#0f172a",
                "surface": "#1e293b",
                "on_surface": "#f1f5f9",
                "on_surface_variant": "#94a3b8",
                "error": "#ef4444",
                "warning": "#f59e0b",
                "success": "#10b981",
                "border": "#374151",
                "input_bg": "#1e293b",
                "input_border": "#374151"
            }
        else:
            return {
                "primary": "#2563eb",
                "background": "#ffffff",
                "surface": "#f8fafc",
                "on_surface": "#1e293b",
                "on_surface_variant": "#64748b",
                "error": "#dc2626",
                "warning": "#f59e0b",
                "success": "#059669",
                "border": "#e2e8f0",
                "input_bg": "#ffffff",
                "input_border": "#e2e8f0"
            }
    
    def update_window_size(self, width: int, height: int):
        """Update window size preferences"""
        if self.preferences.remember_window_size:
            self.preferences.window_width = width
            self.preferences.window_height = height
            self.save_preferences()
    
    def get_quality_settings(self) -> Dict[str, Dict[str, str]]:
        """Get Ghostscript quality settings"""
        return {
            "high": {
                "dPDFSETTINGS": "/printer",
                "dColorImageResolution": "150",
                "dGrayImageResolution": "150",
                "dMonoImageResolution": "300",
                "description": "Alta calidad - Ideal para impresión"
            },
            "medium": {
                "dPDFSETTINGS": "/ebook",
                "dColorImageResolution": "72",
                "dGrayImageResolution": "72",
                "dMonoImageResolution": "150",
                "description": "Calidad media - Balance óptimo"
            },
            "low": {
                "dPDFSETTINGS": "/screen",
                "dColorImageResolution": "36",
                "dGrayImageResolution": "36",
                "dMonoImageResolution": "72",
                "description": "Baja calidad - Máxima compresión"
            }
        }
    
    def get_localized_strings(self) -> Dict[str, str]:
        """Get localized strings based on language preference"""
        if self.preferences.language == "en":
            return {
                "app_title": "HYDRA21 PDF Compressor Pro",
                "select_files": "Select PDF Files",
                "compress_pdfs": "Compress PDFs",
                "compression_quality": "Compression Quality",
                "processing": "Processing...",
                "completed": "Completed",
                "error": "Error",
                "open_file": "Open File",
                "show_in_folder": "Show in Folder",
                "process_more": "Process More"
            }
        else:  # Spanish (default)
            return {
                "app_title": "HYDRA21 PDF Compressor Pro",
                "select_files": "Seleccionar Archivos PDF",
                "compress_pdfs": "Comprimir PDFs",
                "compression_quality": "Calidad de Compresión",
                "processing": "Procesando...",
                "completed": "Completado",
                "error": "Error",
                "open_file": "Abrir Archivo",
                "show_in_folder": "Mostrar en Carpeta",
                "process_more": "Procesar Más"
            }

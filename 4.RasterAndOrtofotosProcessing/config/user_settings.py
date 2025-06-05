"""
HYDRA21 Orthophoto Processor Pro - User Settings Persistence
Save and load user preferences and settings
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

class UserSettings:
    """Manages user settings persistence"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.settings_file = config_dir / "user_settings.json"
        self.default_settings = {
            "output_directory": "./output",
            "last_export_profile": "gis_analysis",
            "last_compression": "lossless",
            "last_quality": 85,
            "preserve_crs": True,
            "create_overviews": True,
            "resampling_method": "bilinear",
            "theme_mode": "light",
            "window_width": 1000,
            "window_height": 800
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    settings = self.default_settings.copy()
                    settings.update(loaded_settings)
                    return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """Save settings to file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value and save"""
        self.settings[key] = value
        self.save_settings()
    
    def update(self, new_settings: Dict[str, Any]) -> None:
        """Update multiple settings and save"""
        self.settings.update(new_settings)
        self.save_settings()
    
    def get_output_directory(self) -> str:
        """Get the output directory setting"""
        return self.get("output_directory", "./output")
    
    def set_output_directory(self, directory: str) -> None:
        """Set the output directory setting"""
        self.set("output_directory", directory)
    
    def get_processing_options(self) -> Dict[str, Any]:
        """Get all processing-related options"""
        return {
            "output_directory": self.get("output_directory"),
            "export_profile": self.get("last_export_profile"),
            "compression": self.get("last_compression"),
            "quality": self.get("last_quality"),
            "preserve_crs": self.get("preserve_crs"),
            "create_overviews": self.get("create_overviews"),
            "resampling_method": self.get("resampling_method")
        }
    
    def save_processing_options(self, options: Dict[str, Any]) -> None:
        """Save processing options"""
        settings_to_save = {}
        
        if "output_directory" in options:
            settings_to_save["output_directory"] = options["output_directory"]
        if "export_profile" in options:
            settings_to_save["last_export_profile"] = options["export_profile"]
        if "compression" in options:
            settings_to_save["last_compression"] = options["compression"]
        if "quality" in options:
            settings_to_save["last_quality"] = options["quality"]
        if "preserve_crs" in options:
            settings_to_save["preserve_crs"] = options["preserve_crs"]
        if "create_overviews" in options:
            settings_to_save["create_overviews"] = options["create_overviews"]
        if "resampling_method" in options:
            settings_to_save["resampling_method"] = options["resampling_method"]
        
        self.update(settings_to_save)
    
    def get_theme_mode(self) -> str:
        """Get theme mode (light/dark)"""
        return self.get("theme_mode", "light")
    
    def set_theme_mode(self, mode: str) -> None:
        """Set theme mode"""
        self.set("theme_mode", mode)
    
    def get_window_settings(self) -> Dict[str, int]:
        """Get window size settings"""
        return {
            "width": self.get("window_width", 1000),
            "height": self.get("window_height", 800)
        }
    
    def set_window_settings(self, width: int, height: int) -> None:
        """Set window size settings"""
        self.update({
            "window_width": width,
            "window_height": height
        })
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.settings = self.default_settings.copy()
        self.save_settings()
    
    def export_settings(self, file_path: Path) -> bool:
        """Export settings to a file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, file_path: Path) -> bool:
        """Import settings from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
                # Validate and merge with defaults
                valid_settings = self.default_settings.copy()
                for key, value in imported_settings.items():
                    if key in valid_settings:
                        valid_settings[key] = value
                
                self.settings = valid_settings
                self.save_settings()
                return True
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False

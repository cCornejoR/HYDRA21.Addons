"""
Ghostscript configuration and detection for HYDRA21 PDF Compressor
"""

import os
import subprocess
import platform
from pathlib import Path
from typing import Optional, List, Tuple
import json

class GhostscriptConfig:
    """Manages Ghostscript configuration and detection"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_file = config_dir / "ghostscript_config.json"
        self._gs_path: Optional[str] = None
        self._load_config()
    
    def _load_config(self):
        """Load Ghostscript configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self._gs_path = config.get('gs_path')
            except Exception as e:
                print(f"Error loading Ghostscript config: {e}")
    
    def _save_config(self):
        """Save Ghostscript configuration to file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            config = {'gs_path': self._gs_path}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving Ghostscript config: {e}")
    
    @property
    def gs_path(self) -> Optional[str]:
        """Get current Ghostscript path"""
        return self._gs_path
    
    @gs_path.setter
    def gs_path(self, path: str):
        """Set Ghostscript path and save configuration"""
        self._gs_path = path
        self._save_config()
    
    def auto_detect_ghostscript(self) -> Optional[str]:
        """Automatically detect Ghostscript installation"""
        system = platform.system().lower()
        
        if system == "windows":
            return self._detect_windows_ghostscript()
        else:
            return self._detect_unix_ghostscript()
    
    def _detect_windows_ghostscript(self) -> Optional[str]:
        """Detect Ghostscript on Windows systems"""
        # Check environment variable first
        gs_path = os.getenv("GS_PATH_APP")
        if gs_path and Path(gs_path).is_file():
            return gs_path
        
        # Check if gswin64c.exe is in PATH
        if self._is_command_available("gswin64c.exe"):
            return "gswin64c.exe"
        
        # Check common installation paths
        program_files = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        ]
        
        # Common Ghostscript versions to check (newest first)
        versions = ["gs10.05.1", "gs10.03.1", "gs10.02.1", "gs10.01.2", "gs10.00.0", "gs"]
        
        for pf in program_files:
            for version in versions:
                if version == "gs":
                    # Generic path without version
                    paths = [
                        Path(pf) / "gs" / "bin" / "gswin64c.exe",
                        Path(pf) / "gs" / "bin" / "gswin32c.exe"
                    ]
                else:
                    # Version-specific paths
                    paths = [
                        Path(pf) / "gs" / version / "bin" / "gswin64c.exe",
                        Path(pf) / "gs" / version / "bin" / "gswin32c.exe"
                    ]
                
                for path in paths:
                    if path.exists():
                        return str(path)
        
        return None
    
    def _detect_unix_ghostscript(self) -> Optional[str]:
        """Detect Ghostscript on Unix-like systems (Linux, macOS)"""
        if self._is_command_available("gs"):
            return "gs"
        return None
    
    def _is_command_available(self, command: str) -> bool:
        """Check if a command is available in PATH"""
        try:
            check_cmd = 'where' if platform.system().lower() == 'windows' else 'which'
            subprocess.run(
                [check_cmd, command],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def verify_ghostscript(self, gs_path: str = None) -> Tuple[bool, str]:
        """
        Verify if Ghostscript is working correctly
        
        Args:
            gs_path: Path to Ghostscript executable (optional)
            
        Returns:
            Tuple of (is_valid, message)
        """
        if gs_path is None:
            gs_path = self._gs_path
        
        if not gs_path:
            return False, "No se ha configurado la ruta de Ghostscript"
        
        # For commands in PATH, don't check file existence
        if gs_path in ["gs", "gswin64c.exe", "gswin32c.exe"]:
            if not self._is_command_available(gs_path):
                return False, f"Comando '{gs_path}' no encontrado en PATH"
        else:
            # For full paths, check file existence
            if not Path(gs_path).is_file():
                return False, f"Archivo no encontrado: {gs_path}"
        
        # Test Ghostscript by running version command
        try:
            result = subprocess.run(
                [gs_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system().lower() == 'windows' else 0
            )
            
            if result.returncode == 0:
                output = result.stdout.lower()
                if "ghostscript" in output:
                    return True, "Ghostscript verificado correctamente"
                else:
                    return False, "La salida no parece ser de Ghostscript"
            else:
                return False, f"Error al ejecutar Ghostscript: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout al verificar Ghostscript"
        except FileNotFoundError:
            return False, f"Ejecutable no encontrado: {gs_path}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def get_ghostscript_info(self) -> dict:
        """Get information about current Ghostscript configuration"""
        if not self._gs_path:
            return {
                "configured": False,
                "path": None,
                "verified": False,
                "version": None,
                "message": "Ghostscript no configurado"
            }
        
        is_verified, message = self.verify_ghostscript()
        version = None
        
        if is_verified:
            try:
                result = subprocess.run(
                    [self._gs_path, "-version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if platform.system().lower() == 'windows' else 0
                )
                if result.returncode == 0:
                    # Extract version from output
                    lines = result.stdout.strip().split('\n')
                    if lines:
                        version = lines[0].strip()
            except Exception:
                pass
        
        return {
            "configured": True,
            "path": self._gs_path,
            "verified": is_verified,
            "version": version,
            "message": message
        }
    
    def setup_ghostscript(self, custom_path: str = None) -> Tuple[bool, str]:
        """
        Setup Ghostscript configuration
        
        Args:
            custom_path: Custom path to Ghostscript executable
            
        Returns:
            Tuple of (success, message)
        """
        if custom_path:
            # Use custom path
            is_valid, message = self.verify_ghostscript(custom_path)
            if is_valid:
                self.gs_path = custom_path
                return True, f"Ghostscript configurado correctamente: {custom_path}"
            else:
                return False, f"Ruta inválida: {message}"
        else:
            # Auto-detect
            detected_path = self.auto_detect_ghostscript()
            if detected_path:
                is_valid, message = self.verify_ghostscript(detected_path)
                if is_valid:
                    self.gs_path = detected_path
                    return True, f"Ghostscript detectado y configurado: {detected_path}"
                else:
                    return False, f"Ghostscript detectado pero no válido: {message}"
            else:
                return False, "No se pudo detectar Ghostscript automáticamente"
    
    def get_common_paths(self) -> List[str]:
        """Get list of common Ghostscript installation paths for manual selection"""
        system = platform.system().lower()
        
        if system == "windows":
            program_files = [
                os.environ.get("ProgramFiles", "C:\\Program Files"),
                os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            ]
            
            paths = []
            versions = ["gs10.05.1", "gs10.03.1", "gs10.02.1", "gs10.01.2", "gs10.00.0"]
            
            for pf in program_files:
                for version in versions:
                    paths.extend([
                        str(Path(pf) / "gs" / version / "bin" / "gswin64c.exe"),
                        str(Path(pf) / "gs" / version / "bin" / "gswin32c.exe")
                    ])
                # Generic paths
                paths.extend([
                    str(Path(pf) / "gs" / "bin" / "gswin64c.exe"),
                    str(Path(pf) / "gs" / "bin" / "gswin32c.exe")
                ])
            
            return paths
        else:
            return ["/usr/bin/gs", "/usr/local/bin/gs", "/opt/local/bin/gs"]

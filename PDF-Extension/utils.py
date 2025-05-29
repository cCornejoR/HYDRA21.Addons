# utils.py - Utilidades para HYDRA21 PDF Compressor
"""
Módulo de utilidades para HYDRA21 PDF Compressor.

Este módulo proporciona clases y funciones de utilidad para diversas
tareas como manejo de archivos, interacción con Ghostscript, gestión
de configuración, cálculo de estadísticas y utilidades del sistema.

Clases:
    FileUtils: Utilidades para manejo de archivos.
    GhostscriptUtils: Utilidades para Ghostscript.
    ConfigManager: Gestor de configuración.
    CompressionStats: Estadísticas de compresión.
    SystemUtils: Utilidades del sistema.

Funciones:
    setup_logging: Configura el sistema de logging.
    get_app_version: Obtiene la versión de la aplicación.
"""

import os
import sys
import json
import glob
import subprocess
import logging
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import tempfile
import shutil
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

class FileUtils:
    """Utilidades para manejo de archivos.
    
    Proporciona métodos estáticos para operaciones comunes con archivos,
    como formateo de tamaños, validación de PDFs, creación de backups
    y limpieza de archivos temporales.
    """
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Formatear tamaño de archivo en formato legible.
        
        Convierte un tamaño en bytes a una representación legible
        con unidades apropiadas (B, KB, MB, GB, TB).
        
        Args:
            size_bytes (int): Tamaño en bytes.
            
        Returns:
            str: Tamaño formateado con unidades.
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    @staticmethod
    def get_file_size(file_path: Path) -> str:
        """Obtener tamaño de archivo formateado"""
        try:
            if not file_path.exists():
                return "0 B"
            
            size_bytes = file_path.stat().st_size
            return FileUtils.format_size(size_bytes)
        except Exception as e:
            logger.error(f"Error obteniendo tamaño del archivo {file_path}: {e}")
            return "0 B"
    
    @staticmethod
    def get_file_info(file_path: Path) -> Dict[str, Any]:
        """Obtener información detallada de un archivo"""
        try:
            stat = file_path.stat()
            return {
                "name": file_path.name,
                "size": stat.st_size,
                "size_formatted": FileUtils.format_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "extension": file_path.suffix.lower(),
                "is_pdf": file_path.suffix.lower() == ".pdf",
                "exists": True
            }
        except Exception as e:
            logger.error(f"Error obteniendo información del archivo {file_path}: {e}")
            return {
                "name": file_path.name if file_path else "Desconocido",
                "size": 0,
                "size_formatted": "0 B",
                "modified": None,
                "extension": "",
                "is_pdf": False,
                "exists": False,
                "error": str(e)
            }
    
    @staticmethod
    def is_valid_pdf(file_path: Path) -> bool:
        """Verificar si un archivo es un PDF válido"""
        try:
            if not file_path.exists():
                return False
            
            # Verificar extensión
            if file_path.suffix.lower() != ".pdf":
                return False
            
            # Verificar header del PDF
            with open(file_path, 'rb') as f:
                header = f.read(8)
                return header.startswith(b'%PDF-')
        
        except Exception as e:
            logger.error(f"Error verificando PDF {file_path}: {e}")
            return False
    
    @staticmethod
    def create_backup(file_path: Path, backup_dir: Optional[Path] = None) -> Optional[Path]:
        """Crear backup de un archivo"""
        try:
            if backup_dir is None:
                backup_dir = file_path.parent / "backups"
            
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
            backup_path = backup_dir / backup_name
            
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup creado: {backup_path}")
            
            return backup_path
        
        except Exception as e:
            logger.error(f"Error creando backup de {file_path}: {e}")
            return None
    
    @staticmethod
    def clean_temp_files(temp_dir: Path, older_than_hours: int = 24):
        """Limpiar archivos temporales antiguos"""
        try:
            if not temp_dir.exists():
                return
            
            current_time = datetime.now().timestamp()
            cutoff_time = current_time - (older_than_hours * 3600)
            
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    file_time = file_path.stat().st_mtime
                    if file_time < cutoff_time:
                        try:
                            file_path.unlink()
                            logger.debug(f"Archivo temporal eliminado: {file_path}")
                        except Exception as e:
                            logger.error(f"Error eliminando {file_path}: {e}")
        
        except Exception as e:
            logger.error(f"Error limpiando archivos temporales: {e}")

class GhostscriptUtils:
    """Utilidades para Ghostscript"""
    
    @staticmethod
    def find_ghostscript_paths() -> List[str]:
        """Encontrar todas las posibles rutas de Ghostscript"""
        paths = []
        
        if os.name == 'nt':
            # Windows
            possible_patterns = [
                r"C:\Program Files\gs\gs*\bin\gswin64c.exe",
                r"C:\Program Files (x86)\gs\gs*\bin\gswin32c.exe",
                r"C:\gs\gs*\bin\gswin64c.exe",
                r"C:\gs\gs*\bin\gswin32c.exe"
            ]
            
            for pattern in possible_patterns:
                matches = glob.glob(pattern)
                paths.extend(matches)
            
            # También verificar PATH
            try:
                result = subprocess.run(
                    ['where', 'gswin64c'], 
                    capture_output=True, 
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    paths.extend(result.stdout.strip().split('\n'))
            except:
                pass
                
        else:
            # Unix-like systems
            try:
                result = subprocess.run(['which', 'gs'], capture_output=True, text=True)
                if result.returncode == 0:
                    paths.append(result.stdout.strip())
            except:
                pass
            
            # Rutas comunes en Unix
            common_paths = [
                '/usr/bin/gs',
                '/usr/local/bin/gs',
                '/opt/local/bin/gs'
            ]
            
            for path in common_paths:
                if Path(path).exists():
                    paths.append(path)
        
        # Remover duplicados y rutas inválidas
        unique_paths = []
        for path in paths:
            if path and Path(path).is_file() and path not in unique_paths:
                unique_paths.append(path)
        
        return unique_paths
    
    @staticmethod
    def verify_ghostscript(gs_path: str, timeout: int = 5) -> Tuple[bool, str]:
        """Verificar que Ghostscript funciona correctamente"""
        try:
            if not gs_path:
                return False, "Ruta de Ghostscript vacía"
            
            if not Path(gs_path).is_file() and not GhostscriptUtils.is_command_available(gs_path):
                return False, "Archivo de Ghostscript no encontrado"
            
            # Ejecutar comando de versión
            cmd = [gs_path, "-version"]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            if process.returncode != 0:
                return False, f"Error ejecutando Ghostscript: {process.stderr}"
            
            # Verificar que la salida contiene información de Ghostscript
            output = process.stdout.lower()
            if "ghostscript" not in output:
                return False, "La salida no contiene información válida de Ghostscript"
              # Extraer versión si es posible
            version_info = process.stdout.strip().split('\n')[0] if process.stdout.strip() else "Versión desconocida"
            
            return True, f"Ghostscript verificado: {version_info}"
            
        except subprocess.TimeoutExpired:
            return False, "Timeout verificando Ghostscript"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    @staticmethod
    def is_command_available(command: str) -> bool:
        """Verificar si un comando está disponible en el PATH"""
        try:
            check_cmd = 'where' if os.name == 'nt' else 'which'
            subprocess.check_call(
                [check_cmd, command],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    @staticmethod
    def is_available() -> bool:
        """Verificar si Ghostscript está disponible en el sistema"""
        try:
            # Buscar rutas disponibles
            paths = GhostscriptUtils.find_ghostscript_paths()
            
            if not paths:
                return False
            
            # Verificar que al menos una ruta funciona
            for path in paths:
                is_valid, _ = GhostscriptUtils.verify_ghostscript(path)
                if is_valid:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando disponibilidad de Ghostscript: {e}")
            return False
    
    @staticmethod
    def get_compression_command(gs_path: str, input_path: Path, output_path: Path, 
                              preset: str, additional_params: Optional[List[str]] = None) -> List[str]:
        """Generar comando de compresión de Ghostscript"""
        cmd = [
            gs_path,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={preset}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH"
        ]
        
        if additional_params:
            cmd.extend(additional_params)
        
        cmd.extend([
            f"-sOutputFile={output_path}",
            str(input_path)
        ])
        
        return cmd

class ConfigManager:
    """Gestor de configuración"""
    
    def __init__(self, config_file: str = "gs_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde archivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Configuración cargada desde {self.config_file}")
                return config
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
        
        return self.get_default_config()
    
    def save_config(self) -> bool:
        """Guardar configuración en archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info(f"Configuración guardada en {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """Obtener configuración por defecto"""
        return {
            "ghostscript_path": "",
            "default_quality": "Calidad Media",
            "output_directory": "output",
            "auto_open_output": True,
            "create_backups": False,
            "theme": "light",
            "last_used": datetime.now().isoformat()
        }
    
    def get(self, key: str, default=None):
        """Obtener valor de configuración"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Establecer valor de configuración"""
        self.config[key] = value
        self.save_config()
    
    def update(self, updates: Dict[str, Any]):
        """Actualizar múltiples valores"""
        self.config.update(updates)
        self.save_config()

class CompressionStats:
    """Estadísticas de compresión"""
    
    def __init__(self, original_path: Path, compressed_path: Path):
        self.original_path = original_path
        self.compressed_path = compressed_path
        self._calculate_stats()
    
    def _calculate_stats(self):
        """Calcular estadísticas"""
        try:
            self.original_size = os.path.getsize(self.original_path)
            self.compressed_size = os.path.getsize(self.compressed_path)
            self.size_reduction = self.original_size - self.compressed_size
            self.compression_ratio = (self.size_reduction / self.original_size) * 100 if self.original_size > 0 else 0
            
            self.original_size_formatted = FileUtils.format_size(self.original_size)
            self.compressed_size_formatted = FileUtils.format_size(self.compressed_size)
            self.size_reduction_formatted = FileUtils.format_size(self.size_reduction)
            
        except Exception as e:
            logger.error(f"Error calculando estadísticas: {e}")
            self.original_size = 0
            self.compressed_size = 0
            self.size_reduction = 0
            self.compression_ratio = 0
            self.original_size_formatted = "0 B"
            self.compressed_size_formatted = "0 B"
            self.size_reduction_formatted = "0 B"
    
    def get_summary(self) -> str:
        """Obtener resumen de compresión"""
        return (
            f"Tamaño original: {self.original_size_formatted}\n"
            f"Tamaño comprimido: {self.compressed_size_formatted}\n"
            f"Reducción: {self.size_reduction_formatted} ({self.compression_ratio:.1f}%)"
        )
    
    def is_successful(self) -> bool:
        """Verificar si la compresión fue exitosa"""
        return self.compressed_size > 0 and self.compressed_size < self.original_size

class SystemUtils:
    """Utilidades del sistema"""
    
    @staticmethod
    def open_file_explorer(path: Path):
        """Abrir explorador de archivos en la ruta especificada"""
        try:
            if os.name == 'nt':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(path)])
            else:
                subprocess.Popen(['xdg-open', str(path)])
        except Exception as e:
            logger.error(f"Error abriendo explorador: {e}")
            raise
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """Obtener información del sistema"""
        return {
            "platform": sys.platform,            "os_name": os.name,
            "python_version": sys.version,
            "architecture": sys.maxsize > 2**32 and "64-bit" or "32-bit"
        }
    
    @staticmethod
    def create_desktop_shortcut(app_path: Path, shortcut_name: str) -> bool:
        """Crear acceso directo en el escritorio (Windows)"""
        if os.name != 'nt':
            return False
        
        try:
            # Importaciones opcionales para Windows
            try:
                import winshell
                from win32com.client import Dispatch
            except ImportError:
                logger.warning("winshell o win32com no disponibles para crear accesos directos")
                return False
            
            desktop = winshell.desktop()
            shortcut_path = Path(desktop) / f"{shortcut_name}.lnk"
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(app_path)
            shortcut.WorkingDirectory = str(app_path.parent)
            shortcut.save()
            
            return True
        except Exception as e:
            logger.error(f"Error creando acceso directo: {e}")
            return False

# Funciones de conveniencia
def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Configurar logging"""
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def get_app_version() -> str:
    """Obtener versión de la aplicación"""
    try:
        # Intentar leer desde archivo VERSION si existe
        version_file = Path("VERSION")
        if version_file.exists():
            return version_file.read_text().strip()
    except:
        pass
    
    return "2.0.0"  # Versión por defecto
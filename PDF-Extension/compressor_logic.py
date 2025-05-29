# compressor_logic.py
"""
Módulo de lógica de compresión para HYDRA21 PDF Compressor.

Este módulo implementa la lógica principal para comprimir archivos PDF
utilizando Ghostscript. Proporciona clases para gestionar estadísticas
de compresión y resultados, así como la funcionalidad principal de compresión
tanto para archivos individuales como para lotes.

Clases:
    CompressionStats: Estadísticas de compresión para un archivo.
    BatchCompressionStats: Estadísticas de compresión para múltiples archivos.
    CompressionResult: Resultado de una operación de compresión individual.
    BatchCompressionResult: Resultado de una operación de compresión por lotes.
    PDFCompressor: Clase principal para compresión de PDFs.

Funciones:
    is_tool: Verifica si un programa está disponible en el PATH.
    find_ghostscript_path: Busca la ruta de Ghostscript en el sistema.
    verify_ghostscript_path: Verifica si una ruta de Ghostscript es válida.
    compress_pdf: Comprime un archivo PDF usando Ghostscript.
"""

import os
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import settings # Importar GS_PRESETS

@dataclass
class CompressionStats:
    """Estadísticas de compresión.
    
    Almacena información sobre el resultado de una operación de compresión,
    incluyendo tamaños original y comprimido, porcentaje de reducción y rutas.
    
    Atributos:
        original_size (int): Tamaño original en bytes.
        compressed_size (int): Tamaño comprimido en bytes.
        reduction_percent (float): Porcentaje de reducción de tamaño.
        original_size_str (str): Tamaño original formateado.
        compressed_size_str (str): Tamaño comprimido formateado.
        output_path (Path): Ruta del archivo comprimido.
    """
    original_size: int
    compressed_size: int
    reduction_percent: float
    original_size_str: str
    compressed_size_str: str
    output_path: Path

@dataclass
class BatchCompressionStats:
    """Estadísticas de compresión por lotes"""
    total_files: int
    successful_files: int
    failed_files: int
    total_original_size: int
    total_compressed_size: int
    total_reduction_percent: float
    total_original_size_str: str
    total_compressed_size_str: str
    individual_stats: list[CompressionStats]
    failed_files_list: list[str]

@dataclass
class CompressionResult:
    """Resultado de la operación de compresión"""
    success: bool
    error_message: Optional[str] = None
    stats: Optional[CompressionStats] = None

@dataclass
class BatchCompressionResult:
    """Resultado de la operación de compresión por lotes"""
    success: bool
    error_message: Optional[str] = None
    batch_stats: Optional[BatchCompressionStats] = None

class PDFCompressor:
    """Clase principal para compresión de PDFs usando Ghostscript"""
    
    def __init__(self, output_dir: Path = None):
        """Inicializar compresor con directorio de salida opcional"""
        # Configurar carpeta de salida por defecto en Documents/HYDRA21-PDFCompressor
        if output_dir is None:
            documents_dir = Path.home() / "Documents"
            self.output_dir = documents_dir / "HYDRA21-PDFCompressor"
        else:
            self.output_dir = output_dir
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar ruta de Ghostscript
        self.gs_path = find_ghostscript_path()
    
    def compress(self, input_path: Path, quality_preset: str) -> CompressionResult:
        """Comprimir un archivo PDF"""
        try:
            # Verificar archivo de entrada
            if not input_path.exists():
                return CompressionResult(
                    success=False,
                    error_message=f"El archivo no existe: {input_path}"
                )
              # Crear archivo de salida
            output_path = self.output_dir / f"{input_path.stem}_comprimido.pdf"
            
            # Obtener tamaño original
            original_size = input_path.stat().st_size
            
            # Ejecutar compresión
            success, error_msg = compress_pdf(
                str(input_path),
                str(output_path),
                self.gs_path,
                self._get_quality_key_from_preset(quality_preset)
            )
            
            if success and output_path.exists():
                # Calcular estadísticas
                compressed_size = output_path.stat().st_size
                reduction_percent = ((original_size - compressed_size) / original_size) * 100
                
                stats = CompressionStats(
                    original_size=original_size,
                    compressed_size=compressed_size,
                    reduction_percent=reduction_percent,
                    original_size_str=self._format_size(original_size),
                    compressed_size_str=self._format_size(compressed_size),
                    output_path=output_path
                )
                
                return CompressionResult(success=True, stats=stats)
            else:
                return CompressionResult(success=False, error_message=error_msg)
                
        except Exception as e:
            return CompressionResult(
                success=False,
                error_message=f"Error inesperado: {str(e)}"
            )
    
    def _find_ghostscript(self) -> str:
        """Encontrar Ghostscript"""
        return find_ghostscript_path()
    
    def _get_quality_key_from_preset(self, preset_value: str) -> str:
        """Convertir valor del preset a clave"""
        # El preset_value viene del dropdown, que es la clave directa
        return preset_value
    
    def _format_size(self, size_bytes: int) -> str:
        """Formatear tamaño de archivo"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.2f} {size_names[i]}"

    def compress_batch(self, input_paths: list[Path], quality_preset: str, 
                      progress_callback=None) -> BatchCompressionResult:
        """Comprimir múltiples archivos PDF en lote"""
        try:
            successful_stats = []
            failed_files = []
            total_original_size = 0
            total_compressed_size = 0
              # Usar directorio de salida configurado
            # Ya está creado en __init__
            
            for i, input_path in enumerate(input_paths):
                try:
                    # Notificar progreso si hay callback
                    if progress_callback:
                        progress_callback(i + 1, len(input_paths), input_path.name)
                    
                    # Verificar archivo de entrada
                    if not input_path.exists():
                        failed_files.append(f"{input_path.name}: Archivo no existe")
                        continue
                      # Crear archivo de salida
                    output_path = self.output_dir / f"{input_path.stem}_comprimido.pdf"
                    
                    # Si ya existe, añadir número
                    counter = 1
                    while output_path.exists():
                        output_path = self.output_dir / f"{input_path.stem}_comprimido_{counter}.pdf"
                        counter += 1
                    
                    # Obtener tamaño original
                    original_size = input_path.stat().st_size
                    total_original_size += original_size
                    
                    # Ejecutar compresión
                    success, error_msg = compress_pdf(
                        str(input_path),
                        str(output_path),
                        self.gs_path,
                        self._get_quality_key_from_preset(quality_preset)
                    )
                    
                    if success and output_path.exists():
                        # Calcular estadísticas individuales
                        compressed_size = output_path.stat().st_size
                        total_compressed_size += compressed_size
                        reduction_percent = ((original_size - compressed_size) / original_size) * 100
                        
                        stats = CompressionStats(
                            original_size=original_size,
                            compressed_size=compressed_size,
                            reduction_percent=reduction_percent,
                            original_size_str=self._format_size(original_size),
                            compressed_size_str=self._format_size(compressed_size),
                            output_path=output_path
                        )
                        successful_stats.append(stats)
                    else:
                        failed_files.append(f"{input_path.name}: {error_msg or 'Error desconocido'}")
                        
                except Exception as e:
                    failed_files.append(f"{input_path.name}: {str(e)}")
            
            # Calcular estadísticas totales
            total_reduction_percent = 0
            if total_original_size > 0:
                total_reduction_percent = ((total_original_size - total_compressed_size) / total_original_size) * 100
            
            batch_stats = BatchCompressionStats(
                total_files=len(input_paths),
                successful_files=len(successful_stats),
                failed_files=len(failed_files),
                total_original_size=total_original_size,
                total_compressed_size=total_compressed_size,
                total_reduction_percent=total_reduction_percent,
                total_original_size_str=self._format_size(total_original_size),
                total_compressed_size_str=self._format_size(total_compressed_size),
                individual_stats=successful_stats,
                failed_files_list=failed_files
            )
            
            # Determinar si la operación fue exitosa
            success = len(successful_stats) > 0
            error_message = None
            if not success:
                error_message = "No se pudo comprimir ningún archivo"
            elif failed_files:
                error_message = f"Se procesaron {len(successful_stats)} archivos. {len(failed_files)} fallaron."
            
            return BatchCompressionResult(
                success=success,
                error_message=error_message,
                batch_stats=batch_stats
            )
            
        except Exception as e:
            return BatchCompressionResult(
                success=False,
                error_message=f"Error inesperado en compresión por lotes: {str(e)}"
            )

def is_tool(name):
    """Revisa si un programa está en el PATH y es ejecutable."""
    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        check_cmd = 'where' if os.name == 'nt' else 'which'
        subprocess.check_call([check_cmd, name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=startupinfo)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return True

def find_ghostscript_path():
    """Intenta detectar automáticamente la ruta del ejecutable de Ghostscript."""
    gs_path = os.getenv("GS_PATH_APP") # Variable de entorno específica de la app
    if gs_path and Path(gs_path).is_file():
        print(f"Ghostscript detectado por variable de entorno GS_PATH_APP: {gs_path}")
        return gs_path

    if os.name == 'nt':
        gs_exe_default = "gswin64c.exe"
        if is_tool(gs_exe_default):
            print(f"Ghostscript detectado en PATH: {gs_exe_default}")
            return gs_exe_default
        
        # Buscar en ubicaciones comunes de Windows (versiones más recientes primero)
        versions_to_check = ["gs10.05.1", "gs10.03.1", "gs10.0.0", "gs"] # gs al final para genérico
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")

        for ver_or_name in versions_to_check:
            common_paths = []
            if ver_or_name == "gs": # Ruta genérica sin versión
                common_paths.extend([
                    Path(program_files) / "gs" / "bin" / "gswin64c.exe",
                    Path(program_files_x86) / "gs" / "bin" / "gswin32c.exe"
                ])
            else: # Rutas con directorio de versión
                common_paths.extend([
                    Path(program_files) / "gs" / ver_or_name / "bin" / "gswin64c.exe",
                    Path(program_files_x86) / "gs" / ver_or_name / "bin" / "gswin32c.exe"
                ])
            
            for p_path in common_paths:
                if p_path.exists():
                    print(f"Ghostscript detectado en ubicación común: {str(p_path)}")
                    return str(p_path)
        print(f"ADVERTENCIA: No se pudo encontrar {gs_exe_default} automáticamente en Windows.")
        return ""
    else:  # macOS/Linux
        if is_tool("gs"):
            print("Ghostscript ('gs') detectado en PATH.")
            return "gs"
        else:
            print("ADVERTENCIA: No se pudo encontrar 'gs' automáticamente en macOS/Linux.")
            return ""

def verify_ghostscript_path(gs_exe_path):
    """Verifica si la ruta de Ghostscript proporcionada es válida ejecutando 'gs -version'."""
    if not gs_exe_path:
        return "NO_CONFIGURADO"

    # Si es solo 'gs' y estamos en un sistema no Windows, asumimos que está en PATH si is_tool lo confirma.
    if os.name != 'nt' and gs_exe_path == "gs":
        if not is_tool("gs"):
            return "NO_ENCONTRADO_TOOL"
    elif not Path(gs_exe_path).is_file():
        return "NO_ES_ARCHIVO"

    try:
        cmd_to_verify = [str(Path(gs_exe_path).resolve()) if Path(gs_exe_path).is_file() else gs_exe_path, "-version"]
        process = subprocess.run(
            cmd_to_verify,
            capture_output=True, 
            text=True, 
            check=False, 
            timeout=10, # Aumentar un poco el timeout para la verificación
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if process.returncode == 0 and process.stdout and ("GPL Ghostscript" in process.stdout or "Artifex Ghostscript" in process.stdout):
            return "VERIFICADO"
        else:
            error_details = process.stderr if process.stderr else process.stdout
            print(f"Error al verificar Ghostscript ({gs_exe_path}), código: {process.returncode}. Detalles: {error_details.strip()}")
            return "FALLO_VERIFICACION"
    except FileNotFoundError:
        print(f"Error al verificar Ghostscript: El ejecutable '{gs_exe_path}' no se encontró al intentar ejecutar -version.")
        return "NO_ENCONTRADO_SUBPROCESS"
    except subprocess.TimeoutExpired:
        print(f"Timeout al verificar Ghostscript ({gs_exe_path}).")
        return "TIMEOUT"
    except Exception as e:
        print(f"Excepción inesperada al verificar Ghostscript ({gs_exe_path}): {e}")
        return "ERROR_INESPERADO"

def compress_pdf(input_pdf_path, output_pdf_path, gs_executable_path, quality_preset_key):
    """
    Comprime un archivo PDF usando Ghostscript.
    Retorna (True, "Éxito") si la compresión es exitosa, o (False, "Mensaje de error") si falla.
    """
    if not Path(input_pdf_path).exists():
        return False, f"El archivo de entrada no existe: {input_pdf_path}"
    if not gs_executable_path:
        return False, "La ruta del ejecutable de Ghostscript no está configurada."
    
    gs_setting = settings.GS_PRESETS.get(quality_preset_key)
    if not gs_setting:
        return False, f"Preset de calidad desconocido: {quality_preset_key}"

    output_dir = Path(output_pdf_path).parent
    output_dir.mkdir(parents=True, exist_ok=True) # Asegurar que el directorio de salida exista

    cmd = [
        str(gs_executable_path),
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={gs_setting}",
        "-dNOPAUSE",
        "-dQUIET", # Para evitar salida verbosa de GS, excepto errores
        "-dBATCH",
        f"-sOutputFile={str(output_pdf_path)}",
        str(input_pdf_path)
    ]

    try:
        print(f"Ejecutando comando de compresión: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        stdout, stderr = process.communicate(timeout=300) # Timeout de 5 minutos para la compresión

        if process.returncode == 0:
            # Verificar si el archivo de salida se creó y tiene tamaño
            if Path(output_pdf_path).exists() and Path(output_pdf_path).stat().st_size > 0:
                print("Compresión de PDF exitosa.")
                return True, "PDF comprimido exitosamente."
            else:
                # A veces GS retorna 0 pero no crea el archivo si hay problemas con permisos o la ruta de salida
                # o si el PDF de entrada estaba corrupto de una manera que GS no reporta como error fatal.
                error_message = f"Ghostscript retornó código 0, pero el archivo de salida '{output_pdf_path}' no se creó o está vacío."
                if stderr:
                    error_message += f" Detalles del error: {stderr.decode('utf-8', errors='ignore').strip()}"
                elif stdout:
                    error_message += f" Detalles de salida: {stdout.decode('utf-8', errors='ignore').strip()}"
                print(error_message)
                return False, error_message
        else:
            error_message = stderr.decode('utf-8', errors='ignore').strip()
            if not error_message and stdout:
                error_message = stdout.decode('utf-8', errors='ignore').strip()
            if not error_message:
                 error_message = f"Error desconocido durante la compresión (código: {process.returncode})."
            print(f"Error de Ghostscript durante la compresión: {error_message}")
            return False, f"Error de Ghostscript: {error_message}"

    except FileNotFoundError:
        msg = f"Error: El ejecutable de Ghostscript '{gs_executable_path}' no se encontró."
        print(msg)
        return False, msg
    except subprocess.TimeoutExpired:
        msg = "La operación de compresión de PDF excedió el tiempo límite."
        print(msg)
        Path(output_pdf_path).unlink(missing_ok=True) # Eliminar archivo parcial si existe
        return False, msg
    except Exception as e:
        msg = f"Ocurrió un error inesperado durante la compresión: {e}"
        print(msg)
        Path(output_pdf_path).unlink(missing_ok=True) # Eliminar archivo parcial si existe
        return False, msg
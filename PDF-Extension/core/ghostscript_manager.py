"""
Ghostscript operations manager for HYDRA21 PDF Compressor
Handles PDF compression, merging, and splitting using Ghostscript
"""

import subprocess
import platform
from pathlib import Path
from typing import Tuple, List, Optional, Callable
from dataclasses import dataclass
from config.settings import GS_QUALITY_PRESETS

@dataclass
class OperationResult:
    """Result of a Ghostscript operation"""
    success: bool
    message: str
    output_path: Optional[Path] = None
    original_size: Optional[int] = None
    final_size: Optional[int] = None
    processing_time: Optional[float] = None

class GhostscriptManager:
    """Manages Ghostscript operations for PDF processing"""
    
    def __init__(self, gs_path: str):
        self.gs_path = gs_path
        self.timeout = 300  # 5 minutes default timeout
    
    def _run_ghostscript_command(
        self, 
        command: List[str], 
        timeout: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Execute Ghostscript command
        
        Args:
            command: List of command arguments
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (success, message)
        """
        if timeout is None:
            timeout = self.timeout
        
        try:
            # Add creation flags for Windows to hide console window
            creation_flags = 0
            if platform.system().lower() == 'windows':
                creation_flags = subprocess.CREATE_NO_WINDOW
            
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=creation_flags
            )
            
            if process.returncode == 0:
                return True, "Operación completada exitosamente"
            else:
                error_msg = process.stderr.strip() if process.stderr else process.stdout.strip()
                return False, f"Error de Ghostscript: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, f"La operación excedió el tiempo límite de {timeout} segundos"
        except FileNotFoundError:
            return False, f"Ejecutable de Ghostscript no encontrado: {self.gs_path}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def compress_pdf(
        self,
        input_path: Path,
        output_path: Path,
        quality: str = "medium",
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> OperationResult:
        """
        Compress PDF file
        
        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF
            quality: Quality preset (high, medium, low)
            progress_callback: Optional progress callback
            
        Returns:
            OperationResult with operation details
        """
        import time
        start_time = time.time()
        
        if progress_callback:
            progress_callback("Iniciando compresión...")
        
        # Validate input
        if not input_path.exists():
            return OperationResult(
                success=False,
                message=f"Archivo de entrada no encontrado: {input_path}"
            )
        
        # Get quality setting
        quality_setting = GS_QUALITY_PRESETS.get(quality, {}).get("setting", "/ebook")
        
        # Get original file size
        original_size = input_path.stat().st_size
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build Ghostscript command
        command = [
            self.gs_path,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={quality_setting}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={str(output_path)}",
            str(input_path)
        ]
        
        if progress_callback:
            progress_callback("Ejecutando compresión...")
        
        # Execute compression
        success, message = self._run_ghostscript_command(command)
        
        processing_time = time.time() - start_time
        
        if success and output_path.exists():
            final_size = output_path.stat().st_size
            return OperationResult(
                success=True,
                message="PDF comprimido exitosamente",
                output_path=output_path,
                original_size=original_size,
                final_size=final_size,
                processing_time=processing_time
            )
        else:
            return OperationResult(
                success=False,
                message=message,
                processing_time=processing_time
            )
    
    def merge_pdfs(
        self,
        input_paths: List[Path],
        output_path: Path,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> OperationResult:
        """
        Merge multiple PDF files
        
        Args:
            input_paths: List of input PDF paths
            output_path: Path for merged PDF
            progress_callback: Optional progress callback
            
        Returns:
            OperationResult with operation details
        """
        import time
        start_time = time.time()
        
        if progress_callback:
            progress_callback("Iniciando fusión de PDFs...")
        
        # Validate inputs
        if not input_paths:
            return OperationResult(
                success=False,
                message="No se proporcionaron archivos para fusionar"
            )
        
        for path in input_paths:
            if not path.exists():
                return OperationResult(
                    success=False,
                    message=f"Archivo no encontrado: {path}"
                )
        
        # Calculate total original size
        original_size = sum(path.stat().st_size for path in input_paths)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build Ghostscript command for merging
        command = [
            self.gs_path,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={str(output_path)}"
        ]
        
        # Add input files
        command.extend([str(path) for path in input_paths])
        
        if progress_callback:
            progress_callback("Fusionando archivos PDF...")
        
        # Execute merge
        success, message = self._run_ghostscript_command(command)
        
        processing_time = time.time() - start_time
        
        if success and output_path.exists():
            final_size = output_path.stat().st_size
            return OperationResult(
                success=True,
                message=f"PDFs fusionados exitosamente ({len(input_paths)} archivos)",
                output_path=output_path,
                original_size=original_size,
                final_size=final_size,
                processing_time=processing_time
            )
        else:
            return OperationResult(
                success=False,
                message=message,
                processing_time=processing_time
            )
    
    def split_pdf(
        self,
        input_path: Path,
        output_dir: Path,
        start_page: int = 1,
        end_page: Optional[int] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> OperationResult:
        """
        Split PDF file into pages or page ranges
        
        Args:
            input_path: Path to input PDF
            output_dir: Directory for output files
            start_page: Starting page number (1-based)
            end_page: Ending page number (optional, if None splits all pages)
            progress_callback: Optional progress callback
            
        Returns:
            OperationResult with operation details
        """
        import time
        start_time = time.time()
        
        if progress_callback:
            progress_callback("Iniciando división de PDF...")
        
        # Validate input
        if not input_path.exists():
            return OperationResult(
                success=False,
                message=f"Archivo de entrada no encontrado: {input_path}"
            )
        
        # Get original file size
        original_size = input_path.stat().st_size
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build output filename pattern
        output_pattern = output_dir / f"{input_path.stem}_page_%d.pdf"
        
        # Build Ghostscript command for splitting
        command = [
            self.gs_path,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={str(output_pattern)}"
        ]
        
        # Add page range if specified
        if end_page is not None:
            command.extend([f"-dFirstPage={start_page}", f"-dLastPage={end_page}"])
        elif start_page > 1:
            command.append(f"-dFirstPage={start_page}")
        
        command.append(str(input_path))
        
        if progress_callback:
            progress_callback("Dividiendo archivo PDF...")
        
        # Execute split
        success, message = self._run_ghostscript_command(command)
        
        processing_time = time.time() - start_time
        
        if success:
            # Count generated files and calculate total size
            generated_files = list(output_dir.glob(f"{input_path.stem}_page_*.pdf"))
            final_size = sum(f.stat().st_size for f in generated_files)
            
            return OperationResult(
                success=True,
                message=f"PDF dividido exitosamente ({len(generated_files)} páginas)",
                output_path=output_dir,
                original_size=original_size,
                final_size=final_size,
                processing_time=processing_time
            )
        else:
            return OperationResult(
                success=False,
                message=message,
                processing_time=processing_time
            )

"""
Input validation utilities for HYDRA21 PDF Compressor
Provides validation functions for user inputs and file operations
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

class ValidationResult:
    """Result of a validation operation"""
    
    def __init__(self, is_valid: bool, message: str = "", details: Dict[str, Any] = None):
        self.is_valid = is_valid
        self.message = message
        self.details = details or {}
    
    def __bool__(self):
        return self.is_valid
    
    def __str__(self):
        return self.message

class FileValidator:
    """Validates file-related inputs and operations"""
    
    @staticmethod
    def validate_file_path(file_path: str) -> ValidationResult:
        """
        Validate file path string
        
        Args:
            file_path: File path to validate
            
        Returns:
            ValidationResult with validation outcome
        """
        if not file_path or not file_path.strip():
            return ValidationResult(False, "La ruta del archivo no puede estar vacía")
        
        # Check for null bytes
        if '\x00' in file_path:
            return ValidationResult(False, "La ruta del archivo contiene caracteres inválidos")
        
        try:
            path = Path(file_path)
            
            # Check if path is too long (Windows limit is ~260 characters)
            if len(str(path)) > 250:
                return ValidationResult(False, "La ruta del archivo es demasiado larga")
            
            # Check for invalid characters in filename
            invalid_chars = '<>:"|?*'
            filename = path.name
            for char in invalid_chars:
                if char in filename:
                    return ValidationResult(
                        False, 
                        f"El nombre del archivo contiene el carácter inválido: '{char}'"
                    )
            
            return ValidationResult(True, "Ruta de archivo válida")
            
        except Exception as e:
            return ValidationResult(False, f"Ruta de archivo inválida: {str(e)}")
    
    @staticmethod
    def validate_file_exists(file_path: Path) -> ValidationResult:
        """
        Validate that file exists and is accessible
        
        Args:
            file_path: Path object to validate
            
        Returns:
            ValidationResult with validation outcome
        """
        if not file_path.exists():
            return ValidationResult(False, f"El archivo no existe: {file_path}")
        
        if not file_path.is_file():
            return ValidationResult(False, f"La ruta no es un archivo: {file_path}")
        
        try:
            # Try to read the file to check permissions
            with open(file_path, 'rb') as f:
                f.read(1)
            return ValidationResult(True, "Archivo accesible")
        except PermissionError:
            return ValidationResult(False, f"Sin permisos para leer el archivo: {file_path}")
        except Exception as e:
            return ValidationResult(False, f"Error al acceder al archivo: {str(e)}")
    
    @staticmethod
    def validate_pdf_file(file_path: Path) -> ValidationResult:
        """
        Validate that file is a valid PDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            ValidationResult with validation outcome
        """
        # First check if file exists
        exists_result = FileValidator.validate_file_exists(file_path)
        if not exists_result:
            return exists_result
        
        # Check file extension
        if file_path.suffix.lower() != '.pdf':
            return ValidationResult(False, "El archivo no tiene extensión .pdf")
        
        # Check file size
        try:
            file_size = file_path.stat().st_size
            if file_size == 0:
                return ValidationResult(False, "El archivo PDF está vacío")
            
            # Check PDF header
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    return ValidationResult(False, "El archivo no es un PDF válido (header incorrecto)")
            
            return ValidationResult(True, "Archivo PDF válido", {"size": file_size})
            
        except Exception as e:
            return ValidationResult(False, f"Error al validar PDF: {str(e)}")
    
    @staticmethod
    def validate_output_directory(dir_path: Path) -> ValidationResult:
        """
        Validate output directory
        
        Args:
            dir_path: Directory path to validate
            
        Returns:
            ValidationResult with validation outcome
        """
        try:
            # Try to create directory if it doesn't exist
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Check if we can write to the directory
            test_file = dir_path / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
                return ValidationResult(True, "Directorio de salida válido")
            except PermissionError:
                return ValidationResult(False, f"Sin permisos de escritura en: {dir_path}")
            
        except Exception as e:
            return ValidationResult(False, f"Error al validar directorio: {str(e)}")

class InputValidator:
    """Validates user inputs and form data"""
    
    @staticmethod
    def validate_quality_setting(quality: str) -> ValidationResult:
        """
        Validate PDF quality setting
        
        Args:
            quality: Quality setting to validate
            
        Returns:
            ValidationResult with validation outcome
        """
        valid_qualities = ["high", "medium", "low"]
        
        if not quality:
            return ValidationResult(False, "La configuración de calidad no puede estar vacía")
        
        if quality not in valid_qualities:
            return ValidationResult(
                False, 
                f"Configuración de calidad inválida. Debe ser una de: {', '.join(valid_qualities)}"
            )
        
        return ValidationResult(True, "Configuración de calidad válida")
    
    @staticmethod
    def validate_page_range(start_page: int, end_page: Optional[int] = None) -> ValidationResult:
        """
        Validate page range for PDF splitting
        
        Args:
            start_page: Starting page number
            end_page: Ending page number (optional)
            
        Returns:
            ValidationResult with validation outcome
        """
        if start_page < 1:
            return ValidationResult(False, "La página inicial debe ser mayor a 0")
        
        if end_page is not None:
            if end_page < 1:
                return ValidationResult(False, "La página final debe ser mayor a 0")
            
            if end_page < start_page:
                return ValidationResult(False, "La página final debe ser mayor o igual a la página inicial")
        
        return ValidationResult(True, "Rango de páginas válido")
    
    @staticmethod
    def validate_filename(filename: str) -> ValidationResult:
        """
        Validate filename for output files
        
        Args:
            filename: Filename to validate
            
        Returns:
            ValidationResult with validation outcome
        """
        if not filename or not filename.strip():
            return ValidationResult(False, "El nombre del archivo no puede estar vacío")
        
        filename = filename.strip()
        
        # Check length
        if len(filename) > 200:
            return ValidationResult(False, "El nombre del archivo es demasiado largo")
        
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            if char in filename:
                return ValidationResult(
                    False, 
                    f"El nombre del archivo contiene el carácter inválido: '{char}'"
                )
        
        # Check for reserved names on Windows
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        name_without_ext = Path(filename).stem.upper()
        if name_without_ext in reserved_names:
            return ValidationResult(False, f"'{filename}' es un nombre reservado del sistema")
        
        return ValidationResult(True, "Nombre de archivo válido")

class BatchValidator:
    """Validates batch operations"""
    
    @staticmethod
    def validate_file_list(file_paths: List[Path], max_files: int = 100) -> ValidationResult:
        """
        Validate list of files for batch processing
        
        Args:
            file_paths: List of file paths to validate
            max_files: Maximum number of files allowed
            
        Returns:
            ValidationResult with validation outcome
        """
        if not file_paths:
            return ValidationResult(False, "No se han seleccionado archivos")
        
        if len(file_paths) > max_files:
            return ValidationResult(
                False, 
                f"Demasiados archivos seleccionados. Máximo permitido: {max_files}"
            )
        
        # Validate each file
        invalid_files = []
        total_size = 0
        
        for file_path in file_paths:
            pdf_result = FileValidator.validate_pdf_file(file_path)
            if not pdf_result:
                invalid_files.append(f"{file_path.name}: {pdf_result.message}")
            else:
                total_size += pdf_result.details.get("size", 0)
        
        if invalid_files:
            return ValidationResult(
                False, 
                f"Archivos inválidos encontrados: {len(invalid_files)}",
                {"invalid_files": invalid_files}
            )
        
        # Check total size (limit to 10GB for batch processing)
        max_total_size = 10 * 1024 * 1024 * 1024  # 10GB
        if total_size > max_total_size:
            return ValidationResult(
                False, 
                f"El tamaño total de los archivos excede el límite de 10GB"
            )
        
        return ValidationResult(
            True, 
            f"Lista de archivos válida ({len(file_paths)} archivos)",
            {"total_files": len(file_paths), "total_size": total_size}
        )
    
    @staticmethod
    def validate_merge_operation(file_paths: List[Path]) -> ValidationResult:
        """
        Validate files for merge operation
        
        Args:
            file_paths: List of PDF files to merge
            
        Returns:
            ValidationResult with validation outcome
        """
        if len(file_paths) < 2:
            return ValidationResult(False, "Se necesitan al menos 2 archivos para fusionar")
        
        # Use the general file list validation
        return BatchValidator.validate_file_list(file_paths, max_files=50)

class GhostscriptValidator:
    """Validates Ghostscript configuration and operations"""
    
    @staticmethod
    def validate_ghostscript_path(gs_path: str) -> ValidationResult:
        """
        Validate Ghostscript executable path
        
        Args:
            gs_path: Path to Ghostscript executable
            
        Returns:
            ValidationResult with validation outcome
        """
        if not gs_path or not gs_path.strip():
            return ValidationResult(False, "La ruta de Ghostscript no puede estar vacía")
        
        gs_path = gs_path.strip()
        
        # For commands in PATH (like 'gs', 'gswin64c.exe')
        if gs_path in ['gs', 'gswin64c.exe', 'gswin32c.exe']:
            return ValidationResult(True, "Comando de Ghostscript válido")
        
        # For full paths
        try:
            path = Path(gs_path)
            
            if not path.exists():
                return ValidationResult(False, f"El archivo de Ghostscript no existe: {gs_path}")
            
            if not path.is_file():
                return ValidationResult(False, f"La ruta no es un archivo: {gs_path}")
            
            # Check if it's executable (basic check)
            if not path.suffix.lower() in ['.exe', ''] and not path.name == 'gs':
                return ValidationResult(False, "El archivo no parece ser un ejecutable de Ghostscript")
            
            return ValidationResult(True, "Ruta de Ghostscript válida")
            
        except Exception as e:
            return ValidationResult(False, f"Error al validar ruta de Ghostscript: {str(e)}")

def validate_all_inputs(
    files: List[Path],
    quality: str,
    output_dir: Path,
    gs_path: str
) -> ValidationResult:
    """
    Validate all inputs for a PDF operation
    
    Args:
        files: List of input files
        quality: Quality setting
        output_dir: Output directory
        gs_path: Ghostscript path
        
    Returns:
        ValidationResult with overall validation outcome
    """
    # Validate files
    files_result = BatchValidator.validate_file_list(files)
    if not files_result:
        return files_result
    
    # Validate quality
    quality_result = InputValidator.validate_quality_setting(quality)
    if not quality_result:
        return quality_result
    
    # Validate output directory
    output_result = FileValidator.validate_output_directory(output_dir)
    if not output_result:
        return output_result
    
    # Validate Ghostscript
    gs_result = GhostscriptValidator.validate_ghostscript_path(gs_path)
    if not gs_result:
        return gs_result
    
    return ValidationResult(True, "Todas las validaciones pasaron correctamente")

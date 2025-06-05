"""
File management utilities for HYDRA21 PDF Compressor
Handles file operations, validation, and system integration
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass

@dataclass
class FileInfo:
    """Information about a file"""
    path: Path
    name: str
    size: int
    size_formatted: str
    extension: str
    is_valid: bool
    error_message: Optional[str] = None

class FileManager:
    """Manages file operations and validation"""
    
    def __init__(self, supported_extensions: List[str] = None, max_file_size_mb: int = 1000):
        self.supported_extensions = supported_extensions or ['.pdf']
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.2f} {size_names[i]}"
    
    def validate_file(self, file_path: Path) -> FileInfo:
        """
        Validate a file for processing
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            FileInfo object with validation results
        """
        try:
            if not file_path.exists():
                return FileInfo(
                    path=file_path,
                    name=file_path.name,
                    size=0,
                    size_formatted="0 B",
                    extension="",
                    is_valid=False,
                    error_message="El archivo no existe"
                )
            
            if not file_path.is_file():
                return FileInfo(
                    path=file_path,
                    name=file_path.name,
                    size=0,
                    size_formatted="0 B",
                    extension="",
                    is_valid=False,
                    error_message="La ruta no es un archivo"
                )
            
            # Get file info
            file_size = file_path.stat().st_size
            file_extension = file_path.suffix.lower()
            
            # Check file extension
            if file_extension not in self.supported_extensions:
                return FileInfo(
                    path=file_path,
                    name=file_path.name,
                    size=file_size,
                    size_formatted=self.format_file_size(file_size),
                    extension=file_extension,
                    is_valid=False,
                    error_message=f"Tipo de archivo no soportado: {file_extension}"
                )
            
            # Check file size
            if file_size > self.max_file_size_bytes:
                max_size_formatted = self.format_file_size(self.max_file_size_bytes)
                return FileInfo(
                    path=file_path,
                    name=file_path.name,
                    size=file_size,
                    size_formatted=self.format_file_size(file_size),
                    extension=file_extension,
                    is_valid=False,
                    error_message=f"Archivo demasiado grande (máximo: {max_size_formatted})"
                )
            
            # Check if file is empty
            if file_size == 0:
                return FileInfo(
                    path=file_path,
                    name=file_path.name,
                    size=file_size,
                    size_formatted=self.format_file_size(file_size),
                    extension=file_extension,
                    is_valid=False,
                    error_message="El archivo está vacío"
                )
            
            # Basic PDF validation (check if it starts with PDF header)
            if file_extension == '.pdf':
                try:
                    with open(file_path, 'rb') as f:
                        header = f.read(4)
                        if header != b'%PDF':
                            return FileInfo(
                                path=file_path,
                                name=file_path.name,
                                size=file_size,
                                size_formatted=self.format_file_size(file_size),
                                extension=file_extension,
                                is_valid=False,
                                error_message="El archivo no es un PDF válido"
                            )
                except Exception as e:
                    return FileInfo(
                        path=file_path,
                        name=file_path.name,
                        size=file_size,
                        size_formatted=self.format_file_size(file_size),
                        extension=file_extension,
                        is_valid=False,
                        error_message=f"Error al leer el archivo: {str(e)}"
                    )
            
            # File is valid
            return FileInfo(
                path=file_path,
                name=file_path.name,
                size=file_size,
                size_formatted=self.format_file_size(file_size),
                extension=file_extension,
                is_valid=True
            )
            
        except Exception as e:
            return FileInfo(
                path=file_path,
                name=file_path.name if file_path else "Unknown",
                size=0,
                size_formatted="0 B",
                extension="",
                is_valid=False,
                error_message=f"Error inesperado: {str(e)}"
            )
    
    def validate_files(self, file_paths: List[Path]) -> Tuple[List[FileInfo], List[FileInfo]]:
        """
        Validate multiple files
        
        Args:
            file_paths: List of file paths to validate
            
        Returns:
            Tuple of (valid_files, invalid_files)
        """
        valid_files = []
        invalid_files = []
        
        for file_path in file_paths:
            file_info = self.validate_file(file_path)
            if file_info.is_valid:
                valid_files.append(file_info)
            else:
                invalid_files.append(file_info)
        
        return valid_files, invalid_files
    
    def open_file(self, file_path: Path) -> bool:
        """
        Open file with default system application
        
        Args:
            file_path: Path to file to open
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not file_path.exists():
                return False
            
            system = platform.system().lower()
            
            if system == "windows":
                os.startfile(str(file_path))
            elif system == "darwin":  # macOS
                subprocess.run(["open", str(file_path)], check=True)
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", str(file_path)], check=True)
            
            return True
            
        except Exception as e:
            print(f"Error opening file {file_path}: {e}")
            return False
    
    def open_folder(self, folder_path: Path) -> bool:
        """
        Open folder in system file explorer
        
        Args:
            folder_path: Path to folder to open
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not folder_path.exists():
                return False
            
            system = platform.system().lower()
            
            if system == "windows":
                subprocess.run(["explorer", str(folder_path)], check=True)
            elif system == "darwin":  # macOS
                subprocess.run(["open", str(folder_path)], check=True)
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", str(folder_path)], check=True)
            
            return True
            
        except Exception as e:
            print(f"Error opening folder {folder_path}: {e}")
            return False
    
    def get_file_info_summary(self, file_infos: List[FileInfo]) -> Dict:
        """
        Get summary information for a list of files
        
        Args:
            file_infos: List of FileInfo objects
            
        Returns:
            Dictionary with summary information
        """
        total_files = len(file_infos)
        valid_files = [f for f in file_infos if f.is_valid]
        invalid_files = [f for f in file_infos if not f.is_valid]
        
        total_size = sum(f.size for f in valid_files)
        
        return {
            "total_files": total_files,
            "valid_files": len(valid_files),
            "invalid_files": len(invalid_files),
            "total_size": total_size,
            "total_size_formatted": self.format_file_size(total_size),
            "invalid_file_messages": [f"{f.name}: {f.error_message}" for f in invalid_files]
        }
    
    def create_unique_filename(self, base_path: Path, suffix: str = "") -> Path:
        """
        Create a unique filename by adding a counter if file exists
        
        Args:
            base_path: Base file path
            suffix: Optional suffix to add before extension
            
        Returns:
            Unique file path
        """
        if suffix:
            new_path = base_path.parent / f"{base_path.stem}{suffix}{base_path.suffix}"
        else:
            new_path = base_path
        
        counter = 1
        original_path = new_path
        
        while new_path.exists():
            if suffix:
                new_path = base_path.parent / f"{base_path.stem}{suffix}_{counter}{base_path.suffix}"
            else:
                new_path = base_path.parent / f"{base_path.stem}_{counter}{base_path.suffix}"
            counter += 1
        
        return new_path
    
    def cleanup_empty_directories(self, directory: Path):
        """
        Remove empty directories recursively
        
        Args:
            directory: Directory to clean up
        """
        try:
            if directory.exists() and directory.is_dir():
                # Remove empty subdirectories first
                for subdir in directory.iterdir():
                    if subdir.is_dir():
                        self.cleanup_empty_directories(subdir)
                
                # Remove this directory if it's empty
                try:
                    directory.rmdir()
                except OSError:
                    # Directory not empty, that's fine
                    pass
        except Exception as e:
            print(f"Error cleaning up directory {directory}: {e}")

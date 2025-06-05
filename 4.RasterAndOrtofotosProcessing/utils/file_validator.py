"""
HYDRA21 Orthophoto Processor Pro - File Validation System
Comprehensive file validation with detailed error detection and reporting
"""

import os
import mimetypes
import struct
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

from utils.logger import get_logger

class ValidationResult(Enum):
    """Validation result types"""
    VALID = "valid"
    INVALID_FORMAT = "invalid_format"
    CORRUPTED = "corrupted"
    PERMISSION_DENIED = "permission_denied"
    NOT_FOUND = "not_found"
    TOO_LARGE = "too_large"
    EMPTY = "empty"
    UNSUPPORTED = "unsupported"

class FileValidator:
    """Comprehensive file validator for orthophoto files"""
    
    def __init__(self, max_file_size: int = 2 * 1024 * 1024 * 1024):  # 2GB default
        self.max_file_size = max_file_size
        self.logger = get_logger()
        
        # Supported formats with their magic bytes
        self.supported_formats = {
            '.tif': {
                'magic_bytes': [
                    b'II*\x00',  # Little-endian TIFF
                    b'MM\x00*',  # Big-endian TIFF
                ],
                'mime_types': ['image/tiff', 'image/tif'],
                'description': 'Tagged Image File Format'
            },
            '.tiff': {
                'magic_bytes': [
                    b'II*\x00',  # Little-endian TIFF
                    b'MM\x00*',  # Big-endian TIFF
                ],
                'mime_types': ['image/tiff', 'image/tif'],
                'description': 'Tagged Image File Format'
            },
            '.ecw': {
                'magic_bytes': [b'\xff\xff\xff\xff'],  # ECW magic
                'mime_types': ['image/ecw'],
                'description': 'Enhanced Compression Wavelet'
            },
            '.jp2': {
                'magic_bytes': [
                    b'\x00\x00\x00\x0cjP  \r\n\x87\n',  # JPEG 2000
                    b'\xff\x4f\xff\x51',  # JPEG 2000 codestream
                ],
                'mime_types': ['image/jp2', 'image/jpeg2000'],
                'description': 'JPEG 2000'
            },
            '.img': {
                'magic_bytes': [],  # ERDAS IMAGINE doesn't have consistent magic bytes
                'mime_types': ['application/octet-stream'],
                'description': 'ERDAS IMAGINE'
            },
            '.bil': {
                'magic_bytes': [],  # ENVI formats don't have magic bytes
                'mime_types': ['application/octet-stream'],
                'description': 'Band Interleaved by Line'
            },
            '.bip': {
                'magic_bytes': [],
                'mime_types': ['application/octet-stream'],
                'description': 'Band Interleaved by Pixel'
            },
            '.bsq': {
                'magic_bytes': [],
                'mime_types': ['application/octet-stream'],
                'description': 'Band Sequential'
            }
        }
    
    def validate_file(self, file_path: Path) -> Tuple[ValidationResult, str, Dict[str, Any]]:
        """
        Comprehensive file validation
        
        Returns:
            Tuple of (result, message, details)
        """
        self.logger.validation_start(file_path)
        
        details = {
            'file_path': str(file_path),
            'file_size': 0,
            'format': None,
            'mime_type': None,
            'magic_bytes': None,
            'permissions': {},
            'errors': []
        }
        
        try:
            # Check if file exists
            if not file_path.exists():
                result = ValidationResult.NOT_FOUND
                message = f"Archivo no encontrado: {file_path}"
                self.logger.validation_result(file_path, False, message)
                return result, message, details
            
            # Check if it's a file (not directory)
            if not file_path.is_file():
                result = ValidationResult.INVALID_FORMAT
                message = f"La ruta no es un archivo: {file_path}"
                self.logger.validation_result(file_path, False, message)
                return result, message, details
            
            # Get file stats
            stat = file_path.stat()
            details['file_size'] = stat.st_size
            
            # Check file size
            if stat.st_size == 0:
                result = ValidationResult.EMPTY
                message = f"Archivo vacío: {file_path}"
                self.logger.validation_result(file_path, False, message)
                return result, message, details
            
            if stat.st_size > self.max_file_size:
                result = ValidationResult.TOO_LARGE
                message = f"Archivo demasiado grande: {stat.st_size / (1024**3):.2f} GB > {self.max_file_size / (1024**3):.2f} GB"
                self.logger.validation_result(file_path, False, message)
                return result, message, details
            
            # Check permissions
            permissions = self._check_permissions(file_path)
            details['permissions'] = permissions
            
            if not permissions['readable']:
                result = ValidationResult.PERMISSION_DENIED
                message = f"Sin permisos de lectura: {file_path}"
                self.logger.validation_result(file_path, False, message)
                return result, message, details
            
            # Check file format by extension
            file_ext = file_path.suffix.lower()
            if file_ext not in self.supported_formats:
                result = ValidationResult.UNSUPPORTED
                message = f"Formato no soportado: {file_ext}"
                self.logger.validation_result(file_path, False, message)
                return result, message, details
            
            details['format'] = self.supported_formats[file_ext]['description']
            
            # Check MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            details['mime_type'] = mime_type
            
            # Validate file content
            content_validation = self._validate_file_content(file_path, file_ext)
            details.update(content_validation)
            
            if not content_validation['valid']:
                result = ValidationResult.CORRUPTED
                message = f"Archivo corrupto o inválido: {content_validation['error']}"
                self.logger.validation_result(file_path, False, message)
                return result, message, details
            
            # All validations passed
            result = ValidationResult.VALID
            message = f"Archivo válido: {file_ext.upper()} - {details['format']}"
            self.logger.validation_result(file_path, True, message)
            return result, message, details
            
        except PermissionError as e:
            result = ValidationResult.PERMISSION_DENIED
            message = f"Error de permisos: {e}"
            details['errors'].append(str(e))
            self.logger.validation_result(file_path, False, message)
            return result, message, details
            
        except Exception as e:
            result = ValidationResult.CORRUPTED
            message = f"Error de validación: {e}"
            details['errors'].append(str(e))
            self.logger.validation_result(file_path, False, message)
            return result, message, details
    
    def _check_permissions(self, file_path: Path) -> Dict[str, bool]:
        """Check file permissions"""
        try:
            return {
                'readable': os.access(file_path, os.R_OK),
                'writable': os.access(file_path, os.W_OK),
                'executable': os.access(file_path, os.X_OK)
            }
        except Exception:
            return {
                'readable': False,
                'writable': False,
                'executable': False
            }
    
    def _validate_file_content(self, file_path: Path, file_ext: str) -> Dict[str, Any]:
        """Validate file content based on format"""
        validation = {
            'valid': False,
            'error': None,
            'magic_bytes': None,
            'header_info': {}
        }
        
        try:
            with open(file_path, 'rb') as f:
                # Read first 16 bytes for magic number validation
                header = f.read(16)
                validation['magic_bytes'] = header.hex()
                
                if len(header) < 4:
                    validation['error'] = "Archivo demasiado pequeño para contener header válido"
                    return validation
                
                # Validate based on format
                format_info = self.supported_formats[file_ext]
                
                if format_info['magic_bytes']:
                    # Check magic bytes
                    magic_found = False
                    for magic in format_info['magic_bytes']:
                        if header.startswith(magic):
                            magic_found = True
                            break
                    
                    if not magic_found:
                        validation['error'] = f"Magic bytes no coinciden para formato {file_ext}"
                        return validation
                
                # Format-specific validation
                if file_ext in ['.tif', '.tiff']:
                    validation.update(self._validate_tiff_header(header))
                elif file_ext == '.jp2':
                    validation.update(self._validate_jp2_header(header))
                elif file_ext == '.ecw':
                    validation.update(self._validate_ecw_header(header))
                else:
                    # For formats without magic bytes, assume valid if readable
                    validation['valid'] = True
                
        except Exception as e:
            validation['error'] = f"Error leyendo archivo: {e}"
            
        return validation
    
    def _validate_tiff_header(self, header: bytes) -> Dict[str, Any]:
        """Validate TIFF header structure"""
        validation = {'valid': False, 'header_info': {}}
        
        try:
            if len(header) < 8:
                validation['error'] = "Header TIFF incompleto"
                return validation
            
            # Check byte order
            if header[:2] == b'II':
                byte_order = 'little-endian'
                endian = '<'
            elif header[:2] == b'MM':
                byte_order = 'big-endian'
                endian = '>'
            else:
                validation['error'] = "Byte order TIFF inválido"
                return validation
            
            validation['header_info']['byte_order'] = byte_order
            
            # Check magic number (42)
            magic = struct.unpack(f'{endian}H', header[2:4])[0]
            if magic != 42:
                validation['error'] = f"Magic number TIFF inválido: {magic} (esperado: 42)"
                return validation
            
            # Get IFD offset
            ifd_offset = struct.unpack(f'{endian}I', header[4:8])[0]
            validation['header_info']['ifd_offset'] = ifd_offset
            
            validation['valid'] = True
            
        except Exception as e:
            validation['error'] = f"Error validando header TIFF: {e}"
            
        return validation
    
    def _validate_jp2_header(self, header: bytes) -> Dict[str, Any]:
        """Validate JPEG 2000 header"""
        validation = {'valid': False, 'header_info': {}}
        
        try:
            if len(header) >= 12:
                # Check JP2 signature box
                if header[:4] == b'\x00\x00\x00\x0c' and header[4:12] == b'jP  \r\n\x87\n':
                    validation['valid'] = True
                    validation['header_info']['format'] = 'JP2'
                elif header[:2] == b'\xff\x4f':
                    validation['valid'] = True
                    validation['header_info']['format'] = 'J2K codestream'
                else:
                    validation['error'] = "Signature JP2 inválida"
            else:
                validation['error'] = "Header JP2 incompleto"
                
        except Exception as e:
            validation['error'] = f"Error validando header JP2: {e}"
            
        return validation
    
    def _validate_ecw_header(self, header: bytes) -> Dict[str, Any]:
        """Validate ECW header"""
        validation = {'valid': False, 'header_info': {}}
        
        try:
            # ECW validation is complex, for now just check if it's readable
            if len(header) >= 4:
                validation['valid'] = True
                validation['header_info']['format'] = 'ECW'
            else:
                validation['error'] = "Header ECW incompleto"
                
        except Exception as e:
            validation['error'] = f"Error validando header ECW: {e}"
            
        return validation
    
    def validate_batch(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Validate multiple files and return summary"""
        results = {
            'valid_files': [],
            'invalid_files': [],
            'total_size': 0,
            'formats': {},
            'errors': []
        }
        
        self.logger.info(f"🔍 Validando {len(file_paths)} archivos...")
        
        for i, file_path in enumerate(file_paths):
            self.logger.progress(i, len(file_paths), f"Validando {file_path.name}")
            
            result, message, details = self.validate_file(file_path)
            
            if result == ValidationResult.VALID:
                results['valid_files'].append({
                    'path': file_path,
                    'size': details['file_size'],
                    'format': details['format'],
                    'details': details
                })
                results['total_size'] += details['file_size']
                
                # Count formats
                format_name = details['format']
                results['formats'][format_name] = results['formats'].get(format_name, 0) + 1
                
            else:
                results['invalid_files'].append({
                    'path': file_path,
                    'result': result,
                    'message': message,
                    'details': details
                })
                results['errors'].append(f"{file_path.name}: {message}")
        
        self.logger.progress(len(file_paths), len(file_paths), "Validación completada")
        
        # Log summary
        self.logger.info(f"✅ Archivos válidos: {len(results['valid_files'])}")
        self.logger.info(f"❌ Archivos inválidos: {len(results['invalid_files'])}")
        self.logger.info(f"📊 Tamaño total: {results['total_size'] / (1024**2):.2f} MB")
        
        if results['formats']:
            format_summary = ", ".join([f"{fmt}: {count}" for fmt, count in results['formats'].items()])
            self.logger.info(f"📁 Formatos: {format_summary}")
        
        return results
    
    def check_output_directory(self, output_dir: Path) -> Tuple[bool, str]:
        """Check if output directory is valid and writable"""
        try:
            # Create directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if it's writable
            test_file = output_dir / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
                return True, f"Directorio de salida válido: {output_dir}"
            except Exception as e:
                return False, f"Sin permisos de escritura en: {output_dir} - {e}"
                
        except Exception as e:
            return False, f"Error creando directorio: {output_dir} - {e}"

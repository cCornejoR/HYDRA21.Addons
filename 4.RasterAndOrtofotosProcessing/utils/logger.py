"""
HYDRA21 Orthophoto Processor Pro - Enhanced Logging System
Comprehensive logging with terminal output, debugging, and progress tracking
"""

import logging
import sys
import time
import psutil
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class LogLevel(Enum):
    """Log levels for different types of messages"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    PROGRESS = "PROGRESS"
    SUCCESS = "SUCCESS"

class ProcessingLogger:
    """Enhanced logger for orthophoto processing with terminal output and debugging"""
    
    def __init__(self, log_file: Optional[Path] = None, verbose: bool = True):
        self.verbose = verbose
        self.log_file = log_file
        self.start_time = None
        self.current_operation = None
        self.processed_files = 0
        self.total_files = 0
        self.errors = []
        self.warnings = []
        
        # Setup logging
        self._setup_logging()
        
        # System monitoring
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        
        # Thread-safe logging
        self._lock = threading.Lock()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logger
        self.logger = logging.getLogger('orthophoto_processor')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler with custom formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        # Custom formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def start_operation(self, operation_name: str, total_files: int = 0):
        """Start a new processing operation"""
        with self._lock:
            self.start_time = time.time()
            self.current_operation = operation_name
            self.processed_files = 0
            self.total_files = total_files
            self.errors.clear()
            self.warnings.clear()
            
            self._log_header(f"🚀 INICIANDO: {operation_name}")
            if total_files > 0:
                self.info(f"📁 Total de archivos a procesar: {total_files}")
            
            # System info
            self._log_system_info()
    
    def _log_header(self, message: str):
        """Log a header message with decorative borders"""
        border = "=" * 80
        print(f"\n{border}")
        print(f"{message}")
        print(f"{border}")
    
    def _log_system_info(self):
        """Log system information"""
        if self.verbose:
            memory_mb = self.process.memory_info().rss / (1024 * 1024)
            cpu_percent = self.process.cpu_percent()
            
            self.debug(f"💻 Sistema - Memoria: {memory_mb:.1f} MB, CPU: {cpu_percent:.1f}%")
            
            # Check available libraries
            self._check_dependencies()
    
    def _check_dependencies(self):
        """Check and log available dependencies"""
        dependencies = [
            ("rasterio", "Rasterio (geospatial processing)"),
            ("PIL", "Pillow (image processing)"),
            ("cv2", "OpenCV (computer vision)"),
            ("skimage", "scikit-image (image processing)"),
            ("numpy", "NumPy (numerical computing)")
        ]
        
        available = []
        missing = []
        
        for module, description in dependencies:
            try:
                __import__(module)
                available.append(description)
            except ImportError:
                missing.append(description)
        
        if available:
            self.debug(f"✅ Librerías disponibles: {', '.join(available)}")
        if missing:
            self.warning(f"⚠️ Librerías faltantes: {', '.join(missing)}")
    
    def debug(self, message: str):
        """Log debug message"""
        if self.verbose:
            self.logger.debug(f"🔍 {message}")
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(f"ℹ️ {message}")
    
    def warning(self, message: str):
        """Log warning message"""
        with self._lock:
            self.warnings.append(message)
        self.logger.warning(f"⚠️ {message}")
    
    def error(self, message: str, exception: Optional[Exception] = None):
        """Log error message"""
        with self._lock:
            error_info = {
                "message": message,
                "exception": str(exception) if exception else None,
                "timestamp": datetime.now().isoformat()
            }
            self.errors.append(error_info)
        
        full_message = f"❌ {message}"
        if exception:
            full_message += f" | Error: {exception}"
        
        self.logger.error(full_message)
    
    def success(self, message: str):
        """Log success message"""
        self.logger.info(f"✅ {message}")
    
    def progress(self, current: int, total: int, message: str = "", details: str = ""):
        """Log progress information"""
        percentage = (current / total * 100) if total > 0 else 0
        
        progress_bar = self._create_progress_bar(percentage)
        
        base_message = f"📊 Progreso: {progress_bar} {percentage:.1f}% ({current}/{total})"
        
        if message:
            base_message += f" | {message}"
        if details:
            base_message += f" | {details}"
        
        # Add memory usage if verbose
        if self.verbose:
            current_memory = self.process.memory_info().rss / (1024 * 1024)
            memory_delta = current_memory - (self.initial_memory / (1024 * 1024))
            base_message += f" | Memoria: {current_memory:.1f}MB ({memory_delta:+.1f}MB)"
        
        print(f"\r{base_message}", end="", flush=True)
        
        # New line on completion
        if current >= total:
            print()
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create a visual progress bar"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def file_start(self, file_path: Path, file_size: int):
        """Log start of file processing"""
        size_mb = file_size / (1024 * 1024)
        self.info(f"📄 Iniciando: {file_path.name} ({size_mb:.2f} MB)")
        
        if self.verbose:
            self.debug(f"   Ruta completa: {file_path}")
            self.debug(f"   Tamaño: {file_size:,} bytes")
    
    def file_complete(self, file_path: Path, processing_time: float, 
                     original_size: int, final_size: int):
        """Log completion of file processing"""
        compression_ratio = ((original_size - final_size) / original_size * 100) if original_size > 0 else 0
        speed_mbps = (original_size / (1024 * 1024)) / processing_time if processing_time > 0 else 0
        
        self.success(f"Completado: {file_path.name}")
        self.info(f"   ⏱️ Tiempo: {processing_time:.2f}s | 🗜️ Compresión: {compression_ratio:.1f}% | ⚡ Velocidad: {speed_mbps:.1f} MB/s")
        
        with self._lock:
            self.processed_files += 1
    
    def file_error(self, file_path: Path, error_message: str, exception: Optional[Exception] = None):
        """Log file processing error"""
        self.error(f"Error procesando {file_path.name}: {error_message}", exception)
    
    def validation_start(self, file_path: Path):
        """Log start of file validation"""
        self.debug(f"🔍 Validando archivo: {file_path.name}")
    
    def validation_result(self, file_path: Path, is_valid: bool, details: str = ""):
        """Log file validation result"""
        if is_valid:
            self.debug(f"✅ Validación exitosa: {file_path.name}")
            if details:
                self.debug(f"   Detalles: {details}")
        else:
            self.warning(f"❌ Validación fallida: {file_path.name} - {details}")
    
    def compression_method(self, method_name: str, file_path: Path):
        """Log compression method being used"""
        self.debug(f"🔧 Método de compresión: {method_name} para {file_path.name}")
    
    def io_operation(self, operation: str, file_path: Path, size: Optional[int] = None):
        """Log I/O operations"""
        if self.verbose:
            size_info = f" ({size:,} bytes)" if size else ""
            self.debug(f"💾 {operation}: {file_path.name}{size_info}")
    
    def memory_usage(self, context: str = ""):
        """Log current memory usage"""
        if self.verbose:
            current_memory = self.process.memory_info().rss / (1024 * 1024)
            memory_delta = current_memory - (self.initial_memory / (1024 * 1024))
            
            message = f"🧠 Memoria: {current_memory:.1f}MB ({memory_delta:+.1f}MB)"
            if context:
                message += f" | {context}"
            
            self.debug(message)
    
    def finish_operation(self):
        """Finish the current operation and log summary"""
        if not self.start_time:
            return
        
        elapsed_time = time.time() - self.start_time
        
        self._log_header(f"🏁 COMPLETADO: {self.current_operation}")
        
        # Summary statistics
        self.info(f"⏱️ Tiempo total: {elapsed_time:.2f} segundos")
        self.info(f"📁 Archivos procesados: {self.processed_files}/{self.total_files}")
        
        if self.processed_files > 0:
            avg_time = elapsed_time / self.processed_files
            self.info(f"📊 Tiempo promedio por archivo: {avg_time:.2f} segundos")
        
        # Error summary
        if self.errors:
            self.warning(f"❌ Errores encontrados: {len(self.errors)}")
            for error in self.errors[-3:]:  # Show last 3 errors
                self.warning(f"   • {error['message']}")
        
        if self.warnings:
            self.info(f"⚠️ Advertencias: {len(self.warnings)}")
        
        # Memory summary
        final_memory = self.process.memory_info().rss / (1024 * 1024)
        memory_delta = final_memory - (self.initial_memory / (1024 * 1024))
        self.info(f"🧠 Memoria final: {final_memory:.1f}MB ({memory_delta:+.1f}MB)")
        
        print("=" * 80)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get processing summary"""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        
        return {
            "operation": self.current_operation,
            "elapsed_time": elapsed_time,
            "processed_files": self.processed_files,
            "total_files": self.total_files,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "error_details": self.errors,
            "warning_details": self.warnings
        }

# Global logger instance
_logger_instance = None

def get_logger(log_file: Optional[Path] = None, verbose: bool = True) -> ProcessingLogger:
    """Get or create global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ProcessingLogger(log_file, verbose)
    return _logger_instance

def create_new_logger(log_file: Optional[Path] = None, verbose: bool = True) -> ProcessingLogger:
    """Create a new logger instance (not global)"""
    return ProcessingLogger(log_file, verbose)

def set_verbose(verbose: bool):
    """Set verbose mode for logging"""
    global _logger_instance
    if _logger_instance:
        _logger_instance.verbose = verbose
        _logger_instance._setup_logging()

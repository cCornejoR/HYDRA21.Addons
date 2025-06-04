"""
Helper utilities for HYDRA21 PDF Compressor
Common utility functions used throughout the application
"""

import time
import threading
from pathlib import Path
from typing import Any, Callable, Optional, Dict, List
from datetime import datetime, timedelta

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.0f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"

def format_timestamp(timestamp: Optional[float] = None) -> str:
    """
    Format timestamp to readable string
    
    Args:
        timestamp: Unix timestamp (optional, defaults to current time)
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = time.time()
    
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing/replacing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Characters not allowed in filenames on Windows
    invalid_chars = '<>:"/\\|?*'
    
    # Replace invalid characters with underscore
    safe_name = filename
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    
    # Ensure filename is not empty
    if not safe_name:
        safe_name = "unnamed_file"
    
    return safe_name

def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """
    Calculate compression ratio percentage
    
    Args:
        original_size: Original file size in bytes
        compressed_size: Compressed file size in bytes
        
    Returns:
        Compression ratio as percentage
    """
    if original_size == 0:
        return 0.0
    
    return ((original_size - compressed_size) / original_size) * 100

def get_file_extension_icon(extension: str) -> str:
    """
    Get appropriate icon for file extension
    
    Args:
        extension: File extension (with or without dot)
        
    Returns:
        Icon name for Flet
    """
    extension = extension.lower().lstrip('.')
    
    icon_map = {
        'pdf': 'picture_as_pdf',
        'doc': 'description',
        'docx': 'description',
        'txt': 'text_snippet',
        'jpg': 'image',
        'jpeg': 'image',
        'png': 'image',
        'gif': 'image',
        'zip': 'archive',
        'rar': 'archive',
        '7z': 'archive'
    }
    
    return icon_map.get(extension, 'insert_drive_file')

class Timer:
    """Simple timer utility for measuring execution time"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        self.end_time = None
    
    def stop(self):
        """Stop the timer"""
        if self.start_time is not None:
            self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0.0
        
        end = self.end_time if self.end_time is not None else time.time()
        return end - self.start_time
    
    @property
    def elapsed_formatted(self) -> str:
        """Get formatted elapsed time"""
        return format_duration(self.elapsed)
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

class Debouncer:
    """Debounce function calls to prevent excessive execution"""
    
    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self._timer = None
        self._lock = threading.Lock()
    
    def __call__(self, func: Callable, *args, **kwargs):
        """
        Debounce a function call
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
        """
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            
            self._timer = threading.Timer(
                self.delay,
                lambda: func(*args, **kwargs)
            )
            self._timer.start()
    
    def cancel(self):
        """Cancel pending debounced call"""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None

class RateLimiter:
    """Rate limiter to control function execution frequency"""
    
    def __init__(self, max_calls: int = 10, time_window: float = 1.0):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self._lock = threading.Lock()
    
    def can_execute(self) -> bool:
        """
        Check if function can be executed within rate limits
        
        Returns:
            True if execution is allowed, False otherwise
        """
        with self._lock:
            now = time.time()
            
            # Remove old calls outside the time window
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < self.time_window]
            
            # Check if we can make another call
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            
            return False
    
    def wait_time(self) -> float:
        """
        Get time to wait before next execution is allowed
        
        Returns:
            Wait time in seconds
        """
        with self._lock:
            if len(self.calls) < self.max_calls:
                return 0.0
            
            oldest_call = min(self.calls)
            return max(0.0, self.time_window - (time.time() - oldest_call))

def validate_path(path_str: str) -> Optional[Path]:
    """
    Validate and convert string to Path object
    
    Args:
        path_str: Path string to validate
        
    Returns:
        Path object if valid, None otherwise
    """
    try:
        path = Path(path_str)
        # Basic validation - check if path is not empty and doesn't contain null bytes
        if str(path).strip() and '\x00' not in str(path):
            return path
    except Exception:
        pass
    
    return None

def ensure_directory(directory: Path) -> bool:
    """
    Ensure directory exists, create if necessary
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")
        return False

def get_available_space(path: Path) -> Optional[int]:
    """
    Get available disk space for given path
    
    Args:
        path: Path to check
        
    Returns:
        Available space in bytes, None if error
    """
    try:
        import shutil
        return shutil.disk_usage(path).free
    except Exception:
        return None

def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human-readable string
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Formatted string
    """
    if bytes_value == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    size = float(bytes_value)
    
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.2f} {size_names[i]}"

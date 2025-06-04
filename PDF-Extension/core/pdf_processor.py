"""
PDF processing coordinator for HYDRA21 PDF Compressor
Manages batch operations and provides high-level PDF processing interface
"""

import asyncio
import time
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from core.ghostscript_manager import GhostscriptManager, OperationResult

@dataclass
class ProcessingStats:
    """Statistics for PDF processing operations"""
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    total_original_size: int = 0
    total_final_size: int = 0
    total_processing_time: float = 0.0
    individual_results: List[OperationResult] = field(default_factory=list)
    failed_files_list: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100
    
    @property
    def compression_ratio(self) -> float:
        """Calculate overall compression ratio percentage"""
        if self.total_original_size == 0:
            return 0.0
        return ((self.total_original_size - self.total_final_size) / self.total_original_size) * 100
    
    @property
    def size_reduction(self) -> int:
        """Calculate total size reduction in bytes"""
        return self.total_original_size - self.total_final_size

@dataclass
class BatchProgress:
    """Progress information for batch operations"""
    current_file: int = 0
    total_files: int = 0
    current_filename: str = ""
    current_operation: str = ""
    overall_progress: float = 0.0
    
    def update(self, current: int, total: int, filename: str, operation: str):
        """Update progress information"""
        self.current_file = current
        self.total_files = total
        self.current_filename = filename
        self.current_operation = operation
        self.overall_progress = (current / total) * 100 if total > 0 else 0.0

class PDFProcessor:
    """High-level PDF processing coordinator"""
    
    def __init__(self, gs_manager: GhostscriptManager, output_dir: Path):
        self.gs_manager = gs_manager
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._executor = ThreadPoolExecutor(max_workers=1)  # Single thread for PDF operations
    
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
    
    def compress_single_pdf(
        self,
        input_path: Path,
        quality: str = "medium",
        custom_output_name: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> OperationResult:
        """
        Compress a single PDF file
        
        Args:
            input_path: Path to input PDF
            quality: Quality preset (high, medium, low)
            custom_output_name: Custom output filename (optional)
            progress_callback: Progress callback function
            
        Returns:
            OperationResult with compression details
        """
        if custom_output_name:
            output_path = self.output_dir / custom_output_name
        else:
            output_path = self.output_dir / f"{input_path.stem}_compressed.pdf"
        
        # Ensure unique filename
        counter = 1
        original_output_path = output_path
        while output_path.exists():
            stem = original_output_path.stem
            suffix = original_output_path.suffix
            output_path = original_output_path.parent / f"{stem}_{counter}{suffix}"
            counter += 1
        
        return self.gs_manager.compress_pdf(
            input_path=input_path,
            output_path=output_path,
            quality=quality,
            progress_callback=progress_callback
        )
    
    def compress_batch(
        self,
        input_paths: List[Path],
        quality: str = "medium",
        progress_callback: Optional[Callable[[BatchProgress], None]] = None
    ) -> ProcessingStats:
        """
        Compress multiple PDF files in batch
        
        Args:
            input_paths: List of input PDF paths
            quality: Quality preset for all files
            progress_callback: Progress callback function
            
        Returns:
            ProcessingStats with batch processing results
        """
        stats = ProcessingStats(total_files=len(input_paths))
        progress = BatchProgress(total_files=len(input_paths))
        
        for i, input_path in enumerate(input_paths):
            # Update progress
            progress.update(
                current=i + 1,
                total=len(input_paths),
                filename=input_path.name,
                operation="Comprimiendo"
            )
            
            if progress_callback:
                progress_callback(progress)
            
            try:
                # Generate unique output filename
                output_path = self.output_dir / f"{input_path.stem}_compressed.pdf"
                counter = 1
                original_output_path = output_path
                while output_path.exists():
                    stem = original_output_path.stem
                    suffix = original_output_path.suffix
                    output_path = original_output_path.parent / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # Compress file
                result = self.gs_manager.compress_pdf(
                    input_path=input_path,
                    output_path=output_path,
                    quality=quality
                )
                
                # Update statistics
                if result.success:
                    stats.processed_files += 1
                    stats.total_original_size += result.original_size or 0
                    stats.total_final_size += result.final_size or 0
                    stats.total_processing_time += result.processing_time or 0
                    stats.individual_results.append(result)
                else:
                    stats.failed_files += 1
                    stats.failed_files_list.append(f"{input_path.name}: {result.message}")
                    
            except Exception as e:
                stats.failed_files += 1
                stats.failed_files_list.append(f"{input_path.name}: Error inesperado - {str(e)}")
        
        return stats
    
    def merge_pdfs(
        self,
        input_paths: List[Path],
        output_filename: str = "merged_document.pdf",
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> OperationResult:
        """
        Merge multiple PDF files into one
        
        Args:
            input_paths: List of PDF files to merge
            output_filename: Name for the merged file
            progress_callback: Progress callback function
            
        Returns:
            OperationResult with merge details
        """
        output_path = self.output_dir / output_filename
        
        # Ensure unique filename
        counter = 1
        original_output_path = output_path
        while output_path.exists():
            stem = original_output_path.stem
            suffix = original_output_path.suffix
            output_path = original_output_path.parent / f"{stem}_{counter}{suffix}"
            counter += 1
        
        return self.gs_manager.merge_pdfs(
            input_paths=input_paths,
            output_path=output_path,
            progress_callback=progress_callback
        )
    
    def split_pdf(
        self,
        input_path: Path,
        start_page: int = 1,
        end_page: Optional[int] = None,
        output_folder_name: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> OperationResult:
        """
        Split PDF into individual pages or page ranges
        
        Args:
            input_path: Path to PDF file to split
            start_page: Starting page number (1-based)
            end_page: Ending page number (optional)
            output_folder_name: Custom folder name for split files
            progress_callback: Progress callback function
            
        Returns:
            OperationResult with split details
        """
        if output_folder_name:
            output_dir = self.output_dir / output_folder_name
        else:
            output_dir = self.output_dir / f"{input_path.stem}_split"
        
        # Ensure unique directory name
        counter = 1
        original_output_dir = output_dir
        while output_dir.exists():
            output_dir = Path(str(original_output_dir) + f"_{counter}")
            counter += 1
        
        return self.gs_manager.split_pdf(
            input_path=input_path,
            output_dir=output_dir,
            start_page=start_page,
            end_page=end_page,
            progress_callback=progress_callback
        )
    
    def get_processing_summary(self, stats: ProcessingStats) -> Dict[str, Any]:
        """
        Generate a comprehensive processing summary
        
        Args:
            stats: ProcessingStats object
            
        Returns:
            Dictionary with formatted summary information
        """
        return {
            "total_files": stats.total_files,
            "processed_files": stats.processed_files,
            "failed_files": stats.failed_files,
            "success_rate": f"{stats.success_rate:.1f}%",
            "original_size": self.format_file_size(stats.total_original_size),
            "final_size": self.format_file_size(stats.total_final_size),
            "size_reduction": self.format_file_size(stats.size_reduction),
            "compression_ratio": f"{stats.compression_ratio:.1f}%",
            "processing_time": f"{stats.total_processing_time:.2f} segundos",
            "average_time_per_file": f"{stats.total_processing_time / max(stats.processed_files, 1):.2f} segundos",
            "failed_files_list": stats.failed_files_list
        }
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        # Implementation for cleaning temporary files if needed
        pass
    
    def __del__(self):
        """Cleanup when processor is destroyed"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)

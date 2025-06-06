#!/usr/bin/env python3
"""
HYDRA21 Orthophoto Processor Pro - OpenCV-based Processing Engine
Procesamiento de ortofotos usando OpenCV con preservación de metadatos
"""

import os
import time
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Core libraries
import numpy as np

# OpenCV for image processing
try:
    import cv2
    OPENCV_AVAILABLE = True
    print("✅ OpenCV disponible")
except ImportError:
    OPENCV_AVAILABLE = False
    print("❌ OpenCV no disponible - funcionalidad crítica faltante")

# PIL for additional image support
try:
    from PIL import Image, ImageOps, ExifTags
    from PIL.ExifTags import TAGS
    PILLOW_AVAILABLE = True
    print("✅ Pillow disponible")
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠️ Pillow no disponible")

# Metadata handling
try:
    import exifread
    EXIFREAD_AVAILABLE = True
    print("✅ ExifRead disponible")
except ImportError:
    EXIFREAD_AVAILABLE = False
    print("⚠️ ExifRead no disponible")

try:
    import piexif
    PIEXIF_AVAILABLE = True
    print("✅ Piexif disponible")
except ImportError:
    PIEXIF_AVAILABLE = False
    print("⚠️ Piexif no disponible")

from utils.logger import get_logger
from config.settings import get_optimal_cpu_count, PROCESSING_CONFIG


class OpenCVProcessor:
    """Procesador de ortofotos basado en OpenCV con preservación de metadatos"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.logger = get_logger("OpenCVProcessor")
        self.is_processing = False
        self.progress_callback = None
        self.statistics_callback = None
        
        # Verificar disponibilidad de librerías
        self._check_dependencies()
        
        # Configuración de procesamiento
        self.max_workers = get_optimal_cpu_count()
        self.logger.info(f"🔧 Configurado para usar {self.max_workers} núcleos de CPU")
        
        # Estadísticas
        self.stats = {
            'files_processed': 0,
            'files_failed': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'processing_start_time': None,
            'processing_end_time': None
        }
    
    def _check_dependencies(self):
        """Verificar dependencias disponibles"""
        if not OPENCV_AVAILABLE:
            raise RuntimeError("OpenCV es requerido para el procesamiento de imágenes")
        
        self.logger.info("📋 Dependencias disponibles:")
        self.logger.info(f"   OpenCV: {'✅' if OPENCV_AVAILABLE else '❌'}")
        self.logger.info(f"   Pillow: {'✅' if PILLOW_AVAILABLE else '❌'}")
        self.logger.info(f"   ExifRead: {'✅' if EXIFREAD_AVAILABLE else '❌'}")
        self.logger.info(f"   Piexif: {'✅' if PIEXIF_AVAILABLE else '❌'}")
    
    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """Establecer callback de progreso"""
        self.progress_callback = callback
    
    def set_statistics_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Establecer callback de estadísticas"""
        self.statistics_callback = callback
    
    def _update_progress(self, progress: float, message: str = ""):
        """Actualizar progreso"""
        if self.progress_callback:
            self.progress_callback(progress, message)
    
    def _update_statistics(self, stats: Dict[str, Any]):
        """Actualizar estadísticas"""
        if self.statistics_callback:
            self.statistics_callback(stats)
    
    def process_files(
        self,
        input_files: List[Path],
        output_dir: Path,
        compression_method: str = "high_quality",
        quality: int = 90,
        preserve_metadata: bool = True,
        max_workers: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Procesar archivos de ortofoto usando OpenCV
        
        Args:
            input_files: Lista de archivos de entrada
            output_dir: Directorio de salida
            compression_method: Método de compresión ('lossless', 'high_quality', 'medium', 'low')
            quality: Calidad de compresión (1-100)
            preserve_metadata: Preservar metadatos
            max_workers: Número máximo de workers
        
        Returns:
            Diccionario con resultados del procesamiento
        """
        
        if max_workers is None:
            max_workers = self.max_workers
        
        self.is_processing = True
        self.stats['processing_start_time'] = time.time()
        
        # Crear directorio de salida
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'success': False,
            'processed_files': [],
            'failed_files': [],
            'total_files': len(input_files),
            'compression_stats': {},
            'processing_time': 0,
            'error': None
        }
        
        try:
            self.logger.info(f"🚀 Iniciando procesamiento de {len(input_files)} archivos")
            self.logger.info(f"📁 Directorio de salida: {output_dir}")
            self.logger.info(f"🔧 Método de compresión: {compression_method}")
            self.logger.info(f"⚙️ Calidad: {quality}")
            self.logger.info(f"💾 Preservar metadatos: {preserve_metadata}")
            
            # Procesar archivos
            if max_workers == 1:
                # Procesamiento secuencial
                for i, input_file in enumerate(input_files):
                    progress = (i / len(input_files)) * 100
                    self._update_progress(progress, f"Procesando {input_file.name}")
                    
                    result = self._process_single_file(
                        input_file, output_dir, compression_method, quality, preserve_metadata
                    )
                    
                    if result['success']:
                        results['processed_files'].append(result)
                        self.stats['files_processed'] += 1
                    else:
                        results['failed_files'].append(result)
                        self.stats['files_failed'] += 1
                    
                    # Actualizar estadísticas
                    self._update_processing_stats()
            
            else:
                # Procesamiento paralelo
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Enviar tareas
                    future_to_file = {
                        executor.submit(
                            self._process_single_file,
                            input_file, output_dir, compression_method, quality, preserve_metadata
                        ): input_file for input_file in input_files
                    }
                    
                    # Procesar resultados
                    completed = 0
                    for future in as_completed(future_to_file):
                        input_file = future_to_file[future]
                        completed += 1
                        progress = (completed / len(input_files)) * 100
                        
                        try:
                            result = future.result()
                            self._update_progress(progress, f"Completado {input_file.name}")
                            
                            if result['success']:
                                results['processed_files'].append(result)
                                self.stats['files_processed'] += 1
                            else:
                                results['failed_files'].append(result)
                                self.stats['files_failed'] += 1
                        
                        except Exception as e:
                            self.logger.error(f"Error procesando {input_file}: {e}")
                            results['failed_files'].append({
                                'input_file': str(input_file),
                                'success': False,
                                'error': str(e)
                            })
                            self.stats['files_failed'] += 1
                        
                        # Actualizar estadísticas
                        self._update_processing_stats()
            
            # Finalizar procesamiento
            self.stats['processing_end_time'] = time.time()
            results['processing_time'] = self.stats['processing_end_time'] - self.stats['processing_start_time']
            results['success'] = len(results['processed_files']) > 0
            
            # Estadísticas finales
            if self.stats['total_original_size'] > 0:
                compression_ratio = (1 - self.stats['total_compressed_size'] / self.stats['total_original_size']) * 100
                results['compression_stats'] = {
                    'original_size_mb': self.stats['total_original_size'] / (1024 * 1024),
                    'compressed_size_mb': self.stats['total_compressed_size'] / (1024 * 1024),
                    'compression_ratio': compression_ratio,
                    'space_saved_mb': (self.stats['total_original_size'] - self.stats['total_compressed_size']) / (1024 * 1024)
                }
            
            self._update_progress(100, "Procesamiento completado")
            
            self.logger.success(f"✅ Procesamiento completado:")
            self.logger.success(f"   Archivos procesados: {len(results['processed_files'])}")
            self.logger.success(f"   Archivos fallidos: {len(results['failed_files'])}")
            self.logger.success(f"   Tiempo total: {results['processing_time']:.2f}s")
            
            if 'compression_ratio' in results['compression_stats']:
                self.logger.success(f"   Compresión: {results['compression_stats']['compression_ratio']:.1f}%")
        
        except Exception as e:
            self.logger.error(f"❌ Error crítico en procesamiento: {e}")
            results['error'] = str(e)
            results['success'] = False
        
        finally:
            self.is_processing = False
        
        return results
    
    def _process_single_file(
        self,
        input_file: Path,
        output_dir: Path,
        compression_method: str,
        quality: int,
        preserve_metadata: bool
    ) -> Dict[str, Any]:
        """Procesar un solo archivo"""
        
        result = {
            'input_file': str(input_file),
            'output_file': '',
            'success': False,
            'original_size': 0,
            'compressed_size': 0,
            'compression_ratio': 0,
            'processing_time': 0,
            'metadata_preserved': False,
            'error': None
        }
        
        start_time = time.time()
        
        try:
            # Verificar archivo de entrada
            if not input_file.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {input_file}")
            
            result['original_size'] = input_file.stat().st_size
            
            # Leer metadatos si es necesario
            metadata = None
            if preserve_metadata:
                metadata = self._extract_metadata(input_file)
            
            # Determinar formato de salida y configuración
            output_config = self._get_output_config(compression_method, quality)
            output_file = output_dir / f"processed_{input_file.stem}{output_config['extension']}"
            result['output_file'] = str(output_file)
            
            # Procesar imagen con OpenCV
            success = self._process_with_opencv(input_file, output_file, output_config)
            
            if success and preserve_metadata and metadata:
                # Restaurar metadatos
                self._restore_metadata(output_file, metadata)
                result['metadata_preserved'] = True
            
            # Verificar archivo de salida
            if output_file.exists():
                result['compressed_size'] = output_file.stat().st_size
                result['compression_ratio'] = (1 - result['compressed_size'] / result['original_size']) * 100
                result['success'] = True
                
                # Actualizar estadísticas globales
                self.stats['total_original_size'] += result['original_size']
                self.stats['total_compressed_size'] += result['compressed_size']
            else:
                raise RuntimeError("Archivo de salida no fue creado")
        
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.error(f"Error procesando {input_file.name}: {e}")
        
        finally:
            result['processing_time'] = time.time() - start_time
        
        return result

    def _extract_metadata(self, input_file: Path) -> Dict[str, Any]:
        """Extraer metadatos del archivo"""
        metadata = {}

        try:
            if PILLOW_AVAILABLE:
                # Usar PIL para extraer EXIF
                with Image.open(input_file) as img:
                    if hasattr(img, '_getexif') and img._getexif():
                        exif_data = img._getexif()
                        if exif_data:
                            for tag_id, value in exif_data.items():
                                tag = TAGS.get(tag_id, tag_id)
                                metadata[f"exif_{tag}"] = value

                    # Información básica de la imagen
                    metadata['width'] = img.width
                    metadata['height'] = img.height
                    metadata['mode'] = img.mode
                    metadata['format'] = img.format

            elif EXIFREAD_AVAILABLE:
                # Usar exifread como alternativa
                with open(input_file, 'rb') as f:
                    tags = exifread.process_file(f)
                    for tag in tags.keys():
                        if tag not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
                            metadata[f"exif_{tag}"] = str(tags[tag])

            # Información del archivo
            stat = input_file.stat()
            metadata['file_size'] = stat.st_size
            metadata['file_mtime'] = stat.st_mtime
            metadata['file_name'] = input_file.name

            self.logger.info(f"📋 Metadatos extraídos: {len(metadata)} campos")

        except Exception as e:
            self.logger.warning(f"⚠️ No se pudieron extraer metadatos: {e}")

        return metadata

    def _restore_metadata(self, output_file: Path, metadata: Dict[str, Any]):
        """Restaurar metadatos al archivo de salida"""
        try:
            if not PIEXIF_AVAILABLE:
                # Crear archivo de metadatos JSON como alternativa
                metadata_file = output_file.with_suffix(output_file.suffix + '.meta.json')
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, default=str)
                self.logger.info(f"💾 Metadatos guardados en: {metadata_file.name}")
                return

            # Usar piexif para restaurar EXIF en JPEG
            if output_file.suffix.lower() in ['.jpg', '.jpeg']:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

                # Convertir metadatos de vuelta a formato EXIF
                for key, value in metadata.items():
                    if key.startswith('exif_') and isinstance(value, (str, int, float)):
                        try:
                            # Mapear algunos campos comunes
                            if 'DateTime' in key:
                                exif_dict["0th"][piexif.ImageIFD.DateTime] = str(value)
                            elif 'Software' in key:
                                exif_dict["0th"][piexif.ImageIFD.Software] = str(value)
                            elif 'ImageWidth' in key:
                                exif_dict["0th"][piexif.ImageIFD.ImageWidth] = int(value)
                            elif 'ImageLength' in key:
                                exif_dict["0th"][piexif.ImageIFD.ImageLength] = int(value)
                        except:
                            pass

                # Insertar EXIF
                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, str(output_file))
                self.logger.info("📋 Metadatos EXIF restaurados")

            else:
                # Para otros formatos, crear archivo de metadatos
                metadata_file = output_file.with_suffix(output_file.suffix + '.meta.json')
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, default=str)
                self.logger.info(f"💾 Metadatos guardados en: {metadata_file.name}")

        except Exception as e:
            self.logger.warning(f"⚠️ No se pudieron restaurar metadatos: {e}")

    def _get_output_config(self, compression_method: str, quality: int) -> Dict[str, Any]:
        """Obtener configuración de salida según método de compresión"""

        configs = {
            'lossless': {
                'extension': '.png',
                'opencv_format': '.png',
                'compression_params': [cv2.IMWRITE_PNG_COMPRESSION, 9]
            },
            'high_quality': {
                'extension': '.jpg',
                'opencv_format': '.jpg',
                'compression_params': [cv2.IMWRITE_JPEG_QUALITY, max(90, quality)]
            },
            'medium': {
                'extension': '.jpg',
                'opencv_format': '.jpg',
                'compression_params': [cv2.IMWRITE_JPEG_QUALITY, max(75, min(quality, 89))]
            },
            'low': {
                'extension': '.jpg',
                'opencv_format': '.jpg',
                'compression_params': [cv2.IMWRITE_JPEG_QUALITY, min(70, quality)]
            }
        }

        return configs.get(compression_method, configs['high_quality'])

    def _process_with_opencv(self, input_file: Path, output_file: Path, config: Dict[str, Any]) -> bool:
        """Procesar imagen usando OpenCV"""
        try:
            # Leer imagen
            img = cv2.imread(str(input_file), cv2.IMREAD_UNCHANGED)
            if img is None:
                raise ValueError(f"No se pudo leer la imagen: {input_file}")

            self.logger.info(f"📷 Imagen cargada: {img.shape}")

            # Aplicar optimizaciones si es necesario
            if len(img.shape) == 3 and img.shape[2] == 4:
                # Imagen con canal alpha - convertir a RGB para JPEG
                if config['extension'] == '.jpg':
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # Guardar imagen con compresión
            success = cv2.imwrite(
                str(output_file),
                img,
                config['compression_params']
            )

            if success:
                self.logger.info(f"💾 Imagen guardada: {output_file.name}")
                return True
            else:
                raise RuntimeError("cv2.imwrite falló")

        except Exception as e:
            self.logger.error(f"❌ Error en procesamiento OpenCV: {e}")

            # Intentar con PIL como fallback
            if PILLOW_AVAILABLE:
                return self._process_with_pillow(input_file, output_file, config)

            return False

    def _process_with_pillow(self, input_file: Path, output_file: Path, config: Dict[str, Any]) -> bool:
        """Procesar imagen usando PIL como fallback"""
        try:
            with Image.open(input_file) as img:
                # Convertir modo si es necesario
                if config['extension'] == '.jpg' and img.mode in ['RGBA', 'LA']:
                    # Convertir a RGB para JPEG
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background

                # Configurar parámetros de guardado
                save_kwargs = {}
                if config['extension'] == '.jpg':
                    quality_value = config['compression_params'][1]
                    save_kwargs = {
                        'quality': quality_value,
                        'optimize': True
                    }
                elif config['extension'] == '.png':
                    save_kwargs = {
                        'optimize': True,
                        'compress_level': 9
                    }

                # Guardar imagen
                img.save(output_file, **save_kwargs)
                self.logger.info(f"💾 Imagen guardada con PIL: {output_file.name}")
                return True

        except Exception as e:
            self.logger.error(f"❌ Error en procesamiento PIL: {e}")
            return False

    def _update_processing_stats(self):
        """Actualizar estadísticas de procesamiento"""
        if self.stats['processing_start_time']:
            elapsed_time = time.time() - self.stats['processing_start_time']
            total_files = self.stats['files_processed'] + self.stats['files_failed']

            stats = {
                'files_processed': self.stats['files_processed'],
                'files_failed': self.stats['files_failed'],
                'total_files': total_files,
                'elapsed_time': elapsed_time,
                'processing_speed': total_files / elapsed_time if elapsed_time > 0 else 0,
                'compression_ratio': 0
            }

            if self.stats['total_original_size'] > 0:
                stats['compression_ratio'] = (1 - self.stats['total_compressed_size'] / self.stats['total_original_size']) * 100

            self._update_statistics(stats)

    def get_supported_formats(self) -> List[str]:
        """Obtener formatos soportados"""
        opencv_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        pillow_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'] if PILLOW_AVAILABLE else []

        # Combinar y eliminar duplicados
        all_formats = list(set(opencv_formats + pillow_formats))
        return sorted(all_formats)

    def stop_processing(self):
        """Detener procesamiento"""
        self.is_processing = False
        self.logger.info("🛑 Procesamiento detenido por el usuario")

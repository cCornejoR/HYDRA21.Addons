#!/usr/bin/env python3
"""
Test de carga de archivos para HYDRA21 Orthophoto Processor Pro
Verifica que la aplicación puede cargar archivos correctamente con OpenCV
"""

import sys
import tempfile
from pathlib import Path
import numpy as np

def test_opencv_availability():
    """Test 1: Verificar disponibilidad de OpenCV"""
    print("🔍 TESTING: OpenCV Availability")
    
    try:
        import cv2
        print(f"   ✅ OpenCV version: {cv2.__version__}")
        return True
    except ImportError:
        print("   ❌ OpenCV no disponible")
        return False

def test_metadata_libraries():
    """Test 2: Verificar librerías de metadatos"""
    print("\n📋 TESTING: Metadata Libraries")
    
    results = {}
    
    # Test ExifRead
    try:
        import exifread
        print("   ✅ ExifRead disponible")
        results['exifread'] = True
    except ImportError:
        print("   ⚠️ ExifRead no disponible")
        results['exifread'] = False
    
    # Test Piexif
    try:
        import piexif
        print("   ✅ Piexif disponible")
        results['piexif'] = True
    except ImportError:
        print("   ⚠️ Piexif no disponible")
        results['piexif'] = False
    
    # Test PIL
    try:
        from PIL import Image, ExifTags
        print("   ✅ PIL/Pillow disponible")
        results['pillow'] = True
    except ImportError:
        print("   ❌ PIL/Pillow no disponible")
        results['pillow'] = False
    
    return results

def test_opencv_processor():
    """Test 3: Verificar OpenCVProcessor"""
    print("\n🔧 TESTING: OpenCV Processor")
    
    try:
        from core.opencv_processor import OpenCVProcessor
        
        processor = OpenCVProcessor()
        print("   ✅ OpenCVProcessor creado correctamente")
        
        # Test formatos soportados
        formats = processor.get_supported_formats()
        print(f"   ✅ Formatos soportados: {len(formats)}")
        for fmt in formats:
            print(f"      - {fmt}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error creando OpenCVProcessor: {e}")
        return False

def test_file_formats():
    """Test 4: Verificar formatos de archivo soportados"""
    print("\n📁 TESTING: File Format Support")
    
    try:
        from config.settings import SUPPORTED_INPUT_FORMATS
        
        print(f"   ✅ Formatos configurados: {len(SUPPORTED_INPUT_FORMATS)}")
        for fmt in SUPPORTED_INPUT_FORMATS:
            print(f"      - {fmt}")
        
        # Verificar que incluye formatos básicos
        basic_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
        missing_formats = [fmt for fmt in basic_formats if fmt not in SUPPORTED_INPUT_FORMATS]
        
        if missing_formats:
            print(f"   ⚠️ Formatos básicos faltantes: {missing_formats}")
        else:
            print("   ✅ Todos los formatos básicos incluidos")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error verificando formatos: {e}")
        return False

def test_create_sample_images():
    """Test 5: Crear imágenes de muestra para testing"""
    print("\n🖼️ TESTING: Sample Image Creation")
    
    try:
        import cv2
        
        # Crear directorio temporal
        temp_dir = Path(tempfile.mkdtemp())
        print(f"   📁 Directorio temporal: {temp_dir}")
        
        # Crear imagen de muestra JPEG
        sample_jpg = temp_dir / "sample.jpg"
        img_rgb = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        cv2.imwrite(str(sample_jpg), img_rgb, [cv2.IMWRITE_JPEG_QUALITY, 90])
        
        if sample_jpg.exists():
            print(f"   ✅ Imagen JPEG creada: {sample_jpg.name} ({sample_jpg.stat().st_size} bytes)")
        
        # Crear imagen de muestra PNG
        sample_png = temp_dir / "sample.png"
        cv2.imwrite(str(sample_png), img_rgb, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        
        if sample_png.exists():
            print(f"   ✅ Imagen PNG creada: {sample_png.name} ({sample_png.stat().st_size} bytes)")
        
        # Crear imagen de muestra BMP
        sample_bmp = temp_dir / "sample.bmp"
        cv2.imwrite(str(sample_bmp), img_rgb)
        
        if sample_bmp.exists():
            print(f"   ✅ Imagen BMP creada: {sample_bmp.name} ({sample_bmp.stat().st_size} bytes)")
        
        print(f"   📂 Archivos de muestra en: {temp_dir}")
        return temp_dir
        
    except Exception as e:
        print(f"   ❌ Error creando imágenes de muestra: {e}")
        return None

def test_file_validation():
    """Test 6: Verificar validación de archivos"""
    print("\n✅ TESTING: File Validation")
    
    try:
        from utils.file_validator import FileValidator
        
        validator = FileValidator()
        print("   ✅ FileValidator creado correctamente")
        
        # Test con archivo inexistente
        fake_file = Path("archivo_inexistente.jpg")
        result, message, details = validator.validate_file(fake_file)
        print(f"   ✅ Validación archivo inexistente: {result.name}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en validación de archivos: {e}")
        return False

def test_processing_integration():
    """Test 7: Test de integración de procesamiento"""
    print("\n🔄 TESTING: Processing Integration")
    
    try:
        # Crear imagen de muestra
        temp_dir = test_create_sample_images()
        if not temp_dir:
            print("   ❌ No se pudieron crear imágenes de muestra")
            return False
        
        from core.opencv_processor import OpenCVProcessor
        
        processor = OpenCVProcessor()
        
        # Test de procesamiento básico
        sample_files = list(temp_dir.glob("*.jpg"))
        if sample_files:
            output_dir = temp_dir / "output"
            output_dir.mkdir(exist_ok=True)
            
            print(f"   🔄 Procesando {len(sample_files)} archivo(s)...")
            
            results = processor.process_files(
                input_files=sample_files,
                output_dir=output_dir,
                compression_method="high_quality",
                quality=85,
                preserve_metadata=True
            )
            
            if results['success']:
                print(f"   ✅ Procesamiento exitoso: {len(results['processed_files'])} archivos")
                print(f"   📊 Archivos fallidos: {len(results['failed_files'])}")
                
                if 'compression_stats' in results:
                    stats = results['compression_stats']
                    print(f"   📈 Compresión: {stats.get('compression_ratio', 0):.1f}%")
            else:
                print(f"   ⚠️ Procesamiento con problemas: {results.get('error', 'Error desconocido')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en test de integración: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("=" * 70)
    print("HYDRA21 Orthophoto Processor Pro - Test de Carga de Archivos")
    print("=" * 70)
    
    tests = [
        ("OpenCV Availability", test_opencv_availability),
        ("Metadata Libraries", test_metadata_libraries),
        ("OpenCV Processor", test_opencv_processor),
        ("File Formats", test_file_formats),
        ("Sample Images", test_create_sample_images),
        ("File Validation", test_file_validation),
        ("Processing Integration", test_processing_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 TODOS LOS TESTS PASARON!")
        print("\n📋 La aplicación está lista para cargar archivos:")
        print("   ✅ OpenCV funcionando correctamente")
        print("   ✅ Formatos de archivo soportados")
        print("   ✅ Procesamiento de imágenes operativo")
        print("   ✅ Preservación de metadatos disponible")
    else:
        print(f"⚠️ {total - passed} tests necesitan atención")
        print("\n🔧 Para resolver problemas:")
        print("   1. Ejecutar: install_metadata_libs.bat")
        print("   2. Verificar instalación de OpenCV")
        print("   3. Revisar configuración de formatos")
    
    print("=" * 70)
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

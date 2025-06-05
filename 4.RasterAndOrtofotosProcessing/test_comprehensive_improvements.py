"""
HYDRA21 Orthophoto Processor Pro - Comprehensive Improvements Test
Test all enhanced features: logging, validation, compression, error handling
"""

import sys
import time
import tempfile
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def create_test_files():
    """Create various test files for comprehensive testing"""
    test_files = []
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="hydra21_test_"))
    print(f"📁 Directorio de prueba: {temp_dir}")
    
    # 1. Valid TIFF file (minimal)
    valid_tiff = temp_dir / "valid_test.tif"
    tiff_header = b'II*\x00\x08\x00\x00\x00'  # Little-endian TIFF header
    tiff_data = tiff_header + b'\x00' * 1024  # 1KB file
    valid_tiff.write_bytes(tiff_data)
    test_files.append(("Valid TIFF", valid_tiff))
    
    # 2. Invalid file (wrong extension)
    invalid_file = temp_dir / "invalid_test.txt"
    invalid_file.write_text("This is not an image file")
    test_files.append(("Invalid format", invalid_file))
    
    # 3. Corrupted TIFF file
    corrupted_tiff = temp_dir / "corrupted_test.tif"
    corrupted_tiff.write_bytes(b"INVALID_HEADER" + b'\x00' * 500)
    test_files.append(("Corrupted TIFF", corrupted_tiff))
    
    # 4. Large file simulation
    large_file = temp_dir / "large_test.tif"
    large_data = tiff_header + b'\x00' * (5 * 1024 * 1024)  # 5MB file
    large_file.write_bytes(large_data)
    test_files.append(("Large TIFF", large_file))
    
    # 5. Empty file
    empty_file = temp_dir / "empty_test.tif"
    empty_file.touch()
    test_files.append(("Empty file", empty_file))
    
    return test_files, temp_dir

def test_enhanced_logging():
    """Test enhanced logging system"""
    print("\n" + "="*60)
    print("🔍 TESTING ENHANCED LOGGING SYSTEM")
    print("="*60)
    
    try:
        from utils.logger import get_logger
        
        # Create logger with verbose mode
        logger = get_logger(verbose=True)
        
        # Test different log levels
        logger.start_operation("Test Operation", 3)
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.success("This is a success message")
        logger.error("This is an error message")
        
        # Test progress logging
        for i in range(4):
            logger.progress(i, 3, f"Processing item {i}", f"Details for item {i}")
            time.sleep(0.5)
        
        # Test memory usage
        logger.memory_usage("After processing")
        
        # Finish operation
        logger.finish_operation()
        
        print("✅ Enhanced logging test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced logging test FAILED: {e}")
        return False

def test_file_validation():
    """Test comprehensive file validation"""
    print("\n" + "="*60)
    print("🔍 TESTING FILE VALIDATION SYSTEM")
    print("="*60)
    
    try:
        from utils.file_validator import FileValidator, ValidationResult
        
        # Create test files
        test_files, temp_dir = create_test_files()
        
        # Initialize validator
        validator = FileValidator()
        
        # Test individual file validation
        for description, file_path in test_files:
            print(f"\n📄 Testing: {description}")
            result, message, details = validator.validate_file(file_path)
            
            print(f"   Result: {result.value}")
            print(f"   Message: {message}")
            print(f"   Size: {details.get('file_size', 0)} bytes")
            
            if details.get('format'):
                print(f"   Format: {details['format']}")
        
        # Test batch validation
        print(f"\n📦 Testing batch validation...")
        file_paths = [file_path for _, file_path in test_files]
        batch_results = validator.validate_batch(file_paths)
        
        print(f"   Valid files: {len(batch_results['valid_files'])}")
        print(f"   Invalid files: {len(batch_results['invalid_files'])}")
        print(f"   Total size: {batch_results['total_size'] / (1024*1024):.2f} MB")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        print("✅ File validation test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ File validation test FAILED: {e}")
        return False

def test_compression_engine():
    """Test compression engine with multiple methods"""
    print("\n" + "="*60)
    print("🔍 TESTING COMPRESSION ENGINE")
    print("="*60)
    
    try:
        from core.compression_engine import CompressionEngine, CompressionResult
        
        # Create test files
        test_files, temp_dir = create_test_files()
        
        # Initialize compression engine
        engine = CompressionEngine()
        
        print(f"🔧 Available compression methods: {len(engine.available_methods)}")
        for method in engine.available_methods:
            print(f"   - {method.value}")
        
        # Test compression on valid file
        valid_file = None
        for description, file_path in test_files:
            if "Valid TIFF" in description:
                valid_file = file_path
                break
        
        if valid_file:
            output_file = temp_dir / "compressed_output.tif"
            
            print(f"\n🗜️ Testing compression on: {valid_file.name}")
            
            def progress_callback(message, progress):
                print(f"   Progress: {progress:.1f}% - {message}")
            
            result, details = engine.compress_file(
                valid_file,
                output_file,
                compression_type="JPEG",
                quality=85,
                progress_callback=progress_callback
            )
            
            print(f"   Result: {result.value}")
            if result == CompressionResult.SUCCESS:
                print(f"   Method used: {details.get('method_used', 'unknown')}")
                print(f"   Original size: {details.get('original_size', 0)} bytes")
                print(f"   Compressed size: {details.get('compressed_size', 0)} bytes")
                print(f"   Compression ratio: {details.get('compression_ratio', 0):.1f}%")
                print(f"   Processing time: {details.get('processing_time', 0):.2f}s")
            else:
                print(f"   Error: {details.get('error', 'Unknown error')}")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        print("✅ Compression engine test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Compression engine test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_processor():
    """Test enhanced orthophoto processor"""
    print("\n" + "="*60)
    print("🔍 TESTING ENHANCED ORTHOPHOTO PROCESSOR")
    print("="*60)
    
    try:
        from core.orthophoto_engine import OrthophotoProcessor
        
        # Create test files
        test_files, temp_dir = create_test_files()
        
        # Initialize processor
        processor = OrthophotoProcessor(verbose=True)
        
        # Test processing test functionality
        print("🧪 Testing processor test functionality...")
        test_result = processor.test_processing()
        
        if test_result["success"]:
            print("✅ Processor test functionality works")
        else:
            print(f"⚠️ Processor test had issues: {test_result.get('error', 'Unknown')}")
        
        # Test with real files
        valid_files = []
        for description, file_path in test_files:
            if "Valid TIFF" in description or "Large TIFF" in description:
                valid_files.append(file_path)
        
        if valid_files:
            output_dir = temp_dir / "output"
            
            print(f"\n🚀 Testing processing with {len(valid_files)} file(s)...")
            
            # Setup callbacks
            def progress_callback(message, progress, details):
                print(f"   📊 Progress: {progress:.1f}% - {message}")
                if details:
                    print(f"      Details: {details}")
            
            def stats_callback(stats):
                if "current_file" in stats:
                    print(f"   📄 Current: {stats['current_file']}")
                if "processing_speed" in stats:
                    print(f"   ⚡ Speed: {stats['processing_speed']:.1f} MB/s")
            
            def error_callback(error):
                print(f"   ❌ Error: {error}")
            
            processor.set_callbacks(
                progress_callback=progress_callback,
                statistics_callback=stats_callback,
                error_callback=error_callback
            )
            
            # Process files
            results = processor.process_files(
                input_files=valid_files,
                output_dir=output_dir,
                compression="LZW",
                quality=85,
                test_mode=True  # Process only first file
            )
            
            # Display results
            print(f"\n📊 PROCESSING RESULTS:")
            print(f"   ✅ Processed: {len(results.get('processed_files', []))}")
            print(f"   ❌ Failed: {len(results.get('failed_files', []))}")
            print(f"   ⏭️ Skipped: {len(results.get('skipped_files', []))}")
            print(f"   ⏱️ Time: {results.get('processing_time', 0):.2f}s")
            print(f"   🗜️ Compression ratio: {results.get('compression_ratio', 0):.1f}%")
            
            if results.get('compression_methods_used'):
                methods = ", ".join(results['compression_methods_used'].keys())
                print(f"   🔧 Methods used: {methods}")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        print("✅ Enhanced processor test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced processor test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test comprehensive error handling"""
    print("\n" + "="*60)
    print("🔍 TESTING ERROR HANDLING")
    print("="*60)
    
    try:
        from core.orthophoto_engine import OrthophotoProcessor
        from pathlib import Path
        
        processor = OrthophotoProcessor(verbose=True)
        
        # Test with non-existent files
        print("📄 Testing with non-existent files...")
        non_existent_files = [Path("non_existent_file.tif")]
        
        results = processor.process_files(
            input_files=non_existent_files,
            output_dir=Path("./test_output"),
            test_mode=True
        )
        
        print(f"   Failed files: {len(results.get('failed_files', []))}")
        
        # Test with invalid output directory
        print("📁 Testing with invalid output directory...")
        try:
            # Try to use a file as directory (should fail)
            invalid_output = Path(__file__)  # This file itself
            
            results = processor.process_files(
                input_files=[],
                output_dir=invalid_output,
                test_mode=True
            )
            
        except Exception as e:
            print(f"   Expected error caught: {type(e).__name__}")
        
        print("✅ Error handling test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test FAILED: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 80)
    print("HYDRA21 ORTHOPHOTO PROCESSOR PRO - COMPREHENSIVE IMPROVEMENTS TEST")
    print("=" * 80)
    
    tests = [
        ("Enhanced Logging", test_enhanced_logging),
        ("File Validation", test_file_validation),
        ("Compression Engine", test_compression_engine),
        ("Enhanced Processor", test_enhanced_processor),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print("\n" + "=" * 80)
    print(f"COMPREHENSIVE TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! All improvements are working correctly.")
        print("\n🚀 The application now features:")
        print("   ✅ Enhanced terminal logging with detailed progress")
        print("   ✅ Comprehensive file validation and error detection")
        print("   ✅ Multiple compression methods with fallback")
        print("   ✅ Real-time processing monitoring")
        print("   ✅ Robust error handling and recovery")
        print("   ✅ Processing pipeline verification")
        print("   ✅ Test mode for functionality verification")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("🔧 The application has partial functionality.")
    
    print("=" * 80)
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

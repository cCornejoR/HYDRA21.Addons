#!/usr/bin/env python3
"""
Simple build script for HYDRA21 PDF Compressor Pro
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 50)
    print("HYDRA21 PDF Compressor Pro v3.0 Builder")
    print("=" * 50)
    
    # Get current directory
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    print(f"Working directory: {current_dir}")
    
    # Check if spec file exists
    spec_file = current_dir / "HYDRA21-PDF-Compressor-Pro.spec"
    if not spec_file.exists():
        print(f"ERROR: Spec file not found: {spec_file}")
        return 1
    
    print(f"Found spec file: {spec_file}")
    
    # Clean previous builds
    print("\nCleaning previous builds...")
    for dir_name in ["dist", "build"]:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            import shutil
            shutil.rmtree(dir_path)
            print(f"Removed: {dir_path}")
    
    # Run PyInstaller
    print("\nRunning PyInstaller...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_file),
        "--clean",
        "--noconfirm"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print(result.stdout)
        
        # Check if executable was created
        exe_path = current_dir / "dist" / "HYDRA21-PDF-Compressor-Pro-v0.5.0.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ Executable created: {exe_path}")
            print(f"✅ Size: {size_mb:.1f} MB")
            return 0
        else:
            print("❌ Executable not found in dist folder")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

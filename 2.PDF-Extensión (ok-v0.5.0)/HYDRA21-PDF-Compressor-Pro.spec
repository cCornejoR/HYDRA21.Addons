# -*- mode: python ; coding: utf-8 -*-
# HYDRA21 PDF Compressor Pro - PyInstaller Spec File
# Professional PDF processing suite with tabbed interface

import os
from pathlib import Path

# Get the current directory
current_dir = Path(os.getcwd())

a = Analysis(
    ['main_professional.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=[
        # Include assets directory
        (str(current_dir / 'assets'), 'assets'),
        # Include config files
        (str(current_dir / 'config'), 'config'),
        # Include UI components
        (str(current_dir / 'ui'), 'ui'),
        # Include core modules
        (str(current_dir / 'core'), 'core'),
        # Include utils
        (str(current_dir / 'utils'), 'utils'),
    ],
    hiddenimports=[
        'flet',
        'PyPDF2',
        'pypdf',
        'psutil',
        'pathlib',
        'pydantic',
        'typing_extensions',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HYDRA21-PDF-Compressor-Pro-v0.5.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(current_dir / 'assets' / 'logo.ico'),
    version=str(current_dir / 'version_info.txt')
)

# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('assets', 'assets')]
binaries = []

# Let collect_all handle flet's hidden imports, binaries, and datas
flet_datas, flet_binaries, flet_hiddenimports = collect_all('flet')
datas += flet_datas
binaries += flet_binaries

# Explicitly add other known hidden imports
hiddenimports = ['pyperclip', 'PIL'] + flet_hiddenimports

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    # Add flet packages directly to ensure they are processed
    packages=['flet', 'flet_core', 'flet_desktop', 'flet_runtime', 'flet_fastapi', 'watchdog'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ClipboardManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True, # Changed to True for production
    console=False, # Changed to False for production
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icons\\logo_clipboard.ico'],
)

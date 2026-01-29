# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Get the base directory
BASE_DIR = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['main.py'],
    pathex=[BASE_DIR],
    binaries=[
        ('tools/r6-dissect.exe', 'tools'),
    ],
    datas=[
        ('web/templates', 'web/templates'),
        ('src/analyze_match_complete.py', 'src'),
    ],
    hiddenimports=[
        'flask',
        'pandas',
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.utils',
        'jinja2',
        'werkzeug',
        'markupsafe',
        'web',
        'web.app',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'PyQt5',
        'tkinter',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='R6Analyst',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='R6Analyst',
)

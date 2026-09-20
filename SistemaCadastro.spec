# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files


datas = collect_data_files('customtkinter')
datas.append(('assets/final_image.png', 'assets/'))

import os
config_build = 'config.ini' if os.path.exists('config.ini') else 'config.example.ini'
datas.append((config_build, '.'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['win32print', 'pywintypes', 'win32api'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SistemaCadastro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='SistemaCadastro',
)

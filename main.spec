# -*- mode: python ; coding: utf-8 -*-

import os
project_dir = os.path.abspath(os.path.dirname(__name__))


a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[('assets/ERT_SMALL.png', 'assets'), ('assets/RE_TRANS.png', 'assets')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='SPLATsim',
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
)

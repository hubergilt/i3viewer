# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['i3viewer/i3main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['vtkmodules.util.data_model', 'vtkmodules.vtkCommonCore', 'vtkmodules.vtkRenderingOpenGL2', 'vtkmodules.vtkInteractionStyle', 'vtkmodules.vtkRenderingFreeType', 'vtkmodules.vtkIOGeometry', 'vtkmodules.util.execution_model'],
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
    name='3dviewer.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

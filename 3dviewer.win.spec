# 3dviewer.spec - Cross-compiling for Windows from Linux (Arch/EndeavourOS)

from PyInstaller.utils.hooks import collect_submodules
import os

# Collect VTK hidden imports
hidden_imports = collect_submodules('vtkmodules')

# Set MinGW-w64 cross-compiler
os.environ["CC"] = "x86_64-w64-mingw32-gcc"
os.environ["CXX"] = "x86_64-w64-mingw32-g++"

a = Analysis(
    ['i3viewer/i3main.py'],
    pathex=['.'],
    hiddenimports=hidden_imports,
    binaries=[],
    datas=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='3dviewer.exe',
    debug=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for a GUI application
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='3dviewer'
)


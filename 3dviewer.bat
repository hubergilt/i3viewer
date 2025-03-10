@echo off

poetry run pyinstaller --clean --onefile --name=3dviewer.exe --target-arch=64 ^
    --hidden-import=vtkmodules.util.data_model ^
    --hidden-import=vtkmodules.vtkCommonCore ^
    --hidden-import=vtkmodules.vtkRenderingOpenGL2 ^
    --hidden-import=vtkmodules.vtkInteractionStyle ^
    --hidden-import=vtkmodules.vtkRenderingFreeType ^
    --hidden-import=vtkmodules.vtkIOGeometry ^
    --hidden-import=vtkmodules.util.execution_model ^
    --distpath=dist-windows ^
    --workpath=build-windows ^
    --specpath=. ^
    --noconsole ^
    i3viewer/i3main.py

echo.
echo PyInstaller process completed.
pause

# Makefile for Cross-Compiling Python Executable for Windows

# Compiler settings for MinGW-w64
CC := x86_64-w64-mingw32-gcc
CXX := x86_64-w64-mingw32-g++
WINDRES := x86_64-w64-mingw32-windres
DLLTOOL := x86_64-w64-mingw32-dlltool

# PyInstaller settings
PYINSTALLER := poetry run pyinstaller
TARGET_NAME := 3dviewer.exe
SOURCE_SCRIPT := i3viewer/i3main.py
DIST_DIR := dist-windows
BUILD_DIR := build-windows
SPEC_FILE := 3dviewer.spec

# Hidden imports for VTK modules
HIDDEN_IMPORTS := \
	--hidden-import=vtkmodules.util.data_model \
	--hidden-import=vtkmodules.vtkCommonCore \
	--hidden-import=vtkmodules.vtkRenderingOpenGL2 \
	--hidden-import=vtkmodules.vtkInteractionStyle \
	--hidden-import=vtkmodules.vtkRenderingFreeType \
	--hidden-import=vtkmodules.vtkIOGeometry \
	--hidden-import=vtkmodules.util.execution_model

# Set environment variables for MinGW-w64
export CC
export CXX
export WINDRES
export DLLTOOL

# Default target: Build the Windows executable
all: build

# Build using PyInstaller with cross-compilation
build:
	$(PYINSTALLER) --clean --onefile --name=$(TARGET_NAME) \
		--distpath=$(DIST_DIR) --workpath=$(BUILD_DIR) \
		$(HIDDEN_IMPORTS) $(SOURCE_SCRIPT)

# Build using the .spec file
spec:
	$(PYINSTALLER) --clean $(SPEC_FILE)

# Clean all build artifacts
clean:
	rm -rf $(DIST_DIR) $(BUILD_DIR) __pycache__ *.spec

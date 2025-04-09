# Makefile for Cross-Compiling Python Executable for Linux and Windows

# Compiler settings for MinGW-w64
CC := x86_64-w64-mingw32-gcc
CXX := x86_64-w64-mingw32-g++
WINDRES := x86_64-w64-mingw32-windres
DLLTOOL := x86_64-w64-mingw32-dlltool

# PyInstaller settings
PYINSTALLER := poetry run pyinstaller
TARGET_NAME := 3dviewer
SOURCE_SCRIPT := i3viewer/i3main.py
DIST_DIR := dist
BUILD_DIR := build
SPEC_FILE := 3dviewer.spec
SPEC_EXE := 3dviewer.exe.spec
SPEC_ELF := 3dviewer.elf.spec

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

# Default target: run on Linux
all:
	poetry run i3viewer
wine:
	wine poetry run i3viewer

# Build using PyInstaller with cross-compilation
build:
	$(PYINSTALLER) --clean --onefile --name=$(TARGET_NAME).exe \
		--distpath=$(DIST_DIR) --workpath=$(BUILD_DIR) \
		$(HIDDEN_IMPORTS) $(SOURCE_SCRIPT)

# Build using the .spec file
elf:
	$(PYINSTALLER) --clean $(SPEC_ELF)
exe:
	wine $(PYINSTALLER) --clean $(SPEC_EXE)
runelf:
	$(DIST_DIR)/$(TARGET_NAME)
runexe:
	wine $(DIST_DIR)/$(TARGET_NAME).exe

7zexe:
	7z a $(DIST_DIR)/$(TARGET_NAME)-bin-$(shell date +%Y-%m-%d).7z $(DIST_DIR)/$(TARGET_NAME).exe
	7z a $(DIST_DIR)/$(TARGET_NAME)-src-$(shell date +%Y-%m-%d).7z * -x\!dist -x\!.git -x\!build

installer:
	makensis setup.nsi

# Clean all build artifacts
clean:
	rm -rf $(DIST_DIR) $(BUILD_DIR) __pycache__

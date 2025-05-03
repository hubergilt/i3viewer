# i3dViewer Documentation

📦 ## Project Overview

i3dViewer is a 3D visualization and analysis application written in Python, designed with a modular architecture and UI support via Qt (likely PyQt or PySide), and visualization capabilities using VTK. This project uses Poetry for dependency management and packaging.

    Author: hubergilt@hotmail.com

    Project Root: $HOME/wd/poetry/i3viewer

    Package Name: i3viewer

📁 Project Structure

`i3viewer/ # Main package
│
├── i3main.py # Main entry point for the application
├── i3mainWindow.py # Main window logic
├── i3mainWindow.ui # Qt Designer UI file
├── i3vtkWidget.py # VTK widget integration for rendering
├── i3model.py # Data model handling
│
├── i3heatmap.py # Heatmap logic
├── i3heatmapDialog.py # Heatmap configuration dialog
├── i3heatmapDialog.ui # UI for heatmap dialog
│
├── i3help.py # Help/documentation logic
├── i3helpDialog.py # Help dialog window
├── i3helpDialog.ui # Qt UI file for help dialog
│
├── i3point.py # Point-related logic
├── i3pointDialog.py # Point configuration dialog
├── i3pointDialog.ui # Corresponding UI
│
├── i3polyline.py # Polyline-related logic
├── i3polylineDialog.py # Polyline configuration
├── i3polylineDialog.ui # UI for polyline dialog
│
├── i3enums.py # Application-specific enums
├── icons/ # Folder with application icons
├── icons.qrc # Qt resource collection file
├── icons_rc.py # Generated Python file from .qrc
├── **init**.py # Marks directory as a Python package`

⚙️ Setup & Installation

1. Install Poetry

If not installed:
`curl -sSL https://install.python-poetry.org | python3 -` 2. Install Project Dependencies

From the project root:
`cd /home/huber/wd/poetry/i3viewer
poetry install` 3. Activate the Virtual Environment
`poetry shell`
🚀 Running the Application

To run the main application:
`poetry run python -m i3viewer.i3main`
Or if you have defined a [tool.poetry.scripts] entry in pyproject.toml, e.g.:
`[tool.poetry.scripts]
i3viewer = "i3viewer.i3main:main"`
Then simply run:
`poetry run i3viewer`
🧪 Testing

A basic tests/ directory is present. To run tests:
`poetry run pytest`
You may need to install pytest via Poetry if not yet added:
`poetry add --dev pytest`
📦 Building Distributables

You have multiple \*.spec files for building with PyInstaller, including ELF and Windows executables. To build:
`poetry run pyinstaller 3dviewer.spec`
For cross-platform builds, customize and use the appropriate .spec file:

    3dviewer.elf.spec

    3dviewer.win.spec

    3dviewer.exe.spec

🧰 Developer Tools

    Makefile and Makefile.origin: Custom build commands.

    pyrightconfig.json: Configuration for Pyright type checking.

    setup.nsi: NSIS installer script for Windows.

    README.md: Project introduction and usage notes.

    .ui files: Designed in Qt Designer, should be converted via pyside6-uic or pyuic5 as needed.

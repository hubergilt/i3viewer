import sys
from PySide6.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt, Signal, QSettings
from i3viewer.i3pointDialog import Ui_Dialog  # Import the generated UI class for points

class NonModalDialog(QDialog, Ui_Dialog):
    # Define a custom signal to emit when the dialog is closed
    dialog_closed = Signal()
    
    def __init__(self, point_id, x, y, z, name):
        super().__init__()
        self.setupUi(self)  # Set up the UI from the generated class
        self.setWindowTitle("i3dViewer - Point Attributes")

        # Ensure the dialog stays on top of the main window
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
    
        # Make all QLineEdit fields read-only and right-aligned
        self.lineEdit.setReadOnly(True)  # Selected Point ID
        self.lineEdit.setAlignment(Qt.AlignRight)
        self.lineEdit_3.setReadOnly(True)  # X Coordinate
        self.lineEdit_3.setAlignment(Qt.AlignRight)
        self.lineEdit_2.setReadOnly(True)  # Y Coordinate
        self.lineEdit_2.setAlignment(Qt.AlignRight)
        self.lineEdit_4.setReadOnly(True)  # Z Coordinate
        self.lineEdit_4.setAlignment(Qt.AlignRight)
        self.lineEdit_5.setReadOnly(True)  # Name
        self.lineEdit_5.setAlignment(Qt.AlignRight)

        # Populate the fields with initial data
        self.update_dialog(point_id, x, y, z, name)

        # Initialize QSettings based on the type of dialog
        self.settings = QSettings("hpgl", "pointDialog")  # Settings for point dialog        

        # Restore the previous geometry (position and size)
        self.restore_geometry()
        
    def restore_geometry(self):
        """Restores the dialog's geometry from QSettings."""
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))        

    def update_dialog(self, point_id, x, y, z, name):
        """Update the dialog with new values."""
        # Populate the fields
        self.lineEdit.setText(str(point_id))  # Selected Point ID (integer as string)
        self.lineEdit_3.setText(f"{x:.3f}")  # X Coordinate (3 decimal places)
        self.lineEdit_2.setText(f"{y:.3f}")  # Y Coordinate (3 decimal places)
        self.lineEdit_4.setText(f"{z:.3f}")  # Z Coordinate (3 decimal places)
        self.lineEdit_5.setText(name)  # Name (text)

    def reset_dialog(self):
        """Clear all QLineEdit fields."""
        self.lineEdit.clear()  # Point ID
        self.lineEdit_3.clear()  # X Coordinate
        self.lineEdit_2.clear()  # Y Coordinate
        self.lineEdit_4.clear()  # Z Coordinate
        self.lineEdit_5.clear()  # Name

    def closeEvent(self, event):
        """Saves the dialog's geometry before closing."""
        self.settings.setValue("geometry", self.saveGeometry())
        """Override closeEvent to reset the dialog and emit a signal before closing."""
        self.reset_dialog()  # Reset the dialog
        self.dialog_closed.emit()  # Emit the custom signal
        event.accept()  # Accept the close event

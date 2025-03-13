import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt, Signal
from i3viewer.i3pickDialog import Ui_Dialog  # Import the generated UI class

class NonModalDialog(QDialog, Ui_Dialog):
    # Define a custom signal to emit when the dialog is closed
    dialog_closed = Signal()
    
    def __init__(self, polyline_id, num_points, length, points):
        super().__init__()
        self.setupUi(self)  # Set up the UI from the generated class
        self.setWindowTitle("i3Dviewer - Polyline Attributes")

        # Ensure the dialog stays on top of the main window
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
    
        # Make all QLineEdit fields read-only and right-aligned
        self.lineEdit.setReadOnly(True)  # Selected Polyline ID
        self.lineEdit.setAlignment(Qt.AlignRight)
        self.lineEdit_2.setReadOnly(True)  # Number of Points
        self.lineEdit_2.setAlignment(Qt.AlignRight)
        self.lineEdit_3.setReadOnly(True)  # Length of Polyline
        self.lineEdit_3.setAlignment(Qt.AlignRight)

        # Make the QTableWidget read-only
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)

        # Populate the fields and table with initial data
        self.update_dialog(polyline_id, num_points, length, points)

    def update_dialog(self, polyline_id, num_points, length, points):
        """Update the dialog with new values."""
        # Populate the fields
        self.lineEdit.setText(str(polyline_id))  # Selected Polyline ID (integer as string)
        self.lineEdit_2.setText(str(num_points))  # Number of Points
        self.lineEdit_3.setText(f"{length:.3f}")  # Length of Polyline (3 decimal places)

        # Populate the table with points
        self.tableWidget.setRowCount(num_points)
        self.tableWidget.setColumnCount(5)  # Id, Longitude, Latitude, Altitude, Gradient
        self.tableWidget.setHorizontalHeaderLabels(["Id", "Longitude", "Latitude", "Altitude", "Gradient"])

        # Calculate and populate the gradient column
        for row, (x, y, z) in enumerate(points):
            # Create QTableWidgetItem for each cell and set text alignment to right
            id_item = QTableWidgetItem(str(polyline_id))  # Id (integer as string)
            id_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 0, id_item)

            lon_item = QTableWidgetItem(f"{x:.3f}")  # Longitude (3 decimal places)
            lon_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 1, lon_item)

            lat_item = QTableWidgetItem(f"{y:.3f}")  # Latitude (3 decimal places)
            lat_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 2, lat_item)

            alt_item = QTableWidgetItem(f"{z:.3f}")  # Altitude (3 decimal places)
            alt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 3, alt_item)

            # Calculate gradient
            if row == 0:
                gradient = 0.0  # Gradient for the first point is 0
            else:
                z_prev = points[row - 1][2]  # Z value of the previous point
                gradient = 100 * (z - z_prev) / float(self.lineEdit_3.text())  # Gradient formula

            gradient_item = QTableWidgetItem(f"{gradient:.3f}")  # Gradient (3 decimal places)
            gradient_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableWidget.setItem(row, 4, gradient_item)


    def reset_dialog(self):
        """Clear all QLineEdit fields and reset the QTableWidget."""
        # Clear QLineEdit fields
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()

        # Clear the QTableWidget
        self.tableWidget.setRowCount(0)  # Remove all rows
        self.tableWidget.clearContents()  # Clear cell contents

    def closeEvent(self, event):
        """Override closeEvent to reset the dialog and emit a signal before closing."""
        self.reset_dialog()  # Reset the dialog
        self.dialog_closed.emit()  # Emit the custom signal
        event.accept()  # Accept the close event

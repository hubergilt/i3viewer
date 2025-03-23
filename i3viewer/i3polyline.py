from PySide6.QtCore import QSettings, Qt, Signal
from PySide6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem

from i3viewer.i3polylineDialog import \
    Ui_Dialog  # Import the generated UI class


class NonModalDialog(QDialog, Ui_Dialog):
    # Define a custom signal to emit when the dialog is closed
    dialog_closed = Signal()

    def __init__(self, polyline_id, num_points, length, points):
        super().__init__()
        self.setupUi(self)  # Set up the UI from the generated class
        self.setWindowTitle("i3dViewer - Polyline Attributes")

        # Ensure the dialog stays on top of the main window
        if hasattr(Qt, "WindowStaysOnTopHint"):
            self.setWindowFlags(
                self.windowFlags() | getattr(Qt, "WindowStaysOnTopHint")
            )

        if hasattr(Qt, "AlignRight"):
            # Make all QLineEdit fields read-only and right-aligned
            self.lineEdit.setReadOnly(True)  # Selected Polyline ID
            self.lineEdit.setAlignment(getattr(Qt, "AlignRight"))
            self.lineEdit_2.setReadOnly(True)  # Number of Points
            self.lineEdit_2.setAlignment(getattr(Qt, "AlignRight"))
            self.lineEdit_3.setReadOnly(True)  # Length of Polyline
            self.lineEdit_3.setAlignment(getattr(Qt, "AlignRight"))

        # Make the QTableWidget read-only
        if hasattr(QTableWidget, "NoEditTriggers"):
            self.tableWidget.setEditTriggers(
                getattr(QTableWidget, "NoEditTriggers"))

        # Populate the fields and table with initial data
        self.update_dialog(polyline_id, num_points, length, points)

        # Initialize QSettings based on the type of dialog
        self.settings = QSettings(
            "hpgl", "polylineDialog"
        )  # Settings for polyline dialog

        # Restore the previous geometry (position and size)
        self.restore_geometry()

    def restore_geometry(self):
        """Restores the dialog's geometry from QSettings."""
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))

    def update_dialog(self, polyline_id, num_points, length, points):
        """Update the dialog with new values."""
        # Populate the fields
        self.lineEdit.setText(
            str(polyline_id)
        )  # Selected Polyline ID (integer as string)
        self.lineEdit_2.setText(str(num_points))  # Number of Points
        self.lineEdit_3.setText(
            f"{length:.3f}"
        )  # Length of Polyline (3 decimal places)

        # Populate the table with points
        self.tableWidget.setRowCount(num_points)
        self.tableWidget.setColumnCount(
            14
        )  # Id, Longitude, Latitude, Altitude, Gradient,
        # velocidad máxima, tonelaje de material por carretera, resistencia a la rodadura,
        # límite máximo de velocidad, velocidad de frenado, rimpull, retardo,
        # consumo de combustible, nombre de la ruta
        self.tableWidget.setHorizontalHeaderLabels(
            [
                "Id",
                "Longitude",
                "Latitude",
                "Altitude",
                "Gradient",
                "velocidad máxima",
                "tonelaje de material por carretera",
                "resistencia a la rodadura",
                "límite máximo de velocidad",
                "velocidad de frenado",
                "rimpull",
                "retardo",
                "consumo de combustible",
                "nombre de la ruta",
            ]
        )

        # Populate the Id, Longitude, Latitude, Altitude, and Gradient column
        for row, (x, y, z, g, *rest) in enumerate(points):

            if hasattr(Qt, "AlignRight") and hasattr(Qt, "AlignVCenter"):
                # Create QTableWidgetItem for each cell and set text alignment to right
                # Id (integer as string)
                id_item = QTableWidgetItem(str(polyline_id))
                id_item.setTextAlignment(
                    getattr(Qt, "AlignRight") | getattr(Qt, "AlignVCenter")
                )
                self.tableWidget.setItem(row, 0, id_item)

                # Longitude (3 decimal places)
                lon_item = QTableWidgetItem(f"{x:.3f}")
                lon_item.setTextAlignment(
                    getattr(Qt, "AlignRight") | getattr(Qt, "AlignVCenter")
                )
                self.tableWidget.setItem(row, 1, lon_item)

                # Latitude (3 decimal places)
                lat_item = QTableWidgetItem(f"{y:.3f}")
                lat_item.setTextAlignment(
                    getattr(Qt, "AlignRight") | getattr(Qt, "AlignVCenter")
                )
                self.tableWidget.setItem(row, 2, lat_item)

                # Altitude (3 decimal places)
                alt_item = QTableWidgetItem(f"{z:.3f}")
                alt_item.setTextAlignment(
                    getattr(Qt, "AlignRight") | getattr(Qt, "AlignVCenter")
                )
                self.tableWidget.setItem(row, 3, alt_item)

                # Gradient (3 decimal places)
                gra_item = QTableWidgetItem(f"{g:.3f}")
                gra_item.setTextAlignment(
                    getattr(Qt, "AlignRight") | getattr(Qt, "AlignVCenter")
                )
                self.tableWidget.setItem(row, 4, gra_item)

                if rest and len(rest) == 9:
                    for index, val in enumerate(rest[:8]):
                        val_item = QTableWidgetItem(
                            f"{val:.3f}" if val is not None else ""
                        )
                        val_item.setTextAlignment(
                            getattr(Qt, "AlignRight") | getattr(
                                Qt, "AlignVCenter")
                        )
                        self.tableWidget.setItem(row, 5 + index, val_item)

                    ruta = rest[8]
                    ruta_item = QTableWidgetItem(ruta)  # nombre de ruta (text)
                    ruta_item.setTextAlignment(
                        getattr(Qt, "AlignRight") | getattr(Qt, "AlignVCenter")
                    )
                    self.tableWidget.setItem(row, 13, ruta_item)

        # Adjust column widths to fit content
        self.tableWidget.resizeColumnsToContents()

    def clear_dialog(self):
        """Clear all QLineEdit fields and reset the QTableWidget."""
        # Clear QLineEdit fields
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()

        # Clear the QTableWidget
        self.tableWidget.setRowCount(0)  # Remove all rows
        self.tableWidget.clearContents()  # Clear cell contents

    def closeEvent(self, event):
        """Saves the dialog's geometry before closing."""
        self.settings.setValue("geometry", self.saveGeometry())
        """Override closeEvent to reset the dialog and emit a signal before closing."""
        self.clear_dialog()  # Reset the dialog
        self.dialog_closed.emit()  # Emit the custom signal
        event.accept()  # Accept the close event

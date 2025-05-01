import csv

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QDialog, QFileDialog, QMessageBox,
                               QProgressDialog)

from i3viewer.i3heatmapDialog import \
    Ui_Dialog  # Import the generated UI class for points


class HeatMapDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Set up the user interface from Designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Customize the dialog (non-modal specific settings)
        self.setWindowTitle("i3dViewer - HeatMap Dialog")
        if hasattr(Qt, "RightToLeft"):
            self.ui.pushButton.setLayoutDirection(getattr(Qt, "RightToLeft"))  # This will put icon on right
            self.ui.pushButton_2.setLayoutDirection(getattr(Qt, "RightToLeft"))  # This will put icon on right

        # Connect signals to slots
        self.ui.pushButton.clicked.connect(self.import_routes_file)
        self.ui.pushButton_2.clicked.connect(self.import_tonnes_file)
        self.ui.pushButton_3.clicked.connect(self.reject)  # Cancel button
        self.ui.pushButton_4.clicked.connect(self.load_configuration)

        # Initialize data storage
        self.routes_file=None
        self.tonnes_file=None
        self.routes_data=[]
        self.tonnes_data=[]

        # Set window title
        self.setWindowTitle("i3 Heatmap Configuration")

    def import_routes_file(self):
        """Handle importing the routes file"""
        file_path, _=QFileDialog.getOpenFileName(
            self, "Select Routes File", "", "Text Files for Routes (*.txt)"
        )

        if file_path:
            self.routes_file=file_path
            self.ui.pushButton.setText(f"{file_path.split('/')[-1]}")
            self.ui.pushButton.setIcon(QIcon(u":/icons/check.svg"))

    def import_tonnes_file(self):
        """Handle importing the tonnes file"""
        file_path, _=QFileDialog.getOpenFileName(
            self, "Select Tonnes File", "", "CSV Files for Tonnes (*.csv)"
        )

        if file_path:
            self.tonnes_file=file_path
            self.ui.pushButton_2.setText(
                f"{file_path.split('/')[-1]}")
            self.ui.pushButton_2.setIcon(QIcon(u":/icons/check.svg"))

    def validate_files(self):
        """Validate the selected files before processing"""
        if not self.routes_file or not self.tonnes_file:
            QMessageBox.warning(
                self,
                "Missing Files",
                "Please select both routes and tonnes files before loading configuration.",
            )
            return False

        return True

    def read_routes_file(self):
        """Read and parse the routes text file"""
        if not self.routes_file:
            return
        try:
            with open(self.routes_file, "r") as file:
                self.routes_data=[line.strip()
                                    for line in file if line.strip()]
            return True
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Reading Routes File",
                f"Could not read routes file:\n{str(e)}",
            )
            return False

    def read_tonnes_file(self):
        """Read and parse the tonnes CSV file"""
        if not self.tonnes_file:
            return
        try:
            with open(self.tonnes_file, "r") as file:
                reader=csv.reader(file)
                self.tonnes_data=[
                    row for row in reader if any(field.strip() for field in row)
                ]
            return True
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Reading Tonnes File",
                f"Could not read tonnes file:\n{str(e)}",
            )
            return False

    def process_data(self):
        """Process the loaded data to create heatmap configuration"""
        # Basic validation of data
        if not self.routes_data or not self.tonnes_data:
            QMessageBox.warning(
                self, "Empty Data", "One or both files contain no valid data."
            )
            return False

        # Here you would add your actual data processing logic
        # For demonstration, we'll just check if we have some data

        routes_count=len(self.routes_data)
        tonnes_count=len(self.tonnes_data)

        return {
            "routes_count": routes_count,
            "tonnes_count": tonnes_count,
            "sample_route": self.routes_data[0] if routes_count > 0 else None,
            "sample_tonnes": self.tonnes_data[0] if tonnes_count > 0 else None,
        }

    def load_configuration(self):
        """Handle loading the configuration with selected files"""
        if not self.validate_files():
            return

        # Create progress dialog
        progress=QProgressDialog("Processing files...", "Cancel", 0, 3, self)
        progress.setWindowTitle("Loading Configuration")
        #progress.setWindowModality(Qt.WindowModal)
        progress.setValue(0)

        # Step 1: Read routes file
        progress.setLabelText("Reading routes file...")
        if not self.read_routes_file():
            return
        progress.setValue(1)

        # Check for cancellation
        if progress.wasCanceled():
            return

        # Step 2: Read tonnes file
        progress.setLabelText("Reading tonnes file...")
        if not self.read_tonnes_file():
            return
        progress.setValue(2)

        # Check for cancellation
        if progress.wasCanceled():
            return

        # Step 3: Process data
        progress.setLabelText("Processing data...")
        result=self.process_data()
        progress.setValue(3)

        if result:
            # Show success message with basic info
            message=(
                f"Configuration loaded successfully!\n\n"
                f"Routes: {result['routes_count']} entries\n"
                f"Tonnes: {result['tonnes_count']} entries\n\n"
                f"Sample route: {result['sample_route']}\n"
                f"Sample tonnes: {result['sample_tonnes']}"
            )

            if hasattr(QMessageBox, "Ok"):
                QMessageBox.information(
                    self,
                    "Success",
                    message,
                    getattr(QMessageBox, "Ok")
                )

            # Close the dialog if everything went well
            self.accept()

    def closeEvent(self, event):
        """Handle window close event"""
        if hasattr(QMessageBox, "Yes") or hasattr(QMessageBox, "No"):
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Are you sure you want to exit?",
                getattr(QMessageBox, "Yes") | getattr(QMessageBox, "No"),
                getattr(QMessageBox, "No")  # Default is No
            )
            if reply != getattr(QMessageBox, "Yes"):
                event.accept()
            else:
                event.ignore()

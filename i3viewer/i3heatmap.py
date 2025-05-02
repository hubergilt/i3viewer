from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from i3viewer.i3heatmapDialog import \
    Ui_Dialog  # Import the generated UI class for points


class HeatMapDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        # Set up the user interface from Designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.model = model

        # Customize the dialog (non-modal specific settings)
        self.setWindowTitle("i3dViewer - HeatMap Dialog")
        if hasattr(Qt, "RightToLeft"):
            self.ui.pushButton.setLayoutDirection(
                getattr(Qt, "RightToLeft")
            )  # This will put icon on right
            self.ui.pushButton_2.setLayoutDirection(
                getattr(Qt, "RightToLeft")
            )  # This will put icon on right
            self.ui.pushButton_4.setLayoutDirection(
                getattr(Qt, "RightToLeft")
            )  # This will put icon on right

        # Connect signals to slots
        self.ui.pushButton.clicked.connect(self.import_routes_file)
        self.ui.pushButton_2.clicked.connect(self.import_tonnes_file)
        self.ui.pushButton_3.clicked.connect(self.reject)  # Cancel button
        self.ui.pushButton_4.clicked.connect(self.load_config)

        # Initialize icons
        self.config_icons()

    def config_icons(self):
        if self.model:
            if self.model.hasRoutesTable():
                self.ui.pushButton.setIcon(QIcon(":/icons/check.svg"))
            else:
                self.ui.pushButton.setIcon(QIcon(":/icons/cross.svg"))
            if self.model.hasTonnesTable():
                self.ui.pushButton_2.setIcon(QIcon(":/icons/check.svg"))
            else:
                self.ui.pushButton_2.setIcon(QIcon(":/icons/cross.svg"))
            if self.model.hasRoutesTonnesTable():
                self.ui.pushButton_4.setIcon(QIcon(":/icons/check.svg"))
            else:
                self.ui.pushButton_4.setIcon(QIcon(":/icons/cross.svg"))

    def import_routes_file(self):
        """Handle importing the routes file"""
        if not self.model:
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Routes File", "", "Text Files for Routes (*.txt)"
        )
        if file_path:
            self.ui.pushButton.setText(f"{file_path.split('/')[-1]}")
            self.model.routes_save_database(file_path)
            self.config_icons()

    def import_tonnes_file(self):
        """Handle importing the tonnes file"""
        if not self.model:
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Tonnes File", "", "CSV Files for Tonnes (*.csv)"
        )
        if file_path:
            self.ui.pushButton_2.setText(f"{file_path.split('/')[-1]}")
            self.model.tonnes_save_database(file_path)
            self.config_icons()

    def validate_config(self):
        if not self.model:
            return False
        if self.model.hasRoutesTable() and self.model.hasTonnesTable():
            return True
        else:
            return False

    def load_config(self):
        """Handle loading the configuration with selected files"""
        if not self.model:
            return
        if self.validate_config():
            self.model.routes_tonnes_save_database()
            if self.model.hasRoutesTonnesTable():
                if hasattr(QMessageBox, "Ok"):
                    QMessageBox.information(
                        self,
                        "Success",
                        "Configuration Loaded",
                        getattr(QMessageBox, "Ok"),
                    )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Invalid Configuration",
                    "The RoutesTonnesTable isn't exist into database.",
                )
                self.close()
        else:
            QMessageBox.warning(
                self,
                "Invalid Configuration",
                "First Import Routes and Tonnes Files into database.",
            )
            self.close()

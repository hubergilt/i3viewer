from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QDialog, QHeaderView,
                               QTableWidget, QTableWidgetItem)

from i3viewer.i3helpDialog import \
    Ui_Dialog  # Import the generated UI class for points


class HelpDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Set up the user interface from Designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Customize the dialog (non-modal specific settings)
        self.setWindowTitle("i3dViewer - Help Dialog")
        self.setMinimumSize(600, 300)

        # Configure table
        if hasattr(QTableWidget, "NoEditTriggers"):
            self.ui.tableWidget.setEditTriggers(
                getattr(QTableWidget, "NoEditTriggers"))
        self.ui.tableWidget.verticalHeader().setDefaultSectionSize(24)
        self.ui.tableWidget.horizontalHeader().setDefaultSectionSize(50)

        self.ui.tableWidget.resizeColumnsToContents()

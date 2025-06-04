from PySide6.QtWidgets import QDialog

from i3viewer.i3aboutDialog import \
    Ui_Dialog  # Import the generated UI class for points
from i3viewer.i3enums import Params


class AboutDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Set up the user interface from Designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Customize the dialog (non-modal specific settings)
        self.setWindowTitle(f"{Params.ApplicationName.value} - About Dialog")
        self.ui.labelApplicationName.setText(f"{Params.ApplicationName.value}")

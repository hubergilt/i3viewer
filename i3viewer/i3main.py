import os
import sys

from PySide6 import QtWidgets
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

from i3viewer.i3mainWindow import \
    Ui_mainWindow  # Import the generated UI class


class MainWindowApp(QtWidgets.QMainWindow, Ui_mainWindow):
    def __init__(self):
        super().__init__()
        # Set up the UI from the generated file
        self.setupUi(self)

        # Initialize VTK
        self.vtkWidget = self.qvtkWidget  # Use the i3vtkWidget from the UI

        # Connect actions to their respective functions
        self.connect_actions()

        self.model = None
        self.db = None
        self.db_path = None

    def connect_actions(self):
        """Connect UI actions to their respective functions."""
        self.actionOpenFile.triggered.connect(self.on_open_file)
        self.actionSave.triggered.connect(self.on_save)
        self.actionHelp.triggered.connect(self.on_help)
        self.actionExit.triggered.connect(self.on_exit)
        self.actionFront.triggered.connect(self.vtkWidget.OnFrontView)
        self.actionBack.triggered.connect(self.vtkWidget.OnBackView)
        self.actionTop.triggered.connect(self.vtkWidget.OnTopView)
        self.actionBottom.triggered.connect(self.vtkWidget.OnBottomView)
        self.actionLeft.triggered.connect(self.vtkWidget.OnLeftView)
        self.actionRight.triggered.connect(self.vtkWidget.OnRightView)
        self.actionIso.triggered.connect(self.vtkWidget.OnIsometricView)
        self.actionFit.triggered.connect(self.vtkWidget.OnFitView)
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

    def on_open_file(self):
        """Handle the 'Open File' action for .xyz files."""
        # Open a file dialog to select an .xyz file
        file_dialog = QtWidgets.QFileDialog(self)
        # Set to home directory
        # Get user's home directory cross-platform
        home_dir = os.path.expanduser("~")
        file_dialog.setDirectory(home_dir)
        file_dialog.setNameFilter("XYZ Files (*.xyz)")
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                if file_path.endswith(".xyz"):
                    self.vtkWidget.import_file(file_path)

                    file_name = os.path.basename(file_path)
                    self.setup_tree_view(file_path, file_name)

                    base_name, _ = os.path.splitext(file_path)
                    self.db_path = base_name + ".db"

                    self.statusbar.showMessage(
                        f"Imported data from the file {file_path}."
                    )
                    self.release_tableview()
                else:
                    QtWidgets.QMessageBox.warning(
                        self, "Invalid File", "Please select a valid .xyz file."
                    )

    def setup_tree_view(self, file_path, file_name):
        model = self.vtkWidget.get_model()
        if model:
            self.treeView.setModel(model.format_tree(file_path, file_name))

    def on_save(self):
        """Handle the 'Save' action."""
        model = self.vtkWidget.get_model()
        if model:
            model.save_to_database(self.db_path)
            self.setup_table_view()
        else:
            QtWidgets.QMessageBox.warning(
                self,
                "Invalid File",
                "Please open a valid .xyz file before save into database.",
            )

    def setup_table_view(self):
        if self.db is None:
            self.db = QSqlDatabase.addDatabase("QSQLITE")

        if self.db_path:
            self.db.setDatabaseName(self.db_path)

        if not self.db.open():
            print("Error: Unable to open database")
            return -1

        self.model = QSqlTableModel(self, self.db)
        self.model.setTable("polylines")
        self.model.select()

        self.tableView.setModel(self.model)

        total_rows = self.get_row_count()
        self.statusbar.showMessage(
            f"Total rows: {total_rows} saved in the database {self.db_path}."
        )

    def get_row_count(self):
        query = QSqlQuery(self.db)
        query.exec("SELECT COUNT(*) FROM polylines")
        if query.next():
            row_count = query.value(0)
            return row_count
        return -1

    def release_tableview(self):
        if self.model:
            self.tableView.setModel(None)
            self.model = None
        if self.db and self.db.isOpen() and self.db_path:
            self.db.close()
            QSqlDatabase.removeDatabase(self.db_path)

    def on_help(self):
        """Handle the 'Help' action."""
        print("Help action triggered")

    def on_exit(self):
        """Handle the 'Exit' action."""
        self.close()

    def on_tab_changed(self, index):
        """Handle tab change events."""
        if index == 0:  # First tab (VTK widget)
            self.refresh_vtk_widget()

    def refresh_vtk_widget(self):
        """Refresh the VTK widget to fix rendering issues."""
        # Force the VTK render window to update
        self.vtkWidget.resize(self.splitter.size())


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Set the application style to Windows
    app.setStyle("Windows")

    window = MainWindowApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

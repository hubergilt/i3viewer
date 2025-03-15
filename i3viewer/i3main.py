import os
import sys

from PySide6 import QtWidgets
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStyledItemDelegate, QMessageBox
from PySide6.QtGui import QStandardItem, QStandardItemModel

from i3viewer.i3mainWindow import Ui_mainWindow  # Import the generated UI class


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
        self.db_file = None
        self.db_path = None        
        self.db = None
        
        self.tabWidget.currentChanged.connect(self.on_tab_changed)        

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

    def on_open_file(self):
        """Handle the 'Open File' action for .xyz files."""
        # Open a file dialog to select an .xyz file
        file_dialog = QtWidgets.QFileDialog(self)
        # Set to home directory
        # Get user's home directory cross-platform
        home_dir = os.path.expanduser("~")
        file_dialog.setDirectory(home_dir)
        file_dialog.setNameFilter("XYZ Files (*.xyz);;SQLite Files (*.db)")
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.file_path = selected_files[0]
                if self.file_path.endswith(".xyz"):
                    self.open_xyz_file()                    
                elif self.file_path.endswith(".db"):
                    self.open_db_file()                 
                else:
                    QMessageBox.warning(
                        self, "Invalid File", "Please select a valid file."
                    )

    
    def open_xyz_file(self):
        base_name, _ = os.path.splitext(self.file_path)
        self.db_path = base_name + ".db"        
        
        self.vtkWidget.import_file(self.file_path)
        
        self.treeview_setup()

        self.statusbar.showMessage(
            f"Imported data from the file {self.file_path}."
        )
        self.tableview_release()
        
    def open_db_file(self):        
        self.db_path = self.file_path
        
        self.vtkWidget.import_file(self.db_path, False)
        
        self.treeview_setup()

        self.statusbar.showMessage(
            f"Imported data from the file {self.db_path}."
        )
        self.tableview_release()  
        self.tableview_setup()
            
    def treeview_setup(self):
        model = self.vtkWidget.model
        if model:
            polyline_count = len(model.polylines)
            tree_model = QStandardItemModel()
            root_item = QStandardItem(f"{self.file_path} ({polyline_count} polylines)")

            for polyline_idx, (polyline_id, points) in enumerate(
                model.polylines.items(), start=1
            ):
                polyline_item = QStandardItem(f"Polyline {polyline_idx}")
                for idx, (x, y, z, *_) in enumerate(points, start=1):
                    point_item = QStandardItem(
                        f"Point {idx} (X={x:.3f}, Y={y:.3f}, Z={z:.3f})"
                    )
                    polyline_item.appendRow(point_item)
                root_item.appendRow(polyline_item)

            tree_model.appendRow(root_item)
            tree_model.setHorizontalHeaderLabels([self.file_path])
            self.treeView.setModel(tree_model)
        
    def on_save(self):
        """Handle the 'Save' action."""
        model = self.vtkWidget.model
        if model:
            if os.path.exists(self.db_path):
                reply = QMessageBox.question(self, 'Message',
                        f"The Database File Already Exists:\n{self.db_path}\nDo you want to create an empty database\noverwriting the existing file?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No) # Default is No

                if reply == QMessageBox.Yes:
                    model.polylines_save_database(self.db_path)
                    self.tableview_setup()
            else:
                model.polylines_save_database(self.db_path)
                self.tableview_setup()                
        else:
            QMessageBox.warning(
                self,
                "Invalid File",
                "Please open a valid .xyz file before save into database.",
            )

    def tableview_setup(self):
        if self.db is None:
            self.db = QSqlDatabase.addDatabase("QSQLITE")

        if self.db_path:
            self.db.setDatabaseName(self.db_path)

        if not self.db.open():
            QMessageBox.warning(
                self,
                "Invalid File",
                "Error: Unable to open database.",
            )            
            print("Error: Unable to open database")
            return -1

        self.model = QSqlTableModel(self, self.db)
        self.model.setTable("polylines")
        self.model.select()

        self.tableView.setModel(self.model)
        
        class FloatRightAlignDelegate(QStyledItemDelegate):
            def initStyleOption(self, option, index):
                super().initStyleOption(option, index)
                option.displayAlignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            
            def displayText(self, value, locale):
                # Try to convert the value to float
                try:
                    float_value = float(value)
                    # Check if it's actually an integer value
                    if float_value.is_integer():
                        return str(int(float_value))  # Display as integer without decimal places
                    else:
                        # Format with 3 decimal places for actual float values
                        return f"{float_value:.3f}"
                except (ValueError, TypeError):
                    # If conversion fails, return the original value
                    return super().displayText(value, locale)
                    
        # Set right alignment for all cells in the table
        column_count = self.model.columnCount()
        for column in range(column_count):
            self.tableView.setItemDelegateForColumn(column, FloatRightAlignDelegate(self.tableView))

        # Auto-adjust column widths to content
        self.tableView.resizeColumnsToContents()
            
        total_rows = self.tableview_row_count()
        self.statusbar.showMessage(
            f"Total rows: {total_rows} saved in the database {self.db_path}."
        )

    def tableview_row_count(self):
        query = QSqlQuery(self.db)
        query.exec("SELECT COUNT(*) FROM polylines")
        if query.next():
            row_count = query.value(0)
            return row_count
        return -1

    def tableview_release(self):
        if self.model:
            self.tableView.setModel(None)
            self.model = None
        if self.db and self.db.isOpen() and self.db_path:
            self.db.close()
            QSqlDatabase.removeDatabase(self.db_path)

    def on_help(self):
        self.vtkWidget.update_polyline_data()        
        print("Help action triggered")

    def on_exit(self):
        """Handle the 'Exit' action."""
        self.close()
        
    def closeEvent(self, event):
        """Override closeEvent to close the dialog when the application is closed."""
        if self.vtkWidget is not None:
            self.vtkWidget.close()  # Close the dialog
        event.accept()  # Accept the close event   
        
    def on_tab_changed(self, index):
        """Handle tab change events."""
        if index == 0 and self.vtkWidget and self.file_path.endswith(".db"):  # First tab (VTK widget)
            self.vtkWidget.update_polyline_data()            

def main():
    app = QtWidgets.QApplication(sys.argv)

    # Set the application style to Windows
    app.setStyle("Windows")

    window = MainWindowApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

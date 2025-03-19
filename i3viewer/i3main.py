import os
import sys

from PySide6 import QtWidgets
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide6.QtCore import Qt, QItemSelectionModel
from PySide6.QtWidgets import QStyledItemDelegate, QMessageBox, QTreeView, QMenu
from PySide6.QtGui import QStandardItem, QStandardItemModel, QIcon

from i3viewer.i3mainWindow import Ui_mainWindow  # Import the generated UI class
import i3viewer.icons_rc

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
        self.file_path = None
        self.db_file = None
        self.db_path = None
        self.db = None
        self.polyline_item = None
        self.tableModel = None

        self.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.setup_context_menu()
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.on_context_menu)

    def connect_actions(self):
        """Connect UI actions to their respective functions."""
        self.actionOpenFile.triggered.connect(self.on_open_file)
        self.actionExport.triggered.connect(self.on_export)
        self.actionHelp.triggered.connect(self.on_help)
        self.actionExit.triggered.connect(self.on_exit)
        self.actionFront.triggered.connect(self.on_front)
        self.actionBack.triggered.connect(self.on_back)
        self.actionTop.triggered.connect(self.on_top)
        self.actionBottom.triggered.connect(self.on_bottom)
        self.actionLeft.triggered.connect(self.on_left)
        self.actionRight.triggered.connect(self.on_right)
        self.actionIso.triggered.connect(self.on_iso)
        self.actionFit.triggered.connect(self.on_fit)

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

                # Switch to the second tab of the tabWidget
                self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the second tab

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

    def isDatabase(self):
        if self.file_path:
            if self.file_path.endswith(".db"):
                return True
            else:
                return False

    def treeview_setup(self):
        model = self.vtkWidget.model
        if model:
            polyline_count = len(model.polylines)
            tree_model = QStandardItemModel()
            root_item = QStandardItem(f"{self.file_path} ({polyline_count} polylines)")

            if self.isDatabase():
                root_item.setIcon(QIcon(u":/icons/db.svg"))  # Set icon for the root node
            else:
                root_item.setIcon(QIcon(u":/icons/xyz.svg"))  # Set icon for the root node

            for polyline_idx, (polyline_id, points) in enumerate(
                model.polylines.items(), start=1
            ):
                polyline_item = QStandardItem(f"Polyline {polyline_idx}")
                polyline_item.setIcon(QIcon(u":/icons/polyline.svg"))
                polyline_item.polyline_id = polyline_id
                for idx, (x, y, z, *_) in enumerate(points, start=1):
                    point_item = QStandardItem(
                        f"Point {idx} (X={x:.3f}, Y={y:.3f}, Z={z:.3f})"
                    )
                    point_item.setIcon(QIcon(u":/icons/point.svg"))
                    polyline_item.appendRow(point_item)
                root_item.appendRow(polyline_item)

            tree_model.appendRow(root_item)
            tree_model.setHorizontalHeaderLabels([self.file_path])
            self.treeView.setModel(tree_model)
            # This line makes the treeview non-editable.
            self.treeView.setEditTriggers(QTreeView.NoEditTriggers)

    def on_export(self):
        """Handle the 'Save' action."""
        model = self.vtkWidget.model
        if not model:
            QMessageBox.warning(
                self,
                "Invalid File",
                "Please open a valid .xyz file before saving into the database."
            )
            return

        if os.path.exists(self.db_path):
            reply = QMessageBox.question(
                self,
                'Message',
                f"The Database File Already Exists:\n{self.db_path}\nDo you want to create an empty database\noverwriting the existing file?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No  # Default is No
            )
            if reply != QMessageBox.Yes:
                return  # User chose not to overwrite
        
        if model.polylines:
            model.polylines_save_database(self.db_path)

        # Switch to the second tab of the tabWidget
        self.tabWidget.setCurrentIndex(1)  # Index 1 corresponds to the second tab

        self.tableview_setup()

        QMessageBox.information(
            self,
            "Save Successful",
            "The data has been successfully saved to the database."
        )

    def tableview_setup(self):
        # Check if the database is already connected
        if self.db is None:
            self.db = QSqlDatabase.addDatabase("QSQLITE")

        # Validate database path
        if not self.db_path:
            QMessageBox.warning(
                self,
                "Invalid File",
                "Error: Database path is not set.",
            )
            return -1

        # Set database name and open the connection
        self.db.setDatabaseName(self.db_path)
        if not self.db.open():
            QMessageBox.warning(
                self,
                "Invalid File",
                "Error: Unable to open database.",
            )
            print("Error: Unable to open database")
            return -1

        # Custom validated model
        class ValidatedSqlTableModel(QSqlTableModel):
            def __init__(self, parent=None, db=None, read_only_columns=None):
                super().__init__(parent, db)
                self.read_only_columns = read_only_columns if read_only_columns else []

            def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
                # Validate numeric input for editable columns
                if index.column() not in self.read_only_columns and role == Qt.ItemDataRole.EditRole:
                    try:
                        float_value = float(value)  # Ensure the value is numeric
                        return super().setData(index, value, role)
                    except (ValueError, TypeError):
                        QMessageBox.warning(
                            None,
                            "Invalid Input",
                            "Please enter a valid numeric value.",
                        )
                        return False
                return super().setData(index, value, role)

            def flags(self, index):
                # Make specified columns read-only
                if index.column() in self.read_only_columns:
                    return super().flags(index) & ~Qt.ItemFlag.ItemIsEditable
                return super().flags(index)

        # Replace the model with the custom validated model
        self.tableModel = ValidatedSqlTableModel(self, self.db, read_only_columns=[0, 1, 2, 3, 4, 5])
        self.tableModel.setTable("polylines")
        self.tableModel.select()
        
        # Force fetching all rows
        self.fetch_all_rows()

        # Set the model for the table view
        self.tableView.setModel(self.tableModel)

        # Custom delegate for right-aligned numeric values
        class FloatRightAlignDelegate(QStyledItemDelegate):
            def initStyleOption(self, option, index):
                super().initStyleOption(option, index)
                option.displayAlignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

            def displayText(self, value, locale):
                try:
                    float_value = float(value)
                    if float_value.is_integer():
                        return str(int(float_value))  # Display as integer
                    else:
                        return f"{float_value:.3f}"  # Format with 3 decimal places
                except (ValueError, TypeError):
                    return super().displayText(value, locale)

        # Apply the delegate to all columns
        column_count = self.tableModel.columnCount()
        for column in range(column_count):
            self.tableView.setItemDelegateForColumn(column, FloatRightAlignDelegate(self.tableView))

        # Auto-adjust column widths
        self.tableView.resizeColumnsToContents()

        # Update status bar with row count
        total_rows = self.tableModel.rowCount()
        self.statusbar.showMessage(
            f"Total rows: {total_rows} saved in the database {self.db_path}."
        )

    def fetch_all_rows(self):
        """
        Forces the model to fetch all rows.
        """
        if self.tableModel:
            while self.tableModel.canFetchMore():
                self.tableModel.fetchMore()    

    def tableview_release(self):
        if self.tableModel:
            self.tableView.setModel(None)
            self.tableModel = None
        if self.db and self.db.isOpen() and self.db_path:
            self.db.close()
            QSqlDatabase.removeDatabase(self.db_path)

    def on_help(self):
        print("On Help function")

    def on_front(self):
        if self.vtkWidget:
            # Switch to the second tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the second tab
            self.vtkWidget.OnFrontView()

    def on_back(self):
        if self.vtkWidget:
            # Switch to the second tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the second tab
            self.vtkWidget.OnBackView()
    def on_top(self):
        if self.vtkWidget:
            # Switch to the second tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the second tab
            self.vtkWidget.OnTopView()

    def on_bottom(self):
        if self.vtkWidget:
            # Switch to the second tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the second tab
            self.vtkWidget.OnBottomView()

    def on_left(self):
        if self.vtkWidget:
            # Switch to the second tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the second tab
            self.vtkWidget.OnLeftView()

    def on_right(self):
        if self.vtkWidget:
            # Switch to the second tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the second tab
            self.vtkWidget.OnRightView()

    def on_iso(self):
        if self.vtkWidget:
            # Switch to the second tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the second tab
            self.vtkWidget.OnIsometricView()

    def on_fit(self):
        if self.vtkWidget:
            # Switch to the second tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the second tab
            self.vtkWidget.OnFitView()

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
        if index == 0 and self.vtkWidget and self.isDatabase():  # First tab (VTK widget)
            self.vtkWidget.update_polyline_data()

    def setup_context_menu(self):
       # Create a context menu
        self.context_menu = QMenu(self)

        # Add actions to the context menu
        selectPolyline = self.context_menu.addAction("Select Polyline")
        unselectPolyline = self.context_menu.addAction("Unselect Polyline")
        showAttribPolyline = self.context_menu.addAction("Show Attributes")
        editAttribPolyline = self.context_menu.addAction("Edit Attributes")

        # Connect actions to slots (you can define your own slots)
        selectPolyline.triggered.connect(self.on_select_polyline)
        unselectPolyline.triggered.connect(self.on_unselect_polyline)
        showAttribPolyline.triggered.connect(self.on_showAttrib_polyline)
        editAttribPolyline.triggered.connect(self.on_editAttrib_polyline)

    def get_item_level(self, index):
        """Helper function to determine the level (depth) of an item in the tree."""
        level = 0
        while index.isValid():
            index = index.parent()
            level += 1
        return level

    def on_context_menu(self, position):
        # Get the index of the item that was right-clicked
        index = self.treeView.indexAt(position)
        if not index.isValid():
            return

        # Check if the item is at the second level
        if self.get_item_level(index) != 2:
            return

        # Get the item from the index
        self.polyline_item = self.treeView.model().itemFromIndex(index)

        # Show the context menu at the cursor's position
        self.context_menu.exec(self.treeView.viewport().mapToGlobal(position))

    def on_select_polyline(self):
        model = self.vtkWidget.model
        if self.polyline_item and model:
            if hasattr(self.polyline_item, "polyline_id"):
                polyline_id = self.polyline_item.polyline_id
                actor = model.actor_by_id(polyline_id)
                if actor:
                    if self.vtkWidget.selected_actor:
                        self.vtkWidget.deselect_actor(self.vtkWidget.selected_actor)
                    self.vtkWidget.select_actor(actor)
                    self.vtkWidget.UpdateView()


    def on_unselect_polyline(self):
        model = self.vtkWidget.model
        if self.polyline_item and model:
            if hasattr(self.polyline_item, "polyline_id"):
                polyline_id = self.polyline_item.polyline_id
                actor = model.actor_by_id(polyline_id)
                if actor:
                    self.vtkWidget.deselect_actor(actor)
                    self.vtkWidget.UpdateView()
                    
    def on_showAttrib_polyline(self):
        model = self.vtkWidget.model
        if self.polyline_item and model:
            if hasattr(self.polyline_item, "polyline_id"):
                polyline_id = self.polyline_item.polyline_id
                actor = model.actor_by_id(polyline_id)
                if actor:
                    self.vtkWidget.show_dialog(actor)
                    
    def on_editAttrib_polyline(self):
        model = self.vtkWidget.model
        
        # Validate database path
        if not self.tableModel:
            QMessageBox.warning(
                self,
                "Invalid Table",
                "First Export or Open Database File.",
            )
            return -1        
        
        if self.polyline_item and model and self.tableModel:
            if hasattr(self.polyline_item, "polyline_id"):
                polyline_id = self.polyline_item.polyline_id
                
                # Switch to the second tab of the tabWidget
                self.tabWidget.setCurrentIndex(1)  # Index 1 corresponds to the second tab

                # Search for the row where the first column matches polyline_id
                found_row = -1
                for row in range(self.tableModel.rowCount()):
                    index = self.tableModel.index(row, 0)  # Check the first column
                    if self.tableModel.data(index, Qt.DisplayRole) == polyline_id:
                        found_row = row
                        break

                if found_row == -1:
                    print(f"No row found with polyline_id '{polyline_id}'.")
                    return

                # Scroll to the matching row
                index = self.tableModel.index(found_row, 0)  # Index of the first column in the row
                self.tableView.scrollTo(index)

                # Select the entire row
                selection_model = self.tableView.selectionModel()
                selection_model.select(index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
                                            
def main():
    app = QtWidgets.QApplication(sys.argv)

    # Set the application style to Windows
    app.setStyle("Windows")

    window = MainWindowApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

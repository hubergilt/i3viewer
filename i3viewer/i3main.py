import sys
import os

from PySide6 import QtWidgets
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtCore import Qt, QItemSelectionModel
from PySide6.QtWidgets import QFileDialog, QStyledItemDelegate, QMessageBox, QTreeView, QMenu
from PySide6.QtGui import QStandardItem, QStandardItemModel, QIcon

from i3viewer.i3mainWindow import Ui_mainWindow  # Import the generated UI class
from i3viewer.i3help import HelpDialog

class MainWindowApp(QtWidgets.QMainWindow, Ui_mainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interactive 3D Model Viewer")

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
        self.base_name = None
        self.db = None
        self.polyline_item = None
        self.tree_model = None
        self.tableModelPolylines = None
        self.tableModelPoints = None
        self.polyline_idx = 1
        self.point_idx = 1
        self.header_label = ""
        self.is_db_open = False

        self.setup_context_menu()

        if hasattr(Qt, "CustomContextMenu"):
            self.treeView.setContextMenuPolicy(getattr(Qt, "CustomContextMenu"))

        self.treeView.customContextMenuRequested.connect(self.on_context_menu)
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

    def connect_actions(self):
        """Connect UI actions to their respective functions."""
        self.actionOpenFile.triggered.connect(self.on_open_file)
        self.actionPlus.triggered.connect(self.on_append_file)
        self.actionMinus.triggered.connect(self.on_clear)
        self.actionExport.triggered.connect(self.on_export)
        self.actionHeatMap.triggered.connect(self.on_heatmap)
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
        if hasattr(QtWidgets.QFileDialog, "Accept"):
            file_dialog.setLabelText(getattr(QtWidgets.QFileDialog, "Accept"), "Open New")

        if self.base_name:
            file_dialog.setDirectory(self.base_name)
        else:
            # Set to home directory
            # Get user's home directory cross-platform
            home_dir = os.path.expanduser("~")
            file_dialog.setDirectory(home_dir)

        file_dialog.setNameFilter("XYZ Files (*.xyz);;SRG Files (*.srg);;SQLite Files (*.db)")

        if hasattr(QtWidgets.QFileDialog, "ExistingFile"):
            file_dialog.setFileMode(getattr(QtWidgets.QFileDialog,"ExistingFile"))

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.file_path = selected_files[0]
                self.base_name, _ = os.path.splitext(self.file_path)
                self.on_clear()
                if self.vtkWidget:
                    self.vtkWidget.hide_dialog()

                # Switch to the second tab of the tabWidget
                self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the second tab

                if self.file_path.endswith(".xyz"):
                    self.open_xyz_file(openNew=True)
                elif self.file_path.endswith(".srg"):
                    self.open_srg_file(openNew=True)
                elif self.file_path.endswith(".db"):
                    self.open_db_file()
                else:
                    QMessageBox.warning(
                        self, "Invalid File", "Please select a valid file."
                    )



    def open_xyz_file(self, openNew=True):

        if self.file_path is None or self.base_name is None:
            return

        self.db_path = self.base_name + ".db"

        self.vtkWidget.import_file(self.file_path, fromFile=True, isPolylines=True, newFile=openNew)

        self.is_db_open = False

        self.treeview_setup(openNew)

        self.statusbar.showMessage(
            f"Imported data from the file {self.file_path}."
        )
        self.tableview_release()

    def open_srg_file(self, openNew=True):

        if self.file_path is None:
            return

        base_name, _ = os.path.splitext(self.file_path)
        self.db_path = base_name + ".db"

        self.vtkWidget.import_file(self.file_path, fromFile=True, isPolylines=False, newFile=openNew)

        self.is_db_open = False

        self.treeview_setup(openNew)

        self.statusbar.showMessage(
            f"Imported data from the file {self.file_path}."
        )
        self.tableview_release()

    def open_db_file(self):
        self.db_path = self.file_path

        self.vtkWidget.import_file(self.db_path, fromFile=False, isPolylines=False, newFile=True)

        self.is_db_open = True

        self.treeview_setup(openNew=True)

        self.statusbar.showMessage(
            f"Imported data from the file {self.db_path}."
        )
        self.tableview_release()

        if self.vtkWidget.model:
            if self.vtkWidget.model.hasPointsTable(self.db_path):
                self.tableview_setup_points()
            if self.vtkWidget.model.hasPolylinesTable(self.db_path):
                self.tableview_setup_polylines()

    def is_db_file(self):
        if self.file_path:
            if self.file_path.endswith(".db"):
                return True
            else:
                return False

    def is_xyz_file(self):
        if self.file_path:
            if self.file_path.endswith(".xyz"):
                return True
            else:
                return False

    def is_srg_file(self):
        if self.file_path:
            if self.file_path.endswith(".srg"):
                return True
            else:
                return False

    def treeview_setup(self, openNew):

        if self.file_path is None:
            return

        model = self.vtkWidget.model
        if model:
            if self.tree_model is None:
                self.tree_model = QStandardItemModel()

            root_item = QStandardItem(f"{self.file_path}")

            if openNew:
                self.header_label = self.file_path
            else:
                self.header_label += f"\n{self.file_path}"

            polyline_count = len(model.polylines)
            point_count = len(model.points)

            if self.is_db_file():
                root_item.setIcon(QIcon(u":/icons/db.svg"))  # Set icon for the root node
                self.treeview_populate_polylines(model, root_item)
                self.treeview_populate_points(model, root_item)
                self.header_label += f" ({polyline_count}L y {point_count}P)"
            elif self.is_xyz_file():
                root_item.setIcon(QIcon(u":/icons/xyz.svg"))  # Set icon for the root node
                self.treeview_populate_polylines(model, root_item)
                self.header_label += f" ({polyline_count}L)"
            elif self.is_srg_file():
                root_item.setIcon(QIcon(u":/icons/srg.svg"))  # Set icon for the root node
                self.treeview_populate_points(model, root_item)
                self.header_label += f" ({point_count}P)"
            else:
                return

            self.tree_model.appendRow(root_item)
            self.tree_model.setHorizontalHeaderLabels([self.header_label])
            self.treeView.setModel(self.tree_model)
            # This line makes the treeview non-editable.
            if hasattr(QTreeView, "NoEditTriggers"):
                self.treeView.setEditTriggers(getattr(QTreeView, "NoEditTriggers"))

    def treeview_populate_polylines(self, model, root_item):
        """Populates the tree view with polylines."""
        if hasattr(model, 'polylines'):

            polylines=dict(sorted(model.polylines.items())[self.polyline_idx-1:])

            polyline_root = QStandardItem("Polylines")
            polyline_root.setIcon(QIcon(u":/icons/polyline.svg"))

            for polyline_id, points in polylines.items():
                polyline_item = QStandardItem(f"Polyline {polyline_id}")
                polyline_item.setIcon(QIcon(u":/icons/polyline.svg"))
                self.polyline_idx += 1
                setattr(polyline_item, "polyline_id", polyline_id)

                for idx, (x, y, z, *_) in enumerate(points, start=1):
                    point_item = QStandardItem(
                        f"Point {idx} (X={x:.3f}, Y={y:.3f}, Z={z:.3f})"
                    )
                    point_item.setIcon(QIcon(u":/icons/point.svg"))
                    polyline_item.appendRow(point_item)

                polyline_root.appendRow(polyline_item)
            root_item.appendRow(polyline_root)

    def treeview_populate_points(self, model, root_item):
        """Populates the tree view with points."""
        if hasattr(model, 'points'):

            points=dict(sorted(model.points.items())[self.point_idx-1:])

            point_root = QStandardItem("Points")
            point_root.setIcon(QIcon(u":/icons/point.svg"))

            for point_id, vertices in points.items():

                (x, y, z, name) = vertices[0]
                point_item = QStandardItem(f"Point {point_id} (X={x:.3f}, Y={y:.3f}, Z={z:.3f})")
                point_item.setIcon(QIcon(u":/icons/point.svg"))
                self.point_idx += 1
                setattr(point_item, "point_id", point_id)
                setattr(point_item, "name", name)

                point_root.appendRow(point_item)
            root_item.appendRow(point_root)

    def on_clear(self):
        if self.vtkWidget:
            self.vtkWidget.RemoveAll()
        self.tree_model = QStandardItemModel()
        self.treeView.setModel(self.tree_model)
        self.polyline_idx = 1
        self.point_idx = 1
        self.tableview_release()

    def on_export(self):
        """Handle the 'Save' action."""

        if self.db_path is None:
            return

        model = self.vtkWidget.model
        if not model:
            QMessageBox.warning(
                self,
                "Invalid File",
                "Please open a valid .xyz or .srg file before saving into the database."
            )
            return

        if (not model.polylines) ^ (not model.points):
            if os.path.exists(self.db_path):
                if hasattr(QMessageBox, "Yes") or hasattr(QMessageBox, "No"):
                    reply = QMessageBox.question(
                        self,
                        'Message',

                        f"The Database File Already Exists:\n{self.db_path}\nDo you want to create an empty database\noverwriting the existing file?",
                        getattr(QMessageBox, "Yes") | getattr(QMessageBox, "No"),
                        getattr(QMessageBox, "No")  # Default is No
                    )
                    if reply != getattr(QMessageBox, "Yes"):
                        return  # User chose not to overwrite
        elif model.polylines and model.points:
            file_dialog = QtWidgets.QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)  # Set to save mode
            file_dialog.setDefaultSuffix("db")  # Default extension if none provided
            file_dialog.setNameFilter("SQLite Files (*.db)")
            if file_dialog.exec():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    self.db_path = selected_files[0]
            else:
                return
        elif not model.polylines and not model.points:
            return
        else:
            return

        if model.polylines:
            model.polylines_save_database(self.db_path)
            # Switch to the second tab of the tabWidget
            self.tabWidget.setCurrentIndex(1)  # Index 1 corresponds to the second tab
            self.tableview_setup_polylines()

            if hasattr(QMessageBox, "Ok"):
                QMessageBox.information(
                    self,
                    "Save Successful",
                    "The polyline data has been successfully saved to the database.",
                    getattr(QMessageBox, "Ok")
                )
        if model.points:
            model.points_save_database(self.db_path)
            # Switch to the second tab of the tabWidget
            self.tabWidget.setCurrentIndex(2)  # Index 2 corresponds to the third tab
            self.tableview_setup_points()

            if hasattr(QMessageBox, "Ok"):
                QMessageBox.information(
                    self,
                    "Save Successful",
                    "The point data has been successfully saved to the database.",
                    getattr(QMessageBox, "Ok")
                )

    def on_append_file(self):
        """Handle the 'Open File' action for .xyz files."""

        if self.is_db_open:
            if hasattr(QMessageBox, "Ok"):
                QMessageBox.information(
                    self,
                    "Append File Dialog",
                    "Cannot append another file if the datababase file is open.",
                    getattr(QMessageBox, "Ok")
                )
            return

        # Open a file dialog to select an .xyz file
        file_dialog = QtWidgets.QFileDialog(self)

        if hasattr(QtWidgets.QFileDialog, "Accept"):
            file_dialog.setLabelText(getattr(QtWidgets.QFileDialog, "Accept"), "Append")

        if self.base_name:
            file_dialog.setDirectory(self.base_name)
        else:
            # Set to home directory
            # Get user's home directory cross-platform
            home_dir = os.path.expanduser("~")
            file_dialog.setDirectory(home_dir)

        file_dialog.setNameFilter("XYZ Files (*.xyz);;SRG Files (*.srg)")

        if hasattr(QtWidgets.QFileDialog, "ExistingFile"):
            file_dialog.setFileMode(getattr(QtWidgets.QFileDialog,"ExistingFile"))

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.file_path = selected_files[0]
                self.base_name, _ = os.path.splitext(self.file_path)

                #if self.vtkWidget:
                #    self.vtkWidget.hide_dialog()

                # Switch to the second tab of the tabWidget
                self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the second tab

                if self.file_path.endswith(".xyz"):
                    self.open_xyz_file(openNew=False)
                elif self.file_path.endswith(".srg"):
                    self.open_srg_file(openNew=False)
                else:
                    QMessageBox.warning(
                        self, "Invalid File", "Please select a valid file."
                    )

    def tableview_setup_polylines(self):
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
            def __init__(self, window, parent=None, db=None, read_only_columns=None):
                # Handle db explicitly to satisfy Pyright type checking
                if db is None:
                    db = QSqlDatabase.database()
                super().__init__(parent, db)
                self.read_only_columns = read_only_columns if read_only_columns else []
                self.window = window

            def setData(self, index, value, role=Qt.ItemDataRole.EditRole):

                # Validate numeric input for editable columns
                if index.column() not in self.read_only_columns and role == Qt.ItemDataRole.EditRole:
                    try:
                        _ = float(value)  # Ensure the value is numeric
                        return super().setData(index, value, role)
                    except (ValueError, TypeError):
                        QMessageBox.warning(
                            self.window,
                            "Invalid Input",
                            "Please enter a valid numeric value."
                        )
                        return False
                return super().setData(index, value, role)

            def flags(self, index):
                # Make specified columns read-only
                if index.column() in self.read_only_columns:
                    return super().flags(index) & ~Qt.ItemFlag.ItemIsEditable
                return super().flags(index)

        # Replace the model with the custom validated model
        self.tableModelPolylines = ValidatedSqlTableModel(self, self, self.db, read_only_columns=[0, 1, 2, 3, 4, 5])
        self.tableModelPolylines.setTable("polylines")
        self.tableModelPolylines.select()

        # Force fetching all rows
        self.tableModelPolylines_fetch_all_rows()

        # Set the model for the table view
        self.tableViewPolylines.setModel(self.tableModelPolylines)

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
        column_count = self.tableModelPolylines.columnCount()
        for column in range(column_count):
            self.tableViewPolylines.setItemDelegateForColumn(column, FloatRightAlignDelegate(self.tableViewPolylines))

        # Auto-adjust column widths
        self.tableViewPolylines.resizeColumnsToContents()

        # Update status bar with row count
        total_rows = self.tableModelPolylines.rowCount()
        self.statusbar.showMessage(
            f"Total rows: {total_rows} saved in the database {self.db_path}."
        )


    def tableview_setup_points(self):
        """Sets up the TableView for the points table."""
        if self.db is None:
            self.db = QSqlDatabase.addDatabase("QSQLITE")

        if not self.db_path:
            QMessageBox.warning(self, "Invalid File", "Error: Database path is not set.")
            return -1

        self.db.setDatabaseName(self.db_path)
        if not self.db.open():
            QMessageBox.warning(self, "Invalid File", "Error: Unable to open database.")
            print("Error: Unable to open database")
            return -1

        class ValidatedSqlTableModel(QSqlTableModel):
            def __init__(self, window, parent=None, db=None, read_only_columns=None):
                # Handle db explicitly to satisfy Pyright type checking
                if db is None:
                    db = QSqlDatabase.database()
                super().__init__(parent, db)
                self.read_only_columns = read_only_columns if read_only_columns else []
                self.window = window

            def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
                if index.column() not in self.read_only_columns and role == Qt.ItemDataRole.EditRole:
                    try:
                        _ = float(value)
                        return super().setData(index, value, role)
                    except (ValueError, TypeError):
                        QMessageBox.warning(self.window, "Invalid Input", "Please enter a valid numeric value.")
                        return False
                return super().setData(index, value, role)

            def flags(self, index):
                if index.column() in self.read_only_columns:
                    return super().flags(index) & ~Qt.ItemFlag.ItemIsEditable
                return super().flags(index)

        self.tableModelPoints = ValidatedSqlTableModel(self, self, self.db, read_only_columns=[0, 1, 2, 3, 4])
        self.tableModelPoints.setTable("points")
        self.tableModelPoints.select()

        self.tableModelPoints_fetch_all_rows()
        self.tableViewPoints.setModel(self.tableModelPoints)

        class FloatRightAlignDelegate(QStyledItemDelegate):
            def initStyleOption(self, option, index):
                super().initStyleOption(option, index)
                option.displayAlignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

            def displayText(self, value, locale):
                try:
                    float_value = float(value)
                    if float_value.is_integer():
                        return str(int(float_value))
                    else:
                        return f"{float_value:.3f}"
                except (ValueError, TypeError):
                    return super().displayText(value, locale)

        column_count = self.tableModelPoints.columnCount()
        for column in range(column_count):
            self.tableViewPoints.setItemDelegateForColumn(column, FloatRightAlignDelegate(self.tableViewPoints))

        self.tableViewPoints.resizeColumnsToContents()
        total_rows = self.tableModelPoints.rowCount()
        self.statusbar.showMessage(f"Total rows: {total_rows} saved in the database {self.db_path}.")


    def tableModelPolylines_fetch_all_rows(self):
        """
        Forces the model to fetch all rows.
        """
        if self.tableModelPolylines:
            while self.tableModelPolylines.canFetchMore():
                self.tableModelPolylines.fetchMore()

    def tableModelPoints_fetch_all_rows(self):
        """
        Forces the model to fetch all rows.
        """
        if self.tableModelPoints:
            while self.tableModelPoints.canFetchMore():
                self.tableModelPoints.fetchMore()

    def tableview_release(self):
        #model = self.vtkWidget.model
        if self.tableModelPolylines:
            self.tableViewPolylines.setModel(None)
            self.tableModelPolylines = None
            #if model:
            #    model.polylines = {}
        if self.tableModelPoints:
            self.tableViewPoints.setModel(None)
            self.tableModelPoints = None
            #if model:
            #    model.points = {}
        if self.db and self.db.isOpen() and self.db_path:
            self.db.close()
            QSqlDatabase.removeDatabase(self.db_path)

    def on_heatmap(self):
        # Cannot perform heatmap operation on files only with database
        if not self.is_db_open:
            if hasattr(QMessageBox, "Ok"):
                QMessageBox.information(
                    self,
                    "HeatMap Tool Dialog",
                    "Cannot perform heamap on the current file, it only works on dababase",
                    getattr(QMessageBox, "Ok")
                )
            return

        if self.vtkWidget:
            # Switch to the first tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the first tab
            self.vtkWidget.OnHeatMap()

    def on_help(self):
        help = HelpDialog(self)
        help.show()

    def on_front(self):
        if self.vtkWidget:
            # Switch to the first tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the first tab
            self.vtkWidget.OnFrontView()

    def on_back(self):
        if self.vtkWidget:
            # Switch to the first tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the first tab
            self.vtkWidget.OnBackView()
    def on_top(self):
        if self.vtkWidget:
            # Switch to the first tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the first tab
            self.vtkWidget.OnTopView()

    def on_bottom(self):
        if self.vtkWidget:
            # Switch to the first tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the first tab
            self.vtkWidget.OnBottomView()

    def on_left(self):
        if self.vtkWidget:
            # Switch to the first tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the first tab
            self.vtkWidget.OnLeftView()

    def on_right(self):
        if self.vtkWidget:
            # Switch to the first tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the first tab
            self.vtkWidget.OnRightView()

    def on_iso(self):
        if self.vtkWidget:
            # Switch to the first tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the first tab
            self.vtkWidget.OnIsometricView()

    def on_fit(self):
        if self.vtkWidget:
            # Switch to the first tab of the tabWidget
            self.tabWidget.setCurrentIndex(0)  # Index 0 corresponds to the first tab
            self.vtkWidget.OnFitView()

    def on_exit(self):
        """Handle the 'Exit' action."""
        self.close()

    def closeEvent(self, event):
        """Override closeEvent to close the dialog when the application is closed."""
        if self.vtkWidget:
            self.vtkWidget.close()  # Close the dialog
        event.accept()  # Accept the close event

    def setup_context_menu(self):
        # Create a context menu
        self.context_menu = QMenu(self)

        # Add actions for polylines
        self.selectPolyline = self.context_menu.addAction("Select Polyline")
        self.unselectPolyline = self.context_menu.addAction("Unselect Polyline")
        self.showAttribPolyline = self.context_menu.addAction("Show Polyline Attributes")
        self.editAttribPolyline = self.context_menu.addAction("Edit Polyline Attributes")

        # Add actions for points
        self.selectPoint = self.context_menu.addAction("Select Point")
        self.unselectPoint = self.context_menu.addAction("Unselect Point")
        self.showAttribPoint = self.context_menu.addAction("Show Point Attributes")
        self.editAttribPoint = self.context_menu.addAction("Edit Point Attributes")

        # Connect actions to slots dynamically
        self.selectPolyline.triggered.connect(self.on_select_polyline)
        self.unselectPolyline.triggered.connect(self.on_unselect_polyline)
        self.showAttribPolyline.triggered.connect(self.on_showAttrib_polyline)
        self.editAttribPolyline.triggered.connect(self.on_editAttrib_polyline)

        self.selectPoint.triggered.connect(self.on_select_point)
        self.unselectPoint.triggered.connect(self.on_unselect_point)
        self.showAttribPoint.triggered.connect(self.on_showAttrib_point)
        self.editAttribPoint.triggered.connect(self.on_editAttrib_point)

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

        # Check if the item is at the third level
        if self.get_item_level(index) != 3:
            return

        # Get the item from the index
        if hasattr(self.treeView.model(), "itemFromIndex"):
            self.context_item = getattr(self.treeView.model(), "itemFromIndex")(index)

        # Determine if the item is a polyline or a point
        if hasattr(self.context_item, "polyline_id"):
            self.context_type = "polyline"
            self.context_id = self.context_item.polyline_id
        elif hasattr(self.context_item, "point_id"):
            self.context_type = "point"
            self.context_id = self.context_item.point_id
        else:
            return

        # Show only relevant actions based on the item type
        if self.context_type == "polyline":
            self.selectPolyline.setVisible(True)
            self.unselectPolyline.setVisible(True)
            self.showAttribPolyline.setVisible(True)
            self.editAttribPolyline.setVisible(True)
            self.selectPoint.setVisible(False)
            self.unselectPoint.setVisible(False)
            self.showAttribPoint.setVisible(False)
            self.editAttribPoint.setVisible(False)
        elif self.context_type == "point":
            self.selectPolyline.setVisible(False)
            self.unselectPolyline.setVisible(False)
            self.showAttribPolyline.setVisible(False)
            self.editAttribPolyline.setVisible(False)
            self.selectPoint.setVisible(True)
            self.unselectPoint.setVisible(True)
            self.showAttribPoint.setVisible(True)
            self.editAttribPoint.setVisible(True)

        # Show the context menu at the cursor's position
        self.context_menu.exec(self.treeView.viewport().mapToGlobal(position))

    def on_select_polyline(self):
        if self.context_type == "polyline":
            polyline_id = self.context_id
            actor = self.vtkWidget.polylines_get_actor(polyline_id)
            if actor:
                if self.vtkWidget.selected_actor:
                    self.vtkWidget.deselect_actor(self.vtkWidget.selected_actor)
                self.vtkWidget.select_actor(actor)
                self.vtkWidget.UpdateView()

    def on_unselect_polyline(self):
        if self.context_type == "polyline":
            polyline_id = self.context_id
            actor = self.vtkWidget.polylines_get_actor(polyline_id)
            if actor:
                self.vtkWidget.deselect_actor(actor)
                self.vtkWidget.UpdateView()

    def on_showAttrib_polyline(self):
        if self.context_type == "polyline":
            polyline_id = self.context_id
            actor = self.vtkWidget.polylines_get_actor(polyline_id)
            if actor:
                self.vtkWidget.show_dialog(actor)

    def on_editAttrib_polyline(self):
        # Validate database path
        if not self.tableModelPolylines:
            QMessageBox.warning(
                self,
                "Invalid Table",
                "First Export or Open Polyline Database File.",
            )
            return

        if self.context_type == "polyline" and self.tableModelPolylines:
            # Switch to the second tab of the tabWidget
            self.tabWidget.setCurrentIndex(1)  # Index 1 corresponds to the second tab

            # Search for the row where the first column matches polyline_id
            found_row = -1
            for row in range(self.tableModelPolylines.rowCount()):
                index = self.tableModelPolylines.index(row, 0)  # Check the first column
                if hasattr(Qt, "DisplayRole"):
                    polyline_id = self.context_id
                    if self.tableModelPolylines.data(index, getattr(Qt, "DisplayRole")) == polyline_id:
                        found_row = row
                        break

            if found_row == -1:
                print(f"No row found with polyline_id '{polyline_id}'.")
                return

            # Scroll to the matching row
            index = self.tableModelPolylines.index(found_row, 0)  # Index of the first column in the row
            self.tableViewPolylines.scrollTo(index)

            # Select the entire row
            selection_model = self.tableViewPolylines.selectionModel()
            if hasattr(QItemSelectionModel, "ClearAndSelect") and hasattr(QItemSelectionModel, "Rows"):
                selection_model.select(index, getattr(QItemSelectionModel, "ClearAndSelect") | getattr(QItemSelectionModel, "Rows"))

    def on_select_point(self):
        if self.context_type == "point":
            point_id = self.context_id
            actor = self.vtkWidget.points_get_actor(point_id)
            if actor:
                if self.vtkWidget.selected_actor:
                    self.vtkWidget.deselect_actor(self.vtkWidget.selected_actor)
                self.vtkWidget.select_actor(actor)
                self.vtkWidget.UpdateView()

    def on_unselect_point(self):
        if self.context_type == "point":
            point_id = self.context_id
            actor = self.vtkWidget.points_get_actor(point_id)
            if actor:
                self.vtkWidget.deselect_actor(actor)
                self.vtkWidget.UpdateView()

    def on_showAttrib_point(self):
        if self.context_type == "point":
            point_id = self.context_id
            actor = self.vtkWidget.points_get_actor(point_id)
            if actor:
                self.vtkWidget.show_dialog(actor)

    def on_editAttrib_point(self):
        # Validate database path
        if not self.tableModelPoints:
            QMessageBox.warning(
                self,
                "Invalid Table",
                "First Export or Open Point Database File.",
            )
            return

        if self.context_type == "point" and self.tableModelPoints:
            # Switch to the second tab of the tabWidget
            self.tabWidget.setCurrentIndex(2)  # Index 2 corresponds to the third tab

            # Search for the row where the first column matches point_id
            found_row = -1
            for row in range(self.tableModelPoints.rowCount()):
                index = self.tableModelPoints.index(row, 0)  # Check the first column
                if hasattr(Qt, "DisplayRole"):
                    point_id = self.context_id
                    if self.tableModelPoints.data(index, getattr(Qt, "DisplayRole")) == point_id:
                        found_row = row
                        break

            if found_row == -1:
                print(f"No row found with point_id '{point_id}'.")
                return

            # Scroll to the matching row
            index = self.tableModelPoints.index(found_row, 0)  # Index of the first column in the row
            self.tableViewPoints.scrollTo(index)

            # Select the entire row
            selection_model = self.tableViewPoints.selectionModel()
            if hasattr(QItemSelectionModel, "ClearAndSelect") and hasattr(QItemSelectionModel, "Rows"):
                selection_model.select(index, getattr(QItemSelectionModel, "ClearAndSelect") | getattr(QItemSelectionModel, "Rows"))

    def on_tab_changed(self, index):
        """Handle tab change events."""
        if index == 0 and self.vtkWidget:  # First tab (VTK widget)
            self.vtkWidget.polylines_update_data()

def main():
    app = QtWidgets.QApplication(sys.argv)

    # Set the application style to Windows
    app.setStyle("Windows")

    window = MainWindowApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

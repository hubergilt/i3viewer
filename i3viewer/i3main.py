import sys
import os
import random

from PySide6 import QtWidgets
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from PySide6.QtCore import Qt, QItemSelectionModel
from PySide6.QtWidgets import (
    QFileDialog, QStyledItemDelegate, QMessageBox,
    QTreeView, QMenu, QDialog,
)
from PySide6.QtGui import QStandardItem, QStandardItemModel, QIcon

from i3viewer.i3mainWindow import Ui_mainWindow
from i3viewer.i3help import HelpDialog
from i3viewer.i3about import AboutDialog
from i3viewer.i3heatmap import HeatMapDialog
from i3viewer.i3surface import SurfaceDialog
from i3viewer.i3enums import DelaunayCfg, FileType, HeatMapCfg, SurfaceCfg, Params


# ---------------------------------------------------------------------------
# Shared inner-class helpers (used by both tableview setup methods)
# ---------------------------------------------------------------------------

class _ValidatedSqlTableModel(QSqlTableModel):
    """QSqlTableModel that rejects non-numeric input and supports read-only columns."""

    def __init__(self, window, parent=None, db=None, read_only_columns=None):
        if db is None:
            db = QSqlDatabase.database()
        super().__init__(parent, db)
        self.read_only_columns = read_only_columns or []
        self.window = window

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.column() not in self.read_only_columns and role == Qt.ItemDataRole.EditRole:
            try:
                float(value)
                return super().setData(index, value, role)
            except (ValueError, TypeError):
                QMessageBox.warning(
                    self.window, "Invalid Input", "Please enter a valid numeric value.")
                return False
        return super().setData(index, value, role)

    def flags(self, index):
        if index.column() in self.read_only_columns:
            return super().flags(index) & ~Qt.ItemFlag.ItemIsEditable
        return super().flags(index)


class _FloatRightAlignDelegate(QStyledItemDelegate):
    """Delegate that right-aligns and formats float values in table cells."""

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = (
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    def displayText(self, value, locale):
        try:
            float_value = float(value)
            return str(int(float_value)) if float_value.is_integer() \
                else f"{float_value:,.3f}"
        except (ValueError, TypeError):
            return super().displayText(value, locale)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MainWindowApp(QtWidgets.QMainWindow, Ui_mainWindow):

    # -----------------------------------------------------------------------
    # Initialization
    # -----------------------------------------------------------------------

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(f"{Params.ApplicationName.value}")

        self.vtkWidget = self.qvtkWidget

        self.model = None
        self.file_path = None
        self.base_name = None
        self.fileType = None

        self.db = None
        self.polyline_item = None
        self.tree_model = None
        self.tableModelPolylines = None
        self.tableModelPoints = None
        self.polyline_idx = 1
        self.point_idx = 1
        self.contours = 0
        self.selected_surface_file_id = None

        self.header_label = ""
        self.currentPeriod = 1
        self.maxPeriod = 12

        self.connect_actions()
        self.setup_context_menu()
        self.config_heatmap(HeatMapCfg.INIT)
        self.config_init_surface()

        if hasattr(Qt, "CustomContextMenu"):
            self.treeView.setContextMenuPolicy(getattr(Qt, "CustomContextMenu"))

        self.treeView.customContextMenuRequested.connect(self.on_context_menu)
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

    # -----------------------------------------------------------------------
    # Surface Configuration
    # -----------------------------------------------------------------------

    def config_init_surface(self):
        self.surfacecfg = SurfaceCfg()
        self.surfacecfg.surface_color = [random.randint(0, 255) / 255.0 for _ in range(3)]
        self.surfacecfg.wireframe_color = [random.randint(0, 255) / 255.0 for _ in range(3)]
        self.delaunaycfg = DelaunayCfg()
        self.contour_color = [random.randint(0, 255) / 255.0 for _ in range(3)]
        self.config_surface()

    def config_surface(self):
        self.vtkWidget.delaunaycfg = self.delaunaycfg
        self.vtkWidget.surfacecfg = self.surfacecfg
        self.vtkWidget.contour_color = self.contour_color

    # -----------------------------------------------------------------------
    # Action Connections
    # -----------------------------------------------------------------------

    def connect_actions(self):
        """Connect UI actions to their respective handler methods."""
        self.actionOpenFile.triggered.connect(self.on_open_file)
        self.actionPlus.triggered.connect(self.on_append_file)
        self.actionMinus.triggered.connect(self.on_clean_workspace)
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

        self.actionHeatMapCfg.triggered.connect(self.on_heatmapcfg)
        self.actionHeatMap.triggered.connect(self.on_heatmap)
        self.actionBackward.triggered.connect(self.on_backward)
        self.actionForward.triggered.connect(self.on_forward)
        self.actionUnpick.triggered.connect(self.on_unpick)
        self.actionPolyLabel.triggered.connect(self.on_polylabel)
        self.actionPointLabel.triggered.connect(self.on_pointlabel)
        self.actionContour.triggered.connect(self.on_contour)
        self.actionSurface.triggered.connect(self.on_surface)
        self.actionWireframe.triggered.connect(self.on_wireframe)
        self.actionSurfaceCfg.triggered.connect(self.on_surface_cfg)
        self.actionAbout.triggered.connect(self.on_about)

    # -----------------------------------------------------------------------
    # File Opening
    # -----------------------------------------------------------------------

    def _make_file_dialog(self, label_text, name_filter):
        """Create and configure a file-open dialog."""
        dlg = QtWidgets.QFileDialog(self)
        if hasattr(QtWidgets.QFileDialog, "Accept"):
            dlg.setLabelText(getattr(QtWidgets.QFileDialog, "Accept"), label_text)
        if self.base_name:
            dlg.setDirectory(self.base_name)
        else:
            dlg.setDirectory(os.path.expanduser("~"))
        dlg.setNameFilter(name_filter)
        if hasattr(QtWidgets.QFileDialog, "ExistingFile"):
            dlg.setFileMode(getattr(QtWidgets.QFileDialog, "ExistingFile"))
        return dlg

    _ALL_FILE_FILTER = (
        "XYZ Files for Polylines (*.xyz);;"
        "CSV Files for Polylines (*.csv);;"
        "SRG Files for Points (*.srg);;"
        "XYZS Files for Surfaces (*.xyzs);;"
        "SQLite Files for Surfaces, Polylines and Points (*.db)"
    )
    _NON_DB_FILE_FILTER = (
        "XYZ Files for Polylines (*.xyz);;"
        "CSV Files for Polylines (*.csv);;"
        "SRG Files for Points (*.srg);;"
        "XYZS Files for Surfaces (*.xyzs)"
    )

    def on_open_file(self):
        """Handle the Open File action (.xyz, .xyzs, .srg, .csv, .db)."""
        dlg = self._make_file_dialog("Open New", self._ALL_FILE_FILTER)
        if not dlg.exec():
            return

        selected = dlg.selectedFiles()
        if not selected:
            return

        self.on_clean_workspace()
        self.file_path = selected[0]
        self.base_name, _ = os.path.splitext(self.file_path)
        self.fileType = FileType.get_fileType(self.file_path)

        if self.fileType is None:
            QMessageBox.warning(self, "Invalid File", "Please select a valid file.")
            return

        if self.vtkWidget:
            self.vtkWidget.hide_dialog()

        self.tabWidget.setCurrentIndex(0)

        dispatch = {
            FileType.XYZ:  lambda: self.open_xyz_file(openNew=True),
            FileType.XYZS: lambda: self.open_xyzs_file(openNew=True),
            FileType.SRG:  lambda: self.open_srg_file(openNew=True),
            FileType.DB:   self.open_db_file,
            FileType.CSV:  lambda: self.open_csv_file(openNew=True),
        }
        handler = dispatch.get(self.fileType)
        if handler:
            handler()
        else:
            QMessageBox.warning(self, "Invalid File", "Please select a valid file.")

    def on_append_file(self):
        """Handle the Append File action."""
        if self.fileType == FileType.DB:
            if hasattr(QMessageBox, "Ok"):
                QMessageBox.information(
                    self, "Append File Dialog",
                    "Cannot append another file if the database file is open.",
                    getattr(QMessageBox, "Ok"),
                )
            return

        dlg = self._make_file_dialog("Append", self._NON_DB_FILE_FILTER)
        if not dlg.exec():
            return

        selected = dlg.selectedFiles()
        if not selected:
            return

        self.file_path = selected[0]
        self.base_name, _ = os.path.splitext(self.file_path)
        self.fileType = FileType.get_fileType(self.file_path)

        if self.fileType is None:
            QMessageBox.warning(self, "Invalid File", "Please select a valid file.")
            return

        self.tabWidget.setCurrentIndex(0)

        dispatch = {
            FileType.XYZ:  lambda: self.open_xyz_file(openNew=False),
            FileType.SRG:  lambda: self.open_srg_file(openNew=False),
            FileType.CSV:  lambda: self.open_csv_file(openNew=False),
            FileType.XYZS: lambda: self.open_xyzs_file(openNew=False),
        }
        handler = dispatch.get(self.fileType)
        if handler:
            handler()
        else:
            QMessageBox.warning(self, "Invalid File", "Please select a valid file.")

    def _show_import_status(self):
        self.statusbar.showMessage(f"Imported data from the file {self.file_path}.")

    def open_xyz_file(self, openNew=True):
        """Open an XYZ file for polyline data."""
        if self.file_path is None:
            return
        self.vtkWidget.import_file(self.file_path, FileType.XYZ, newFile=openNew)
        self.treeview_setup()
        self.tableview_release()
        self._show_import_status()

    def open_xyzs_file(self, openNew=True):
        """Open an XYZS file for surface data."""
        if self.file_path is None:
            return
        self.vtkWidget.import_file(self.file_path, FileType.XYZS, newFile=openNew)
        self.actionSurface.setChecked(True)
        self.actionWireframe.setChecked(True)
        self.treeview_setup()
        self.tableview_release()
        self._show_import_status()
        # Auto-select the first surface file when only one is loaded
        if self.vtkWidget.model.surface_file_id == 2:
            self.selected_surface_file_id = 1

    def open_srg_file(self, openNew=True):
        """Open an SRG file for point data."""
        if self.file_path is None:
            return
        self.vtkWidget.import_file(self.file_path, FileType.SRG, newFile=openNew)
        self.treeview_setup()
        self.tableview_release()
        self._show_import_status()

    def open_db_file(self):
        """Open a SQLite DB file for polylines, points, and surfaces."""
        if self.file_path is None:
            return
        self.vtkWidget.import_file(self.file_path, FileType.DB, newFile=True)
        if self.vtkWidget and self.vtkWidget.model and self.vtkWidget.model.hasSurfacesTable():
            self.actionSurface.setChecked(True)
            self.actionWireframe.setChecked(True)
        self.treeview_setup()
        self.tableview_release()
        self.tableview_setup()
        self.config_heatmap(HeatMapCfg.OPEN)
        self._show_import_status()

    def open_csv_file(self, openNew=True):
        """Open a CSV file for polyline data."""
        if self.file_path is None:
            return
        self.vtkWidget.import_file(self.file_path, FileType.CSV, newFile=openNew)
        self.treeview_setup()
        self.tableview_release()
        self._show_import_status()

    # -----------------------------------------------------------------------
    # Tree View
    # -----------------------------------------------------------------------

    def treeview_setup(self):
        if self.file_path is None:
            return

        if self.fileType is None:
            return

        model = self.vtkWidget.model
        if not model:
            return

        if self.tree_model is None:
            self.tree_model = QStandardItemModel()

        root_item = QStandardItem(f"{self.file_path}")

        self.header_label = self.file_path if self.header_label == "" \
            else f"{self.header_label}\n{self.file_path}"

        polyline_count = len(model.polylines)
        point_count = len(model.points)
        surface_count = len(model.surfaces)

        icon_map = {
            FileType.DB:   "db",
            FileType.XYZ:  "xyz",
            FileType.SRG:  "srg",
            FileType.CSV:  "csv",
            FileType.XYZS: "xyzs",
        }
        icon_name = icon_map.get(self.fileType)
        if icon_name:
            root_item.setIcon(QIcon(f":/icons/{icon_name}.svg"))
        else:
            return

        if self.fileType == FileType.DB:
            self.treeview_populate_polylines(model, root_item)
            self.treeview_populate_points(model, root_item)
            self.treeview_populate_surfaces(model, root_item)
            self.header_label += f" ({polyline_count}L;{point_count}P;{surface_count}S)"
        elif self.fileType in (FileType.XYZ, FileType.CSV):
            self.treeview_populate_polylines(model, root_item)
            self.header_label += f" ({polyline_count}L)"
        elif self.fileType == FileType.SRG:
            self.treeview_populate_points(model, root_item)
            self.header_label += f" ({point_count}P)"
        elif self.fileType == FileType.XYZS:
            self.treeview_populate_surfaces(model, root_item)
            self.header_label += f" ({surface_count}S)"

        self.tree_model.appendRow(root_item)
        self.tree_model.setHorizontalHeaderLabels([self.header_label])
        self.treeView.setModel(self.tree_model)
        self.treeView.selectionModel().selectionChanged.connect(
            self.on_tree_selection_changed)
        if hasattr(QTreeView, "NoEditTriggers"):
            self.treeView.setEditTriggers(getattr(QTreeView, "NoEditTriggers"))

    def treeview_populate_polylines(self, model, root_item):
        """Populate the tree view with polyline nodes."""
        if not hasattr(model, "polylines"):
            return

        polylines = dict(sorted(model.polylines.items())[self.polyline_idx - 1:])
        polyline_root = QStandardItem("Polylines")
        polyline_root.setIcon(QIcon(":/icons/polyline.svg"))

        for polyline_id, points in polylines.items():
            polyline_item = QStandardItem(f"Polyline {polyline_id}")
            polyline_item.setIcon(QIcon(":/icons/polyline.svg"))
            setattr(polyline_item, "polyline_id", polyline_id)
            self.polyline_idx += 1

            for idx, (x, y, z, *_) in enumerate(points, start=1):
                point_item = QStandardItem(
                    f"Point {idx} (X={x:.3f}, Y={y:.3f}, Z={z:.3f})")
                point_item.setIcon(QIcon(":/icons/point.svg"))
                polyline_item.appendRow(point_item)

            polyline_root.appendRow(polyline_item)

        root_item.appendRow(polyline_root)

    def treeview_populate_points(self, model, root_item):
        """Populate the tree view with point nodes."""
        if not hasattr(model, "points"):
            return

        points = dict(sorted(model.points.items())[self.point_idx - 1:])
        point_root = QStandardItem("Points")
        point_root.setIcon(QIcon(":/icons/point.svg"))

        for point_id, vertices in points.items():
            x, y, z, name = vertices[0]
            point_item = QStandardItem(
                f"Point {point_id} (X={x:.3f}, Y={y:.3f}, Z={z:.3f})")
            point_item.setIcon(QIcon(":/icons/point.svg"))
            setattr(point_item, "point_id", point_id)
            setattr(point_item, "name", name)
            self.point_idx += 1
            point_root.appendRow(point_item)

        root_item.appendRow(point_root)

    def treeview_populate_surfaces(self, model, root_item):
        """Populate the tree view with surface/contour nodes."""
        if not hasattr(model, "surfaces"):
            return

        surface_root = QStandardItem("Surface")
        surface_root.setIcon(QIcon(":/icons/polyline.svg"))
        setattr(surface_root, "surface_file_id",
                self.vtkWidget.model.surface_file_id - 1)

        total = len(model.surfaces)
        new_contours = total - self.contours
        surface_item = QStandardItem(f"Contours {new_contours}")
        surface_item.setIcon(QIcon(":/icons/polyline.svg"))
        self.contours = total

        surface_root.appendRow(surface_item)
        root_item.appendRow(surface_root)

    # -----------------------------------------------------------------------
    # Context Menu
    # -----------------------------------------------------------------------

    def setup_context_menu(self):
        self.context_menu = QMenu(self)

        self.selectPolyline     = self.context_menu.addAction("Select Polyline")
        self.unselectPolyline   = self.context_menu.addAction("Unselect Polyline")
        self.showAttribPolyline = self.context_menu.addAction("Show Polyline Attributes")
        self.editAttribPolyline = self.context_menu.addAction("Edit Polyline Attributes")

        self.selectPoint     = self.context_menu.addAction("Select Point")
        self.unselectPoint   = self.context_menu.addAction("Unselect Point")
        self.showAttribPoint = self.context_menu.addAction("Show Point Attributes")
        self.editAttribPoint = self.context_menu.addAction("Edit Point Attributes")

        self.toggleSurfaceActor    = self.context_menu.addAction("Show/Hide Surface Actor")
        self.toggleWireframeActor  = self.context_menu.addAction("Show/Hide Wireframe Actor")
        self.toggleContourActors   = self.context_menu.addAction("Show/Hide Contour Actors")
        self.contourDifference     = self.context_menu.addAction("Difference from the first Surface")
        self.exportContoursXyzs    = self.context_menu.addAction("Export Contours to XYZS")

        self.selectPolyline.triggered.connect(self.on_select_polyline)
        self.unselectPolyline.triggered.connect(self.on_unselect_polyline)
        self.showAttribPolyline.triggered.connect(self.on_showAttrib_polyline)
        self.editAttribPolyline.triggered.connect(self.on_editAttrib_polyline)

        self.selectPoint.triggered.connect(self.on_select_point)
        self.unselectPoint.triggered.connect(self.on_unselect_point)
        self.showAttribPoint.triggered.connect(self.on_showAttrib_point)
        self.editAttribPoint.triggered.connect(self.on_editAttrib_point)

        self.toggleSurfaceActor.triggered.connect(self.on_toggle_surface_actor)
        self.toggleWireframeActor.triggered.connect(self.on_toggle_wireframe_actor)
        self.toggleContourActors.triggered.connect(self.on_toggle_contour_actors)
        self.contourDifference.triggered.connect(self.on_contour_difference)
        self.exportContoursXyzs.triggered.connect(self.on_export_contours_xyzs)

    def get_item_level(self, index):
        """Return the depth of a tree item (root = 1)."""
        level = 0
        while index.isValid():
            index = index.parent()
            level += 1
        return level

    def on_tree_selection_changed(self, selected, deselected):
        """Track which surface tree item is currently selected."""
        indexes = selected.indexes()
        if not indexes:
            self.selected_surface_file_id = None
            return

        index = indexes[0]
        model = self.treeView.model()
        if hasattr(model, "itemFromIndex"):
            item = model.itemFromIndex(index)
            if hasattr(item, "surface_file_id"):
                self.selected_surface_file_id = item.surface_file_id
                return

        self.selected_surface_file_id = None

    def on_context_menu(self, position):
        index = self.treeView.indexAt(position)
        if not index.isValid():
            return

        level = self.get_item_level(index)
        if level not in (2, 3):
            return

        if hasattr(self.treeView.model(), "itemFromIndex"):
            self.context_item = getattr(self.treeView.model(), "itemFromIndex")(index)

        if hasattr(self.context_item, "surface_file_id"):
            self.context_type = "surface"
            self.context_id = self.context_item.surface_file_id
        elif level == 3 and hasattr(self.context_item, "polyline_id"):
            self.context_type = "polyline"
            self.context_id = self.context_item.polyline_id
        elif level == 3 and hasattr(self.context_item, "point_id"):
            self.context_type = "point"
            self.context_id = self.context_item.point_id
        else:
            return

        is_polyline  = self.context_type == "polyline"
        is_point     = self.context_type == "point"
        is_surface   = self.context_type == "surface"

        self.selectPolyline.setVisible(is_polyline)
        self.unselectPolyline.setVisible(is_polyline)
        self.showAttribPolyline.setVisible(is_polyline)
        self.editAttribPolyline.setVisible(is_polyline)

        self.selectPoint.setVisible(is_point)
        self.unselectPoint.setVisible(is_point)
        self.showAttribPoint.setVisible(is_point)
        self.editAttribPoint.setVisible(is_point)

        self.toggleSurfaceActor.setVisible(is_surface)
        self.toggleWireframeActor.setVisible(is_surface)
        self.toggleContourActors.setVisible(is_surface)
        self.contourDifference.setVisible(
            is_surface and self.context_id != 1)
        self.exportContoursXyzs.setVisible(
            is_surface and self.context_id == 1)

        self.context_menu.exec(self.treeView.viewport().mapToGlobal(position))

    # -----------------------------------------------------------------------
    # Context Menu Actions — Polylines
    # -----------------------------------------------------------------------

    def on_select_polyline(self):
        if self.context_type != "polyline":
            return
        actor = self.vtkWidget.polylines_get_actor(self.context_id)
        if actor:
            if self.vtkWidget.selected_actor:
                self.vtkWidget.deselect_actor(self.vtkWidget.selected_actor)
            self.vtkWidget.select_actor(actor)
            self.vtkWidget.UpdateView()

    def on_unselect_polyline(self):
        if self.context_type != "polyline":
            return
        actor = self.vtkWidget.polylines_get_actor(self.context_id)
        if actor:
            self.vtkWidget.deselect_actor(actor)
            self.vtkWidget.UpdateView()

    def on_showAttrib_polyline(self):
        if self.context_type != "polyline":
            return
        actor = self.vtkWidget.polylines_get_actor(self.context_id)
        if actor:
            self.vtkWidget.show_dialog(actor)

    def on_editAttrib_polyline(self):
        if not self.tableModelPolylines:
            QMessageBox.warning(
                self, "Invalid Table",
                "First Export or Open Polyline Database File.")
            return

        if self.context_type != "polyline":
            return

        self.tabWidget.setCurrentIndex(1)
        found_row = self._find_table_row(self.tableModelPolylines, self.context_id)
        if found_row == -1:
            print(f"No row found with polyline_id '{self.context_id}'.")
            return
        self._scroll_and_select_row(self.tableViewPolylines,
                                    self.tableModelPolylines, found_row)

    # -----------------------------------------------------------------------
    # Context Menu Actions — Points
    # -----------------------------------------------------------------------

    def on_select_point(self):
        if self.context_type != "point":
            return
        actor = self.vtkWidget.points_get_actor(self.context_id)
        if actor:
            if self.vtkWidget.selected_actor:
                self.vtkWidget.deselect_actor(self.vtkWidget.selected_actor)
            self.vtkWidget.select_actor(actor)
            self.vtkWidget.UpdateView()

    def on_unselect_point(self):
        if self.context_type != "point":
            return
        actor = self.vtkWidget.points_get_actor(self.context_id)
        if actor:
            self.vtkWidget.deselect_actor(actor)
            self.vtkWidget.UpdateView()

    def on_showAttrib_point(self):
        if self.context_type != "point":
            return
        actor = self.vtkWidget.points_get_actor(self.context_id)
        if actor:
            self.vtkWidget.show_dialog(actor)

    def on_editAttrib_point(self):
        if not self.tableModelPoints:
            QMessageBox.warning(
                self, "Invalid Table",
                "First Export or Open Point Database File.")
            return

        if self.context_type != "point":
            return

        self.tabWidget.setCurrentIndex(2)
        found_row = self._find_table_row(self.tableModelPoints, self.context_id)
        if found_row == -1:
            print(f"No row found with point_id '{self.context_id}'.")
            return
        self._scroll_and_select_row(self.tableViewPoints,
                                    self.tableModelPoints, found_row)

    # -----------------------------------------------------------------------
    # Context Menu Actions — Surfaces
    # -----------------------------------------------------------------------

    def on_toggle_surface_actor(self):
        if self.context_type != "surface":
            return
        actor = self.vtkWidget.surfaces_get_surface_actor(self.context_id)
        if actor:
            actor.SetVisibility(1 - actor.GetVisibility())
            self.vtkWidget.UpdateView(False)

    def on_toggle_wireframe_actor(self):
        if self.context_type != "surface":
            return
        actor = self.vtkWidget.surfaces_get_wireframe_actor(self.context_id)
        if actor:
            actor.SetVisibility(1 - actor.GetVisibility())
            self.vtkWidget.UpdateView(False)

    def on_toggle_contour_actors(self):
        if self.context_type != "surface":
            return
        actors = list(self.vtkWidget.contourActorsMap.get(self.context_id, []))
        for actor in actors:
            actor.SetVisibility(1 - actor.GetVisibility())
        if actors:
            self.vtkWidget.UpdateView(False)

    def on_contour_difference(self):
        if self.context_type != "surface" or self.context_id == 1:
            return
        success = self.vtkWidget.contour_difference(self.context_id)
        if not success:
            QMessageBox.warning(
                self, "Contour Difference",
                "Could not compute contour difference. "
                "The surfaces may not share a Z level or the geometry is invalid."
            )

    def on_export_contours_xyzs(self):
        """Export the current contour actors for fid=1 to an .xyzs file.

        Each contour actor's polyline cells are written as X Y Z lines,
        with a $ separator between actors. Reflects any difference operations
        already applied — i.e. exports the modified result, not the original.
        """
        if self.context_type != "surface" or self.context_id != 1:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Contours to XYZS", "", "XYZS Files (*.xyzs);;All Files (*)"
        )
        if not file_path:
            return

        actors = self.vtkWidget.contourActorsMap.get(1, [])
        if not actors:
            QMessageBox.warning(self, "Export Contours",
                                "No contour actors found for the first surface.")
            return

        try:
            with open(file_path, "w") as f:
                for actor_idx, actor in enumerate(actors):
                    mapper = actor.GetMapper()
                    if mapper is None:
                        continue
                    poly = mapper.GetInput()
                    if poly is None or poly.GetNumberOfPoints() == 0:
                        continue

                    written = False
                    for cell_idx in range(poly.GetNumberOfCells()):
                        cell = poly.GetCell(cell_idx)
                        n_pts = cell.GetNumberOfPoints()
                        if n_pts < 2:
                            continue
                        for j in range(n_pts):
                            pid = cell.GetPointId(j)
                            x, y, z = poly.GetPoint(pid)
                            f.write(f"{x:.3f}\t{y:.3f}\t{z:.3f}\n")
                        written = True

                    if written and actor_idx < len(actors) - 1:
                        f.write("$\n")

            QMessageBox.information(
                self, "Export Contours",
                f"Contours exported successfully to:\n{file_path}"
            )
        except OSError as e:
            QMessageBox.critical(self, "Export Contours",
                                 f"Could not write file:\n{e}")

    # -----------------------------------------------------------------------
    # Table-row Helpers
    # -----------------------------------------------------------------------

    def _find_table_row(self, table_model, target_id):
        """Return the first row whose column-0 value equals target_id, or -1."""
        if not hasattr(Qt, "DisplayRole"):
            return -1
        for row in range(table_model.rowCount()):
            index = table_model.index(row, 0)
            if table_model.data(index, getattr(Qt, "DisplayRole")) == target_id:
                return row
        return -1

    def _scroll_and_select_row(self, table_view, table_model, row):
        """Scroll a table view to the given row and select it."""
        index = table_model.index(row, 0)
        table_view.scrollTo(index)
        selection_model = table_view.selectionModel()
        if hasattr(QItemSelectionModel, "ClearAndSelect") and \
                hasattr(QItemSelectionModel, "Rows"):
            selection_model.select(
                index,
                getattr(QItemSelectionModel, "ClearAndSelect") |
                getattr(QItemSelectionModel, "Rows"),
            )

    # -----------------------------------------------------------------------
    # Table Views
    # -----------------------------------------------------------------------

    def _open_db_connection(self):
        """Ensure a SQLite connection is open. Returns False on failure."""
        if self.db is None:
            self.db = QSqlDatabase.addDatabase("QSQLITE")
        if not self.file_path:
            QMessageBox.warning(self, "Invalid File", "Error: Database path is not set.")
            return False
        self.db.setDatabaseName(self.file_path)
        if not self.db.open():
            QMessageBox.warning(self, "Invalid File", "Error: Unable to open database.")
            print("Error: Unable to open database")
            return False
        return True

    def _apply_float_delegate(self, table_view, column_count):
        """Apply the float-formatting delegate to all columns of a table view."""
        for col in range(column_count):
            table_view.setItemDelegateForColumn(col, _FloatRightAlignDelegate(table_view))

    def tableview_setup(self):
        if self.vtkWidget.model is None:
            return
        model = self.vtkWidget.model
        if model.hasPointsTable():
            self.tableview_setup_points()
        if model.hasPolylinesTable():
            self.tableview_setup_polylines()

    def tableview_setup_polylines(self):
        if not self._open_db_connection():
            return

        self.tableModelPolylines = _ValidatedSqlTableModel(
            self, self, self.db, read_only_columns=[0, 1, 2, 3, 4, 5])
        self.tableModelPolylines.setTable("polylines")
        self.tableModelPolylines.select()
        self._fetch_all_rows(self.tableModelPolylines)

        self.tableViewPolylines.setModel(self.tableModelPolylines)
        self._apply_float_delegate(
            self.tableViewPolylines, self.tableModelPolylines.columnCount())
        self.tableViewPolylines.resizeColumnsToContents()

        total_rows = self.tableModelPolylines.rowCount()
        self.statusbar.showMessage(
            f"Total rows: {total_rows} saved in the database {self.file_path}.")

    def tableview_setup_points(self):
        """Set up the TableView for the points table."""
        if not self._open_db_connection():
            return

        self.tableModelPoints = _ValidatedSqlTableModel(
            self, self, self.db, read_only_columns=[0, 1, 2, 3, 4])
        self.tableModelPoints.setTable("points")
        self.tableModelPoints.select()
        self._fetch_all_rows(self.tableModelPoints)

        self.tableViewPoints.setModel(self.tableModelPoints)
        self._apply_float_delegate(
            self.tableViewPoints, self.tableModelPoints.columnCount())
        self.tableViewPoints.resizeColumnsToContents()

        total_rows = self.tableModelPoints.rowCount()
        self.statusbar.showMessage(
            f"Total rows: {total_rows} saved in the database {self.file_path}.")

    def _fetch_all_rows(self, table_model):
        """Force a QSqlTableModel to fetch all available rows."""
        while table_model.canFetchMore():
            table_model.fetchMore()

    def tableview_release(self):
        if self.tableModelPolylines:
            self.tableViewPolylines.setModel(None)
            self.tableModelPolylines = None
        if self.tableModelPoints:
            self.tableViewPoints.setModel(None)
            self.tableModelPoints = None
        if self.db and self.db.isOpen() and self.file_path:
            self.db.close()
            QSqlDatabase.removeDatabase(self.file_path)

    # -----------------------------------------------------------------------
    # Export / Database Save
    # -----------------------------------------------------------------------

    def on_export(self):
        """Handle the Export to Database action."""
        if self.file_path is None:
            return

        self.configure_db_path(self.file_path)
        model = self.vtkWidget.model

        if not model:
            QMessageBox.warning(
                self, "Invalid File",
                "Please open a valid .xyz or .srg or .xyzs file before saving into the database.")
            return

        has_poly = bool(model.polylines)
        has_pts = bool(model.points)
        has_surf = bool(model.surfaces)
        single_type = (has_poly and not has_pts and not has_surf) or \
                      (not has_poly and has_pts and not has_surf) or \
                      (not has_poly and not has_pts and has_surf)
        multi_type = (has_poly and has_pts) or \
                     (has_poly and has_surf) or \
                     (has_pts and has_surf)

        if single_type:
            if os.path.exists(self.file_path):
                if hasattr(QMessageBox, "Yes") or hasattr(QMessageBox, "No"):
                    reply = QMessageBox.question(
                        self, "Message",
                        f"The Database File Already Exists:\n{self.file_path}\n"
                        "Do you want to create an empty database overwriting the existing file?",
                        getattr(QMessageBox, "Yes") | getattr(QMessageBox, "No"),
                        getattr(QMessageBox, "No"),
                    )
                    if reply != getattr(QMessageBox, "Yes"):
                        return
        elif multi_type:
            dlg = QtWidgets.QFileDialog(self)
            dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dlg.setDefaultSuffix("db")
            dlg.setNameFilter("SQLite Files (*.db)")
            if dlg.exec():
                selected = dlg.selectedFiles()
                if selected:
                    self.file_path = selected[0]
            else:
                return
        elif not has_poly and not has_pts:
            return
        else:
            return

        self.save_database(model)

    def configure_db_path(self, file):
        if file:
            base_name, _ = os.path.splitext(file)
            self.file_path = base_name + ".db"

    def save_database(self, model):
        if model.polylines:
            model.polylines_save_database(self.file_path)
            self.tabWidget.setCurrentIndex(1)
            self.tableview_setup_polylines()
            if hasattr(QMessageBox, "Ok"):
                QMessageBox.information(
                    self, "Save Successful",
                    "The polyline data has been successfully saved to the database.",
                    getattr(QMessageBox, "Ok"),
                )

        if model.points:
            model.points_save_database(self.file_path)
            self.tabWidget.setCurrentIndex(2)
            self.tableview_setup_points()
            if hasattr(QMessageBox, "Ok"):
                QMessageBox.information(
                    self, "Save Successful",
                    "The point data has been successfully saved to the database.",
                    getattr(QMessageBox, "Ok"),
                )

        if model.surfaces:
            model.surfaces_save_database(self.file_path)
            if hasattr(QMessageBox, "Ok"):
                QMessageBox.information(
                    self, "Save Successful",
                    "The surfaces data has been successfully saved to the database.",
                    getattr(QMessageBox, "Ok"),
                )

    # -----------------------------------------------------------------------
    # Workspace
    # -----------------------------------------------------------------------

    def on_clean_workspace(self):
        if self.vtkWidget:
            self.actionPolyLabel.setChecked(False)
            self.actionPointLabel.setChecked(False)
            self.vtkWidget.CleanPolylabels()
            self.vtkWidget.CleanPointlabels()
            self.vtkWidget.RemoveAllActors()
            self.actionContour.setChecked(False)
            self.actionSurface.setChecked(False)
            self.actionWireframe.setChecked(False)
            self.vtkWidget.UpdateView(False)

        self.tree_model = QStandardItemModel()
        self.treeView.setModel(self.tree_model)
        self.polyline_idx = 1
        self.point_idx = 1
        self.contours = 0
        self.selected_surface_file_id = None
        self.header_label = ""
        self.tableview_release()

        if self.file_path:
            self.fileType = None
        self.config_heatmap(HeatMapCfg.CLEAR)

    # -----------------------------------------------------------------------
    # View Controls
    # -----------------------------------------------------------------------

    def _switch_to_vtk_tab(self):
        self.tabWidget.setCurrentIndex(0)

    def on_front(self):
        if self.vtkWidget:
            self._switch_to_vtk_tab()
            self.vtkWidget.OnFrontView()

    def on_back(self):
        if self.vtkWidget:
            self._switch_to_vtk_tab()
            self.vtkWidget.OnBackView()

    def on_top(self):
        if self.vtkWidget:
            self._switch_to_vtk_tab()
            self.vtkWidget.OnTopView()

    def on_bottom(self):
        if self.vtkWidget:
            self._switch_to_vtk_tab()
            self.vtkWidget.OnBottomView()

    def on_left(self):
        if self.vtkWidget:
            self._switch_to_vtk_tab()
            self.vtkWidget.OnLeftView()

    def on_right(self):
        if self.vtkWidget:
            self._switch_to_vtk_tab()
            self.vtkWidget.OnRightView()

    def on_iso(self):
        if self.vtkWidget:
            self._switch_to_vtk_tab()
            self.vtkWidget.OnIsometricView()

    def on_fit(self):
        if self.vtkWidget:
            self._switch_to_vtk_tab()
            self.vtkWidget.OnFitView()

    # -----------------------------------------------------------------------
    # HeatMap
    # -----------------------------------------------------------------------

    def on_heatmapcfg(self):
        """Open the HeatMap configuration dialog."""
        if self.fileType != FileType.DB:
            if hasattr(QMessageBox, "Ok"):
                QMessageBox.information(
                    self, "HeatMap Tool Dialog",
                    "Cannot perform heatmap on the current file, it only works on database.",
                    getattr(QMessageBox, "Ok"),
                )
            return

        if not (self.vtkWidget and self.vtkWidget.model):
            return

        self._switch_to_vtk_tab()
        dialog = HeatMapDialog(self, self.vtkWidget.model)
        result = dialog.exec()
        if hasattr(QDialog, "Accepted") and result == getattr(QDialog, "Accepted"):
            self.config_heatmap(HeatMapCfg.CONF)

    def on_heatmap(self, checked):
        model = self.vtkWidget.model
        if not model:
            return
        if model.hasPeriods():
            self.currentPeriod = 1
            self.maxPeriod = model.getMaxPeriod()
            self.labelPeriod.setText(f"P: 01/{self.maxPeriod:02d}")
            model.updateRoutesTonnes(1)
            self.vtkWidget.polylines_update_data()
            self.vtkWidget.OnHeatMap(checked)
        self.config_heatmap(HeatMapCfg.PERIOD, checked)

    def on_backward(self):
        self.currentPeriod = self.currentPeriod - 1 if self.currentPeriod > 1 \
            else self.maxPeriod
        self.labelPeriod.setText(f"P: {self.currentPeriod:02d}/{self.maxPeriod:02d}")
        self._update_heatmap_period()

    def on_forward(self):
        self.currentPeriod = self.currentPeriod + 1 if self.currentPeriod < self.maxPeriod \
            else 1
        self.labelPeriod.setText(f"P: {self.currentPeriod:02d}/{self.maxPeriod:02d}")
        self._update_heatmap_period()

    def _update_heatmap_period(self):
        model = self.vtkWidget.model
        if not model:
            return
        model.updateRoutesTonnes(self.currentPeriod)
        self.vtkWidget.polylines_update_data()
        self.vtkWidget.OnHeatMap(True)

    def config_heatmap(self, heatmapcfg, checked=True):
        """Update the heatmap toolbar controls based on state."""
        model = self.vtkWidget.model
        if not model and heatmapcfg != HeatMapCfg.INIT:
            return

        if heatmapcfg == HeatMapCfg.INIT:
            self.config_heatmap_init()
        elif heatmapcfg in (HeatMapCfg.OPEN, HeatMapCfg.CONF):
            if model and model.hasRoutesTonnesTable():
                self.actionHeatMap.setEnabled(True)
        elif heatmapcfg == HeatMapCfg.CLEAR:
            self.actionHeatMap.setChecked(False)
            self.actionHeatMap.setDisabled(True)
            self.labelPeriod.setText("P: 00/00")
            self.actionBackward.setDisabled(True)
            self.labelPeriod.setDisabled(True)
            self.actionForward.setDisabled(True)
        elif heatmapcfg == HeatMapCfg.PERIOD:
            if checked:
                self.currentPeriod = 1
                self.actionBackward.setEnabled(True)
                self.labelPeriod.setEnabled(True)
                self.actionForward.setEnabled(True)
            else:
                self.labelPeriod.setText("P: 00/00")
                self.actionBackward.setDisabled(True)
                self.labelPeriod.setDisabled(True)
                self.actionForward.setDisabled(True)

    def config_heatmap_init(self):
        self.labelPeriod.setText("P: 00/00")
        self.actionHeatMap.setDisabled(True)
        self.actionBackward.setDisabled(True)
        self.labelPeriod.setDisabled(True)
        self.actionForward.setDisabled(True)

    # -----------------------------------------------------------------------
    # Labels & Picking
    # -----------------------------------------------------------------------

    def on_unpick(self, checked):
        if self.vtkWidget.model:
            self.vtkWidget.unpick = checked

    def on_polylabel(self, checked):
        if self.vtkWidget.model:
            self.vtkWidget.polylabel = checked
            self.vtkWidget.OnPolylabels(checked, self.fileType)

    def on_pointlabel(self, checked):
        if self.vtkWidget.model:
            self.vtkWidget.pointlabel = checked
            self.vtkWidget.OnPointLabels(checked, self.fileType)

    # -----------------------------------------------------------------------
    # Surface / Wireframe / Contour
    # -----------------------------------------------------------------------

    def _check_valid_surfaces(self, action_to_uncheck=None):
        """Show a warning and optionally uncheck an action if no valid surfaces exist
        or no surface tree item is selected."""
        if not self.vtkWidget.ValidSurfaces():
            if hasattr(QMessageBox, "Ok"):
                QMessageBox.information(
                    self, "Surface Reconstruction Dialog",
                    "Cannot perform Surface Reconstruction Operation, "
                    "it only works with valid surface data.",
                    getattr(QMessageBox, "Ok"),
                )
            if action_to_uncheck:
                action_to_uncheck.setChecked(False)
            return False

        if self.selected_surface_file_id is None:
            if hasattr(QMessageBox, "Ok"):
                QMessageBox.information(
                    self, "Surface Reconstruction Dialog",
                    "Please select a Surface item in the tree first.",
                    getattr(QMessageBox, "Ok"),
                )
            if action_to_uncheck:
                action_to_uncheck.setChecked(False)
            return False

        return True

    def on_contour(self, checked):
        if not self._check_valid_surfaces(self.actionContour):
            return
        if self.vtkWidget:
            self.vtkWidget.SetVisibilityContourActors(
                self.selected_surface_file_id, checked)
            self.vtkWidget.UpdateView(False)

    def on_surface(self, checked):
        if not self._check_valid_surfaces(self.actionSurface):
            return
        if self.vtkWidget:
            self.vtkWidget.SetVisibilitySurfaceActor(
                self.selected_surface_file_id, checked)
            self.vtkWidget.UpdateView(False)

    def on_wireframe(self, checked):
        if not self._check_valid_surfaces(self.actionWireframe):
            return
        if self.vtkWidget:
            self.vtkWidget.SetVisibilityWireframeActor(
                self.selected_surface_file_id, checked)
            self.vtkWidget.UpdateView(False)

    def on_surface_cfg(self):
        """Open the Surface configuration dialog."""
        if not self._check_valid_surfaces():
            return
        if not (self.vtkWidget and self.vtkWidget.model):
            return

        self._switch_to_vtk_tab()
        dialog = SurfaceDialog(
            self, self.contour_color, self.surfacecfg, self.delaunaycfg)
        result = dialog.exec()
        if hasattr(QDialog, "Accepted") and result == getattr(QDialog, "Accepted"):
            self.delaunaycfg = dialog.delaunaycfg
            self.surfacecfg = dialog.surfacecfg
            self.contour_color = dialog.contour_color
            self.config_surface()
            self.vtkWidget.UpdateSurface(self.fileType)
            self.vtkWidget.UpdateColorContourActors(self.contour_color)

            # Re-apply current toolbar visibility states to all files
            surface_visible  = self.actionSurface.isChecked()
            wireframe_visible = self.actionWireframe.isChecked()
            contour_visible  = self.actionContour.isChecked()
            for fid in self.vtkWidget.contourActorsMap:
                self.vtkWidget.SetVisibilitySurfaceActor(fid, surface_visible)
                self.vtkWidget.SetVisibilityWireframeActor(fid, wireframe_visible)
                self.vtkWidget.SetVisibilityContourActors(fid, contour_visible)

            self.actionSurface.setChecked(True)
            self.vtkWidget.SetVisibilitySurfaceActor(
                self.selected_surface_file_id, True)
            self.vtkWidget.UpdateView(False)

    # -----------------------------------------------------------------------
    # Tab Events
    # -----------------------------------------------------------------------

    def on_tab_changed(self, index):
        """Refresh polyline data when switching back to the VTK tab."""
        if index == 0 and self.vtkWidget and self.fileType == FileType.DB:
            model = self.vtkWidget.model
            if model and model.polylines:
                self.vtkWidget.polylines_update_data()

    # -----------------------------------------------------------------------
    # Help / About / Exit
    # -----------------------------------------------------------------------

    def on_help(self):
        HelpDialog(self).show()

    def on_about(self):
        AboutDialog(self).show()

    def on_exit(self):
        if hasattr(QMessageBox, "Yes") or hasattr(QMessageBox, "No"):
            reply = QMessageBox.question(
                self, "Confirm Exit", "Are you sure you want to exit?",
                getattr(QMessageBox, "Yes") | getattr(QMessageBox, "No"),
                getattr(QMessageBox, "No"),
            )
            if reply == getattr(QMessageBox, "Yes"):
                self.close()

    def closeEvent(self, event):
        """Close the VTK widget when the application window is closed."""
        if self.vtkWidget:
            self.vtkWidget.close()
        event.accept()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindowApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

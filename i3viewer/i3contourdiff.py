import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QMessageBox,
    QTableWidgetItem,
)

from i3viewer.i3enums import Params
from i3viewer.i3contourdiffDialog import \
    Ui_Dialog  # Import the generated UI class for contour diff


class ContourDiffDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        # Set up the user interface from Designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.model = model

        self.folder_path = None
        self.scanned_files = []

        # Customize the dialog (non-modal specific settings)
        self.setWindowTitle(f"{Params.ApplicationName.value} - Contour Difference Dialog")
        if hasattr(Qt, "RightToLeft"):
            self.ui.pushButton_browse.setLayoutDirection(
                getattr(Qt, "RightToLeft")
            )  # This will put icon on right
            self.ui.pushButton_scan.setLayoutDirection(
                getattr(Qt, "RightToLeft")
            )  # This will put icon on right
            self.ui.pushButton_step1.setLayoutDirection(
                getattr(Qt, "RightToLeft")
            )  # This will put icon on right
            self.ui.pushButton_step2.setLayoutDirection(
                getattr(Qt, "RightToLeft")
            )  # This will put icon on right

        # Step buttons start disabled until their prerequisite is met
        self.ui.pushButton_scan.setEnabled(False)
        self.ui.pushButton_step1.setEnabled(False)
        self.ui.pushButton_step2.setEnabled(False)
        self.ui.comboBox_shovel.setEnabled(False)

        self.ui.tableWidget_sessions.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        # Connect signals to slots
        self.ui.pushButton_browse.clicked.connect(self.pick_folder)
        self.ui.pushButton_scan.clicked.connect(self.scan_folder)
        self.ui.pushButton_step1.clicked.connect(self.import_to_db)
        self.ui.pushButton_step2.clicked.connect(self.perform_contour_diff)
        self.ui.pushButton_confirmDelete.clicked.connect(self.delete_selected_session)
        self.ui.pushButton_close.clicked.connect(self.reject)
        self.ui.lineEdit_search.textChanged.connect(self.filter_sessions)

        # Initialize icons and session table
        self.config_icons()
        self.refresh_sessions_table()

    def config_icons(self):
        if self.model:
            if self.model.hasImportedTable():
                self.ui.pushButton_step1.setIcon(QIcon(":/icons/check.svg"))
            else:
                self.ui.pushButton_step1.setIcon(QIcon(":/icons/cross.svg"))
            if self.model.hasContourDiffResult():
                self.ui.pushButton_step2.setIcon(QIcon(":/icons/check.svg"))
            else:
                self.ui.pushButton_step2.setIcon(QIcon(":/icons/cross.svg"))

    def log(self, message):
        """Append a line to the log box."""
        self.ui.plainTextEdit_log.appendPlainText(message)

    def set_progress(self, pct, label):
        self.ui.progressBar.setValue(int(pct))
        self.ui.label_progressPct.setText(f"{int(pct)}%")
        self.ui.label_progressStatus.setText(label)

    def pick_folder(self):
        """Handle picking the folder to scan."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_path = folder_path
            self.ui.lineEdit_folderPath.setText(folder_path)
            self.ui.pushButton_scan.setEnabled(True)
            self.log(f"Folder: {folder_path}")

    def scan_folder(self):
        """Scan the selected folder for XYZ files and populate the shovel combo box."""
        if not self.model or not self.folder_path:
            return

        self.set_progress(0, "Scanning…")
        self.log("Scanning for XYZ files…")

        self.scanned_files = self.model.scan_folder(self.folder_path)

        if not self.scanned_files:
            QMessageBox.warning(
                self,
                "No Files Found",
                "No XYZ files were found in the selected folder.",
            )
            self.set_progress(0, "Ready")
            return

        for f in self.scanned_files:
            self.log(f"  found {os.path.basename(f)}")
        self.log(f"{len(self.scanned_files)} files found")

        # Populate the shovel name combo box from the scan results
        shovel_names = self.model.get_shovel_names(self.scanned_files)
        self.ui.comboBox_shovel.clear()
        self.ui.comboBox_shovel.addItems(shovel_names)
        self.ui.comboBox_shovel.setEnabled(bool(shovel_names))

        self.ui.pushButton_step1.setEnabled(True)
        self.set_progress(33, "Scan complete")

    def import_to_db(self):
        """Step 1: import the scanned files into the database."""
        if not self.model or not self.scanned_files:
            return

        self.set_progress(33, "Importing to DB…")
        self.log("Importing files to DB…")

        self.model.import_files(self.scanned_files)

        self.log(f"{len(self.scanned_files)} XYZ files imported")
        self.set_progress(50, "Import complete")
        self.config_icons()
        self.ui.pushButton_step2.setEnabled(True)

    def perform_contour_diff(self):
        """Step 2: run the contour difference for the selected shovel, then
        write the resulting session to the database."""
        if not self.model:
            return

        shovel_name = self.ui.comboBox_shovel.currentText()
        if not shovel_name:
            QMessageBox.warning(
                self,
                "No Shovel Selected",
                "Select a shovel name before running the contour difference.",
            )
            return

        self.set_progress(50, "Running contour difference…")
        self.log(f"Contour difference — shovel '{shovel_name}'…")

        result = self.model.run_contour_diff(shovel_name)

        self.log(f"Contour difference complete — {result.contours} regions processed")
        self.set_progress(75, "Contour diff done")

        self.set_progress(80, "Writing to DB…")
        self.log("Writing results to database…")

        session = self.model.write_results()

        self.log(
            f"Done — {session.rows} rows, {session.contours} contours, "
            f"session {session.id} saved"
        )
        self.set_progress(100, "Complete")
        self.config_icons()
        self.refresh_sessions_table()

    def refresh_sessions_table(self):
        """Reload the sessions table from the model."""
        if not self.model:
            return

        sessions = self.model.get_sessions()
        table = self.ui.tableWidget_sessions
        table.setRowCount(0)

        for session in sessions:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(session.id)))
            table.setItem(row, 1, QTableWidgetItem(str(session.date)))
            table.setItem(row, 2, QTableWidgetItem(str(session.folder)))
            table.setItem(row, 3, QTableWidgetItem(f"{session.rows:,}"))
            table.setItem(row, 4, QTableWidgetItem(str(session.contours)))
            table.setItem(row, 5, QTableWidgetItem(str(session.status)))

        self.update_db_summary(sessions)

    def update_db_summary(self, sessions):
        total_rows = sum(s.rows for s in sessions)
        self.ui.label_dbSummary.setText(
            f"{len(sessions)} sessions · {total_rows:,} rows"
        )

    def filter_sessions(self, text):
        """Hide session rows that don't match the search text."""
        table = self.ui.tableWidget_sessions
        text = text.lower()
        for row in range(table.rowCount()):
            match = any(
                text in (table.item(row, col).text().lower())
                for col in range(table.columnCount())
                if table.item(row, col)
            )
            table.setRowHidden(row, bool(text) and not match)

    def delete_selected_session(self):
        """Delete the currently selected session from the DB after confirmation."""
        if not self.model:
            return

        table = self.ui.tableWidget_sessions
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(
                self,
                "No Session Selected",
                "Select a session in the table before deleting.",
            )
            return

        row = selected_rows[0].row()
        session_id = table.item(row, 0).text()

        confirm = QMessageBox.question(
            self,
            "Delete Session",
            f"Remove session {session_id} from the database?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.model.delete_session(session_id)
            self.log(f"Session {session_id} removed from DB")
            self.refresh_sessions_table()

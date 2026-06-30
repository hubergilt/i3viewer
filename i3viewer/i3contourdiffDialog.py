# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'i3contourdiffDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDialog,
    QFormLayout, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPlainTextEdit, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)
import i3viewer.icons_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(640, 660)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.horizontalLayout_folder = QHBoxLayout()
        self.horizontalLayout_folder.setObjectName(u"horizontalLayout_folder")
        self.lineEdit_folderPath = QLineEdit(Dialog)
        self.lineEdit_folderPath.setObjectName(u"lineEdit_folderPath")
        self.lineEdit_folderPath.setReadOnly(True)

        self.horizontalLayout_folder.addWidget(self.lineEdit_folderPath)

        self.pushButton_browse = QPushButton(Dialog)
        self.pushButton_browse.setObjectName(u"pushButton_browse")
        self.pushButton_browse.setStyleSheet(u"")
        icon = QIcon()
        icon.addFile(u":/icons/folder-open.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_browse.setIcon(icon)

        self.horizontalLayout_folder.addWidget(self.pushButton_browse)

        self.pushButton_scan = QPushButton(Dialog)
        self.pushButton_scan.setObjectName(u"pushButton_scan")
        self.pushButton_scan.setEnabled(False)
        self.pushButton_scan.setStyleSheet(u"")
        icon1 = QIcon()
        icon1.addFile(u":/icons/scan.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_scan.setIcon(icon1)

        self.horizontalLayout_folder.addWidget(self.pushButton_scan)

        self.pushButton_step1 = QPushButton(Dialog)
        self.pushButton_step1.setObjectName(u"pushButton_step1")
        self.pushButton_step1.setEnabled(False)
        self.pushButton_step1.setStyleSheet(u"")
        icon2 = QIcon()
        icon2.addFile(u":/icons/folder-search.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_step1.setIcon(icon2)

        self.horizontalLayout_folder.addWidget(self.pushButton_step1)


        self.formLayout.setLayout(0, QFormLayout.FieldRole, self.horizontalLayout_folder)


        self.verticalLayout.addLayout(self.formLayout)

        self.line_1 = QFrame(Dialog)
        self.line_1.setObjectName(u"line_1")
        self.line_1.setFrameShape(QFrame.Shape.HLine)
        self.line_1.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line_1)

        self.horizontalLayout_steps = QHBoxLayout()
        self.horizontalLayout_steps.setObjectName(u"horizontalLayout_steps")
        self.label_shovel = QLabel(Dialog)
        self.label_shovel.setObjectName(u"label_shovel")

        self.horizontalLayout_steps.addWidget(self.label_shovel)

        self.comboBox_shovel = QComboBox(Dialog)
        self.comboBox_shovel.setObjectName(u"comboBox_shovel")
        self.comboBox_shovel.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_shovel.sizePolicy().hasHeightForWidth())
        self.comboBox_shovel.setSizePolicy(sizePolicy)

        self.horizontalLayout_steps.addWidget(self.comboBox_shovel)

        self.label_result = QLabel(Dialog)
        self.label_result.setObjectName(u"label_result")

        self.horizontalLayout_steps.addWidget(self.label_result)

        self.lineEdit_result = QLineEdit(Dialog)
        self.lineEdit_result.setObjectName(u"lineEdit_result")

        self.horizontalLayout_steps.addWidget(self.lineEdit_result)

        self.pushButton_step2 = QPushButton(Dialog)
        self.pushButton_step2.setObjectName(u"pushButton_step2")
        self.pushButton_step2.setEnabled(False)
        self.pushButton_step2.setStyleSheet(u"")
        icon3 = QIcon()
        icon3.addFile(u":/icons/vector-triangle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_step2.setIcon(icon3)

        self.horizontalLayout_steps.addWidget(self.pushButton_step2)


        self.verticalLayout.addLayout(self.horizontalLayout_steps)

        self.horizontalLayout_shovel = QHBoxLayout()
        self.horizontalLayout_shovel.setObjectName(u"horizontalLayout_shovel")

        self.verticalLayout.addLayout(self.horizontalLayout_shovel)

        self.horizontalLayout_progressMeta = QHBoxLayout()
        self.horizontalLayout_progressMeta.setObjectName(u"horizontalLayout_progressMeta")
        self.label_progressStatus = QLabel(Dialog)
        self.label_progressStatus.setObjectName(u"label_progressStatus")

        self.horizontalLayout_progressMeta.addWidget(self.label_progressStatus)

        self.horizontalSpacer_progress = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_progressMeta.addItem(self.horizontalSpacer_progress)

        self.label_progressPct = QLabel(Dialog)
        self.label_progressPct.setObjectName(u"label_progressPct")

        self.horizontalLayout_progressMeta.addWidget(self.label_progressPct)


        self.verticalLayout.addLayout(self.horizontalLayout_progressMeta)

        self.progressBar = QProgressBar(Dialog)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.verticalLayout.addWidget(self.progressBar)

        self.plainTextEdit_log = QPlainTextEdit(Dialog)
        self.plainTextEdit_log.setObjectName(u"plainTextEdit_log")
        self.plainTextEdit_log.setReadOnly(True)
        self.plainTextEdit_log.setMaximumBlockCount(500)

        self.verticalLayout.addWidget(self.plainTextEdit_log)

        self.line_2 = QFrame(Dialog)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line_2)

        self.horizontalLayout_sessionsHeader = QHBoxLayout()
        self.horizontalLayout_sessionsHeader.setObjectName(u"horizontalLayout_sessionsHeader")
        self.label_sessionsInDb = QLabel(Dialog)
        self.label_sessionsInDb.setObjectName(u"label_sessionsInDb")

        self.horizontalLayout_sessionsHeader.addWidget(self.label_sessionsInDb)

        self.horizontalSpacer_sessions = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_sessionsHeader.addItem(self.horizontalSpacer_sessions)

        self.pushButton_confirmDelete = QPushButton(Dialog)
        self.pushButton_confirmDelete.setObjectName(u"pushButton_confirmDelete")
        self.pushButton_confirmDelete.setStyleSheet(u"")
        icon4 = QIcon()
        icon4.addFile(u":/icons/trash.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_confirmDelete.setIcon(icon4)

        self.horizontalLayout_sessionsHeader.addWidget(self.pushButton_confirmDelete)

        self.lineEdit_search = QLineEdit(Dialog)
        self.lineEdit_search.setObjectName(u"lineEdit_search")
        self.lineEdit_search.setMaximumSize(QSize(160, 16777215))

        self.horizontalLayout_sessionsHeader.addWidget(self.lineEdit_search)


        self.verticalLayout.addLayout(self.horizontalLayout_sessionsHeader)

        self.tableWidget_sessions = QTableWidget(Dialog)
        if (self.tableWidget_sessions.columnCount() < 7):
            self.tableWidget_sessions.setColumnCount(7)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget_sessions.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget_sessions.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_sessions.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget_sessions.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget_sessions.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget_sessions.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget_sessions.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        self.tableWidget_sessions.setObjectName(u"tableWidget_sessions")
        self.tableWidget_sessions.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget_sessions.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget_sessions.setColumnCount(7)
        self.tableWidget_sessions.horizontalHeader().setStretchLastSection(False)
        self.tableWidget_sessions.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.tableWidget_sessions)

        self.widget_confirmBar = QWidget(Dialog)
        self.widget_confirmBar.setObjectName(u"widget_confirmBar")
        self.horizontalLayout_confirmBar = QHBoxLayout(self.widget_confirmBar)
        self.horizontalLayout_confirmBar.setObjectName(u"horizontalLayout_confirmBar")

        self.verticalLayout.addWidget(self.widget_confirmBar)

        self.horizontalLayout_footer = QHBoxLayout()
        self.horizontalLayout_footer.setObjectName(u"horizontalLayout_footer")
        self.label_statusText = QLabel(Dialog)
        self.label_statusText.setObjectName(u"label_statusText")

        self.horizontalLayout_footer.addWidget(self.label_statusText)

        self.horizontalSpacer_footer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_footer.addItem(self.horizontalSpacer_footer)

        self.label_dbSummary = QLabel(Dialog)
        self.label_dbSummary.setObjectName(u"label_dbSummary")

        self.horizontalLayout_footer.addWidget(self.label_dbSummary)


        self.verticalLayout.addLayout(self.horizontalLayout_footer)

        self.horizontalLayout_buttons = QHBoxLayout()
        self.horizontalLayout_buttons.setObjectName(u"horizontalLayout_buttons")
        self.horizontalSpacer_buttons = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_buttons.addItem(self.horizontalSpacer_buttons)

        self.pushButton_close = QPushButton(Dialog)
        self.pushButton_close.setObjectName(u"pushButton_close")

        self.horizontalLayout_buttons.addWidget(self.pushButton_close)


        self.verticalLayout.addLayout(self.horizontalLayout_buttons)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Contour Difference Tool", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-weight:600;\">Contour difference tool</span></p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Select a folder", None))
        self.lineEdit_folderPath.setPlaceholderText(QCoreApplication.translate("Dialog", u"Select a folder...", None))
        self.pushButton_browse.setText(QCoreApplication.translate("Dialog", u"Browse...", None))
        self.pushButton_scan.setText(QCoreApplication.translate("Dialog", u"Scan", None))
        self.pushButton_step1.setText(QCoreApplication.translate("Dialog", u"Import DB", None))
        self.label_shovel.setText(QCoreApplication.translate("Dialog", u"Shovel: ", None))
        self.label_result.setText(QCoreApplication.translate("Dialog", u"Result Name:", None))
        self.pushButton_step2.setText(QCoreApplication.translate("Dialog", u"Diff and Write DB", None))
        self.label_progressStatus.setText(QCoreApplication.translate("Dialog", u"Ready", None))
        self.label_progressPct.setText(QCoreApplication.translate("Dialog", u"0%", None))
        self.plainTextEdit_log.setPlainText(QCoreApplication.translate("Dialog", u"Ready \u2014 browse and scan a folder, then run.", None))
        self.label_sessionsInDb.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-weight:600;\">Sessions in DB</span></p></body></html>", None))
        self.pushButton_confirmDelete.setText(QCoreApplication.translate("Dialog", u"Delete", None))
        self.lineEdit_search.setPlaceholderText(QCoreApplication.translate("Dialog", u"Search...", None))
        ___qtablewidgetitem = self.tableWidget_sessions.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Dialog", u"ID", None));
        ___qtablewidgetitem1 = self.tableWidget_sessions.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Dialog", u"Date", None));
        ___qtablewidgetitem2 = self.tableWidget_sessions.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Dialog", u"Folder", None));
        ___qtablewidgetitem3 = self.tableWidget_sessions.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Dialog", u"Rows", None));
        ___qtablewidgetitem4 = self.tableWidget_sessions.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Dialog", u"Conts.", None));
        ___qtablewidgetitem5 = self.tableWidget_sessions.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Dialog", u"Status", None));
        self.label_statusText.setText(QCoreApplication.translate("Dialog", u"Idle", None))
        self.label_dbSummary.setText("")
        self.pushButton_close.setText(QCoreApplication.translate("Dialog", u"Close", None))
    # retranslateUi


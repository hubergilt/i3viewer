# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'i3mainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QHeaderView, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QSplitter, QStatusBar, QTabWidget,
    QTableView, QToolBar, QTreeView, QWidget)

from i3viewer.i3vtkWidget import i3vtkWidget
import i3viewer.icons_rc

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")
        mainWindow.resize(1002, 666)
        icon = QIcon()
        icon.addFile(u":/icons/help.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        mainWindow.setWindowIcon(icon)
        mainWindow.setIconSize(QSize(22, 22))
        self.actionOpenFile = QAction(mainWindow)
        self.actionOpenFile.setObjectName(u"actionOpenFile")
        self.actionOpenFile.setEnabled(True)
        icon1 = QIcon()
        icon1.addFile(u":/icons/fileopen.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionOpenFile.setIcon(icon1)
        self.actionExit = QAction(mainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionHelp = QAction(mainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        self.actionHelp.setIcon(icon)
        self.actionSave = QAction(mainWindow)
        self.actionSave.setObjectName(u"actionSave")
        icon2 = QIcon()
        icon2.addFile(u":/icons/filesave.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionSave.setIcon(icon2)
        self.actionFront = QAction(mainWindow)
        self.actionFront.setObjectName(u"actionFront")
        icon3 = QIcon()
        icon3.addFile(u":/icons/front.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionFront.setIcon(icon3)
        self.actionFront.setMenuRole(QAction.NoRole)
        self.actionBack = QAction(mainWindow)
        self.actionBack.setObjectName(u"actionBack")
        icon4 = QIcon()
        icon4.addFile(u":/icons/back.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionBack.setIcon(icon4)
        self.actionBack.setMenuRole(QAction.NoRole)
        self.actionTop = QAction(mainWindow)
        self.actionTop.setObjectName(u"actionTop")
        icon5 = QIcon()
        icon5.addFile(u":/icons/top.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionTop.setIcon(icon5)
        self.actionTop.setMenuRole(QAction.NoRole)
        self.actionBottom = QAction(mainWindow)
        self.actionBottom.setObjectName(u"actionBottom")
        icon6 = QIcon()
        icon6.addFile(u":/icons/bottom.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionBottom.setIcon(icon6)
        self.actionBottom.setMenuRole(QAction.NoRole)
        self.actionLeft = QAction(mainWindow)
        self.actionLeft.setObjectName(u"actionLeft")
        icon7 = QIcon()
        icon7.addFile(u":/icons/left.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionLeft.setIcon(icon7)
        self.actionLeft.setMenuRole(QAction.NoRole)
        self.actionRight = QAction(mainWindow)
        self.actionRight.setObjectName(u"actionRight")
        icon8 = QIcon()
        icon8.addFile(u":/icons/right.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionRight.setIcon(icon8)
        self.actionRight.setMenuRole(QAction.NoRole)
        self.actionIso = QAction(mainWindow)
        self.actionIso.setObjectName(u"actionIso")
        icon9 = QIcon()
        icon9.addFile(u":/icons/iso.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionIso.setIcon(icon9)
        self.actionIso.setMenuRole(QAction.NoRole)
        self.actionFit = QAction(mainWindow)
        self.actionFit.setObjectName(u"actionFit")
        icon10 = QIcon()
        icon10.addFile(u":/icons/resize.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionFit.setIcon(icon10)
        self.actionFit.setMenuRole(QAction.NoRole)
        self.centralwidget = QWidget(mainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_3 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayout_4 = QHBoxLayout(self.tab)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.groupBoxGraph = QGroupBox(self.tab)
        self.groupBoxGraph.setObjectName(u"groupBoxGraph")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.groupBoxGraph.sizePolicy().hasHeightForWidth())
        self.groupBoxGraph.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.groupBoxGraph)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(self.groupBoxGraph)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.tableFrame = QFrame(self.splitter)
        self.tableFrame.setObjectName(u"tableFrame")
        self.horizontalLayout_2 = QHBoxLayout(self.tableFrame)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.treeView = QTreeView(self.tableFrame)
        self.treeView.setObjectName(u"treeView")

        self.horizontalLayout_2.addWidget(self.treeView)

        self.splitter.addWidget(self.tableFrame)
        self.qvtkWidget = i3vtkWidget(self.splitter)
        self.qvtkWidget.setObjectName(u"qvtkWidget")
        sizePolicy.setHeightForWidth(self.qvtkWidget.sizePolicy().hasHeightForWidth())
        self.qvtkWidget.setSizePolicy(sizePolicy)
        self.qvtkWidget.setMinimumSize(QSize(300, 300))
        self.splitter.addWidget(self.qvtkWidget)

        self.horizontalLayout.addWidget(self.splitter)


        self.horizontalLayout_4.addWidget(self.groupBoxGraph)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.horizontalLayout_5 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.tableView = QTableView(self.tab_2)
        self.tableView.setObjectName(u"tableView")

        self.horizontalLayout_5.addWidget(self.tableView)

        self.tabWidget.addTab(self.tab_2, "")

        self.horizontalLayout_3.addWidget(self.tabWidget)

        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(mainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1002, 27))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(mainWindow)
        self.statusbar.setObjectName(u"statusbar")
        mainWindow.setStatusBar(self.statusbar)
        self.mainToolBar = QToolBar(mainWindow)
        self.mainToolBar.setObjectName(u"mainToolBar")
        self.mainToolBar.setOrientation(Qt.Horizontal)
        self.mainToolBar.setIconSize(QSize(22, 22))
        mainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.mainToolBar)
        self.viewToolBar = QToolBar(mainWindow)
        self.viewToolBar.setObjectName(u"viewToolBar")
        mainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.viewToolBar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionOpenFile)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionHelp)
        self.menuFile.addAction(self.actionExit)
        self.mainToolBar.addAction(self.actionOpenFile)
        self.mainToolBar.addAction(self.actionSave)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionHelp)
        self.mainToolBar.addSeparator()
        self.viewToolBar.addAction(self.actionFront)
        self.viewToolBar.addAction(self.actionBack)
        self.viewToolBar.addAction(self.actionTop)
        self.viewToolBar.addAction(self.actionBottom)
        self.viewToolBar.addAction(self.actionLeft)
        self.viewToolBar.addAction(self.actionRight)
        self.viewToolBar.addSeparator()
        self.viewToolBar.addAction(self.actionIso)
        self.viewToolBar.addAction(self.actionFit)

        self.retranslateUi(mainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(mainWindow)
    # setupUi

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(QCoreApplication.translate("mainWindow", u"Interactive 3D Model Viewer", None))
        self.actionOpenFile.setText(QCoreApplication.translate("mainWindow", u"Open File...", None))
        self.actionExit.setText(QCoreApplication.translate("mainWindow", u"Exit", None))
        self.actionHelp.setText(QCoreApplication.translate("mainWindow", u"Help", None))
        self.actionSave.setText(QCoreApplication.translate("mainWindow", u"Save", None))
        self.actionFront.setText(QCoreApplication.translate("mainWindow", u"Front", None))
        self.actionBack.setText(QCoreApplication.translate("mainWindow", u"Back", None))
        self.actionTop.setText(QCoreApplication.translate("mainWindow", u"Top", None))
        self.actionBottom.setText(QCoreApplication.translate("mainWindow", u"Bottom", None))
        self.actionLeft.setText(QCoreApplication.translate("mainWindow", u"Left", None))
        self.actionRight.setText(QCoreApplication.translate("mainWindow", u"Right", None))
        self.actionIso.setText(QCoreApplication.translate("mainWindow", u"Iso", None))
        self.actionFit.setText(QCoreApplication.translate("mainWindow", u"Fit", None))
        self.groupBoxGraph.setTitle(QCoreApplication.translate("mainWindow", u"Views", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("mainWindow", u"Viewer", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("mainWindow", u"Table", None))
        self.menuFile.setTitle(QCoreApplication.translate("mainWindow", u"File", None))
        self.viewToolBar.setWindowTitle(QCoreApplication.translate("mainWindow", u"toolBar", None))
    # retranslateUi


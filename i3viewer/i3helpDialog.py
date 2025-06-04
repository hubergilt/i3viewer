# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'i3helpDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QHeaderView,
    QSizePolicy, QTableWidget, QTableWidgetItem, QWidget)
import i3viewer.icons_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 300)
        self.horizontalLayout = QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tableWidget = QTableWidget(Dialog)
        if (self.tableWidget.columnCount() < 1):
            self.tableWidget.setColumnCount(1)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        if (self.tableWidget.rowCount() < 25):
            self.tableWidget.setRowCount(25)
        icon = QIcon()
        icon.addFile(u":/icons/open.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setIcon(icon);
        self.tableWidget.setVerticalHeaderItem(0, __qtablewidgetitem1)
        icon1 = QIcon()
        icon1.addFile(u":/icons/plus.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setIcon(icon1);
        self.tableWidget.setVerticalHeaderItem(1, __qtablewidgetitem2)
        icon2 = QIcon()
        icon2.addFile(u":/icons/minus.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setIcon(icon2);
        self.tableWidget.setVerticalHeaderItem(2, __qtablewidgetitem3)
        icon3 = QIcon()
        icon3.addFile(u":/icons/export.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setIcon(icon3);
        self.tableWidget.setVerticalHeaderItem(3, __qtablewidgetitem4)
        icon4 = QIcon()
        icon4.addFile(u":/icons/help.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setIcon(icon4);
        self.tableWidget.setVerticalHeaderItem(4, __qtablewidgetitem5)
        icon5 = QIcon()
        icon5.addFile(u":/icons/exit.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setIcon(icon5);
        self.tableWidget.setVerticalHeaderItem(5, __qtablewidgetitem6)
        icon6 = QIcon()
        icon6.addFile(u":/icons/front.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem7 = QTableWidgetItem()
        __qtablewidgetitem7.setIcon(icon6);
        self.tableWidget.setVerticalHeaderItem(6, __qtablewidgetitem7)
        icon7 = QIcon()
        icon7.addFile(u":/icons/back.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setIcon(icon7);
        self.tableWidget.setVerticalHeaderItem(7, __qtablewidgetitem8)
        icon8 = QIcon()
        icon8.addFile(u":/icons/top.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem9 = QTableWidgetItem()
        __qtablewidgetitem9.setIcon(icon8);
        self.tableWidget.setVerticalHeaderItem(8, __qtablewidgetitem9)
        icon9 = QIcon()
        icon9.addFile(u":/icons/bottom.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem10 = QTableWidgetItem()
        __qtablewidgetitem10.setIcon(icon9);
        self.tableWidget.setVerticalHeaderItem(9, __qtablewidgetitem10)
        icon10 = QIcon()
        icon10.addFile(u":/icons/left.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem11 = QTableWidgetItem()
        __qtablewidgetitem11.setIcon(icon10);
        self.tableWidget.setVerticalHeaderItem(10, __qtablewidgetitem11)
        icon11 = QIcon()
        icon11.addFile(u":/icons/right.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem12 = QTableWidgetItem()
        __qtablewidgetitem12.setIcon(icon11);
        self.tableWidget.setVerticalHeaderItem(11, __qtablewidgetitem12)
        icon12 = QIcon()
        icon12.addFile(u":/icons/iso.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem13 = QTableWidgetItem()
        __qtablewidgetitem13.setIcon(icon12);
        self.tableWidget.setVerticalHeaderItem(12, __qtablewidgetitem13)
        icon13 = QIcon()
        icon13.addFile(u":/icons/resize.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem14 = QTableWidgetItem()
        __qtablewidgetitem14.setIcon(icon13);
        self.tableWidget.setVerticalHeaderItem(13, __qtablewidgetitem14)
        icon14 = QIcon()
        icon14.addFile(u":/icons/heatmapcfg.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem15 = QTableWidgetItem()
        __qtablewidgetitem15.setIcon(icon14);
        self.tableWidget.setVerticalHeaderItem(14, __qtablewidgetitem15)
        icon15 = QIcon()
        icon15.addFile(u":/icons/heatmap.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem16 = QTableWidgetItem()
        __qtablewidgetitem16.setIcon(icon15);
        self.tableWidget.setVerticalHeaderItem(15, __qtablewidgetitem16)
        icon16 = QIcon()
        icon16.addFile(u":/icons/backward.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem17 = QTableWidgetItem()
        __qtablewidgetitem17.setIcon(icon16);
        self.tableWidget.setVerticalHeaderItem(16, __qtablewidgetitem17)
        icon17 = QIcon()
        icon17.addFile(u":/icons/forward.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem18 = QTableWidgetItem()
        __qtablewidgetitem18.setIcon(icon17);
        self.tableWidget.setVerticalHeaderItem(17, __qtablewidgetitem18)
        icon18 = QIcon()
        icon18.addFile(u":/icons/unpick.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem19 = QTableWidgetItem()
        __qtablewidgetitem19.setIcon(icon18);
        self.tableWidget.setVerticalHeaderItem(18, __qtablewidgetitem19)
        icon19 = QIcon()
        icon19.addFile(u":/icons/polyabc.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem20 = QTableWidgetItem()
        __qtablewidgetitem20.setIcon(icon19);
        self.tableWidget.setVerticalHeaderItem(19, __qtablewidgetitem20)
        icon20 = QIcon()
        icon20.addFile(u":/icons/pointabc.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem21 = QTableWidgetItem()
        __qtablewidgetitem21.setIcon(icon20);
        self.tableWidget.setVerticalHeaderItem(20, __qtablewidgetitem21)
        icon21 = QIcon()
        icon21.addFile(u":/icons/contour.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem22 = QTableWidgetItem()
        __qtablewidgetitem22.setIcon(icon21);
        self.tableWidget.setVerticalHeaderItem(21, __qtablewidgetitem22)
        icon22 = QIcon()
        icon22.addFile(u":/icons/surface.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem23 = QTableWidgetItem()
        __qtablewidgetitem23.setIcon(icon22);
        self.tableWidget.setVerticalHeaderItem(22, __qtablewidgetitem23)
        icon23 = QIcon()
        icon23.addFile(u":/icons/wireframe.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem24 = QTableWidgetItem()
        __qtablewidgetitem24.setIcon(icon23);
        self.tableWidget.setVerticalHeaderItem(23, __qtablewidgetitem24)
        icon24 = QIcon()
        icon24.addFile(u":/icons/surfacecfg.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem25 = QTableWidgetItem()
        __qtablewidgetitem25.setIcon(icon24);
        self.tableWidget.setVerticalHeaderItem(24, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        __qtablewidgetitem26.setTextAlignment(Qt.AlignJustify|Qt.AlignVCenter);
        self.tableWidget.setItem(0, 0, __qtablewidgetitem26)
        __qtablewidgetitem27 = QTableWidgetItem()
        self.tableWidget.setItem(1, 0, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        self.tableWidget.setItem(2, 0, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        self.tableWidget.setItem(3, 0, __qtablewidgetitem29)
        __qtablewidgetitem30 = QTableWidgetItem()
        self.tableWidget.setItem(4, 0, __qtablewidgetitem30)
        __qtablewidgetitem31 = QTableWidgetItem()
        self.tableWidget.setItem(5, 0, __qtablewidgetitem31)
        __qtablewidgetitem32 = QTableWidgetItem()
        self.tableWidget.setItem(6, 0, __qtablewidgetitem32)
        __qtablewidgetitem33 = QTableWidgetItem()
        self.tableWidget.setItem(7, 0, __qtablewidgetitem33)
        __qtablewidgetitem34 = QTableWidgetItem()
        self.tableWidget.setItem(8, 0, __qtablewidgetitem34)
        __qtablewidgetitem35 = QTableWidgetItem()
        self.tableWidget.setItem(9, 0, __qtablewidgetitem35)
        __qtablewidgetitem36 = QTableWidgetItem()
        self.tableWidget.setItem(10, 0, __qtablewidgetitem36)
        __qtablewidgetitem37 = QTableWidgetItem()
        self.tableWidget.setItem(11, 0, __qtablewidgetitem37)
        __qtablewidgetitem38 = QTableWidgetItem()
        self.tableWidget.setItem(12, 0, __qtablewidgetitem38)
        __qtablewidgetitem39 = QTableWidgetItem()
        self.tableWidget.setItem(13, 0, __qtablewidgetitem39)
        __qtablewidgetitem40 = QTableWidgetItem()
        self.tableWidget.setItem(14, 0, __qtablewidgetitem40)
        __qtablewidgetitem41 = QTableWidgetItem()
        self.tableWidget.setItem(15, 0, __qtablewidgetitem41)
        __qtablewidgetitem42 = QTableWidgetItem()
        self.tableWidget.setItem(16, 0, __qtablewidgetitem42)
        __qtablewidgetitem43 = QTableWidgetItem()
        self.tableWidget.setItem(17, 0, __qtablewidgetitem43)
        __qtablewidgetitem44 = QTableWidgetItem()
        self.tableWidget.setItem(18, 0, __qtablewidgetitem44)
        __qtablewidgetitem45 = QTableWidgetItem()
        self.tableWidget.setItem(19, 0, __qtablewidgetitem45)
        __qtablewidgetitem46 = QTableWidgetItem()
        self.tableWidget.setItem(20, 0, __qtablewidgetitem46)
        __qtablewidgetitem47 = QTableWidgetItem()
        self.tableWidget.setItem(21, 0, __qtablewidgetitem47)
        __qtablewidgetitem48 = QTableWidgetItem()
        self.tableWidget.setItem(22, 0, __qtablewidgetitem48)
        __qtablewidgetitem49 = QTableWidgetItem()
        self.tableWidget.setItem(23, 0, __qtablewidgetitem49)
        __qtablewidgetitem50 = QTableWidgetItem()
        self.tableWidget.setItem(24, 0, __qtablewidgetitem50)
        self.tableWidget.setObjectName(u"tableWidget")

        self.horizontalLayout.addWidget(self.tableWidget)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Dialog", u"Help icon and a description of how to use each tool", None));

        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        ___qtablewidgetitem1 = self.tableWidget.item(0, 0)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Dialog", u"Use to open a new file (e.g., XYZ and CSV for polylines, SRG for nodes, XYZS for surfaces, and DB for all formats).", None));
        ___qtablewidgetitem2 = self.tableWidget.item(1, 0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Dialog", u"Append a file (e.g., XYZ and CSV for polylines, SRG for nodes, and XYZS for surface formats) to an existing open file.", None));
        ___qtablewidgetitem3 = self.tableWidget.item(2, 0)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Dialog", u"Close all opened files and clean the viewer and tables for the current workspace for all supported format files.", None));
        ___qtablewidgetitem4 = self.tableWidget.item(3, 0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Dialog", u"Export the opened files (e.g., XYZ and CSV for polylines, SRG for nodes, and XYZS for surfaces formats) to DB for the database.", None));
        ___qtablewidgetitem5 = self.tableWidget.item(4, 0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Dialog", u"Use it to open this current help window.", None));
        ___qtablewidgetitem6 = self.tableWidget.item(5, 0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("Dialog", u"Exit the current interactive 3D Model Viewer application instance.", None));
        ___qtablewidgetitem7 = self.tableWidget.item(6, 0)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("Dialog", u"Use to show the front perspective of the current viewer instance.", None));
        ___qtablewidgetitem8 = self.tableWidget.item(7, 0)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("Dialog", u"Use to show the back perspective of the current viewer instance.", None));
        ___qtablewidgetitem9 = self.tableWidget.item(8, 0)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("Dialog", u"Use to show the top perspective of the current viewer instance.", None));
        ___qtablewidgetitem10 = self.tableWidget.item(9, 0)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("Dialog", u"Use to show the bottom perspective of the current viewer instance.", None));
        ___qtablewidgetitem11 = self.tableWidget.item(10, 0)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("Dialog", u"Use to show the left perspective of the current viewer instance.", None));
        ___qtablewidgetitem12 = self.tableWidget.item(11, 0)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("Dialog", u"Use to show the right perspective of the current viewer instance.", None));
        ___qtablewidgetitem13 = self.tableWidget.item(12, 0)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("Dialog", u"Use to show the ISO perspective of the current viewer instance.", None));
        ___qtablewidgetitem14 = self.tableWidget.item(13, 0)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("Dialog", u"Use it to fit the current polylines and points extension on the viewer instance.", None));
        ___qtablewidgetitem15 = self.tableWidget.item(14, 0)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("Dialog", u"Open the Configure Heatmap dialog to import the routes TXT file and the tonnes CSV file into the database.", None));
        ___qtablewidgetitem16 = self.tableWidget.item(15, 0)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("Dialog", u"Active the heatmap tool showing the initial view at period 01 using the rainbow color palette.", None));
        ___qtablewidgetitem17 = self.tableWidget.item(16, 0)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("Dialog", u"Backward the current heatmap view to the previous one view if it is the first period then it shows the last period.", None));
        ___qtablewidgetitem18 = self.tableWidget.item(17, 0)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("Dialog", u"Forward the current heatmap view to the next one view if it is the last period then it shows the first period.", None));
        ___qtablewidgetitem19 = self.tableWidget.item(18, 0)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("Dialog", u"Disable the default selection mode to pick polylines and points Dialogs that helps to navigate in the current view.", None));
        ___qtablewidgetitem20 = self.tableWidget.item(19, 0)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("Dialog", u"Active or Disable the current label text for the polylines with the polyline name or route name with the tonnes value.", None));
        ___qtablewidgetitem21 = self.tableWidget.item(20, 0)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("Dialog", u"Active or Disable the current label text for the points with the point name in the current view.", None));
        ___qtablewidgetitem22 = self.tableWidget.item(21, 0)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("Dialog", u"Active or Disable the current contour lines in the current view.", None));
        ___qtablewidgetitem23 = self.tableWidget.item(22, 0)
        ___qtablewidgetitem23.setText(QCoreApplication.translate("Dialog", u"Active or Disable the current surface reconstruction in the current view.", None));
        ___qtablewidgetitem24 = self.tableWidget.item(23, 0)
        ___qtablewidgetitem24.setText(QCoreApplication.translate("Dialog", u"Active or Disable the current wireframe reconstruction in the current view.", None));
        ___qtablewidgetitem25 = self.tableWidget.item(24, 0)
        ___qtablewidgetitem25.setText(QCoreApplication.translate("Dialog", u"Custom the values (e.g. Color,Width, and etc.) for the contour lines, surface, wireframes reconstruction in the current view.", None));
        self.tableWidget.setSortingEnabled(__sortingEnabled)

    # retranslateUi


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
        if (self.tableWidget.rowCount() < 15):
            self.tableWidget.setRowCount(15)
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
        icon14.addFile(u":/icons/heatmap.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        __qtablewidgetitem15 = QTableWidgetItem()
        __qtablewidgetitem15.setIcon(icon14);
        self.tableWidget.setVerticalHeaderItem(14, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        __qtablewidgetitem16.setTextAlignment(Qt.AlignJustify|Qt.AlignVCenter);
        self.tableWidget.setItem(0, 0, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tableWidget.setItem(1, 0, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.tableWidget.setItem(2, 0, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.tableWidget.setItem(3, 0, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        self.tableWidget.setItem(4, 0, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        self.tableWidget.setItem(5, 0, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        self.tableWidget.setItem(6, 0, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        self.tableWidget.setItem(7, 0, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        self.tableWidget.setItem(8, 0, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        self.tableWidget.setItem(9, 0, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        self.tableWidget.setItem(10, 0, __qtablewidgetitem26)
        __qtablewidgetitem27 = QTableWidgetItem()
        self.tableWidget.setItem(11, 0, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        self.tableWidget.setItem(12, 0, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        self.tableWidget.setItem(13, 0, __qtablewidgetitem29)
        __qtablewidgetitem30 = QTableWidgetItem()
        self.tableWidget.setItem(14, 0, __qtablewidgetitem30)
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
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Dialog", u"Use to open a new file (e.g., xyz, srg, and db formats).", None));
        ___qtablewidgetitem2 = self.tableWidget.item(1, 0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Dialog", u"Append a file (e.g., XYZ and SRG formats) to an existing open file.", None));
        ___qtablewidgetitem3 = self.tableWidget.item(2, 0)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Dialog", u"Close all opened files and clean the viewer and tables.", None));
        ___qtablewidgetitem4 = self.tableWidget.item(3, 0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Dialog", u"Export the opened files (e.g., XYZ and SRG formats) to a database file.", None));
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
        ___qtablewidgetitem15.setText(QCoreApplication.translate("Dialog", u"Show a heatmap of the current database polylines loaded using the rainbow color palette.", None));
        self.tableWidget.setSortingEnabled(__sortingEnabled)

    # retranslateUi


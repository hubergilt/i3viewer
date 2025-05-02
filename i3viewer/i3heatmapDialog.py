# -*- coding: utf-8 -*-

################################################################################
# Form generated from reading UI file 'i3heatmapDialog.ui'
##
# Created by: Qt User Interface Compiler version 6.8.2
##
# WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect, QSize, Qt,
                            QTime, QUrl)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
                           QFontDatabase, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette,
                           QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout,
                               QLabel, QPushButton, QSizePolicy, QVBoxLayout,
                               QWidget)

import i3viewer.icons_rc


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(400, 191)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName("label")

        self.verticalLayout.addWidget(self.label)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName("label_2")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.pushButton = QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setStyleSheet("")
        icon = QIcon()
        icon.addFile(":/icons/cross.svg", QSize(),
                     QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton.setIcon(icon)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.pushButton)

        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName("label_3")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_3)

        self.pushButton_2 = QPushButton(Dialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setStyleSheet("")
        self.pushButton_2.setIcon(icon)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.pushButton_2)

        self.verticalLayout.addLayout(self.formLayout)

        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName("label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_4 = QPushButton(Dialog)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setStyleSheet("")
        self.pushButton_4.setIcon(icon)

        self.horizontalLayout.addWidget(self.pushButton_4)

        self.pushButton_3 = QPushButton(Dialog)
        self.pushButton_3.setObjectName("pushButton_3")

        self.horizontalLayout.addWidget(self.pushButton_3)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(
            QCoreApplication.translate("Dialog", "Dialog", None))
        self.label.setText(
            QCoreApplication.translate(
                "Dialog", "Import configuration files into the database:", None
            )
        )
        self.label_2.setText(
            QCoreApplication.translate(
                "Dialog", "Select routes file (*.txt)", None)
        )
        self.pushButton.setText(
            QCoreApplication.translate(
                "Dialog", "Import routes table...", None)
        )
        self.label_3.setText(
            QCoreApplication.translate(
                "Dialog", "Select tonnes file (*.csv)", None)
        )
        self.pushButton_2.setText(
            QCoreApplication.translate(
                "Dialog", "Import tonnes table...", None)
        )
        self.label_4.setText(
            QCoreApplication.translate(
                "Dialog", "Note: don't use headers in configuration files", None
            )
        )
        self.pushButton_4.setText(
            QCoreApplication.translate("Dialog", "Load Configuration", None)
        )
        self.pushButton_3.setText(
            QCoreApplication.translate("Dialog", "Cancel", None))

    # retranslateUi

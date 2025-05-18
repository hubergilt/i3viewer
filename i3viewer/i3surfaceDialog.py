# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'i3surfaceDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QComboBox, QDialog,
    QFrame, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QSizePolicy, QSlider,
    QTabWidget, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(467, 577)
        self.verticalLayout_2 = QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.West)
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_10 = QVBoxLayout(self.tab_3)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label = QLabel(self.tab_3)
        self.label.setObjectName(u"label")

        self.verticalLayout_10.addWidget(self.label)

        self.frame_15 = QFrame(self.tab_3)
        self.frame_15.setObjectName(u"frame_15")
        self.frame_15.setFrameShape(QFrame.StyledPanel)
        self.frame_15.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frame_15)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.groupBox = QGroupBox(self.frame_15)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_12 = QVBoxLayout(self.groupBox)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.frame = QFrame(self.groupBox)
        self.frame.setObjectName(u"frame")
        self.horizontalLayout_20 = QHBoxLayout(self.frame)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.radioButtonRandom = QRadioButton(self.frame)
        self.buttonGroup = QButtonGroup(Dialog)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radioButtonRandom)
        self.radioButtonRandom.setObjectName(u"radioButtonRandom")

        self.horizontalLayout_20.addWidget(self.radioButtonRandom)

        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.frameSurface = QFrame(self.frame)
        self.frameSurface.setObjectName(u"frameSurface")
        self.frameSurface.setFrameShape(QFrame.StyledPanel)
        self.frameSurface.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frameSurface)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelSurface = QLabel(self.frameSurface)
        self.labelSurface.setObjectName(u"labelSurface")

        self.horizontalLayout_2.addWidget(self.labelSurface)


        self.verticalLayout_16.addWidget(self.frameSurface)


        self.horizontalLayout_20.addLayout(self.verticalLayout_16)

        self.pushButtonSurface = QPushButton(self.frame)
        self.pushButtonSurface.setObjectName(u"pushButtonSurface")

        self.horizontalLayout_20.addWidget(self.pushButtonSurface)


        self.verticalLayout_12.addWidget(self.frame)

        self.frame_11 = QFrame(self.groupBox)
        self.frame_11.setObjectName(u"frame_11")
        self.horizontalLayout_11 = QHBoxLayout(self.frame_11)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.radioButtonCustom = QRadioButton(self.frame_11)
        self.buttonGroup.addButton(self.radioButtonCustom)
        self.radioButtonCustom.setObjectName(u"radioButtonCustom")

        self.horizontalLayout_11.addWidget(self.radioButtonCustom)

        self.verticalLayout_17 = QVBoxLayout()
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.frameWireframe = QFrame(self.frame_11)
        self.frameWireframe.setObjectName(u"frameWireframe")
        self.frameWireframe.setFrameShape(QFrame.StyledPanel)
        self.frameWireframe.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.frameWireframe)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.labelWireframe = QLabel(self.frameWireframe)
        self.labelWireframe.setObjectName(u"labelWireframe")

        self.horizontalLayout_12.addWidget(self.labelWireframe)


        self.verticalLayout_17.addWidget(self.frameWireframe)


        self.horizontalLayout_11.addLayout(self.verticalLayout_17)

        self.pushButtonWireframe = QPushButton(self.frame_11)
        self.pushButtonWireframe.setObjectName(u"pushButtonWireframe")

        self.horizontalLayout_11.addWidget(self.pushButtonWireframe)


        self.verticalLayout_12.addWidget(self.frame_11)


        self.verticalLayout_9.addWidget(self.groupBox)

        self.groupBox_3 = QGroupBox(self.frame_15)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_13 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.horizontalSliderOpacity = QSlider(self.groupBox_3)
        self.horizontalSliderOpacity.setObjectName(u"horizontalSliderOpacity")
        self.horizontalSliderOpacity.setMinimum(0)
        self.horizontalSliderOpacity.setMaximum(100)
        self.horizontalSliderOpacity.setSingleStep(10)
        self.horizontalSliderOpacity.setPageStep(10)
        self.horizontalSliderOpacity.setOrientation(Qt.Horizontal)
        self.horizontalSliderOpacity.setTickPosition(QSlider.TicksBelow)

        self.verticalLayout_13.addWidget(self.horizontalSliderOpacity)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.labelOpacityMin = QLabel(self.groupBox_3)
        self.labelOpacityMin.setObjectName(u"labelOpacityMin")

        self.horizontalLayout_4.addWidget(self.labelOpacityMin)

        self.labelOpacityValue = QLabel(self.groupBox_3)
        self.labelOpacityValue.setObjectName(u"labelOpacityValue")

        self.horizontalLayout_4.addWidget(self.labelOpacityValue, 0, Qt.AlignHCenter)

        self.labelOpacityMax = QLabel(self.groupBox_3)
        self.labelOpacityMax.setObjectName(u"labelOpacityMax")

        self.horizontalLayout_4.addWidget(self.labelOpacityMax, 0, Qt.AlignRight)


        self.verticalLayout_13.addLayout(self.horizontalLayout_4)


        self.verticalLayout_9.addWidget(self.groupBox_3)

        self.groupBox_4 = QGroupBox(self.frame_15)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalSliderThickness = QSlider(self.groupBox_4)
        self.horizontalSliderThickness.setObjectName(u"horizontalSliderThickness")
        self.horizontalSliderThickness.setMinimum(1)
        self.horizontalSliderThickness.setMaximum(10)
        self.horizontalSliderThickness.setPageStep(1)
        self.horizontalSliderThickness.setOrientation(Qt.Horizontal)
        self.horizontalSliderThickness.setTickPosition(QSlider.TicksBelow)

        self.verticalLayout_3.addWidget(self.horizontalSliderThickness)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.labelThicknessMin = QLabel(self.groupBox_4)
        self.labelThicknessMin.setObjectName(u"labelThicknessMin")

        self.horizontalLayout_5.addWidget(self.labelThicknessMin)

        self.labelThicknessValue = QLabel(self.groupBox_4)
        self.labelThicknessValue.setObjectName(u"labelThicknessValue")

        self.horizontalLayout_5.addWidget(self.labelThicknessValue, 0, Qt.AlignHCenter)

        self.labelThicknessMax = QLabel(self.groupBox_4)
        self.labelThicknessMax.setObjectName(u"labelThicknessMax")

        self.horizontalLayout_5.addWidget(self.labelThicknessMax, 0, Qt.AlignRight)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)


        self.verticalLayout_9.addWidget(self.groupBox_4)


        self.verticalLayout_10.addWidget(self.frame_15)

        self.label_3 = QLabel(self.tab_3)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_10.addWidget(self.label_3)

        self.label_4 = QLabel(self.tab_3)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_10.addWidget(self.label_4)

        self.label_2 = QLabel(self.tab_3)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_10.addWidget(self.label_2)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.verticalLayout_11 = QVBoxLayout(self.tab_4)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.label_12 = QLabel(self.tab_4)
        self.label_12.setObjectName(u"label_12")

        self.verticalLayout_11.addWidget(self.label_12)

        self.frame_13 = QFrame(self.tab_4)
        self.frame_13.setObjectName(u"frame_13")
        self.frame_13.setFrameShape(QFrame.StyledPanel)
        self.frame_13.setFrameShadow(QFrame.Raised)
        self.verticalLayout_14 = QVBoxLayout(self.frame_13)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.label_38 = QLabel(self.frame_13)
        self.label_38.setObjectName(u"label_38")

        self.horizontalLayout_13.addWidget(self.label_38)

        self.comboBoxProfile = QComboBox(self.frame_13)
        self.comboBoxProfile.addItem("")
        self.comboBoxProfile.addItem("")
        self.comboBoxProfile.addItem("")
        self.comboBoxProfile.addItem("")
        self.comboBoxProfile.addItem("")
        self.comboBoxProfile.setObjectName(u"comboBoxProfile")

        self.horizontalLayout_13.addWidget(self.comboBoxProfile)


        self.verticalLayout_14.addLayout(self.horizontalLayout_13)

        self.frame_2 = QFrame(self.frame_13)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_13 = QLabel(self.frame_2)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout.addWidget(self.label_13)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalSliderCTolerance = QSlider(self.frame_2)
        self.horizontalSliderCTolerance.setObjectName(u"horizontalSliderCTolerance")
        self.horizontalSliderCTolerance.setMinimum(10)
        self.horizontalSliderCTolerance.setMaximum(10000)
        self.horizontalSliderCTolerance.setSingleStep(100)
        self.horizontalSliderCTolerance.setPageStep(1000)
        self.horizontalSliderCTolerance.setOrientation(Qt.Horizontal)
        self.horizontalSliderCTolerance.setTickPosition(QSlider.TicksBelow)

        self.verticalLayout.addWidget(self.horizontalSliderCTolerance)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.labelCToleranceMin = QLabel(self.frame_2)
        self.labelCToleranceMin.setObjectName(u"labelCToleranceMin")

        self.horizontalLayout_6.addWidget(self.labelCToleranceMin)

        self.labelCToleranceValue = QLabel(self.frame_2)
        self.labelCToleranceValue.setObjectName(u"labelCToleranceValue")

        self.horizontalLayout_6.addWidget(self.labelCToleranceValue, 0, Qt.AlignHCenter)

        self.labelCToleranceMax = QLabel(self.frame_2)
        self.labelCToleranceMax.setObjectName(u"labelCToleranceMax")

        self.horizontalLayout_6.addWidget(self.labelCToleranceMax, 0, Qt.AlignRight)


        self.verticalLayout.addLayout(self.horizontalLayout_6)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.verticalLayout_14.addWidget(self.frame_2)

        self.frame_6 = QFrame(self.frame_13)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_14 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_17 = QLabel(self.frame_6)
        self.label_17.setObjectName(u"label_17")

        self.horizontalLayout_14.addWidget(self.label_17)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalSliderDAlpha = QSlider(self.frame_6)
        self.horizontalSliderDAlpha.setObjectName(u"horizontalSliderDAlpha")
        self.horizontalSliderDAlpha.setMaximum(100)
        self.horizontalSliderDAlpha.setOrientation(Qt.Horizontal)
        self.horizontalSliderDAlpha.setTickPosition(QSlider.TicksBelow)

        self.verticalLayout_5.addWidget(self.horizontalSliderDAlpha)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.labelDAlphaMin = QLabel(self.frame_6)
        self.labelDAlphaMin.setObjectName(u"labelDAlphaMin")

        self.horizontalLayout_7.addWidget(self.labelDAlphaMin)

        self.labelDAlphaValue = QLabel(self.frame_6)
        self.labelDAlphaValue.setObjectName(u"labelDAlphaValue")

        self.horizontalLayout_7.addWidget(self.labelDAlphaValue, 0, Qt.AlignHCenter)

        self.labelDAlphaMax = QLabel(self.frame_6)
        self.labelDAlphaMax.setObjectName(u"labelDAlphaMax")

        self.horizontalLayout_7.addWidget(self.labelDAlphaMax, 0, Qt.AlignRight)


        self.verticalLayout_5.addLayout(self.horizontalLayout_7)


        self.horizontalLayout_14.addLayout(self.verticalLayout_5)


        self.verticalLayout_14.addWidget(self.frame_6)

        self.frame_7 = QFrame(self.frame_13)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_15 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label_21 = QLabel(self.frame_7)
        self.label_21.setObjectName(u"label_21")

        self.horizontalLayout_15.addWidget(self.label_21)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalSliderDTolerance = QSlider(self.frame_7)
        self.horizontalSliderDTolerance.setObjectName(u"horizontalSliderDTolerance")
        self.horizontalSliderDTolerance.setMinimum(10)
        self.horizontalSliderDTolerance.setMaximum(10000)
        self.horizontalSliderDTolerance.setSingleStep(100)
        self.horizontalSliderDTolerance.setPageStep(1000)
        self.horizontalSliderDTolerance.setOrientation(Qt.Horizontal)
        self.horizontalSliderDTolerance.setTickPosition(QSlider.TicksBelow)

        self.verticalLayout_4.addWidget(self.horizontalSliderDTolerance)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.labelDToleranceMin = QLabel(self.frame_7)
        self.labelDToleranceMin.setObjectName(u"labelDToleranceMin")

        self.horizontalLayout_8.addWidget(self.labelDToleranceMin)

        self.labelDToleranceValue = QLabel(self.frame_7)
        self.labelDToleranceValue.setObjectName(u"labelDToleranceValue")

        self.horizontalLayout_8.addWidget(self.labelDToleranceValue, 0, Qt.AlignHCenter)

        self.labelDToleranceMax = QLabel(self.frame_7)
        self.labelDToleranceMax.setObjectName(u"labelDToleranceMax")

        self.horizontalLayout_8.addWidget(self.labelDToleranceMax, 0, Qt.AlignRight)


        self.verticalLayout_4.addLayout(self.horizontalLayout_8)


        self.horizontalLayout_15.addLayout(self.verticalLayout_4)


        self.verticalLayout_14.addWidget(self.frame_7)

        self.frame_8 = QFrame(self.frame_13)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_16 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.label_22 = QLabel(self.frame_8)
        self.label_22.setObjectName(u"label_22")

        self.horizontalLayout_16.addWidget(self.label_22)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalSliderDOffset = QSlider(self.frame_8)
        self.horizontalSliderDOffset.setObjectName(u"horizontalSliderDOffset")
        self.horizontalSliderDOffset.setMinimum(1)
        self.horizontalSliderDOffset.setMaximum(20)
        self.horizontalSliderDOffset.setPageStep(2)
        self.horizontalSliderDOffset.setOrientation(Qt.Horizontal)
        self.horizontalSliderDOffset.setTickPosition(QSlider.TicksBelow)

        self.verticalLayout_6.addWidget(self.horizontalSliderDOffset)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.labelDOffsetMin = QLabel(self.frame_8)
        self.labelDOffsetMin.setObjectName(u"labelDOffsetMin")

        self.horizontalLayout_9.addWidget(self.labelDOffsetMin)

        self.labelDOffsetValue = QLabel(self.frame_8)
        self.labelDOffsetValue.setObjectName(u"labelDOffsetValue")

        self.horizontalLayout_9.addWidget(self.labelDOffsetValue)

        self.labelDOffsetMax = QLabel(self.frame_8)
        self.labelDOffsetMax.setObjectName(u"labelDOffsetMax")

        self.horizontalLayout_9.addWidget(self.labelDOffsetMax, 0, Qt.AlignRight)


        self.verticalLayout_6.addLayout(self.horizontalLayout_9)


        self.horizontalLayout_16.addLayout(self.verticalLayout_6)


        self.verticalLayout_14.addWidget(self.frame_8)

        self.frame_9 = QFrame(self.frame_13)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setFrameShape(QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_17 = QHBoxLayout(self.frame_9)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.label_23 = QLabel(self.frame_9)
        self.label_23.setObjectName(u"label_23")

        self.horizontalLayout_17.addWidget(self.label_23)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalSliderFAngle = QSlider(self.frame_9)
        self.horizontalSliderFAngle.setObjectName(u"horizontalSliderFAngle")
        self.horizontalSliderFAngle.setMaximum(180)
        self.horizontalSliderFAngle.setPageStep(20)
        self.horizontalSliderFAngle.setOrientation(Qt.Horizontal)
        self.horizontalSliderFAngle.setTickPosition(QSlider.TicksBelow)

        self.verticalLayout_7.addWidget(self.horizontalSliderFAngle)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.labelFAngleMin = QLabel(self.frame_9)
        self.labelFAngleMin.setObjectName(u"labelFAngleMin")

        self.horizontalLayout_10.addWidget(self.labelFAngleMin)

        self.labelFAngleValue = QLabel(self.frame_9)
        self.labelFAngleValue.setObjectName(u"labelFAngleValue")

        self.horizontalLayout_10.addWidget(self.labelFAngleValue, 0, Qt.AlignHCenter)

        self.labelFAngleMax = QLabel(self.frame_9)
        self.labelFAngleMax.setObjectName(u"labelFAngleMax")

        self.horizontalLayout_10.addWidget(self.labelFAngleMax, 0, Qt.AlignRight)


        self.verticalLayout_7.addLayout(self.horizontalLayout_10)


        self.horizontalLayout_17.addLayout(self.verticalLayout_7)


        self.verticalLayout_14.addWidget(self.frame_9)


        self.verticalLayout_11.addWidget(self.frame_13)

        self.frame_14 = QFrame(self.tab_4)
        self.frame_14.setObjectName(u"frame_14")
        self.frame_14.setFrameShape(QFrame.StyledPanel)
        self.frame_14.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_18 = QHBoxLayout(self.frame_14)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.comboBoxPlane = QComboBox(self.frame_14)
        self.comboBoxPlane.addItem("")
        self.comboBoxPlane.addItem("")
        self.comboBoxPlane.addItem("")
        self.comboBoxPlane.addItem("")
        self.comboBoxPlane.setObjectName(u"comboBoxPlane")

        self.horizontalLayout_18.addWidget(self.comboBoxPlane)

        self.label_37 = QLabel(self.frame_14)
        self.label_37.setObjectName(u"label_37")

        self.horizontalLayout_18.addWidget(self.label_37)


        self.verticalLayout_11.addWidget(self.frame_14)

        self.tabWidget.addTab(self.tab_4, "")

        self.verticalLayout_2.addWidget(self.tabWidget)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pushButton_4 = QPushButton(Dialog)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.horizontalLayout_3.addWidget(self.pushButton_4)

        self.pushButton_3 = QPushButton(Dialog)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout_3.addWidget(self.pushButton_3)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)


        self.retranslateUi(Dialog)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-weight:600;\">Configure Appearance Surface Parameters:</span></p></body></html>", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"Surface and Wireframe Colors:", None))
        self.radioButtonRandom.setText(QCoreApplication.translate("Dialog", u"Random", None))
        self.labelSurface.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.pushButtonSurface.setText(QCoreApplication.translate("Dialog", u"Suraface Color...    ", None))
        self.radioButtonCustom.setText(QCoreApplication.translate("Dialog", u"Custom", None))
        self.labelWireframe.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.pushButtonWireframe.setText(QCoreApplication.translate("Dialog", u"Wireframe Color...", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Dialog", u"Surface Opacity:", None))
        self.labelOpacityMin.setText(QCoreApplication.translate("Dialog", u"min:0", None))
        self.labelOpacityValue.setText(QCoreApplication.translate("Dialog", u"value:50", None))
        self.labelOpacityMax.setText(QCoreApplication.translate("Dialog", u"max:100", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("Dialog", u"Edge Thickness:", None))
        self.labelThicknessMin.setText(QCoreApplication.translate("Dialog", u"min:0", None))
        self.labelThicknessValue.setText(QCoreApplication.translate("Dialog", u"value:50", None))
        self.labelThicknessMax.setText(QCoreApplication.translate("Dialog", u"max:100", None))
        self.label_3.setText("")
        self.label_4.setText("")
        self.label_2.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("Dialog", u"Surface Appearance", None))
        self.label_12.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-weight:600;\">Configure Delaunay Surface Reconstruction Parameters:</span></p></body></html>", None))
        self.label_38.setText(QCoreApplication.translate("Dialog", u"Profiles:", None))
        self.comboBoxProfile.setItemText(0, QCoreApplication.translate("Dialog", u"High Resolution", None))
        self.comboBoxProfile.setItemText(1, QCoreApplication.translate("Dialog", u"Typical Gis", None))
        self.comboBoxProfile.setItemText(2, QCoreApplication.translate("Dialog", u"Noisy Data", None))
        self.comboBoxProfile.setItemText(3, QCoreApplication.translate("Dialog", u"Contour Preserving", None))
        self.comboBoxProfile.setItemText(4, QCoreApplication.translate("Dialog", u"Custom", None))

        self.label_13.setText(QCoreApplication.translate("Dialog", u"Cleaner Tolerance:      ", None))
        self.labelCToleranceMin.setText(QCoreApplication.translate("Dialog", u"min:0", None))
        self.labelCToleranceValue.setText(QCoreApplication.translate("Dialog", u"value:50", None))
        self.labelCToleranceMax.setText(QCoreApplication.translate("Dialog", u"max:100", None))
        self.label_17.setText(QCoreApplication.translate("Dialog", u"Delaunay's Alpha:        ", None))
        self.labelDAlphaMin.setText(QCoreApplication.translate("Dialog", u"min:0", None))
        self.labelDAlphaValue.setText(QCoreApplication.translate("Dialog", u"value:50", None))
        self.labelDAlphaMax.setText(QCoreApplication.translate("Dialog", u"max:100", None))
        self.label_21.setText(QCoreApplication.translate("Dialog", u"Delaunay's Tolerance:", None))
        self.labelDToleranceMin.setText(QCoreApplication.translate("Dialog", u"min:0", None))
        self.labelDToleranceValue.setText(QCoreApplication.translate("Dialog", u"value:50", None))
        self.labelDToleranceMax.setText(QCoreApplication.translate("Dialog", u"max:100", None))
        self.label_22.setText(QCoreApplication.translate("Dialog", u"Delaunay's Offset:       ", None))
        self.labelDOffsetMin.setText(QCoreApplication.translate("Dialog", u"min:0", None))
        self.labelDOffsetValue.setText(QCoreApplication.translate("Dialog", u"value:50", None))
        self.labelDOffsetMax.setText(QCoreApplication.translate("Dialog", u"max:100", None))
        self.label_23.setText(QCoreApplication.translate("Dialog", u"Feature's Angle:           ", None))
        self.labelFAngleMin.setText(QCoreApplication.translate("Dialog", u"min:0", None))
        self.labelFAngleValue.setText(QCoreApplication.translate("Dialog", u"value:50", None))
        self.labelFAngleMax.setText(QCoreApplication.translate("Dialog", u"max:100", None))
        self.comboBoxPlane.setItemText(0, QCoreApplication.translate("Dialog", u"Best Fitting Plane", None))
        self.comboBoxPlane.setItemText(1, QCoreApplication.translate("Dialog", u"XY Plane", None))
        self.comboBoxPlane.setItemText(2, QCoreApplication.translate("Dialog", u"YZ Plane", None))
        self.comboBoxPlane.setItemText(3, QCoreApplication.translate("Dialog", u"XZ Plane", None))

        self.label_37.setText(QCoreApplication.translate("Dialog", u"Projection Plane Mode:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("Dialog", u"Surface Reconstruction", None))
        self.pushButton_4.setText(QCoreApplication.translate("Dialog", u"Accept", None))
        self.pushButton_3.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
    # retranslateUi


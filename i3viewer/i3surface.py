from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (QApplication, QColorDialog, QDialog, QFrame,
                               QLabel, QPushButton, QVBoxLayout, QWidget)

from i3viewer.i3enums import DelaunayCfg, SurfaceCfg
from i3viewer.i3surfaceDialog import \
    Ui_Dialog  # Import the generated UI class for surface


class SurfaceDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None, surfacecfg=None):
        super().__init__(parent)
        # Set up the user interface from Designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Customize the dialog (modal specific settings)
        self.setWindowTitle("i3dViewer - Surface Dialog")

        self.surfacecfg = surfacecfg
        self.delaunaycfg = DelaunayCfg()

        self.surfaceColor = (
            QColor(*[int(round(255 * val))
                   for val in surfacecfg.surface_color])
            if surfacecfg
            else QColor(255, 255, 255)
        )

        self.wireframeColor = (
            QColor(*[int(round(255 * val))
                   for val in surfacecfg.wireframe_color])
            if surfacecfg
            else QColor(255, 255, 255)
        )

        self.update_surface_color()
        self.update_wireframe_color()

        self.configureSliders()

        # Connect signals to slots
        self.ui.pushButtonSurface.clicked.connect(self.surface_color_dialog)
        self.ui.pushButtonWireframe.clicked.connect(
            self.wireframe_color_dialog)

        self.ui.horizontalSliderOpacity.valueChanged.connect(
            self.update_opacity)
        self.ui.horizontalSliderThickness.valueChanged.connect(
            self.update_thickness)
        self.ui.horizontalSliderCTolerance.valueChanged.connect(
            self.update_cleaner_tolerance
        )
        self.ui.horizontalSliderDAlpha.valueChanged.connect(
            self.update_delaunay_alpha)
        self.ui.horizontalSliderDTolerance.valueChanged.connect(
            self.update_delaunay_tolerance
        )
        self.ui.horizontalSliderDOffset.valueChanged.connect(
            self.update_delaunay_offset
        )
        self.ui.horizontalSliderFAngle.valueChanged.connect(
            self.update_feature_angle)

    def surface_color_dialog(self):
        color = QColorDialog.getColor(
            self.surfaceColor, self, "Select Surface Color")
        if color.isValid():
            self.surfaceColor = color
            self.update_surface_color()

    def wireframe_color_dialog(self):
        color = QColorDialog.getColor(
            self.wireframeColor, self, "Select Wireframe Color"
        )
        if color.isValid():
            self.wireframeColor = color
            self.update_wireframe_color()

    def update_surface_color(self):
        palette = self.ui.frameSurface.palette()
        if hasattr(QPalette, "Window"):
            palette.setColor(getattr(QPalette, "Window"), self.surfaceColor)
        self.ui.frameSurface.setPalette(palette)
        self.ui.frameSurface.setAutoFillBackground(True)
        self.ui.labelSurface.setText(self.surfaceColor.name().upper())

    def update_wireframe_color(self):
        palette = self.ui.frameWireframe.palette()
        if hasattr(QPalette, "Window"):
            palette.setColor(getattr(QPalette, "Window"), self.wireframeColor)
        self.ui.frameWireframe.setPalette(palette)
        self.ui.frameWireframe.setAutoFillBackground(True)
        self.ui.labelWireframe.setText(self.wireframeColor.name().upper())

    def configureSliders(self):

        # configure surface opacity
        self.ui.labelOpacityMin.setText(
            f"{SurfaceCfg.min_max_range()["surface_opacity"][0]:.2f}"
        )
        self.ui.labelOpacityMax.setText(
            f"{SurfaceCfg.min_max_range()["surface_opacity"][1]:.2f}"
        )

        # configure edge thickness
        self.ui.labelThicknessMin.setText(
            str(SurfaceCfg.min_max_range()["edge_thickness"][0])
        )
        self.ui.labelThicknessMax.setText(
            str(SurfaceCfg.min_max_range()["edge_thickness"][1])
        )

        # configure cleaner tolerance
        self.ui.labelCToleranceMin.setText(
            str(DelaunayCfg.min_max_range()["cleaner_tolerance"][0])
        )
        self.ui.labelCToleranceMax.setText(
            f"{DelaunayCfg.min_max_range()["cleaner_tolerance"][1]:.4f}"
        )

        # configure delaunay alpha
        self.ui.labelDAlphaMin.setText(
            str(DelaunayCfg.min_max_range()["delaunay_alpha"][0])
        )
        self.ui.labelDAlphaMax.setText(
            str(DelaunayCfg.min_max_range()["delaunay_alpha"][1])
        )

        # configure delaunay tolerance
        self.ui.labelDToleranceMin.setText(
            str(DelaunayCfg.min_max_range()["delaunay_tolerance"][0])
        )
        self.ui.labelDToleranceMax.setText(
            f"{DelaunayCfg.min_max_range()["delaunay_tolerance"][1]:.4f}"
        )

        # configure delaunay offset
        self.ui.labelDOffsetMin.setText(
            str(DelaunayCfg.min_max_range()["delaunay_offset"][0])
        )
        self.ui.labelDOffsetMax.setText(
            str(DelaunayCfg.min_max_range()["delaunay_offset"][1])
        )

        # configure feature angle
        self.ui.labelFAngleMin.setText(
            str(DelaunayCfg.min_max_range()["feature_angle"][0])
        )
        self.ui.labelFAngleMax.setText(
            str(DelaunayCfg.min_max_range()["feature_angle"][1])
        )

    def update_opacity(self, value):
        if self.surfacecfg:
            self.surfacecfg.surface_color = value / 100
            self.ui.labelOpacityValue.setText(
                f"{self.surfacecfg.surface_color: .2f}")

    def update_thickness(self, value):
        if self.surfacecfg:
            self.surfacecfg.edge_thickness = value
            self.ui.labelThicknessValue.setText(
                f"{self.surfacecfg.edge_thickness}")

    def update_cleaner_tolerance(self, value):
        if self.delaunaycfg:
            self.delaunaycfg.cleaner_tolerance = value / 100000
            self.ui.labelCToleranceValue.setText(
                f"{self.delaunaycfg.cleaner_tolerance:.4f}"
            )

    def update_delaunay_alpha(self, value):
        if self.delaunaycfg:
            self.delaunaycfg.delaunay_alpha = value
            self.ui.labelDAlphaValue.setText(
                f"{self.delaunaycfg.delaunay_alpha:.1f}")

    def update_delaunay_tolerance(self, value):
        if self.delaunaycfg:
            self.delaunaycfg.delaunay_tolerance = value / 100000
            self.ui.labelDToleranceValue.setText(
                f"{self.delaunaycfg.delaunay_tolerance:.4f}"
            )

    def update_delaunay_offset(self, value):
        if self.delaunaycfg:
            self.delaunaycfg.delaunay_offset = value
            self.ui.labelDOffsetValue.setText(
                f"{self.delaunaycfg.delaunay_offset:.1f}")

    def update_feature_angle(self, value):
        if self.delaunaycfg:
            self.delaunaycfg.feature_angle = value
            self.ui.labelFAngleValue.setText(
                f"{self.delaunaycfg.feature_angle:.1f}")

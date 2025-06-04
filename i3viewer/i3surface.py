import random

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QColorDialog, QDialog
from PySide6.QtCore import QSettings
from i3viewer.i3enums import (DelaunayCfg, DelaunayProfile, ProjectionPlane,
                              SurfaceCfg, SurfaceProfile)
from i3viewer.i3surfaceDialog import \
    Ui_Dialog  # Import the generated UI class for surface
from i3viewer.i3enums import Params


class SurfaceDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None, contour_color=None, surfacecfg=SurfaceCfg(), delaunaycfg=DelaunayCfg()):
        super().__init__(parent)
        # Set up the user interface from Designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Customize the dialog (modal specific settings)
        self.setWindowTitle(f"{Params.ApplicationName.value} - Surface Dialog")

        self.surfacecfg = surfacecfg
        self.delaunaycfg = delaunaycfg
        self.contour_color = contour_color

        # Configure frame colors
        self.update_current_colors()

        # Configure max and min for slider
        self.configureSliders()

        # Connect signals to slots
        self.ui.pushButtonSurface.clicked.connect(self.surface_color_dialog)
        self.ui.pushButtonWireframe.clicked.connect(self.wireframe_color_dialog)
        self.ui.pushButtonContour.clicked.connect(self.contour_color_dialog)

        # Update radio button selection
        self.ui.radioButtonProfile.toggled.connect(self.update_selection_color)
        self.ui.radioButtonRandom.toggled.connect(self.update_selection_color)
        self.ui.radioButtonCustom.toggled.connect(self.update_selection_color)

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

        self.ui.comboBoxSProfile.currentIndexChanged.connect(
            self.update_selection_sprofile)
        self.ui.comboBoxDProfile.currentIndexChanged.connect(
            self.update_selection_dprofile)
        self.ui.comboBoxPlane.currentIndexChanged.connect(
            self.update_selection_plane)

        self.ui.pushButtonAccept.clicked.connect(self.accept)
        self.ui.pushButtonReject.clicked.connect(self.reject)

        # Restore saved settings
        self.restore_settings()

    def save_settings(self):
        settings = QSettings("hpgl", "i3dViewer")
        settings.beginGroup("SurfaceDialog")

        # Save combo box selections
        settings.setValue("comboBoxSProfile", self.ui.comboBoxSProfile.currentIndex())
        settings.setValue("comboBoxDProfile", self.ui.comboBoxDProfile.currentIndex())
        settings.setValue("comboBoxPlane", self.ui.comboBoxPlane.currentIndex())

        # Save radio button selection
        if self.ui.radioButtonProfile.isChecked():
            settings.setValue("colorMode", "profile")
        elif self.ui.radioButtonRandom.isChecked():
            settings.setValue("colorMode", "random")
        elif self.ui.radioButtonCustom.isChecked():
            settings.setValue("colorMode", "custom")

        # Save frame colors
        settings.setValue("frameSurfaceColor", self.surfaceColor.name())
        settings.setValue("frameWireframeColor", self.wireframeColor.name())
        settings.setValue("frameContourColor", self.contourColor.name())

        # Save label texts
        settings.setValue("labelSurfaceText", self.ui.labelSurface.text())
        settings.setValue("labelWireframeText", self.ui.labelWireframe.text())
        settings.setValue("labelContourText", self.ui.labelContour.text())

        # Save slider values
        settings.setValue("sliderOpacity", self.ui.horizontalSliderOpacity.value())
        settings.setValue("sliderThickness", self.ui.horizontalSliderThickness.value())
        settings.setValue("sliderCTolerance", self.ui.horizontalSliderCTolerance.value())
        settings.setValue("sliderDAlpha", self.ui.horizontalSliderDAlpha.value())
        settings.setValue("sliderDTolerance", self.ui.horizontalSliderDTolerance.value())
        settings.setValue("sliderDOffset", self.ui.horizontalSliderDOffset.value())
        settings.setValue("sliderFAngle", self.ui.horizontalSliderFAngle.value())

        # Save value label texts
        settings.setValue("labelOpacityValue", self.ui.labelOpacityValue.text())
        settings.setValue("labelThicknessValue", self.ui.labelThicknessValue.text())
        settings.setValue("labelCToleranceValue", self.ui.labelCToleranceValue.text())
        settings.setValue("labelDAlphaValue", self.ui.labelDAlphaValue.text())
        settings.setValue("labelDToleranceValue", self.ui.labelDToleranceValue.text())
        settings.setValue("labelDOffsetValue", self.ui.labelDOffsetValue.text())
        settings.setValue("labelFAngleValue", self.ui.labelFAngleValue.text())

        settings.endGroup()

    def restore_settings(self):
        settings = QSettings("hpgl", "i3dViewer")
        settings.beginGroup("SurfaceDialog")

        # Helper function for safe conversion
        def get_setting(key, default, type_converter):
            value = settings.value(key)
            try:
                return type_converter(value) if value is not None else default
            except (TypeError, ValueError):
                return default

        # Restore combo box selections
        self.ui.comboBoxSProfile.setCurrentIndex(
            get_setting("comboBoxSProfile", 1, int))
        self.ui.comboBoxDProfile.setCurrentIndex(
            get_setting("comboBoxDProfile", 0, int))
        self.ui.comboBoxPlane.setCurrentIndex(
            get_setting("comboBoxPlane", 0, int))

        # Restore radio button selection
        color_mode = get_setting("colorMode", "profile", str)
        if color_mode == "profile":
            self.ui.radioButtonProfile.setChecked(True)
        elif color_mode == "random":
            self.ui.radioButtonRandom.setChecked(True)
        elif color_mode == "custom":
            self.ui.radioButtonCustom.setChecked(True)

        # Restore frame colors
        surface_color = QColor(get_setting("frameSurfaceColor", "#ffffff", str))
        wireframe_color = QColor(get_setting("frameWireframeColor", "#ffffff", str))
        contour_color = QColor(get_setting("frameContourColor", "#ffffff", str))
        self.surfaceColor = surface_color
        self.wireframeColor = wireframe_color
        self.contourColor = contour_color

        # Update frame colors in UI
        palette = self.ui.frameSurface.palette()
        if hasattr(QPalette, "Window"):
            palette.setColor(getattr(QPalette, "Window"), surface_color)
        self.ui.frameSurface.setPalette(palette)
        self.ui.frameSurface.setAutoFillBackground(True)

        palette = self.ui.frameWireframe.palette()
        if hasattr(QPalette, "Window"):
            palette.setColor(getattr(QPalette, "Window"), wireframe_color)
        self.ui.frameWireframe.setPalette(palette)
        self.ui.frameWireframe.setAutoFillBackground(True)

        palette = self.ui.frameWireframe.palette()
        if hasattr(QPalette, "Window"):
            palette.setColor(getattr(QPalette, "Window"), contour_color)
        self.ui.frameContour.setPalette(palette)
        self.ui.frameContour.setAutoFillBackground(True)

        # Restore label texts
        self.ui.labelSurface.setText(
            get_setting("labelSurfaceText", surface_color.name().upper(), str))
        self.ui.labelWireframe.setText(
            get_setting("labelWireframeText", wireframe_color.name().upper(), str))
        self.ui.labelContour.setText(
            get_setting("labelContourText", contour_color.name().upper(), str))

        # Restore slider values
        self.ui.horizontalSliderOpacity.setValue(
            get_setting("sliderOpacity", 100, int))
        self.ui.horizontalSliderThickness.setValue(
            get_setting("sliderThickness", 1, int))
        self.ui.horizontalSliderCTolerance.setValue(
            get_setting("sliderCTolerance", 100, int))
        self.ui.horizontalSliderDAlpha.setValue(
            get_setting("sliderDAlpha", 60, int))
        self.ui.horizontalSliderDTolerance.setValue(
            get_setting("sliderDTolerance", 100, int))
        self.ui.horizontalSliderDOffset.setValue(
            get_setting("sliderDOffset", 5, int))
        self.ui.horizontalSliderFAngle.setValue(
            get_setting("sliderFAngle", 60, int))

        # Restore value label texts
        self.ui.labelOpacityValue.setText(
            get_setting("labelOpacityValue", "1.00", str))
        self.ui.labelThicknessValue.setText(
            get_setting("labelThicknessValue", "1", str))
        self.ui.labelCToleranceValue.setText(
            get_setting("labelCToleranceValue", "0.0010", str))
        self.ui.labelDAlphaValue.setText(
            get_setting("labelDAlphaValue", "60.0", str))
        self.ui.labelDToleranceValue.setText(
            get_setting("labelDToleranceValue", "0.0010", str))
        self.ui.labelDOffsetValue.setText(
            get_setting("labelDOffsetValue", "5.0", str))
        self.ui.labelFAngleValue.setText(
            get_setting("labelFAngleValue", "60.0", str))

        # Update configuration objects
        if self.surfacecfg:
            self.surfacecfg.surface_color = [
                surface_color.redF(),
                surface_color.greenF(),
                surface_color.blueF()
            ]
            self.surfacecfg.wireframe_color = [
                wireframe_color.redF(),
                wireframe_color.greenF(),
                wireframe_color.blueF()
            ]
            self.surfacecfg.surface_opacity = self.ui.horizontalSliderOpacity.value() / 100
            self.surfacecfg.edge_thickness = self.ui.horizontalSliderThickness.value()

        if self.delaunaycfg:
            self.delaunaycfg.cleaner_tolerance = self.ui.horizontalSliderCTolerance.value() / 100000
            self.delaunaycfg.delaunay_alpha = self.ui.horizontalSliderDAlpha.value()
            self.delaunaycfg.delaunay_tolerance = self.ui.horizontalSliderDTolerance.value() / 100000
            self.delaunaycfg.delaunay_offset = self.ui.horizontalSliderDOffset.value()
            self.delaunaycfg.feature_angle = self.ui.horizontalSliderFAngle.value()

        settings.endGroup()

    def convert_qcolor(self, color):
        return (QColor(*[int(round(255 * val)) for val in color])
                if self.surfacecfg
                else QColor(255, 255, 255))

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

    def contour_color_dialog(self):
        color = QColorDialog.getColor(
            self.contourColor, self, "Select Contour Color"
        )
        if color.isValid():
            self.contourColor = color
            self.update_contour_color()

    def update_surface_color(self):
        palette = self.ui.frameSurface.palette()
        if hasattr(QPalette, "Window"):
            palette.setColor(getattr(QPalette, "Window"), self.surfaceColor)
        self.ui.frameSurface.setPalette(palette)
        self.ui.frameSurface.setAutoFillBackground(True)
        self.ui.labelSurface.setText(self.surfaceColor.name().upper())

        if self.surfacecfg:
            r = self.surfaceColor.redF()
            g = self.surfaceColor.greenF()
            b = self.surfaceColor.blueF()
            self.surfacecfg.surface_color = [r, g, b]

    def update_wireframe_color(self):
        palette = self.ui.frameWireframe.palette()
        if hasattr(QPalette, "Window"):
            palette.setColor(getattr(QPalette, "Window"), self.wireframeColor)
        self.ui.frameWireframe.setPalette(palette)
        self.ui.frameWireframe.setAutoFillBackground(True)
        self.ui.labelWireframe.setText(self.wireframeColor.name().upper())

        if self.surfacecfg:
            r = self.wireframeColor.redF()
            g = self.wireframeColor.greenF()
            b = self.wireframeColor.blueF()
            self.surfacecfg.wireframe_color = [r, g, b]

    def update_contour_color(self):
        palette = self.ui.frameContour.palette()
        if hasattr(QPalette, "Window"):
            palette.setColor(getattr(QPalette, "Window"), self.contourColor)
        self.ui.frameContour.setPalette(palette)
        self.ui.frameContour.setAutoFillBackground(True)
        self.ui.labelContour.setText(self.contourColor.name().upper())

        r = self.contourColor.redF()
        g = self.contourColor.greenF()
        b = self.contourColor.blueF()
        self.contour_color = [r, g, b]

    def configureSliders(self):

        # configure surface opacity
        self.ui.labelOpacityMin.setText(
            f"{SurfaceCfg.min_max_range()["surface_opacity"][0]:.2f}"
        )
        self.ui.labelOpacityMax.setText(
            f"{SurfaceCfg.min_max_range()["surface_opacity"][1]:.2f}"
        )
        opacity = 100 * self.surfacecfg.surface_opacity if self.surfacecfg else 1
        self.ui.horizontalSliderOpacity.setValue(int(opacity))
        self.ui.labelOpacityValue.setText(f"{opacity/100: .2f}")

        # configure edge thickness
        self.ui.labelThicknessMin.setText(
            str(SurfaceCfg.min_max_range()["edge_thickness"][0])
        )
        self.ui.labelThicknessMax.setText(
            str(SurfaceCfg.min_max_range()["edge_thickness"][1])
        )
        thickness = self.surfacecfg.edge_thickness if self.surfacecfg else 1
        self.ui.horizontalSliderThickness.setValue(int(thickness))
        self.ui.labelThicknessValue.setText(f"{thickness: .2f}")

        # configure cleaner tolerance
        self.ui.labelCToleranceMin.setText(
            str(DelaunayCfg.min_max_range()["cleaner_tolerance"][0])
        )
        self.ui.labelCToleranceMax.setText(
            f"{DelaunayCfg.min_max_range()["cleaner_tolerance"][1]:.4f}"
        )
        ctolerance = 100000 * self.delaunaycfg.cleaner_tolerance if self.delaunaycfg else 100
        self.ui.horizontalSliderCTolerance.setValue(int(ctolerance))
        self.ui.labelCToleranceValue.setText(f"{ctolerance/100000: .4f}")

        # configure delaunay alpha
        self.ui.labelDAlphaMin.setText(
            str(DelaunayCfg.min_max_range()["delaunay_alpha"][0])
        )
        self.ui.labelDAlphaMax.setText(
            str(DelaunayCfg.min_max_range()["delaunay_alpha"][1])
        )
        dalpha = self.delaunaycfg.delaunay_alpha if self.delaunaycfg else 60
        self.ui.horizontalSliderDAlpha.setValue(int(dalpha))
        self.ui.labelDAlphaValue.setText(f"{dalpha: .1f}")

        # configure delaunay tolerance
        self.ui.labelDToleranceMin.setText(
            str(DelaunayCfg.min_max_range()["delaunay_tolerance"][0])
        )
        self.ui.labelDToleranceMax.setText(
            f"{DelaunayCfg.min_max_range()["delaunay_tolerance"][1]:.4f}"
        )
        dtolerance = 100000 * self.delaunaycfg.delaunay_tolerance if self.delaunaycfg else 100
        self.ui.horizontalSliderDTolerance.setValue(int(dtolerance))
        self.ui.labelDToleranceValue.setText(f"{dtolerance/100000: .4f}")

        # configure delaunay offset
        self.ui.labelDOffsetMin.setText(
            str(DelaunayCfg.min_max_range()["delaunay_offset"][0])
        )
        self.ui.labelDOffsetMax.setText(
            str(DelaunayCfg.min_max_range()["delaunay_offset"][1])
        )
        offset = self.delaunaycfg.delaunay_offset if self.delaunaycfg else 5
        self.ui.horizontalSliderDOffset.setValue(int(offset))
        self.ui.labelDOffsetValue.setText(f"{offset: .1f}")

        # configure feature angle
        self.ui.labelFAngleMin.setText(
            str(DelaunayCfg.min_max_range()["feature_angle"][0])
        )
        self.ui.labelFAngleMax.setText(
            str(DelaunayCfg.min_max_range()["feature_angle"][1])
        )
        angle = self.delaunaycfg.feature_angle if self.delaunaycfg else 60
        self.ui.horizontalSliderFAngle.setValue(int(angle))
        self.ui.labelFAngleValue.setText(f"{angle: .1f}")

    def update_opacity(self, value):
        if self.surfacecfg:
            self.surfacecfg.surface_opacity = value / 100
            self.ui.labelOpacityValue.setText(
                f"{self.surfacecfg.surface_opacity: .2f}")

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

    def update_selection_color(self):
        if self.ui.radioButtonProfile.isChecked():
            self.ui.comboBoxSProfile.setEnabled(True)
            self.ui.pushButtonSurface.setDisabled(True)
            self.ui.pushButtonWireframe.setDisabled(True)
            self.surfacecfg.config_default()
            self.update_current_colors()
            self.configureSliders()
        elif self.ui.radioButtonRandom.isChecked():
            self.ui.comboBoxSProfile.setDisabled(True)
            self.ui.pushButtonSurface.setDisabled(True)
            self.ui.pushButtonWireframe.setDisabled(True)
            self.update_random_colors()
        elif self.ui.radioButtonCustom.isChecked():
            self.ui.comboBoxSProfile.setDisabled(True)
            self.ui.pushButtonSurface.setEnabled(True)
            self.ui.pushButtonWireframe.setEnabled(True)

    def update_random_colors(self):
        self.surfaceColor = QColor(*[random.randint(0, 255) for _ in range(3)])
        self.wireframeColor = QColor(*[random.randint(0, 255) for _ in range(3)])
        self.update_surface_color()
        self.update_wireframe_color()

    def update_current_colors(self):
        self.surfaceColor = self.convert_qcolor(self.surfacecfg.surface_color)
        self.wireframeColor = self.convert_qcolor(self.surfacecfg.wireframe_color)
        self.contourColor = self.convert_qcolor(self.contour_color)
        self.update_surface_color()
        self.update_wireframe_color()
        self.update_contour_color()

    def update_selection_sprofile(self, index):
        if index == SurfaceProfile.DEFAULT.value:
            self.surfacecfg.config_default()
        if index == SurfaceProfile.TERRAIN.value:
            self.surfacecfg.config_terrain()
        elif index == SurfaceProfile.WIREFRAME.value:
            self.surfacecfg.config_wireframe()
        elif index == SurfaceProfile.TRANSPARENT.value:
            self.surfacecfg.config_transparent()
        elif index == SurfaceProfile.PRESENTATION.value:
            self.surfacecfg.config_presentation()
        self.configureSliders()
        self.update_current_colors()

    def update_selection_dprofile(self, index):
        if index == DelaunayProfile.DEFAULT.value:
            self.delaunaycfg.config_default()
        if index == DelaunayProfile.HIGH_RESOLUTION.value:
            self.delaunaycfg.config_high_resolution()
        elif index == DelaunayProfile.TYPICAL_GIS.value:
            self.delaunaycfg.config_typical_gis()
        elif index == DelaunayProfile.NOISY_DATA.value:
            self.delaunaycfg.config_noisy_data()
        elif index == DelaunayProfile.CONTOUR_PRESERVING.value:
            self.delaunaycfg.config_contour_preserving()
        self.configureSliders()

    def update_selection_plane(self, index):
        if index == ProjectionPlane.BEST_FIT.value:
            self.delaunaycfg.projection_plane_mode=ProjectionPlane.BEST_FIT.value
        elif index == ProjectionPlane.XY_PLANE.value:
            self.delaunaycfg.projection_plane_mode=ProjectionPlane.XY_PLANE.value
        elif index == ProjectionPlane.YZ_PLANE.value:
            self.delaunaycfg.projection_plane_mode=ProjectionPlane.YZ_PLANE.value
        elif index == ProjectionPlane.XZ_PLANE.value:
            self.delaunaycfg.projection_plane_mode=ProjectionPlane.XZ_PLANE.value

    def accept(self):
        """Override accept to save settings before closing"""
        self.save_settings()
        super().accept()

    def reject(self):
        """Override reject to save settings before closing"""
        self.save_settings()
        super().reject()


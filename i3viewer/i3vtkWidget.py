import vtk
import vtkmodules.qt.QVTKRenderWindowInteractor as QVTK
from PySide6.QtWidgets import QHBoxLayout, QWidget
from vtk import vtkActor

from i3viewer.i3enums import FileType, Params
from i3viewer.i3model import i3model
from i3viewer.i3point import NonModalDialog as PointDialog
from i3viewer.i3polyline import NonModalDialog as PolylineDialog


class i3vtkWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.Parent = parent
        self.renderer = None
        self.interactor = None
        self.picker = None
        self.model = None
        self.actors = []
        self.TrihedronPos = 1
        self.selected_actor = None
        self.polylineDialog = PolylineDialog(0, 0, 0, [])
        self.pointDialog = PointDialog(0, 0, 0, 0, "")
        self.heatmap = False
        self.unpick = False
        self.polylabel = False
        self.pointlabel = False
        self.surfaceActor = False
        self.surface = False
        self.wireframe = False
        self.scalarBar = vtk.vtkScalarBarActor()

        if self.Parent == None:
            self.resize(500, 500)
        else:
            self.resize(self.Parent.size())

        self.ShowEdges = False
        self.SetupWnd()

    def import_file(self, file_path, fileType, newFile=True):

        if self.model is None:
            self.model = i3model(file_path)
        else:
            self.model.file_path = file_path

        actors = []
        if newFile:
            self.RemoveAllActors()
            self.actors = []
            self.model.polyline_id = 1
            self.model.point_id = 1
            self.model.surface_id = 1

        if fileType == FileType.DB:
            if self.model.hasPointsTable():
                actors = self.model.points_format_actors(fileType)
                self.actors.extend(actors)
            if self.model.hasPolylinesTable():
                actors = self.model.polylines_format_actors(fileType)
                self.actors.extend(actors)
            if self.model.hasSurfacesTable():
                actors = self.model.surfaces_format_actors(fileType)
                self.actors.extend(actors)
        elif fileType == FileType.XYZ or fileType == FileType.CSV:
            actors = self.model.polylines_format_actors(fileType)
            self.actors.extend(actors)
            self.polylabels_create_actors(fileType)
        elif fileType == FileType.SRG:
            actors = self.model.points_format_actors(fileType)
            self.actors.extend(actors)
            self.pointlabels_create_actors(fileType)
        elif fileType == FileType.XYZS:
            actors = self.model.surfaces_format_actors(fileType)
            self.actors.extend(actors)

        if self.actors:
            for actor in self.actors:
                self.AddActor(actor)

        self.UpdateView()

    def polylines_update_data(self):
        if self.model:
            self.model.polylines_reread_table()

    def polylines_get_actor(self, polyline_id):
        """Returns the VTK actor associated with the given polyline_id, or None if not found."""
        for actor in self.actors:
            if hasattr(actor, "polyline_id") and actor.polyline_id == polyline_id:
                return actor
        return None

    def points_get_actor(self, point_id):
        """Returns the VTK actor associated with the given point_id, or None if not found."""
        for actor in self.actors:
            if hasattr(actor, "point_id") and actor.point_id == point_id:
                return actor
        return None

    def surfaces_get_actor(self, surface_id):
        """Returns the VTK actor associated with the given surface_id, or None if not found."""
        for actor in self.actors:
            if hasattr(actor, "surface_id") and actor.surface_id == surface_id:
                return actor
        return None

    def RemoveAllActors(self):
        if self.actors:
            for actor in self.actors:
                self.RemoveActor(actor)
            self.actors = []
        self.UpdateView()
        if self.model:
            self.model.RemoveAllActors()

    def calculate_polyline_length(self, polyline):
        """Calculates the total length of a polyline."""
        length = 0.0
        for i in range(1, len(polyline)):
            x1, y1, z1, *_ = polyline[i - 1]
            x2, y2, z2, *_ = polyline[i]
            length += ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2) ** 0.5
        return round(length, 3)

    def on_pick(self, obj, event):  # pyright: ignore[reportUnusedVariable]
        """Handles picking an actor and updates selection and dialog accordingly."""
        _, _ = obj, event
        if (self.interactor is None or \
            self.picker is None or \
            self.renderer is None or \
            self.unpick):
            return

        click_pos = self.interactor.GetEventPosition()

        self.picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)
        actor = self.picker.GetActor()

        if actor:
            if self.selected_actor == actor:
                self.deselect_actor(actor)
                self.clear_dialog()
            else:
                if self.selected_actor:
                    self.deselect_actor(self.selected_actor)
                    # self.hide_dialog()
                self.select_actor(actor)
                self.show_dialog(actor)
        else:
            if self.selected_actor:
                self.deselect_actor(self.selected_actor)
                self.clear_dialog()

        self.UpdateView(False)

    def select_actor(self, actor):
        """Select a new actor (point or polyline) by changing its color and line width."""

        if self.model is None:
            return

        if hasattr(actor, 'polyline_id') and actor.polyline_id in self.model.polylines:
            # Handle polyline selection
            actor.GetProperty().SetColor(Params.SelectedColor.value)  # Yellow color
            actor.GetProperty().SetLineWidth(Params.PolylineSelectedWidth.value)
        elif hasattr(actor, 'point_id') and actor.point_id in self.model.points:
            # Handle point selection
            actor.GetProperty().SetColor(Params.SelectedColor.value)  # Yellow color
            actor = self.model.point_select(actor, Params.PointWinSelectedRadius.value)
        else:
            return  # Ignore invalid actors

        self.selected_actor = actor

    def deselect_actor(self, actor):
        """Deselect the given actor (point or polyline) by restoring its original color and size."""

        if self.model is None:
            return

        if hasattr(actor, "polyline_id") and hasattr(actor, "color"):
            # Handle polyline deselection
            if self.heatmap:
                rainbow_color = getattr(actor, "rainbow_color")
                rainbow_width = getattr(actor, "rainbow_width")
                color = rainbow_color
                width = rainbow_width
            else:
                original_color = getattr(actor, "color")
                color = original_color
                width = Params.PolylineDefaultWidth.value
            actor.GetProperty().SetColor(color)
            actor.GetProperty().SetLineWidth(width)
        elif hasattr(actor, "point_id") and hasattr(actor, "color"):
            # Handle point deselection
            original_color = getattr(actor, "color")
            actor.GetProperty().SetColor(original_color)
            self.model.point_select(actor, Params.PointWinRadius.value)
        else:
            return  # Ignore invalid actors

        self.selected_actor = None

    def show_dialog(self, actor):
        """Displays or updates the dialog with polyline or point information."""

        if self.model is None:
            return

        if hasattr(actor, 'polyline_id'):
            # Handle polyline
            polyline_id = actor.polyline_id
            points = self.model.polylines[polyline_id]
            num_points = len(points)
            polyline_length = self.calculate_polyline_length(points)

            if self.polylineDialog is None:
                self.polylineDialog = PolylineDialog(
                    polyline_id, num_points, polyline_length, points)
                self.polylineDialog.dialog_closed.connect(
                    self.handle_dialog_closed)

            # self.polylineDialog.setWindowFlags(Qt.WindowStaysOnTopHint)  # Force the dialog to stay on top
            self.polylineDialog.show()  # Keep it non-modal
            self.polylineDialog.clear_dialog()
            self.polylineDialog.update_dialog(
                polyline_id, num_points, polyline_length, points)

        elif hasattr(actor, 'point_id'):
            # Handle point
            point_id = actor.point_id
            # Assuming self.model.points stores point data
            point_data = self.model.points[point_id]

            if self.pointDialog is None:
                self.pointDialog = PointDialog(point_id, *point_data[0])
                self.pointDialog.dialog_closed.connect(
                    self.handle_dialog_closed)

            # self.pointDialog.setWindowFlags(Qt.WindowStaysOnTopHint)  # Force the dialog to stay on top
            self.pointDialog.show()  # Keep it non-modal
            self.pointDialog.clear_dialog()
            self.pointDialog.update_dialog(point_id, *point_data[0])

    def hide_dialog(self):
        """Resets the dialog when a polyline is deselected."""
        if self.polylineDialog:
            self.polylineDialog.hide()
        if self.pointDialog:
            self.pointDialog.hide()

    def clear_dialog(self):
        """Resets the dialog when a polyline is deselected."""
        if self.polylineDialog:
            self.polylineDialog.clear_dialog()
        if self.pointDialog:
            self.pointDialog.clear_dialog()

    def handle_dialog_closed(self):
        """Handle the dialog_closed signal to clean up the dialog reference."""
        if self.polylineDialog:
            self.polylineDialog = None
        if self.pointDialog:
            self.pointDialog = None
        # print("Dialog closed and reference cleaned up.")

    def closeEvent(self, event):
        """Override closeEvent to close the dialog when the application is closed."""
        if self.polylineDialog:
            self.polylineDialog.close()
        if self.pointDialog:
            self.pointDialog.close()
        event.accept()  # Accept the close event

    def SetupWnd(self):
        self.SetupRenderer()
        self.SetupTrihedron()
        self.ResetCamera()

    def SetupRenderer(self):
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.2, 0.3, 0.4)
        # Keep self as parent for correct Qt integration
        self.interactor = QVTK.QVTKRenderWindowInteractor(self)

        self.trackball = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(self.trackball)

        self.interactor.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor.GetRenderWindow().PointSmoothingOn()
        self.interactor.GetRenderWindow().LineSmoothingOn()

        layout = self.layout()
        if layout is None:
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
        layout.addWidget(self.interactor)

        # Create picker
        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.005)
        self.interactor.SetPicker(self.picker)

        # Attach the picker event to the interactor
        self.interactor.AddObserver("LeftButtonPressEvent", self.on_pick)

        self.interactor.Initialize()
        self.interactor.Start()

    def MakeAxesActor(self):
        axes = vtk.vtkAxesActor()
        # axes.SetShaftTypeToCylinder()
        axes.SetShaftTypeToLine()
        axes.SetXAxisLabelText('X')
        axes.SetYAxisLabelText('Y')
        axes.SetZAxisLabelText('Z')
        axes.SetTotalLength(1.5, 1.5, 1.5)
        axes.SetCylinderRadius(0.5 * axes.GetCylinderRadius())
        axes.SetConeRadius(1.025 * axes.GetConeRadius())
        axes.SetSphereRadius(1.5 * axes.GetSphereRadius())
        return axes

    def SetupTrihedron(self):
        self.Trihedron = self.MakeAxesActor()
        self.om1 = vtk.vtkOrientationMarkerWidget()
        self.om1.SetOrientationMarker(self.Trihedron)
        self.om1.SetInteractor(self.interactor)
        self.om1.EnabledOn()
        self.om1.InteractiveOff()

    def ResizeTrihedron(self, width, height):
        if self.Trihedron:
            if (width == 0):
                width = 100
            if (height == 0):
                height = 100

            if self.TrihedronPos == 1:  # Position lower Left in the viewport.
                self.om1.SetViewport(0, 0, (200.0 / width), (200.0 / height))

            if self.TrihedronPos == 2:  # Position lower Right in the viewport.
                self.om1.SetViewport(1 - (200.0 / width),
                                     0, 1, (200.0 / height))

    def paintEvent(self, event) -> None:
        """Handle resize events to ensure the VTK render window matches the widget size."""
        _ = event
        # Get the new size of the widget
        new_size = self.size()

        # Resize the VTK render window to match the widget size
        if self.interactor and self.interactor.GetRenderWindow():
            self.interactor.GetRenderWindow().SetSize(new_size.width(), new_size.height())
            self.interactor.GetRenderWindow().Render()  # Force a re-render
        self.ResizeTrihedron(new_size.width(), new_size.height())

    def UpdateView(self, resetCamara=True):
        if self.interactor is None:
            raise RuntimeError("self.interactor could not be created.")
        if resetCamara:
            self.ResetCamera()
        self.interactor.ReInitialize()
        self.interactor.GetRenderWindow().Render()
        self.repaint()

    def ResetCamera(self):
        if self.renderer is None:
            raise RuntimeError("self.interactor could not be created.")
        self.renderer.ResetCamera()
        self.camera = self.renderer.GetActiveCamera()
        self.camera.ParallelProjectionOn()

    def AddActor(self, pvtkActor):
        if self.renderer is None:
            raise RuntimeError("self.interactor could not be created.")
        self.renderer.AddActor(pvtkActor)

    def RemoveActor(self, pvtkActor):
        if self.renderer is None:
            raise RuntimeError("self.interactor could not be created.")
        self.renderer.RemoveActor(pvtkActor)

    def AddActor2D(self, pvtkActor):
        if self.renderer is None:
            raise RuntimeError("self.interactor could not be created.")
        self.renderer.AddActor2D(pvtkActor)

    def RemoveActor2D(self, pvtkActor):
        if self.renderer is None:
            raise RuntimeError("self.interactor could not be created.")
        self.renderer.RemoveActor2D(pvtkActor)

    def SetRepresentation(self, aTyp):
        ''' aTyp = 1 - Points
            aTyp = 2 - Wireframe
            aTyp = 3 - Surface
            aTyp = 4 - Surface with edges
        '''
        if self.renderer is None:
            raise RuntimeError("self.interactor could not be created.")
        num_actors = self.renderer.GetActors().GetNumberOfItems()
        for i in range(num_actors):
            actor = self.renderer.GetActors().GetItemAsObject(i)
            if isinstance(actor, vtkActor):
                if (aTyp == 1):
                    actor.GetProperty().SetRepresentationToPoints()
                    actor.GetProperty().SetPointSize(4.0)
                    self.ShowEdges = False

                if (aTyp == 2):
                    actor.GetProperty().SetRepresentationToWireframe()
                    self.ShowEdges = False

                if (aTyp == 3):
                    actor.GetProperty().SetRepresentationToSurface()
                    actor.GetProperty().EdgeVisibilityOff()
                    self.ShowEdges = False

                if (aTyp == 4):
                    actor.GetProperty().SetRepresentationToSurface()
                    actor.GetProperty().EdgeVisibilityOn()
                    self.ShowEdges = True
        self.UpdateView()

    def OnFrontView(self):
        delta = 1
        lookAt = self.camera.GetFocalPoint()
        self.camera.SetPosition(lookAt[0], lookAt[1], lookAt[2] + delta)
        self.camera.SetViewUp(0, 1, 0)

        self.ResetCamera()
        self.UpdateView()

    def OnBackView(self):
        delta = -1
        lookAt = self.camera.GetFocalPoint()
        self.camera.SetPosition(lookAt[0], lookAt[1], lookAt[2] + delta)
        self.camera.SetViewUp(0, 1, 0)

        self.ResetCamera()
        self.UpdateView()

    def OnTopView(self):
        delta = 1
        lookAt = self.camera.GetFocalPoint()
        self.camera.SetPosition(lookAt[0], lookAt[1] + delta, lookAt[2])
        self.camera.SetViewUp(0, 0, -delta)

        self.ResetCamera()
        self.UpdateView()

    def OnBottomView(self):
        delta = -1
        lookAt = self.camera.GetFocalPoint()
        self.camera.SetPosition(lookAt[0], lookAt[1] + delta, lookAt[2])
        self.camera.SetViewUp(0, 0, -delta)

        self.ResetCamera()
        self.UpdateView()

    def OnLeftView(self):
        delta = 1
        lookAt = self.camera.GetFocalPoint()
        self.camera.SetPosition(lookAt[0] + delta, lookAt[1], lookAt[2])
        self.camera.SetViewUp(0, 1, 0)

        self.ResetCamera()
        self.UpdateView()

    def OnRightView(self):
        delta = -1
        lookAt = self.camera.GetFocalPoint()
        self.camera.SetPosition(lookAt[0] + delta, lookAt[1], lookAt[2])
        self.camera.SetViewUp(0, 1, 0)

        self.ResetCamera()
        self.UpdateView()

    def OnIsometricView(self):
        delta = 1
        lookAt = self.camera.GetFocalPoint()
        self.camera.SetPosition(
            lookAt[0] + delta, lookAt[1] + delta, lookAt[2] + delta)

        self.camera.SetViewUp(0, 1, 0)
        self.ResetCamera()
        self.UpdateView()

    def OnFitView(self):
        if self.renderer is None:
            raise RuntimeError("self.interactor could not be created.")
        self.renderer.ResetCameraClippingRange()
        self.ResetCamera()
        self.UpdateView()

    def OnHeatMap(self, enable):
        if self.model and self.model.polylines:
            self.heatmap = enable
            tonelajes = [polyline[0][5] \
                if polyline[0][5] is not None \
                else 0 \
                for polyline in self.model.polylines.values()]
            min_tonelaje = min(tonelajes)
            max_tonelaje = max(tonelajes)
            for polyline_id, polyline in self.model.polylines.items():

                tonelaje = polyline[0][5] if polyline[0][5] is not None else 0
                actor = self.polylines_get_actor(polyline_id)

                if enable:
                    color = self.rainbow_color(tonelaje, min_tonelaje, max_tonelaje)
                    setattr(actor, "rainbow_color", color)
                    width = self.rainbow_width(tonelaje, min_tonelaje, max_tonelaje)
                    setattr(actor, "rainbow_width", width)
                else:
                    color = getattr(actor, "color")
                    width = Params.PolylineDefaultWidth.value

                if hasattr(actor, "GetProperty"):
                    property = getattr(actor, 'GetProperty')()
                    property.SetColor(color)
                    property.SetLineWidth(width)

            if enable:
                self.AddScaleBar()
            else:
                self.RemoveScaleBar()

            if self.polylabel:
                self.CleanPolylabels()
                self.OnPolylabels(self.polylabel, FileType.DB)
            else:
                self.UpdateView(False)

    def rainbow_color(self, tonne, min_tonne=0, max_tonne=100):
        """Convert a value to a color using the VTK rainbow colormap."""
        # Create rainbow colormap
        lut = Params.LookupTable.value
        lut.SetTableRange(min_tonne, max_tonne)
        lut.Build()

        # Get color for value
        rgb = [0.0, 0.0, 0.0]
        lut.GetColor(tonne, rgb)

        # Convert to integers in range 0-255
        rgb_int = tuple(int(255 * c) for c in rgb)

        return rgb_int

    def rainbow_width(self, tonne, min_tonne, max_tonne):
        """
        Calculates the proportional width of a polyline based on current tonne value.

        Args:
            tonne (float): The current tonne value for which to calculate the width.
            min_tonne (float): The minimum tonne value in the data range.
            max_tonne (float): The maximum tonne value in the data range.

        Returns:
            float: The calculated polyline width, clamped between min_width and max_width.
                  Returns min_width if current_tonne is less than or equal to min_tonne.
                  Returns max_width if current_tonne is greater than or equal to max_tonne.
        """

        min_width = Params.PolylineMinWidth.value
        max_width = Params.PolylineMaxWidth.value

        if min_tonne == max_tonne:
            # Avoid division by zero if the tonne range is a single point
            return (min_width + max_width) / 2

        # Clamp current_tonne to the valid range to ensure width stays within min/max_width
        clamped_tonne = max(min_tonne, min(max_tonne, tonne))

        # Perform linear interpolation
        # normalized_tonne = (clamped_tonne - min_tonne) / (max_tonne - min_tonne)
        # polyline_width = min_width + (max_width - min_width) * normalized_tonne

        # Simplified linear interpolation:
        polyline_width = min_width + (clamped_tonne - min_tonne) * \
                         (max_width - min_width) / (max_tonne - min_tonne)

        return polyline_width


    def AddScaleBar(self):
        """ Add Color Scale Bar for Tonnes """
        lut = Params.LookupTable.value
        min_tonne, max_tonne = lut.GetTableRange()
        lut.SetTableRange(min_tonne/1000000, max_tonne/1000000)
        lut.Build()

        # Create scalar bar (color bar)
        self.scalarBar.SetLookupTable(lut)
        self.scalarBar.SetTitle("Mt     ")
        self.scalarBar.SetNumberOfLabels(5)
        self.scalarBar.SetPosition(0.85, 0.1)  # Position on right side
        self.scalarBar.SetWidth(0.04)
        self.scalarBar.SetHeight(0.8)
        self.scalarBar.SetLabelFormat("%.1f")

        # Customize scalar bar appearance
        self.scalarBar.GetTitleTextProperty().SetColor(1, 1, 0)
        self.scalarBar.GetTitleTextProperty().SetFontSize(14)
        self.scalarBar.GetLabelTextProperty().SetColor(1, 1, 0)
        self.scalarBar.GetLabelTextProperty().SetFontSize(12)

        self.AddActor2D(self.scalarBar)

    def RemoveScaleBar(self):
        """ Remove Color Scale Bar for Tonnes """
        if self.scalarBar:
            self.RemoveActor2D(self.scalarBar)

    def OnPolylabels(self, enable, fileType):
        if not self.model:
            return
        if enable:
            self.polylabels_create_actors(fileType)
        for _, label in self.model.polylabels.items():
            if enable:
                self.AddActor(label)
            else:
                self.RemoveActor(label)
        self.UpdateView(False)

    def polylabels_create_actors(self, fileType):
        if self.model and self.model.polylines:

            if fileType == FileType.DB:
                self.model.polylabels = {}
                self.model.polylabel_id = 1

            for polyline_id, polyline in self.model.polylines.items():
                actor = self.polylines_get_actor(polyline_id)
                label = ""
                if fileType == FileType.DB and self.heatmap:
                    route = polyline[0][4] if polyline[0][4] is not None else str(polyline_id)
                    tonelaje = polyline[0][5] if polyline[0][5] is not None else 0
                    label = f"{route}={tonelaje/1000000:,.1f}Mt"
                if fileType == FileType.DB and not self.heatmap:
                    route = polyline[0][4] if polyline[0][4] is not None else str(polyline_id)
                    label = f"{route}"
                elif fileType == FileType.XYZ or fileType == FileType.CSV:
                    label = f"{polyline_id}"
                label_actor = self.model.polylabels_create_actor(actor, label)
                self.model.polylabels[self.model.polylabel_id] = label_actor # Add to dictionary with current label actor
                self.model.polylabel_id += 1  # Increment for next label

    def CleanPolylabels(self):
        if not self.model:
            return
        for _, label in self.model.polylabels.items():
            self.RemoveActor(label)

    def OnPointLabels(self, enable, fileType):
        if not self.model:
            return
        if enable:
            self.pointlabels_create_actors(fileType)
        for _, label in self.model.pointlabels.items():
            if enable:
                self.AddActor(label)
            else:
                self.RemoveActor(label)
        self.UpdateView(False)

    def pointlabels_create_actors(self, fileType):
        if self.model and self.model.points:

            if fileType == FileType.DB:
                self.model.pointlabels = {}
                self.model.pointlabel_id = 1

            for point_id, point in self.model.points.items():
                actor = self.points_get_actor(point_id)
                label = ""
                if fileType == FileType.SRG or fileType == FileType.DB:
                    name = point[0][3] if point[0][3] is not None else ""
                    label = name.upper()
                label_actor = self.model.pointlabels_create_actor(actor, label)
                self.model.pointlabels[self.model.pointlabel_id] = label_actor # Add to dictionary with current label actor
                self.model.pointlabel_id += 1  # Increment for next label

    def CleanPointlabels(self):
        if not self.model:
            return
        for _, label in self.model.pointlabels.items():
            self.RemoveActor(label)

    def ValidSurfaces(self):
        if self.model and self.model.surfaces:
            return True
        else:
            return False

    def AddSurfaceActor(self):
        if self.surfaceActor:
            self.AddActor(self.surfaceActor)

    def RemoveSurfaceActor(self):
        if self.surfaceActor:
            self.RemoveActor(self.surfaceActor)

    def OnSurfaceReconstruction(self, enable, fileType, surfacecfg, delaunaycfg):
        if not self.model:
            return
        if self.ValidSurfaces():
            if enable:
                self.reconstruction_surface_actor(fileType, delaunaycfg)
                self.AddSurfaceActor()
            else:
                if not self.wireframe:
                    self.RemoveSurfaceActor()
            self.configSurface(surfacecfg)
            self.UpdateView(False)

    def OnWireframeReconstruction(self, enable, fileType, surfacecfg, delaunaycfg):
        if not self.model:
            return
        if self.ValidSurfaces():
            if enable:
                self.reconstruction_surface_actor(fileType, delaunaycfg)
                self.AddSurfaceActor()
            else:
                if not self.surface:
                    self.RemoveSurfaceActor()
            self.configSurface(surfacecfg)
            self.UpdateView(False)

    def reconstruction_surface_actor(self, fileType, delaunaycfg):
        if not self.model:
            return
        if self.surfaceActor:
            self.RemoveActor(self.surfaceActor)

        # Create a vtkAppendPolyData to combine all contour lines
        append_contours = vtk.vtkAppendPolyData()

        # Track if we have any valid surfaces to process
        valid_surfaces_found = False

        # Create contours at different surface elevations
        for surface_id, _ in self.model.surfaces.items():
            actor = self.surfaces_get_actor(surface_id)
            if actor:
                mapper = actor.GetMapper()
                if mapper:
                    polyData = mapper.GetInput()
                    if polyData and polyData.GetNumberOfPoints() > 0:
                        if fileType == FileType.XYZS or fileType == FileType.DB:
                            append_contours.AddInputData(polyData)
                            valid_surfaces_found = True

        # Only proceed if we found valid surfaces to process
        if valid_surfaces_found:
            append_contours.Update()
            contour_polydata = append_contours.GetOutput()
            self.surfaceActor = self.model.surface_reconstruction_actor(contour_polydata, delaunaycfg)
            if self.surfaceActor:
                self.AddActor(self.surfaceActor)
        else:
            print("No valid surfaces found for reconstruction")


    def configSurface(self, surfacecfg):
        surface_color = surfacecfg.surface_color
        wireframe_color= surfacecfg.wireframe_color
        surface_opacity = surfacecfg.surface_opacity
        edge_thickness= surfacecfg.edge_thickness
        if hasattr(self.surfaceActor, 'GetProperty'):
            property = getattr(self.surfaceActor, 'GetProperty')()
            if self.surface and self.wireframe:
                property.SetColor(surface_color)
                property.SetOpacity(surface_opacity)
                property.SetEdgeVisibility(True)
                property.SetEdgeColor(wireframe_color)
                property.SetLineWidth(edge_thickness)
                property.SetRepresentationToSurface()
            elif self.surface and not self.wireframe:
                property.SetColor(surface_color)
                property.SetOpacity(surface_opacity)
                property.SetEdgeVisibility(False)
                property.SetEdgeColor(wireframe_color)
                property.SetLineWidth(edge_thickness)
                property.SetRepresentationToSurface()
            elif not self.surface and self.wireframe:
                surface_color = wireframe_color
                property.SetColor(surface_color)
                property.SetOpacity(surface_opacity)
                property.SetEdgeVisibility(True)
                property.SetEdgeColor(wireframe_color)
                property.SetLineWidth(edge_thickness)
                property.SetRepresentationToWireframe()

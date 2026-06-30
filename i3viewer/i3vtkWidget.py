import vtk
import vtkmodules.qt.QVTKRenderWindowInteractor as QVTK
from PySide6.QtWidgets import QHBoxLayout, QWidget
from vtk import vtkActor

from i3viewer.i3enums import DelaunayCfg, FileType, Params, SurfaceCfg
from i3viewer.i3model import i3model
from i3viewer.i3point import NonModalDialog as PointDialog
from i3viewer.i3polyline import NonModalDialog as PolylineDialog


class i3vtkWidget(QWidget):

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def __init__(self, parent=None):
        super().__init__(parent)

        self.Parent = parent
        self.renderer = None
        self.interactor = None
        self.picker = None
        self.model = None

        self.actors = []
        self.contourActors = []
        self.contourActorsMap = {}
        self.contourDiffActors = []
        self.selected_actor = None
        self.surfaceActor = None
        self.wireframeActor = None

        self.TrihedronPos = 1
        self.ShowEdges = False
        self.heatmap = False
        self.unpick = False
        self.polylabel = False
        self.pointlabel = False
        self.surface = False
        self.wireframe = False
        self.contourdiff = False

        self.scalarBarActor = vtk.vtkScalarBarActor()
        self.contour_color = []
        self.delaunaycfg = DelaunayCfg()
        self.surfacecfg = SurfaceCfg()

        self.polylineDialog = PolylineDialog(0, 0, 0, [])
        self.pointDialog = PointDialog(0, 0, 0, 0, "")

        if self.Parent is None:
            self.resize(500, 500)
        else:
            self.resize(self.Parent.size())

        self.SetupWnd()

    # -------------------------------------------------------------------------
    # File Import
    # -------------------------------------------------------------------------

    def import_file(self, file_path, fileType, newFile):
        if self.model is None:
            self.model = i3model(file_path)
            self.model.contourColor = self.contour_color
        else:
            self.model.file_path = file_path

        if newFile:
            self.RemoveAllActors()
            self.actors = []
            self.model.polyline_id = 1
            self.model.point_id = 1
            self.model.surface_id = 1
            self.model.surface_file_id = 1

        cfg = (self.delaunaycfg, self.surfacecfg) \
            if (self.delaunaycfg and self.surfacecfg) \
            else (DelaunayCfg(), SurfaceCfg())

        existing_count = len(self.actors)

        if fileType == FileType.DB:
            if self.model.hasPointsTable():
                self.actors.extend(self.model.points_format_actors(fileType))
            if self.model.hasPolylinesTable():
                self.actors.extend(self.model.polylines_format_actors(fileType))
            if self.model.hasSurfacesTable():
                existing_contour_count = len(self.contourActors)
                self.contourActors.extend(self.model.surfaces_format_actors(fileType))
                new_contour_actors = self.contourActors[existing_contour_count:]
                self.contourActorsMap[self.model.surface_file_id] = new_contour_actors
                for actor in new_contour_actors:
                    self.AddActor(actor)
                self.surfaceActor = self.surface_reconstruction_actor(
                    fileType, *cfg, contour_actors=new_contour_actors)
                if self.surfaceActor:
                    self.surfaceActor.surface_file_id = self.model.surface_file_id
                    self.surfaceActor.actor_type = "surface"
                    self.actors.append(self.surfaceActor)
                self.wireframeActor = self.wireframe_reconstruction_actor(
                    fileType, *cfg, contour_actors=new_contour_actors)
                if self.wireframeActor:
                    self.wireframeActor.surface_file_id = self.model.surface_file_id
                    self.wireframeActor.actor_type = "wireframe"
                    self.actors.append(self.wireframeActor)
                self.model.surface_file_id += 1

        elif fileType in (FileType.XYZ, FileType.CSV):
            self.actors.extend(self.model.polylines_format_actors(fileType))
            self.polylabels_create_actors(fileType)

        elif fileType == FileType.SRG:
            self.actors.extend(self.model.points_format_actors(fileType))
            self.pointlabels_create_actors(fileType)

        elif fileType == FileType.XYZS:
            existing_contour_count = len(self.contourActors)
            self.contourActors.extend(self.model.surfaces_format_actors(fileType))
            new_contour_actors = self.contourActors[existing_contour_count:]
            self.contourActorsMap[self.model.surface_file_id] = new_contour_actors
            for actor in new_contour_actors:
                self.AddActor(actor)
            self.surfaceActor = self.surface_reconstruction_actor(
                fileType, *cfg, contour_actors=new_contour_actors)
            if self.surfaceActor:
                self.surfaceActor.surface_file_id = self.model.surface_file_id
                self.surfaceActor.actor_type = "surface"
                self.actors.append(self.surfaceActor)
            self.wireframeActor = self.wireframe_reconstruction_actor(
                fileType, *cfg, contour_actors=new_contour_actors)
            if self.wireframeActor:
                self.wireframeActor.surface_file_id = self.model.surface_file_id
                self.wireframeActor.actor_type = "wireframe"
                self.actors.append(self.wireframeActor)
            self.model.surface_file_id += 1

        for actor in self.actors[existing_count:]:
            self.AddActor(actor)

        self.UpdateView()

    # -------------------------------------------------------------------------
    # Actor Lookup
    # -------------------------------------------------------------------------

    def polylines_get_actor(self, polyline_id):
        """Return the VTK actor for the given polyline_id, or None."""
        for actor in self.actors:
            if hasattr(actor, "polyline_id") and actor.polyline_id == polyline_id:
                return actor
        return None

    def points_get_actor(self, point_id):
        """Return the VTK actor for the given point_id, or None."""
        for actor in self.actors:
            if hasattr(actor, "point_id") and actor.point_id == point_id:
                return actor
        return None

    def surfaces_get_actor(self, surface_id):
        """Return the VTK actor for the given surface_id, or None."""
        for actor in self.actors:
            if hasattr(actor, "surface_id") and actor.surface_id == surface_id:
                return actor
        return None

    def surfaces_get_surface_actor(self, surface_file_id):
        """Return the surface actor for the given surface_file_id, or None."""
        for actor in self.actors:
            if (hasattr(actor, "surface_file_id")
                    and actor.surface_file_id == surface_file_id
                    and hasattr(actor, "actor_type")
                    and actor.actor_type == "surface"):
                return actor
        return None

    def surfaces_get_wireframe_actor(self, surface_file_id):
        """Return the wireframe actor for the given surface_file_id, or None."""
        for actor in self.actors:
            if (hasattr(actor, "surface_file_id")
                    and actor.surface_file_id == surface_file_id
                    and hasattr(actor, "actor_type")
                    and actor.actor_type == "wireframe"):
                return actor
        return None

    # Sentinel returned by _clip_actor_against_fid_b when actor_a is
    # unaffected by every actor in actors_b (kept in place, untouched).
    _UNCHANGED = object()

    def contour_difference(self, fid_b):
        """Apply contour difference fid=1 minus fid_b, updating contour actors.

        Pairs actors from file A and file B that share the same z altitude.
        For each matching pair, reads geometry directly from the actors' VTK
        polydata, runs the boundary substitution algorithm, and swaps the A
        actor for the clipped result.

        Returns True if at least one actor was updated, False otherwise.
        """
        fid_a = 1

        actors_a = self.contourActorsMap.get(fid_a, [])
        actors_b = self.contourActorsMap.get(fid_b, [])
        if not actors_a or not actors_b:
            return False

        color   = self.model.contourColor or [1.0, 1.0, 0.0]
        changed = False
        new_actor_list = []

        for actor_a in actors_a:
            new_actor = self._clip_actor_against_fid_b(actor_a, actors_b, color)

            if new_actor is self._UNCHANGED:
                new_actor_list.append(actor_a)   # unaffected — keep in place
                continue

            changed = True
            self.RemoveActor(actor_a)
            if actor_a in self.contourActors:
                self.contourActors.remove(actor_a)

            if new_actor is not None:            # None → fully consumed
                new_actor.surface_id = actor_a.surface_id
                self.AddActor(new_actor)
                self.contourActors.append(new_actor)
                new_actor_list.append(new_actor)

        if not changed:
            return False

        self.contourActorsMap[fid_a] = new_actor_list
        self.UpdateView(False)
        return True

    def _clip_actor_against_fid_b(self, actor_a, actors_b, color):
        """Clip one A contour actor against every same-Z actor in actors_b.

        Returns:
            _UNCHANGED   — actor_a is unaffected (no B actor produced a result)
            None         — actor_a is fully consumed (should be removed)
            vtkActor     — the rebuilt, clipped actor to use in actor_a's place
        """
        if not hasattr(actor_a, "z") or not hasattr(actor_a, "surface_id"):
            return self._UNCHANGED

        z = actor_a.z
        combined_arcs = None

        for actor_b in actors_b:
            if not (hasattr(actor_b, "z") and actor_b.z == z):
                continue

            arcs, fills = i3model.contour_difference_clip_one_sid(
                actor_a, actor_b, z)
            # fills (B's inner boundary arcs) are intentionally discarded —
            # only A's clipped contour is visualized.

            if arcs is None:
                continue
            if not arcs:
                return None   # fully consumed
            combined_arcs = arcs

        if combined_arcs is None:
            return self._UNCHANGED

        poly = i3model.contour_difference_build_polydata(combined_arcs, [], z)
        return i3model.contour_difference_build_actor(poly, color, z)

    # -------------------------------------------------------------------------
    # Actor Management
    # -------------------------------------------------------------------------

    def RemoveAllActors(self):
        for actor in self.actors:
            self.RemoveActor(actor)
        self.actors = []
        self.RemoveContourActors()
        self.RemoveContourDiffActors()
        self.RemoveSurfaceActor()
        self.RemoveWireframeActor()
        self.RemoveScaleBarActor()
        self.contourActors = []
        self.contourActorsMap = {}
        self.contourDiffActors = []
        self.UpdateView()
        if self.model:
            self.model.RemoveAllActors()

    def AddActor(self, pvtkActor):
        if self.renderer is None:
            raise RuntimeError("Renderer is not initialized.")
        self.renderer.AddActor(pvtkActor)

    def RemoveActor(self, pvtkActor):
        if self.renderer is None:
            raise RuntimeError("Renderer is not initialized.")
        self.renderer.RemoveActor(pvtkActor)

    def AddActor2D(self, pvtkActor):
        if self.renderer is None:
            raise RuntimeError("Renderer is not initialized.")
        self.renderer.AddActor2D(pvtkActor)

    def RemoveActor2D(self, pvtkActor):
        if self.renderer is None:
            raise RuntimeError("Renderer is not initialized.")
        self.renderer.RemoveActor2D(pvtkActor)

    def polylines_update_data(self):
        if self.model:
            self.model.polylines_reread_table()

    # -------------------------------------------------------------------------
    # Picking & Selection
    # -------------------------------------------------------------------------

    def on_pick(self, obj, event):  # pyright: ignore[reportUnusedVariable]
        """Handle actor picking on left-button press."""
        _, _ = obj, event
        if (self.interactor is None
                or self.picker is None
                or self.renderer is None
                or self.unpick):
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
                self.select_actor(actor)
                self.show_dialog(actor)
        else:
            if self.selected_actor:
                self.deselect_actor(self.selected_actor)
                self.clear_dialog()

        self.UpdateView(False)

    def select_actor(self, actor):
        """Highlight a polyline or point actor on selection."""
        if self.model is None:
            return

        if hasattr(actor, "polyline_id") and actor.polyline_id in self.model.polylines:
            actor.GetProperty().SetColor(Params.SelectedColor.value)
            actor.GetProperty().SetLineWidth(Params.PolylineSelectedWidth.value)
        elif hasattr(actor, "point_id") and actor.point_id in self.model.points:
            actor.GetProperty().SetColor(Params.SelectedColor.value)
            actor = self.model.point_select(actor, Params.PointWinSelectedRadius.value)
        else:
            return

        self.selected_actor = actor

    def deselect_actor(self, actor):
        """Restore a polyline or point actor to its original appearance."""
        if self.model is None:
            return

        if hasattr(actor, "polyline_id") and hasattr(actor, "color"):
            if self.heatmap:
                color = getattr(actor, "rainbow_color")
                width = getattr(actor, "rainbow_width")
            else:
                color = getattr(actor, "color")
                width = Params.PolylineDefaultWidth.value
            actor.GetProperty().SetColor(color)
            actor.GetProperty().SetLineWidth(width)

        elif hasattr(actor, "point_id") and hasattr(actor, "color"):
            actor.GetProperty().SetColor(getattr(actor, "color"))
            self.model.point_select(actor, Params.PointWinRadius.value)

        else:
            return

        self.selected_actor = None

    # -------------------------------------------------------------------------
    # Dialogs
    # -------------------------------------------------------------------------

    def show_dialog(self, actor):
        """Show or update the info dialog for a selected polyline or point."""
        if self.model is None:
            return

        if hasattr(actor, "polyline_id"):
            polyline_id = actor.polyline_id
            points = self.model.polylines[polyline_id]
            num_points = len(points)
            polyline_length = self.calculate_polyline_length(points)

            if self.polylineDialog is None:
                self.polylineDialog = PolylineDialog(
                    polyline_id, num_points, polyline_length, points)
                self.polylineDialog.dialog_closed.connect(self.handle_dialog_closed)

            self.polylineDialog.show()
            self.polylineDialog.clear_dialog()
            self.polylineDialog.update_dialog(
                polyline_id, num_points, polyline_length, points)

        elif hasattr(actor, "point_id"):
            point_id = actor.point_id
            point_data = self.model.points[point_id]

            if self.pointDialog is None:
                self.pointDialog = PointDialog(point_id, *point_data[0])
                self.pointDialog.dialog_closed.connect(self.handle_dialog_closed)

            self.pointDialog.show()
            self.pointDialog.clear_dialog()
            self.pointDialog.update_dialog(point_id, *point_data[0])

    def hide_dialog(self):
        """Hide all open info dialogs."""
        if self.polylineDialog:
            self.polylineDialog.hide()
        if self.pointDialog:
            self.pointDialog.hide()

    def clear_dialog(self):
        """Clear content in all open info dialogs."""
        if self.polylineDialog:
            self.polylineDialog.clear_dialog()
        if self.pointDialog:
            self.pointDialog.clear_dialog()

    def handle_dialog_closed(self):
        """Clean up dialog references after they are closed."""
        if self.polylineDialog:
            self.polylineDialog = None
        if self.pointDialog:
            self.pointDialog = None

    def closeEvent(self, event):
        """Close open dialogs when the widget is closed."""
        if self.polylineDialog:
            self.polylineDialog.close()
        if self.pointDialog:
            self.pointDialog.close()
        event.accept()

    # -------------------------------------------------------------------------
    # Renderer & Window Setup
    # -------------------------------------------------------------------------

    def SetupWnd(self):
        self.SetupRenderer()
        self.SetupTrihedron()
        self.ResetCamera()

    def SetupRenderer(self):
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.2, 0.3, 0.4)

        self.interactor = QVTK.QVTKRenderWindowInteractor(self)
        self.trackball = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(self.trackball)

        render_window = self.interactor.GetRenderWindow()
        render_window.AddRenderer(self.renderer)
        render_window.PointSmoothingOn()
        render_window.LineSmoothingOn()

        layout = self.layout()
        if layout is None:
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
        layout.addWidget(self.interactor)

        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.005)
        self.interactor.SetPicker(self.picker)
        self.interactor.AddObserver("LeftButtonPressEvent", self.on_pick)

        self.interactor.Initialize()
        self.interactor.Start()

    def MakeAxesActor(self):
        """Build and return a configured vtkAxesActor."""
        axes = vtk.vtkAxesActor()
        axes.SetShaftTypeToLine()
        axes.SetXAxisLabelText("X")
        axes.SetYAxisLabelText("Y")
        axes.SetZAxisLabelText("Z")
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
        if not self.Trihedron:
            return
        width = max(width, 100)
        height = max(height, 100)
        if self.TrihedronPos == 1:  # Lower-left
            self.om1.SetViewport(0, 0, 200.0 / width, 200.0 / height)
        elif self.TrihedronPos == 2:  # Lower-right
            self.om1.SetViewport(1 - 200.0 / width, 0, 1, 200.0 / height)

    def paintEvent(self, event) -> None:
        """Resize the VTK render window to match the widget on repaint."""
        _ = event
        new_size = self.size()
        if self.interactor and self.interactor.GetRenderWindow():
            self.interactor.GetRenderWindow().SetSize(
                new_size.width(), new_size.height())
            self.interactor.GetRenderWindow().Render()
        self.ResizeTrihedron(new_size.width(), new_size.height())

    # -------------------------------------------------------------------------
    # Camera & View
    # -------------------------------------------------------------------------

    def UpdateView(self, resetCamera=True):
        if self.interactor is None:
            raise RuntimeError("Interactor is not initialized.")
        if resetCamera:
            self.ResetCamera()
        self.interactor.ReInitialize()
        self.interactor.GetRenderWindow().Render()
        self.repaint()

    def ResetCamera(self):
        if self.renderer is None:
            raise RuntimeError("Renderer is not initialized.")
        self.renderer.ResetCamera()
        self.camera = self.renderer.GetActiveCamera()
        self.camera.ParallelProjectionOn()

    def OnFrontView(self):
        focal = self.camera.GetFocalPoint()
        self.camera.SetPosition(focal[0], focal[1], focal[2] + 1)
        self.camera.SetViewUp(0, 1, 0)
        self.ResetCamera()
        self.UpdateView()

    def OnBackView(self):
        focal = self.camera.GetFocalPoint()
        self.camera.SetPosition(focal[0], focal[1], focal[2] - 1)
        self.camera.SetViewUp(0, 1, 0)
        self.ResetCamera()
        self.UpdateView()

    def OnTopView(self):
        focal = self.camera.GetFocalPoint()
        self.camera.SetPosition(focal[0], focal[1] + 1, focal[2])
        self.camera.SetViewUp(0, 0, -1)
        self.ResetCamera()
        self.UpdateView()

    def OnBottomView(self):
        focal = self.camera.GetFocalPoint()
        self.camera.SetPosition(focal[0], focal[1] - 1, focal[2])
        self.camera.SetViewUp(0, 0, 1)
        self.ResetCamera()
        self.UpdateView()

    def OnLeftView(self):
        focal = self.camera.GetFocalPoint()
        self.camera.SetPosition(focal[0] + 1, focal[1], focal[2])
        self.camera.SetViewUp(0, 1, 0)
        self.ResetCamera()
        self.UpdateView()

    def OnRightView(self):
        focal = self.camera.GetFocalPoint()
        self.camera.SetPosition(focal[0] - 1, focal[1], focal[2])
        self.camera.SetViewUp(0, 1, 0)
        self.ResetCamera()
        self.UpdateView()

    def OnIsometricView(self):
        focal = self.camera.GetFocalPoint()
        self.camera.SetPosition(focal[0] + 1, focal[1] + 1, focal[2] + 1)
        self.camera.SetViewUp(0, 1, 0)
        self.ResetCamera()
        self.UpdateView()

    def OnFitView(self):
        if self.renderer is None:
            raise RuntimeError("Renderer is not initialized.")
        self.renderer.ResetCameraClippingRange()
        self.ResetCamera()
        self.UpdateView()

    # -------------------------------------------------------------------------
    # Representation
    # -------------------------------------------------------------------------

    def SetRepresentation(self, aTyp):
        """Set actor representation mode.

        aTyp:
            1 – Points
            2 – Wireframe
            3 – Surface
            4 – Surface with edges
        """
        if self.renderer is None:
            raise RuntimeError("Renderer is not initialized.")

        for i in range(self.renderer.GetActors().GetNumberOfItems()):
            actor = self.renderer.GetActors().GetItemAsObject(i)
            if not isinstance(actor, vtkActor):
                continue
            prop = actor.GetProperty()
            if aTyp == 1:
                prop.SetRepresentationToPoints()
                prop.SetPointSize(4.0)
                self.ShowEdges = False
            elif aTyp == 2:
                prop.SetRepresentationToWireframe()
                self.ShowEdges = False
            elif aTyp == 3:
                prop.SetRepresentationToSurface()
                prop.EdgeVisibilityOff()
                self.ShowEdges = False
            elif aTyp == 4:
                prop.SetRepresentationToSurface()
                prop.EdgeVisibilityOn()
                self.ShowEdges = True

        self.UpdateView()

    # -------------------------------------------------------------------------
    # Heatmap
    # -------------------------------------------------------------------------

    def OnHeatMap(self, enable):
        if not (self.model and self.model.polylines):
            return

        self.heatmap = enable
        tonelajes = [
            polyline[0][5] if polyline[0][5] is not None else 0
            for polyline in self.model.polylines.values()
        ]
        min_tonelaje = min(tonelajes)
        max_tonelaje = max(tonelajes)

        for polyline_id, polyline in self.model.polylines.items():
            tonelaje = polyline[0][5] if polyline[0][5] is not None else 0
            actor = self.polylines_get_actor(polyline_id)

            if enable:
                color = self.rainbow_color(tonelaje, min_tonelaje, max_tonelaje)
                width = self.rainbow_width(tonelaje, min_tonelaje, max_tonelaje)
                setattr(actor, "rainbow_color", color)
                setattr(actor, "rainbow_width", width)
            else:
                color = getattr(actor, "color")
                width = Params.PolylineDefaultWidth.value

            if hasattr(actor, "GetProperty"):
                prop = getattr(actor, 'GetProperty')()
                prop.SetColor(color)
                prop.SetLineWidth(width)

        if enable:
            self.AddScaleBarActor()
        else:
            self.RemoveScaleBarActor()

        if self.polylabel:
            self.CleanPolylabels()
            self.OnPolylabels(self.polylabel, FileType.DB)
        else:
            self.UpdateView(False)

    def rainbow_color(self, tonne, min_tonne=0, max_tonne=100):
        """Map a tonne value to an RGB tuple using VTK's rainbow colormap."""
        lut = Params.LookupTable.value
        lut.SetTableRange(min_tonne, max_tonne)
        lut.Build()
        rgb = [0.0, 0.0, 0.0]
        lut.GetColor(tonne, rgb)
        return tuple(int(255 * c) for c in rgb)

    def rainbow_width(self, tonne, min_tonne, max_tonne):
        """Calculate proportional polyline width based on tonne value.

        Args:
            tonne: Current tonne value.
            min_tonne: Minimum of the data range.
            max_tonne: Maximum of the data range.

        Returns:
            float: Linearly interpolated width, clamped to [min_width, max_width].
        """
        min_width = Params.PolylineMinWidth.value
        max_width = Params.PolylineMaxWidth.value

        if min_tonne == max_tonne:
            return (min_width + max_width) / 2

        clamped = max(min_tonne, min(max_tonne, tonne))
        return min_width + (clamped - min_tonne) * (max_width - min_width) / (max_tonne - min_tonne)

    # -------------------------------------------------------------------------
    # Contour Diff — Period Browsing
    # -------------------------------------------------------------------------

    def OnContourDiff(self, enable):
        """Toggle the contour-diff period overlay on/off.

        Reads from model.contourdiff_polylines — the period most recently
        loaded by model.updateContourDiff() — and rebuilds a dedicated set
        of actors for it (self.contourDiffActors), kept separate from the
        route-polyline actors so toggling contour diff never touches the
        regular polyline rendering.

        Called both on initial toggle (i3main.on_contourdiff) and after
        every backward/forward period step (i3main._update_contourdiff_period),
        each time with the model's contourdiff_polylines already refreshed
        for the period to display.
        """
        self.contourdiff = enable

        self.RemoveContourDiffActors()
        self.contourDiffActors = []

        if enable and self.model:
            self.contourDiffActors = self.model.contourdiff_create_actors()
            self.AddContourDiffActors()

        self.UpdateView(False)

    # -------------------------------------------------------------------------
    # Scale Bar
    # -------------------------------------------------------------------------

    def AddScaleBarActor(self):
        """Add the colour scale bar (Mt) to the renderer."""
        lut = Params.LookupTable.value
        min_tonne, max_tonne = lut.GetTableRange()
        lut.SetTableRange(min_tonne / 1_000_000, max_tonne / 1_000_000)
        lut.Build()

        self.scalarBarActor.SetLookupTable(lut)
        self.scalarBarActor.SetTitle("Mt     ")
        self.scalarBarActor.SetNumberOfLabels(5)
        self.scalarBarActor.SetPosition(0.85, 0.1)
        self.scalarBarActor.SetWidth(0.04)
        self.scalarBarActor.SetHeight(0.8)
        self.scalarBarActor.SetLabelFormat("%.1f")

        title_prop = self.scalarBarActor.GetTitleTextProperty()
        title_prop.SetColor(1, 1, 0)
        title_prop.SetFontSize(14)

        label_prop = self.scalarBarActor.GetLabelTextProperty()
        label_prop.SetColor(1, 1, 0)
        label_prop.SetFontSize(12)

        self.AddActor2D(self.scalarBarActor)

    def RemoveScaleBarActor(self):
        """Remove the colour scale bar from the renderer."""
        if self.scalarBarActor:
            self.RemoveActor2D(self.scalarBarActor)

    # -------------------------------------------------------------------------
    # Polyline Labels
    # -------------------------------------------------------------------------

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
        if not (self.model and self.model.polylines):
            return

        if fileType == FileType.DB:
            self.model.polylabels = {}
            self.model.polylabel_id = 1

        for polyline_id, polyline in self.model.polylines.items():
            actor = self.polylines_get_actor(polyline_id)
            row = polyline[0]

            if fileType == FileType.DB and self.heatmap:
                route = row[4] if row[4] is not None else str(polyline_id)
                tonelaje = row[5] if row[5] is not None else 0
                label = f"{route}={tonelaje / 1_000_000:,.1f}Mt"
            elif fileType == FileType.DB and not self.heatmap:
                route = row[4] if row[4] is not None else str(polyline_id)
                label = f"{route}"
            elif fileType in (FileType.XYZ, FileType.CSV):
                label = f"{polyline_id}"
            else:
                label = ""

            label_actor = self.model.polylabels_create_actor(actor, label)
            self.model.polylabels[self.model.polylabel_id] = label_actor
            self.model.polylabel_id += 1

    def CleanPolylabels(self):
        if not self.model:
            return
        for _, label in self.model.polylabels.items():
            self.RemoveActor(label)

    # -------------------------------------------------------------------------
    # Point Labels
    # -------------------------------------------------------------------------

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
        if not (self.model and self.model.points):
            return

        if fileType == FileType.DB:
            self.model.pointlabels = {}
            self.model.pointlabel_id = 1

        for point_id, point in self.model.points.items():
            actor = self.points_get_actor(point_id)
            label = ""
            if fileType in (FileType.SRG, FileType.DB):
                name = point[0][3] if point[0][3] is not None else ""
                label = name.upper()

            label_actor = self.model.pointlabels_create_actor(actor, label)
            self.model.pointlabels[self.model.pointlabel_id] = label_actor
            self.model.pointlabel_id += 1

    def CleanPointlabels(self):
        if not self.model:
            return
        for _, label in self.model.pointlabels.items():
            self.RemoveActor(label)

    # -------------------------------------------------------------------------
    # Surface & Wireframe
    # -------------------------------------------------------------------------

    def ValidSurfaces(self):
        return bool(self.model and self.model.surfaces)

    def AddSurfaceActor(self):
        if self.surfaceActor:
            self.AddActor(self.surfaceActor)

    def RemoveSurfaceActor(self):
        if self.surfaceActor:
            self.RemoveActor(self.surfaceActor)

    def AddContourActors(self):
        for actor in self.contourActors:
            self.AddActor(actor)

    def RemoveContourActors(self):
        for actor in self.contourActors:
            self.RemoveActor(actor)

    def AddContourDiffActors(self):
        for actor in self.contourDiffActors:
            self.AddActor(actor)

    def RemoveContourDiffActors(self):
        for actor in self.contourDiffActors:
            self.RemoveActor(actor)

    def UpdateColorContourActors(self, color):
        for actor in self.contourActors:
            if hasattr(actor, "GetProperty"):
                actor.GetProperty().SetColor(color)

    def AddWireframeActor(self):
        if self.wireframeActor:
            self.AddActor(self.wireframeActor)

    def RemoveWireframeActor(self):
        if self.wireframeActor:
            self.RemoveActor(self.wireframeActor)

    def SetVisibilitySurfaceActor(self, surface_file_id, visible):
        """Show or hide the surface actor for the given surface_file_id."""
        actor = self.surfaces_get_surface_actor(surface_file_id)
        if actor:
            actor.SetVisibility(1 if visible else 0)

    def SetVisibilityWireframeActor(self, surface_file_id, visible):
        """Show or hide the wireframe actor for the given surface_file_id."""
        actor = self.surfaces_get_wireframe_actor(surface_file_id)
        if actor:
            actor.SetVisibility(1 if visible else 0)

    def SetVisibilityContourActors(self, surface_file_id, visible):
        """Show or hide all contour actors for the given surface_file_id."""
        for actor in self.contourActorsMap.get(surface_file_id, []):
            actor.SetVisibility(1 if visible else 0)

    def _build_contour_polydata(self, fileType, contour_actors=None):
        """Combine surface actor poly data into a single vtkPolyData."""
        if contour_actors is None:
            contour_actors = self.contourActors
        append = vtk.vtkAppendPolyData()
        for actor in contour_actors:
            mapper = actor.GetMapper()
            if mapper:
                poly_data = mapper.GetInput()
                if poly_data and poly_data.GetNumberOfPoints() > 0:
                    if fileType in (FileType.XYZS, FileType.DB):
                        append.AddInputData(poly_data)
        append.Update()
        return append.GetOutput()

    def surface_reconstruction_actor(self, fileType, delaunaycfg, surfacecfg,
                                      contour_actors=None):
        if not self.model:
            return None
        contour_polydata = self._build_contour_polydata(fileType, contour_actors)
        return self.model.surface_reconstruction_actor(
            contour_polydata, delaunaycfg, surfacecfg)

    def wireframe_reconstruction_actor(self, fileType, delaunaycfg, surfacecfg,
                                        contour_actors=None):
        if not self.model:
            return None
        contour_polydata = self._build_contour_polydata(fileType, contour_actors)
        return self.model.wireframe_reconstruction_actor(
            contour_polydata, delaunaycfg, surfacecfg)

    def UpdateSurface(self, fileType):
        cfg = self.delaunaycfg, self.surfacecfg

        for fid, contour_actors in self.contourActorsMap.items():
            # Remove and replace surface actor for this file
            old_surface = self.surfaces_get_surface_actor(fid)
            if old_surface:
                self.RemoveActor(old_surface)
                self.actors.remove(old_surface)

            new_surface = self.surface_reconstruction_actor(
                fileType, *cfg, contour_actors=contour_actors)
            if new_surface:
                new_surface.surface_file_id = fid
                new_surface.actor_type = "surface"
                self.actors.append(new_surface)
                self.AddActor(new_surface)
                self.surfaceActor = new_surface

            # Remove and replace wireframe actor for this file
            old_wireframe = self.surfaces_get_wireframe_actor(fid)
            if old_wireframe:
                self.RemoveActor(old_wireframe)
                self.actors.remove(old_wireframe)

            new_wireframe = self.wireframe_reconstruction_actor(
                fileType, *cfg, contour_actors=contour_actors)
            if new_wireframe:
                new_wireframe.surface_file_id = fid
                new_wireframe.actor_type = "wireframe"
                self.actors.append(new_wireframe)
                self.AddActor(new_wireframe)
                self.wireframeActor = new_wireframe

    # -------------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------------

    def calculate_polyline_length(self, polyline):
        """Return the total 3-D length of a polyline, rounded to 3 decimal places."""
        length = 0.0
        for i in range(1, len(polyline)):
            x1, y1, z1, *_ = polyline[i - 1]
            x2, y2, z2, *_ = polyline[i]
            length += ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5
        return round(length, 3)

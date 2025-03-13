import sys

from PySide6.QtGui import QStandardItemModel
import vtk
import vtkmodules.qt.QVTKRenderWindowInteractor as QVTK
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtWidgets import QHBoxLayout
from vtk import vtkActor

from i3viewer.i3model import i3model
from i3viewer.i3pick import NonModalDialog as Dialog

class i3vtkWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.Parent = parent
        self.renderer = None
        self.interactor = None
        self.model = None
        self.actors = None
        self.TrihedronPos = 1
        self.selected_actor = None
        self.dialog = None
        
        if self.Parent == None:
            self.resize(500, 500)
        else:
            self.resize(self.Parent.size())
            
        self.ShowEdges = False
        self.SetupWnd()

    def import_file(self, file_path):
        if self.actors:
            for actor in self.actors:
                self.RemoveActor(actor)        
        self.model = i3model(file_path)
        self.actors = self.model.format_data()
        for actor in self.actors:
            self.AddActor(actor)
        self.SetRepresentation(2)  # Surface with edges

    def get_model(self):
        if self.model:
            return self.model

    def calculate_polyline_length(self, polyline):
        """Calculates the total length of a polyline."""
        length = 0.0
        for i in range(1, len(polyline)):
            x1, y1, z1 = polyline[i - 1]
            x2, y2, z2 = polyline[i]
            length += ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2) ** 0.5
        return round(length, 3)

    def on_pick(self, obj, event):
        click_pos = self.interactor.GetEventPosition()
        self.picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)
        actor = self.picker.GetActor()

        if actor:
            if self.selected_actor == actor:
                # Deselect the currently selected polyline
                original_color = self.model.colors[actor.polyline_id]
                actor.GetProperty().SetColor(original_color)
                actor.GetProperty().SetLineWidth(2.0)
                self.selected_actor = None
                if self.dialog:
                    self.dialog.reset_dialog()                
                #print("Polyline deselected.")
            else:
                # Deselect previously selected polyline (if any)
                if self.selected_actor:
                    original_color = self.model.colors[self.selected_actor.polyline_id]
                    self.selected_actor.GetProperty().SetColor(original_color)
                    self.selected_actor.GetProperty().SetLineWidth(2.0)

                # Select new polyline
                actor.GetProperty().SetColor(1, 1, 0)  # Yellow color
                actor.GetProperty().SetLineWidth(5.0)
                self.selected_actor = actor

                # Display polyline information
                number_points = len(self.model.polylines[actor.polyline_id])
                polyline_length = self.calculate_polyline_length(self.model.polylines[actor.polyline_id])
                points = self.model.polylines[actor.polyline_id]

                polyline_id = actor.polyline_id
                num_points = number_points
                length = polyline_length
                points = self.model.polylines[actor.polyline_id]

                # Create and show the non-modal dialog
                if self.dialog is None:
                    self.dialog = Dialog(polyline_id, num_points, length, points)
                    # Connect the dialog's custom signal to a slot in MainWindow
                    self.dialog.dialog_closed.connect(self.handle_dialog_closed)
                    self.dialog.show()  # Use show() to make it non-modal
                
                self.dialog.reset_dialog()
                self.dialog.update_dialog(polyline_id, num_points, length, points)                                        
        else:
            # If no polyline is picked, deselect any currently selected one
            if self.selected_actor:
                original_color = self.model.colors[self.selected_actor.polyline_id]
                self.selected_actor.GetProperty().SetColor(original_color)
                self.selected_actor.GetProperty().SetLineWidth(2.0)
                self.selected_actor = None
                if self.dialog:
                    self.dialog.reset_dialog()
                #print("No polyline selected. Previous selection cleared.")

        self.UpdateView()

    def handle_dialog_closed(self):
        """Handle the dialog_closed signal to clean up the dialog reference."""
        self.dialog = None  # Set the dialog reference to None
        #print("Dialog closed and reference cleaned up.")

    def closeEvent(self, event):
        """Override closeEvent to close the dialog when the application is closed."""
        if self.dialog is not None:
            self.dialog.close()  # Close the dialog
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
        self.picker.SetTolerance(0.01)
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
        # Get the new size of the widget
        new_size = self.size()

        # Resize the VTK render window to match the widget size
        if self.interactor and self.interactor.GetRenderWindow():
            self.interactor.GetRenderWindow().SetSize(new_size.width(), new_size.height())
            self.interactor.GetRenderWindow().Render()  # Force a re-render
        self.ResizeTrihedron(new_size.width(), new_size.height())

    def UpdateView(self):
        if self.interactor is None:
            raise RuntimeError("self.interactor could not be created.")
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
        if self.ShowEdges:
            pvtkActor.GetProperty().EdgeVisibilityOn()

        if self.renderer is None:
            raise RuntimeError("self.interactor could not be created.")
        self.renderer.AddActor(pvtkActor)
        self.ResetCamera()

    def RemoveActor(self, pvtkActor):
        if self.renderer is None:
            raise RuntimeError("self.interactor could not be created.")
        self.renderer.RemoveActor(pvtkActor)
        self.ResetCamera()

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
            raise RuntimeError("self.interactor could not be created.");
        self.renderer.ResetCameraClippingRange()
        self.ResetCamera()
        self.UpdateView()

if __name__ == "__main__":
    app = QApplication.instance()  # Check for existing instance
    if app is None:  # Create only if it doesn't exist
        app = QApplication(sys.argv)
    window = vtkViewer()
    window.setWindowTitle("QWidget's QVTKRenderWindowInteractor")
    window.show()
    sys.exit(app.exec())

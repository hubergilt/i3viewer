import sys

from PySide6.QtGui import QStandardItemModel
import vtk
import vtkmodules.qt.QVTKRenderWindowInteractor as QVTK
from PySide6.QtWidgets import QApplication, QWidget
from vtk import vtkActor

from i3viewer.i3model import i3model


class i3vtkWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.Parent = parent
        self.renderer = None
        self.interactor = None
        self.model = None
        self.actor = None
        self.TrihedronPos = 1

        if self.Parent == None:
            self.resize(500, 500)
        self.ShowEdges = False
        self.SetupWnd()

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

    def import_file(self, file_path):
        if self.actor is not None:
            self.RemoveActor(self.actor)
        self.model = i3model(file_path)
        self.actor = self.model.format_data()
        self.AddActor(self.actor)
        self.SetRepresentation(2)  # Surface with edges

    def get_model(self):
        if self.model:
            return self.model

if __name__ == "__main__":
    app = QApplication.instance()  # Check for existing instance
    if app is None:  # Create only if it doesn't exist
        app = QApplication(sys.argv)
    window = vtkViewer()
    window.setWindowTitle("QWidget's QVTKRenderWindowInteractor")
    window.show()
    sys.exit(app.exec())

import random
import sqlite3

import vtk
from PySide6.QtGui import QStandardItem, QStandardItemModel


class i3model:
    def __init__(self, file_path):
        self.file_path = file_path
        self.polylines = {}
        self.poly_data = vtk.vtkPolyData()

    def read_xyz_file(self):
        """Reads the XYZ file and stores polylines."""
        self.polylines = {}
        polyline_id = 0
        self.polylines[polyline_id] = []

        with open(self.file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line == "$":
                    polyline_id += 1  # Start a new polyline
                    self.polylines[polyline_id] = []
                else:
                    parts = line.split()
                    if len(parts) == 3:
                        x, y, z = map(
                            lambda v: round(float(v), 3), parts
                        )  # Round to 3 decimals
                        self.polylines[polyline_id].append((x, y, z))

        self.polylines = {
            k: v for k, v in self.polylines.items() if v
        }  # Remove empty polylines

    def save_to_database(self, db_path):
        """Saves the polylines data into the SQLite database."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS polylines (
                polyline_id INTEGER NOT NULL,
                point_id INTEGER NOT NULL,
                X REAL,
                Y REAL,
                Z REAL,
                "velocidad máxima" REAL,
                "tonelaje de material por carretera" REAL,
                "resistencia a la rodadura" REAL,
                "límite máximo de velocidad" REAL,
                "velocidad de frenado" REAL,
                "rimpull" REAL,
                "retardo" REAL,
                "consumo de combustible" REAL,
                "nombre de la ruta" TEXT,
                PRIMARY KEY (polyline_id, point_id)
            )
        """
        )

        # Clear table before inserting new data
        cursor.execute("DELETE FROM polylines")

        for polyline_id, points in self.polylines.items():
            point_id = 1
            for x, y, z in points:
                cursor.execute(
                    "INSERT INTO polylines (polyline_id, point_id, X, Y, Z) VALUES (?, ?, ?, ?, ?)",
                    (polyline_id + 1, point_id, x, y, z),
                )
                point_id += 1

        conn.commit()
        conn.close()

    def create_vtk_polylines(self):
        """Creates VTK polyline geometry from the parsed data."""
        points = vtk.vtkPoints()
        cells = vtk.vtkCellArray()
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)  # RGB format
        colors.SetName("Colors")

        point_index = 0

        for polyline_id, vertices in self.polylines.items():
            polyline = vtk.vtkPolyLine()
            polyline.GetPointIds().SetNumberOfIds(len(vertices))

            # Generate a random color for the polyline
            color = [random.randint(0, 255) for _ in range(3)]

            for i, (x, y, z) in enumerate(vertices):
                points.InsertNextPoint(x, y, z)
                polyline.GetPointIds().SetId(i, point_index)
                # Assign color to each point
                colors.InsertNextTypedTuple(color)
                point_index += 1

            cells.InsertNextCell(polyline)

        self.poly_data.SetPoints(points)
        self.poly_data.SetLines(cells)
        self.poly_data.GetPointData().SetScalars(colors)  # Assign colors to the points

    def visualize_polylines(self):
        """Displays the VTK polyline geometry."""
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderer.SetBackground(0.1, 0.1, 0.1)  # Dark background

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)

        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        render_window.Render()
        interactor.Start()

    def format_actor(self):
        """Displays the VTK polyline geometry."""
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        return actor

    def format_data(self):
        """Executes the full pipeline."""
        self.read_xyz_file()
        # self.save_to_database()
        self.create_vtk_polylines()
        return self.format_actor()

    def format_tree(self, file_path, file_name):
        polyline_count = len(self.polylines)
        tree_model = QStandardItemModel()
        root_item = QStandardItem(f"{file_name} ({polyline_count} polylines)")

        for polyline_idx, (polyline_id, points) in enumerate(
            self.polylines.items(), start=1
        ):
            polyline_item = QStandardItem(f"Polyline {polyline_idx}")
            for idx, (x, y, z) in enumerate(points, start=1):
                point_item = QStandardItem(
                    f"Point {idx} (X={x:.3f}, Y={y:.3f}, Z={z:.3f})"
                )
                polyline_item.appendRow(point_item)
            root_item.appendRow(polyline_item)

        tree_model.appendRow(root_item)
        tree_model.setHorizontalHeaderLabels([file_path])
        return tree_model

    def run(self):
        """Executes the full pipeline."""
        self.read_xyz_file()
        self.save_to_database()
        self.create_vtk_polylines()
        self.visualize_polylines()


if __name__ == "__main__":
    model = i3model("data.xyz")
    model.run()

import random
import sqlite3

import vtk
from PySide6.QtGui import QStandardItem, QStandardItemModel
import math


class i3model:
    def __init__(self, file_path):
        self.file_path = file_path
        self.polylines = {}
        self.poly_data = vtk.vtkPolyData()
        self.actors = []
        self.colors = {}

    def format_data(self):
        """Executes the full pipeline."""
        self.read_xyz_file()
        self.create_vtk_polylines()
        return self.actors      


    def read_xyz_file(self):
        """Reads the XYZ file and stores polylines with gradient values (multiplied by 100)."""
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

                        # Compute gradient
                        if not self.polylines[polyline_id]:  # First point in polyline
                            gradient = 0.0
                        else:
                            prev_x, prev_y, prev_z, _ = self.polylines[polyline_id][-1]
                            delta_z = z - prev_z
                            distance = math.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2)
                            gradient = (delta_z / distance) * 100 if distance != 0 else 0.0  # Multiply by 100

                        # Append the point with gradient
                        self.polylines[polyline_id].append((x, y, z, round(gradient, 3)))  # Round gradient to 3 decimals

        # Remove empty polylines
        self.polylines = {k: v for k, v in self.polylines.items() if v}

    def create_vtk_polylines(self):
        """Creates separate VTK actors for each polyline, using the modified self.polylines dictionary."""
        self.actors = []
        
        for polyline_id, vertices in self.polylines.items():
            points = vtk.vtkPoints()
            cells = vtk.vtkCellArray()
            polyline = vtk.vtkPolyLine()
            polyline.GetPointIds().SetNumberOfIds(len(vertices))
            
            # Generate a random color for the polyline
            color = [random.randint(0, 255) / 255.0 for _ in range(3)]
            self.colors[polyline_id] = color
            
            # Iterate over vertices (x, y, z, gradient)
            for i, (x, y, z, _) in enumerate(vertices):
                point_id = points.InsertNextPoint(x, y, z)
                polyline.GetPointIds().SetId(i, point_id)
            
            cells.InsertNextCell(polyline)
            
            # Create poly data
            poly_data = vtk.vtkPolyData()
            poly_data.SetPoints(points)
            poly_data.SetLines(cells)
            
            # Create mapper
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(poly_data)
            
            # Create actor
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(color)
            actor.GetProperty().SetLineWidth(2.0)
            actor.polyline_id = polyline_id
            
            self.actors.append(actor)

    def format_tree(self, file_path, file_name):
        polyline_count = len(self.polylines)
        tree_model = QStandardItemModel()
        root_item = QStandardItem(f"{file_name} ({polyline_count} polylines)")

        for polyline_idx, (polyline_id, points) in enumerate(
            self.polylines.items(), start=1
        ):
            polyline_item = QStandardItem(f"Polyline {polyline_idx}")
            for idx, (x, y, z, _) in enumerate(points, start=1):
                point_item = QStandardItem(
                    f"Point {idx} (X={x:.3f}, Y={y:.3f}, Z={z:.3f})"
                )
                polyline_item.appendRow(point_item)
            root_item.appendRow(polyline_item)

        tree_model.appendRow(root_item)
        tree_model.setHorizontalHeaderLabels([file_path])
        return tree_model
        
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
                "gradient" REAL,
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
            for x, y, z, g in points:
                cursor.execute(
                    "INSERT INTO polylines (polyline_id, point_id, X, Y, Z, gradient) VALUES (?, ?, ?, ?, ?, ?)",
                    (polyline_id + 1, point_id, x, y, z, g),
                )
                point_id += 1

        conn.commit()
        conn.close()
        

    def run(self):
        """Executes the full pipeline."""
        self.read_xyz_file()
        self.save_to_database()
        self.create_vtk_polylines()
        self.visualize_polylines()


if __name__ == "__main__":
    model = i3model("data.xyz")
    model.run()

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

    def polylines_format_actors(self, fromFile=True):
        """Executes the full pipeline."""
        if fromFile:
            self.polylines_read_file()
        else:
            self.polylines_read_table()
        self.polylines_create_actors()
        return self.actors

    def polylines_read_file(self):
        """Reads the XYZ file and stores polylines with gradient values (multiplied by 100)."""
        self.polylines = {}
        polyline_id = 1
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

    
    def polylines_read_table(self):
        """Fetch polylines grouped by polyline_id from the SQLite database."""
        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT polyline_id, X, Y, Z, gradient,
                "velocidad máxima",
                "tonelaje de material por carretera",
                "resistencia a la rodadura",
                "límite máximo de velocidad",
                "velocidad de frenado",
                "rimpull",
                "retardo",
                "consumo de combustible",
                "nombre de la ruta"
                FROM polylines ORDER BY polyline_id, point_id
            """)
        data = cursor.fetchall()
        
        conn.close()

        self.polylines = {}
        for polyline_id, x, y, z, g, *rest in data:
            if polyline_id not in self.polylines:
                self.polylines[polyline_id] = []
            self.polylines[polyline_id].append((x, y, z, g, *rest))
        
    def polylines_create_actors(self):
        """Creates separate VTK actors for each polyline in self.polylines."""
        self.actors = []
        self.colors = {}

        for polyline_id, vertices in self.polylines.items():
            actor = self.create_actor(polyline_id, vertices)
            if actor:
                self.actors.append(actor)

    def create_actor(self, polyline_id, vertices):
        """Creates a VTK actor for a given polyline."""
        if not vertices:
            return None  # Ignore empty polylines

        points = vtk.vtkPoints()
        cells = vtk.vtkCellArray()
        polyline = vtk.vtkPolyLine()
        polyline.GetPointIds().SetNumberOfIds(len(vertices))

        # Generate and store a random color for this polyline
        color = [random.randint(0, 255) / 255.0 for _ in range(3)]
        self.colors[polyline_id] = color

        # Insert points and define polyline connectivity
        for i, (x, y, z, *_) in enumerate(vertices):
            point_id = points.InsertNextPoint(x, y, z)
            polyline.GetPointIds().SetId(i, point_id)

        cells.InsertNextCell(polyline)

        # Create and configure polyline actor
        return self.build_actor(points, cells, color, polyline_id)

    def build_actor(self, points, cells, color, polyline_id):
        """Helper function to construct and return a VTK actor."""
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetLines(cells)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(2.0)
        actor.polyline_id = polyline_id

        return actor
        
    def actor_by_id(self, polyline_id):
        """Returns the VTK actor associated with the given polyline_id, or None if not found."""
        for actor in self.actors:
            if hasattr(actor, "polyline_id") and actor.polyline_id == polyline_id:
                return actor
        return None        
            
    def polylines_save_database(self, db_path):
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
            for x, y, z, g, *rest in points:
                cursor.execute(
                    "INSERT INTO polylines (polyline_id, point_id, X, Y, Z, gradient) VALUES (?, ?, ?, ?, ?, ?)",
                    (polyline_id, point_id, x, y, z, g),
                )
                point_id += 1

        conn.commit()
        conn.close()

import random
import sqlite3

import vtk
import math
import csv
import sys

class i3model:
    def __init__(self, file_path):
        self.file_path = file_path

        self.polylines = {}
        self.points = {}

        self.polyline_id = 1
        self.point_id = 1

        self.actors = []

    def polylines_format_actors(self, fromFile=True):
        """Executes the full pipeline."""
        polylines = None
        if fromFile:
            polylines = self.polylines_read_file()
        else:
            polylines = self.polylines_read_table()

        if polylines:
            self.polylines.update(polylines)
        return self.polylines_create_actors()

    def polylines_read_file(self):
        """Reads the XYZ file and stores polylines with gradient values (multiplied by 100)."""
        polylines = {}
        polylines[self.polyline_id] = []

        with open(self.file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line == "$":
                    self.polyline_id += 1  # Start a new polyline
                    polylines[self.polyline_id] = []
                else:
                    parts = line.split()
                    if len(parts) == 3:
                        x, y, z = map(
                            lambda v: round(float(v), 3), parts
                        )  # Round to 3 decimals

                        # Compute gradient
                        if not polylines[self.polyline_id]:  # First point in polyline
                            gradient = 0.0
                        else:
                            prev_x, prev_y, prev_z, _ = polylines[self.polyline_id][-1]
                            delta_z = z - prev_z
                            distance = math.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2)
                            gradient = (delta_z / distance) * 100 if distance != 0 else 0.0  # Multiply by 100

                        # Append the point with gradient
                        polylines[self.polyline_id].append((x, y, z, round(gradient, 3)))  # Round gradient to 3 decimals

        # Remove empty polylines
        polylines = {k: v for k, v in polylines.items() if v}
        return polylines

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

        polylines = {}
        for polyline_id, x, y, z, g, *rest in data:
            if polyline_id not in polylines:
                polylines[polyline_id] = []
            polylines[polyline_id].append((x, y, z, g, *rest))
        return polylines

    def polylines_create_actors(self):
        """Creates separate VTK actors for each polyline in self.polylines."""
        self.actors = []

        for polyline_id, vertices in self.polylines.items():
            actor = self.polylines_create_actor(polyline_id, vertices)
            if actor:
                self.actors.append(actor)

        return self.actors

    def polylines_create_actor(self, polyline_id, vertices):
        """Creates a VTK actor for a given polyline."""
        if not vertices:
            return None  # Ignore empty polylines

        points = vtk.vtkPoints()
        cells = vtk.vtkCellArray()
        polyline = vtk.vtkPolyLine()
        polyline.GetPointIds().SetNumberOfIds(len(vertices))

        # Generate and store a random color for this polyline
        color = [random.randint(0, 255) / 255.0 for _ in range(3)]

        # Insert points and define polyline connectivity
        for i, (x, y, z, *_) in enumerate(vertices):
            point_id = points.InsertNextPoint(x, y, z)
            polyline.GetPointIds().SetId(i, point_id)

        cells.InsertNextCell(polyline)

        # Create and configure polyline actor
        return self.polylines_build_actor(points, cells, color, polyline_id)

    def polylines_build_actor(self, points, cells, color, polyline_id):
        """Helper function to construct and return a VTK actor."""
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetLines(cells)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(2)
        setattr(actor, "polyline_id", polyline_id)
        setattr(actor, "color", color)
        return actor

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
            for x, y, z, g, *_ in points:
                cursor.execute(
                    "INSERT INTO polylines (polyline_id, point_id, X, Y, Z, gradient) VALUES (?, ?, ?, ?, ?, ?)",
                    (polyline_id, point_id, x, y, z, g),
                )
                point_id += 1

        conn.commit()
        conn.close()

    def points_format_actors(self, fromFile=True):
        """Executes the full pipeline."""
        points = None
        if fromFile:
            points = self.points_read_file()
        else:
            points = self.points_read_table()

        if points:
            self.points.update(points)

        return self.points_create_actors()

    def points_read_file(self):
        """Reads the SRG file and store points"""

        points = {}
        points[self.point_id] = []

        with open(self.file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)

            for row in reader:
                if len(row) < 6:
                    continue  # Skip invalid lines

                try:
                    x = float(row[0])
                    y = float(row[1])
                    z = float(row[2])
                    name = row[5]

                    points[self.point_id] = [(x, y, z, name)]
                    self.point_id += 1
                except ValueError:
                    continue  # Skip lines with conversion errors
        return points

    def points_read_table(self):
        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()

        # Query for points
        cursor.execute(
            """
            SELECT point_id, X, Y, Z, name
            FROM points ORDER BY point_id
            """
        )

        data = cursor.fetchall()
        conn.close()

        points = {}
        for point_id, x, y, z, name in data:
            if point_id not in points:
                points[point_id] = []
            points[point_id].append((x, y, z, name))

        return points


    def points_create_actors(self):
        """Creates separate VTK actors for each point in self.points."""
        self.actors = []
        #self.colors = {}

        for point_id, vertices in self.points.items():
            actor = self.point_create_actor(point_id, vertices)
            if actor:
                self.actors.append(actor)

        return self.actors

    def point_create_actor(self, point_id, vertices):
        """Creates a VTK actor for a given point."""
        if not vertices:
            return None  # Ignore empty points

        points = vtk.vtkPoints()
        vertices_cell = vtk.vtkCellArray()

        # Generate and store a random color for this point
        color = [random.randint(0, 255) / 255.0 for _ in range(3)]
        #self.colors[point_id] = color

        # Insert points
        x, y, z, _ = vertices[0]
        vertex_id = points.InsertNextPoint(x, y, z)
        vertices_cell.InsertNextCell(1)
        vertices_cell.InsertCellPoint(vertex_id)

        # Create and configure point actor
        if sys.platform.startswith('win'):
            return self.point_build_actor_win(points, vertices_cell, color, point_id)
        else:
            return self.point_build_actor(points, vertices_cell, color, point_id)

    def point_build_actor_win(self, points, vertices_cell, color, point_id):
        # Create polydata
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetVerts(vertices_cell)

        # Create a sphere source for glyphing
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(20)  # Size of each sphere
        sphere.SetThetaResolution(20)
        sphere.SetPhiResolution(20)

        # Create glyph3D filter
        glyph = vtk.vtkGlyph3D()
        glyph.SetInputData(poly_data)
        glyph.SetSourceConnection(sphere.GetOutputPort())
        glyph.SetScaleModeToDataScalingOff()

        # Mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(glyph.GetOutputPort())

        # Actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        #actor.GetProperty().SetRepresentationToPoints()
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetPointSize(5.0)
        actor.GetProperty().SetOpacity(1.0)

        # Custom point ID attribute
        setattr(actor, "point_id", point_id)
        setattr(actor, "color", color)
        setattr(actor, "sphere_source", sphere)

        return actor

    def point_build_actor(self, points, vertices_cell, color, point_id):
        """Helper function to construct and return a VTK actor for points."""
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetVerts(vertices_cell)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToPoints()
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetPointSize(8.0)
        actor.GetProperty().SetOpacity(1.0)
        actor.GetProperty().RenderPointsAsSpheresOn()  # Enable circular points

        setattr(actor, "point_id", point_id)
        setattr(actor, "color", color)
        return actor

    def point_select(self, actor, radius):
        if radius:
            # Check if the actor has a sphere_source attribute
            if hasattr(actor, "sphere_source"):
                sphere = getattr(actor, "sphere_source")
                sphere.SetRadius(radius)
                sphere.Modified()
        return actor

    def points_save_database(self, db_path):
        """Saves the polylines data into the SQLite database."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS points (
                point_id INTEGER PRIMARY KEY,
                X REAL,
                Y REAL,
                Z REAL,
                Name TEXT
            )
            """
        )

        # Clear table before inserting new data
        cursor.execute("DELETE FROM points")

        """Inserts point data into the database."""
        for point_id, vertices in self.points.items():
            for x, y, z, name in vertices:
                cursor.execute(
                    """
                    INSERT INTO points (point_id, X, Y, Z, Name)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (point_id, x, y, z, name),
                )

        conn.commit()
        conn.close()

    def hasPolylinesTable(self, db_path):
        return self.table_exists(db_path, "polylines")

    def hasPointsTable(self, db_path):
        return self.table_exists(db_path, "points")

    def table_exists(self, db_path, table_name):
        """
        Check if the 'polylines' table exists in the SQLite database.

        Args:
            db_path (str): Path to the SQLite database file.

        Returns:
            bool: True if the 'polylines' table exists, False otherwise.
        """
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Query the sqlite_master table for the specified table
            cursor.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?
                """,
                (table_name,)
            )

            # Fetch the result
            result = cursor.fetchone()

            # Close the connection
            conn.close()

            # If result is not None, the table exists
            return result is not None

        except sqlite3.Error as e:
            print(f"An error occurred while checking for the 'polylines' table: {e}")
            return False

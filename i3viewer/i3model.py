import csv
import math
import random
import sqlite3
import sys

import vtk

from i3viewer.i3enums import FileType, Params


class i3model:

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def __init__(self, file_path):
        self.file_path = file_path

        self.polylines = {}
        self.points = {}
        self.surfaces = {}
        self.polylabels = {}
        self.pointlabels = {}

        self.polyline_id = 1
        self.point_id = 1
        self.surface_id = 1
        self.polylabel_id = 1
        self.pointlabel_id = 1

        self.actors = []
        self.contourColor = []

    def RemoveAllActors(self):
        self.polylines = {}
        self.points = {}
        self.surfaces = {}
        self.polylabels = {}
        self.pointlabels = {}

        self.polyline_id = 1
        self.point_id = 1
        self.surface_id = 1
        self.polylabel_id = 1
        self.pointlabel_id = 1

    # -------------------------------------------------------------------------
    # Database Utilities
    # -------------------------------------------------------------------------

    def _connect(self):
        """Return a new SQLite connection to the current file path."""
        return sqlite3.connect(self.file_path)

    def table_exists(self, table_name):
        """Return True if the given table exists in the SQLite database."""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
            )
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except sqlite3.Error as e:
            print(e.sqlite_errorcode)
            return False

    def hasPolylinesTable(self):
        return self.table_exists("polylines")

    def hasPointsTable(self):
        return self.table_exists("points")

    def hasSurfacesTable(self):
        return self.table_exists("surfaces")

    def hasRoutesTable(self):
        return self.table_exists("routes")

    def hasTonnesTable(self):
        return self.table_exists("tonnes")

    def hasRoutesTonnesTable(self):
        return self.table_exists("routes_tonnes")

    # -------------------------------------------------------------------------
    # Gradient Helper
    # -------------------------------------------------------------------------

    @staticmethod
    def _compute_gradient(current, previous):
        """Return gradient (%) between two (x, y, z) points, or 0.0 for the first point."""
        if previous is None:
            return 0.0
        prev_x, prev_y, prev_z = previous[:3]
        x, y, z = current[:3]
        delta_z = z - prev_z
        distance = math.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2)
        return (delta_z / distance) * 100 if distance != 0 else 0.0

    # -------------------------------------------------------------------------
    # Polylines — Read
    # -------------------------------------------------------------------------

    def polylines_read_xyz_file(self):
        """Read an XYZ file and return polylines with computed gradient values."""
        polylines = {self.polyline_id: []}

        with open(self.file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line == "$":
                    self.polyline_id += 1
                    polylines[self.polyline_id] = []
                else:
                    parts = line.split()
                    if len(parts) == 3:
                        x, y, z = (round(float(v), 3) for v in parts)
                        prev = polylines[self.polyline_id][-1] if polylines[self.polyline_id] else None
                        gradient = round(self._compute_gradient((x, y, z), prev), 3)
                        polylines[self.polyline_id].append((x, y, z, gradient, None, None))

        return {k: v for k, v in polylines.items() if v}

    def polylines_read_csv_file(self):
        """Read a CSV file and return polylines with computed gradient values."""
        polylines = {self.polyline_id: []}

        with open(self.file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line == "$":
                    self.polyline_id += 1
                    polylines[self.polyline_id] = []
                else:
                    parts = line.split(",")
                    if len(parts) == 4:
                        name, *xyz = parts
                        x, y, z = (round(float(v), 3) for v in xyz)
                        prev = polylines[self.polyline_id][-1] if polylines[self.polyline_id] else None
                        gradient = round(self._compute_gradient((x, y, z), prev), 3)
                        polylines[self.polyline_id].append((x, y, z, gradient, name, None))

        return {k: v for k, v in polylines.items() if v}

    def polylines_read_table(self):
        """Fetch polylines grouped by polyline_id from the SQLite database."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT polyline_id, X, Y, Z, gradient, route, tonne,
                "velocidad máxima",
                "resistencia a la rodadura",
                "límite máximo de velocidad",
                "velocidad de frenado",
                "rimpull",
                "retardo",
                "consumo de combustible"
            FROM polylines ORDER BY polyline_id, point_id
            """
        )
        data = cursor.fetchall()
        conn.close()

        polylines = {}
        for polyline_id, x, y, z, g, *rest in data:
            polylines.setdefault(polyline_id, []).append((x, y, z, g, *rest))
        return polylines

    def polylines_reread_table(self):
        polylines = self.polylines_read_table()
        if polylines:
            self.polylines.update(polylines)

    # -------------------------------------------------------------------------
    # Polylines — Actors
    # -------------------------------------------------------------------------

    def polylines_format_actors(self, fileType):
        """Read polylines from the appropriate source and return VTK actors."""
        readers = {
            FileType.DB:  self.polylines_read_table,
            FileType.XYZ: self.polylines_read_xyz_file,
            FileType.CSV: self.polylines_read_csv_file,
        }
        reader = readers.get(fileType)
        if reader is None:
            return []

        polylines = reader()
        if polylines:
            self.polylines.update(polylines)
        return self.polylines_create_actors()

    def polylines_create_actors(self):
        """Create and return a VTK actor for every polyline in self.polylines."""
        self.actors = []
        for polyline_id, vertices in self.polylines.items():
            actor = self.polylines_create_actor(polyline_id, vertices)
            if actor:
                self.actors.append(actor)
        return self.actors

    def polylines_create_actor(self, polyline_id, vertices):
        """Create a VTK actor for a single polyline."""
        if not vertices:
            return None

        points = vtk.vtkPoints()
        cells = vtk.vtkCellArray()
        polyline = vtk.vtkPolyLine()
        polyline.GetPointIds().SetNumberOfIds(len(vertices))

        color = [random.randint(0, 255) / 255.0 for _ in range(3)]

        for i, (x, y, z, *_) in enumerate(vertices):
            pid = points.InsertNextPoint(x, y, z)
            polyline.GetPointIds().SetId(i, pid)

        cells.InsertNextCell(polyline)
        return self.polylines_build_actor(points, cells, color, polyline_id)

    def polylines_build_actor(self, points, cells, color, polyline_id):
        """Construct and return a VTK actor for a polyline."""
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetLines(cells)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(Params.PolylineDefaultWidth.value)
        setattr(actor, "polyline_id", polyline_id)
        setattr(actor, "color", color)
        return actor

    # -------------------------------------------------------------------------
    # Polylines — Save to Database
    # -------------------------------------------------------------------------

    def polylines_save_database(self, db_path):
        """Save polyline data to the SQLite database."""
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
                gradient REAL,
                route TEXT,
                tonne REAL,
                "velocidad máxima" REAL,
                "resistencia a la rodadura" REAL,
                "límite máximo de velocidad" REAL,
                "velocidad de frenado" REAL,
                "rimpull" REAL,
                "retardo" REAL,
                "consumo de combustible" REAL,
                PRIMARY KEY (polyline_id, point_id)
            )
            """
        )
        cursor.execute("DELETE FROM polylines")

        for polyline_id, points in self.polylines.items():
            for pt_idx, (x, y, z, g, r, *_) in enumerate(points, start=1):
                cursor.execute(
                    "INSERT INTO polylines (polyline_id, point_id, X, Y, Z, gradient, route) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (polyline_id, pt_idx, x, y, z, g, r),
                )

        conn.commit()
        conn.close()

    # -------------------------------------------------------------------------
    # Points — Read
    # -------------------------------------------------------------------------

    def points_read_srg_file(self):
        """Read an SRG file and return points."""
        points = {}

        with open(self.file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 6:
                    continue
                try:
                    x, y, z = float(row[0]), float(row[1]), float(row[2])
                    name = row[5]
                    points[self.point_id] = [(x, y, z, name)]
                    self.point_id += 1
                except ValueError:
                    continue

        return points

    def points_read_table(self):
        """Fetch points from the SQLite database."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT point_id, X, Y, Z, name FROM points ORDER BY point_id"
        )
        data = cursor.fetchall()
        conn.close()

        points = {}
        for point_id, x, y, z, name in data:
            points.setdefault(point_id, []).append((x, y, z, name))
        return points

    # -------------------------------------------------------------------------
    # Points — Actors
    # -------------------------------------------------------------------------

    def points_format_actors(self, fileType):
        """Read points from the appropriate source and return VTK actors."""
        readers = {
            FileType.DB:  self.points_read_table,
            FileType.SRG: self.points_read_srg_file,
        }
        reader = readers.get(fileType)
        if reader is None:
            return []

        points = reader()
        if points:
            self.points.update(points)
        return self.points_create_actors()

    def points_create_actors(self):
        """Create and return a VTK actor for every point in self.points."""
        self.actors = []
        for point_id, vertices in self.points.items():
            actor = self.point_create_actor(point_id, vertices)
            if actor:
                self.actors.append(actor)
        return self.actors

    def point_create_actor(self, point_id, vertices):
        """Create a VTK actor for a single point."""
        if not vertices:
            return None

        points = vtk.vtkPoints()
        vertices_cell = vtk.vtkCellArray()
        color = [random.randint(0, 255) / 255.0 for _ in range(3)]

        x, y, z, _ = vertices[0]
        vid = points.InsertNextPoint(x, y, z)
        vertices_cell.InsertNextCell(1)
        vertices_cell.InsertCellPoint(vid)

        if sys.platform.startswith("win"):
            return self.points_build_actor_win(points, vertices_cell, color, point_id)
        return self.points_build_actor(points, vertices_cell, color, point_id)

    def points_build_actor_win(self, points, vertices_cell, color, point_id):
        """Build a sphere-glyphed point actor for Windows."""
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetVerts(vertices_cell)

        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(Params.PointWinRadius.value)
        sphere.SetThetaResolution(Params.PointWinTheta.value)
        sphere.SetPhiResolution(Params.PointWinPhi.value)

        glyph = vtk.vtkGlyph3D()
        glyph.SetInputData(poly_data)
        glyph.SetSourceConnection(sphere.GetOutputPort())
        glyph.SetScaleModeToDataScalingOff()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(glyph.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetPointSize(Params.PointWinSize.value)
        setattr(actor, "point_id", point_id)
        setattr(actor, "color", color)
        setattr(actor, "sphere_source", sphere)
        return actor

    def points_build_actor(self, points, vertices_cell, color, point_id):
        """Build a standard point actor."""
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetVerts(vertices_cell)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToPoints()
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetPointSize(Params.PointSize.value)
        actor.GetProperty().RenderPointsAsSpheresOn()
        setattr(actor, "point_id", point_id)
        setattr(actor, "color", color)
        return actor

    def point_select(self, actor, radius):
        """Resize a point actor's sphere glyph to the given radius."""
        if radius and hasattr(actor, "sphere_source"):
            sphere = getattr(actor, "sphere_source")
            sphere.SetRadius(radius)
            sphere.Modified()
        return actor

    # -------------------------------------------------------------------------
    # Points — Save to Database
    # -------------------------------------------------------------------------

    def points_save_database(self, db_path):
        """Save point data to the SQLite database."""
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
        cursor.execute("DELETE FROM points")

        for point_id, vertices in self.points.items():
            for x, y, z, name in vertices:
                cursor.execute(
                    "INSERT INTO points (point_id, X, Y, Z, Name) VALUES (?, ?, ?, ?, ?)",
                    (point_id, x, y, z, name),
                )

        conn.commit()
        conn.close()

    # -------------------------------------------------------------------------
    # Surfaces — Read
    # -------------------------------------------------------------------------

    def surfaces_read_xyzs_file(self):
        """Read an XYZS file and return surfaces."""
        surfaces = {self.surface_id: []}

        with open(self.file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line == "$":
                    self.surface_id += 1
                    surfaces[self.surface_id] = []
                else:
                    parts = line.split()
                    if len(parts) == 3:
                        x, y, z = (round(float(v), 3) for v in parts)
                        surfaces[self.surface_id].append((x, y, z))

        return {k: v for k, v in surfaces.items() if v}

    def surfaces_read_table(self):
        """Fetch surfaces grouped by surface_id from the SQLite database."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT surface_id, X, Y, Z FROM surfaces ORDER BY surface_id, point_id"
        )
        data = cursor.fetchall()
        conn.close()

        surfaces = {}
        for surface_id, x, y, z in data:
            surfaces.setdefault(surface_id, []).append((x, y, z))
        return surfaces

    # -------------------------------------------------------------------------
    # Surfaces — Actors
    # -------------------------------------------------------------------------

    def surfaces_format_actors(self, fileType):
        """Read surfaces from the appropriate source and return VTK actors."""
        readers = {
            FileType.XYZS: self.surfaces_read_xyzs_file,
            FileType.DB:   self.surfaces_read_table,
        }
        reader = readers.get(fileType)
        if reader is None:
            return []

        surfaces = reader()
        if surfaces:
            self.surfaces.update(surfaces)
        return self.surfaces_create_actors()

    def surfaces_create_actors(self):
        """Create and return a VTK actor for every surface in self.surfaces."""
        self.actors = []
        color = self.contourColor or [random.randint(0, 255) / 255.0 for _ in range(3)]

        for surface_id, vertices in self.surfaces.items():
            actor = self.surfaces_create_actor(surface_id, vertices, color)
            if actor:
                self.actors.append(actor)
        return self.actors

    def surfaces_create_actor(self, surface_id, vertices, color):
        """Create a VTK actor for a single surface contour."""
        if not vertices:
            return None

        points = vtk.vtkPoints()
        cells = vtk.vtkCellArray()
        polyline = vtk.vtkPolyLine()
        polyline.GetPointIds().SetNumberOfIds(len(vertices))

        for i, (x, y, z, *_) in enumerate(vertices):
            pid = points.InsertNextPoint(x, y, z)
            polyline.GetPointIds().SetId(i, pid)

        cells.InsertNextCell(polyline)
        return self.surfaces_build_actor(points, cells, color, surface_id)

    def surfaces_build_actor(self, points, cells, color, surface_id):
        """Construct and return a VTK actor for a surface contour."""
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.SetLines(cells)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToSurface()
        actor.GetProperty().EdgeVisibilityOff()
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(2)
        setattr(actor, "surface_id", surface_id)
        setattr(actor, "color", color)
        return actor

    # -------------------------------------------------------------------------
    # Surfaces — Save to Database
    # -------------------------------------------------------------------------

    def surfaces_save_database(self, db_path):
        """Save surface data to the SQLite database."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS surfaces (
                surface_id INTEGER NOT NULL,
                point_id INTEGER NOT NULL,
                X REAL,
                Y REAL,
                Z REAL,
                PRIMARY KEY (surface_id, point_id)
            )
            """
        )
        cursor.execute("DELETE FROM surfaces")

        for surface_id, points in self.surfaces.items():
            for pt_idx, (x, y, z) in enumerate(points, start=1):
                cursor.execute(
                    "INSERT INTO surfaces (surface_id, point_id, X, Y, Z) VALUES (?, ?, ?, ?, ?)",
                    (surface_id, pt_idx, x, y, z),
                )

        conn.commit()
        conn.close()

    # -------------------------------------------------------------------------
    # Surface Reconstruction
    # -------------------------------------------------------------------------

    def delaunay_reconstruction_actor(self, contour_polydata, delaunaycfg):
        """Create a Delaunay-triangulated surface mesh from contour polydata."""
        cleaner = vtk.vtkCleanPolyData()
        cleaner.SetInputData(contour_polydata)
        cleaner.SetTolerance(delaunaycfg.cleaner_tolerance)
        cleaner.Update()

        delaunay = vtk.vtkDelaunay2D()
        delaunay.SetInputData(cleaner.GetOutput())
        delaunay.SetAlpha(delaunaycfg.delaunay_alpha)
        delaunay.SetTolerance(delaunaycfg.delaunay_tolerance)
        delaunay.SetOffset(delaunaycfg.delaunay_offset)
        # Projection plane modes: 0=best fit, 1=XY, 2=YZ, 3=XZ
        delaunay.SetProjectionPlaneMode(delaunaycfg.projection_plane_mode)
        delaunay.Update()

        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(delaunay.GetOutput())
        normals.SetFeatureAngle(delaunaycfg.feature_angle)
        normals.ComputePointNormalsOn()
        normals.ComputeCellNormalsOn()
        normals.ConsistencyOn()
        normals.SplittingOff()
        normals.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(normals.GetOutput())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor

    def _apply_surface_properties(self, actor, surfacecfg, wireframe=False):
        """Apply appearance properties to a Delaunay-reconstructed actor."""
        if not hasattr(actor, "GetProperty"):
            return
        prop = actor.GetProperty()
        color = surfacecfg.wireframe_color if wireframe else surfacecfg.surface_color
        prop.SetColor(color)
        prop.SetOpacity(surfacecfg.surface_opacity)
        prop.SetEdgeColor(surfacecfg.wireframe_color)
        prop.SetLineWidth(surfacecfg.edge_thickness)
        if wireframe:
            prop.SetEdgeVisibility(True)
            prop.SetRepresentationToWireframe()
        else:
            prop.SetEdgeVisibility(False)
            prop.SetRepresentationToSurface()

    def surface_reconstruction_actor(self, contour_polydata, delaunaycfg, surfacecfg):
        """Return a solid-surface actor built from contour polydata."""
        actor = self.delaunay_reconstruction_actor(contour_polydata, delaunaycfg)
        self._apply_surface_properties(actor, surfacecfg, wireframe=False)
        return actor

    def wireframe_reconstruction_actor(self, contour_polydata, delaunaycfg, surfacecfg):
        """Return a wireframe actor built from contour polydata."""
        actor = self.delaunay_reconstruction_actor(contour_polydata, delaunaycfg)
        self._apply_surface_properties(actor, surfacecfg, wireframe=True)
        return actor

    # -------------------------------------------------------------------------
    # Labels
    # -------------------------------------------------------------------------

    def polylabels_create_actor(self, actor, label_text="Polyline Label"):
        """Create a 3D billboard label at the arc-length midpoint of a polyline actor."""
        mapper = actor.GetMapper()
        poly_data = mapper.GetInput()

        if poly_data is None:
            raise ValueError("Actor does not contain polydata.")

        points = poly_data.GetPoints()
        lines = poly_data.GetLines()
        lines.InitTraversal()

        id_list = vtk.vtkIdList()
        if not lines.GetNextCell(id_list):
            raise ValueError("No polyline found in polydata.")

        n_points = id_list.GetNumberOfIds()

        # Compute cumulative arc lengths
        arc_lengths = [0.0]
        total_length = 0.0
        for i in range(1, n_points):
            p1 = points.GetPoint(id_list.GetId(i - 1))
            p2 = points.GetPoint(id_list.GetId(i))
            total_length += vtk.vtkMath.Distance2BetweenPoints(p1, p2) ** 0.5
            arc_lengths.append(total_length)

        half_length = total_length / 2.0

        # Interpolate position at the midpoint
        midpoint = [0.0, 0.0, 0.0]
        for i in range(1, n_points):
            if arc_lengths[i] >= half_length:
                p1 = points.GetPoint(id_list.GetId(i - 1))
                p2 = points.GetPoint(id_list.GetId(i))
                denom = arc_lengths[i] - arc_lengths[i - 1]
                if denom == 0.0:
                    midpoint = list(p1)
                else:
                    t = (half_length - arc_lengths[i - 1]) / denom
                    midpoint = [p1[j] + t * (p2[j] - p1[j]) for j in range(3)]
                break

        label = vtk.vtkBillboardTextActor3D()
        label.SetInput(label_text)
        label.SetPosition(midpoint)
        label.GetTextProperty().SetFontSize(int(Params.PolylabelFontSize.value))
        label.GetTextProperty().SetColor(Params.PolylabelColor.value)
        return label

    def pointlabels_create_actor(self, actor, label_text="Point Label"):
        """Create a 3D billboard label at the position of a point actor."""
        mapper = actor.GetMapper()
        poly_data = mapper.GetInput()

        if poly_data is None or poly_data.GetNumberOfPoints() == 0:
            return None

        label = vtk.vtkBillboardTextActor3D()
        label.SetInput(label_text)
        label.SetPosition(poly_data.GetPoint(0))
        label.GetTextProperty().SetFontSize(int(Params.PointlabelFontSize.value))
        label.GetTextProperty().SetColor(Params.PointlabelColor.value)
        return label

    # -------------------------------------------------------------------------
    # Routes & Tonnes Database
    # -------------------------------------------------------------------------

    def routes_save_database(self, routes_file):
        """Import a CSV routes file into the SQLite database."""
        try:
            conn = self._connect()
            cursor = conn.cursor()

            cursor.execute("DROP TABLE IF EXISTS routes")
            conn.commit()
            cursor.execute(
                "CREATE TABLE routes (route_id TEXT, segments TEXT)"
            )

            with open(routes_file, "r") as f:
                for row in csv.reader(f):
                    if not row:
                        continue
                    route_id = row[0]
                    segments = ",".join(row[1:]) if len(row) > 1 else ""
                    cursor.execute(
                        "INSERT INTO routes VALUES (?, ?)", (route_id, segments))

            conn.commit()
        finally:
            if "conn" in locals():
                conn.close()

    def tonnes_save_database(self, tonnes_file):
        """Import a CSV tonnes file into the SQLite database."""
        try:
            conn = self._connect()
            cursor = conn.cursor()

            cursor.execute("DROP TABLE IF EXISTS tonnes")
            conn.commit()
            cursor.execute(
                "CREATE TABLE tonnes (period INTEGER, route_id TEXT, tonne REAL)"
            )

            with open(tonnes_file, "r") as f:
                for row in csv.reader(f):
                    if len(row) < 3:
                        continue
                    try:
                        period = int(row[0])
                        route_id = row[1]
                        tonne = float(row[2])
                        cursor.execute(
                            "INSERT INTO tonnes VALUES (?, ?, ?)",
                            (period, route_id, tonne),
                        )
                    except ValueError:
                        print(
                            f"Warning: Could not parse period '{row[0]}' or "
                            f"tonne '{row[2]}'. Skipping row."
                        )

            conn.commit()
        finally:
            if "conn" in locals():
                conn.close()

    def routes_tonnes_save_database(self):
        """Create the routes_tonnes joined table in the SQLite database."""
        try:
            conn = self._connect()
            cursor = conn.cursor()

            cursor.execute("DROP TABLE IF EXISTS routes_tonnes")
            conn.commit()
            cursor.execute(
                """
                CREATE TABLE routes_tonnes AS
                SELECT t.period, r.route_id, t.tonne, r.segments
                FROM tonnes t
                JOIN routes r ON t.route_id = r.route_id
                ORDER BY t.period, r.route_id
                """
            )
            conn.commit()
        finally:
            if "conn" in locals():
                conn.close()

    def hasPeriods(self):
        """Return True if the routes_tonnes table has at least one row."""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM routes_tonnes")
            result = cursor.fetchone()
            return bool(result)
        finally:
            if "conn" in locals():
                conn.close()

    def getMaxPeriod(self):
        """Return the maximum period value in the routes_tonnes table."""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT max(period) FROM routes_tonnes")
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            if "conn" in locals():
                conn.close()

    def updateRoutesTonnes(self, period):
        """Update the tonne column in polylines for the given period."""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE polylines
                SET tonne = (
                    SELECT COALESCE(SUM(rt.tonne), 0)
                    FROM routes_tonnes rt
                    WHERE rt.period = ?
                    AND rt.segments LIKE '%' || polylines.route || '%'
                )
                """,
                (period,),
            )
            conn.commit()
        finally:
            if "conn" in locals():
                conn.close()
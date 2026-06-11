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
        self.surfaces_by_file = {}
        self.polylabels = {}
        self.pointlabels = {}

        self.polyline_id = 1
        self.point_id = 1
        self.surface_id = 1
        self.surface_file_id = 1
        self.polylabel_id = 1
        self.pointlabel_id = 1

        self.actors = []
        self.contourColor = []

    def RemoveAllActors(self):
        self.polylines = {}
        self.points = {}
        self.surfaces = {}
        self.surfaces_by_file = {}
        self.polylabels = {}
        self.pointlabels = {}

        self.polyline_id = 1
        self.point_id = 1
        self.surface_id = 1
        self.surface_file_id = 1
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
        """Read surfaces from the appropriate source and return VTK actors for the new file only."""
        readers = {
            FileType.XYZS: self.surfaces_read_xyzs_file,
            FileType.DB:   self.surfaces_read_table,
        }
        reader = readers.get(fileType)
        if reader is None:
            return []

        surfaces = reader()
        if not surfaces:
            return []

        self.surfaces.update(surfaces)

        # Build Z-grouped contours for this file: {z: {surface_id: [pts]}}
        # Preserving per-surface_id separation is essential — merging multiple
        # surface_ids into one flat list would falsely connect their endpoints
        # when building contour polylines, producing crossing diagonal lines.
        surfaces_by_z = {}
        for sid, vertices in surfaces.items():
            if not vertices:
                continue
            z = vertices[0][2]          # all points in one surface_id share one Z
            surfaces_by_z.setdefault(z, {})[sid] = list(vertices)

        self.surfaces_by_file[self.surface_file_id] = surfaces_by_z

        return self.surfaces_create_new_actors(surfaces)

    def surfaces_create_new_actors(self, surfaces):
        """Create and return VTK actors only for the surfaces in the given dict."""
        actors = []
        color = self.contourColor or [random.randint(0, 255) / 255.0 for _ in range(3)]

        for surface_id, vertices in surfaces.items():
            actor = self.surfaces_create_actor(surface_id, vertices, color)
            if actor:
                actors.append(actor)
        return actors

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
    # Surfaces — 2D polygon clipping helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _point_in_polygon_2d(px, py, polygon):
        """Ray casting point-in-polygon test in XY plane.

        Works correctly for any polygon shape including non-convex.
        polygon is a list of (x, y, ...) tuples; only x, y are used.
        Returns True if (px, py) is strictly inside polygon.
        """
        n = len(polygon)
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = polygon[i][0], polygon[i][1]
            xj, yj = polygon[j][0], polygon[j][1]
            if ((yi > py) != (yj > py)):
                if px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                    inside = not inside
            j = i
        return inside

    @staticmethod
    def _segment_intersect_2d(p1, p2, p3, p4):
        """Find the intersection of segment p1-p2 with segment p3-p4 in XY.

        Uses parametric form. t is the parameter along p1-p2, u along p3-p4.
        Accepts intersections where t is strictly in (0, 1) — excludes A
        segment endpoints to avoid double-counting at shared vertices.
        u is in [0, 1] — B edge endpoints are included so corner intersections
        are found.

        Returns (t, u, ix, iy) or None if no intersection.
        """
        dx1 = p2[0] - p1[0]
        dy1 = p2[1] - p1[1]
        dx2 = p4[0] - p3[0]
        dy2 = p4[1] - p3[1]
        denom = dx1 * dy2 - dy1 * dx2
        if abs(denom) < 1e-10:
            return None
        t = ((p3[0] - p1[0]) * dy2 - (p3[1] - p1[1]) * dx2) / denom
        u = ((p3[0] - p1[0]) * dy1 - (p3[1] - p1[1]) * dx1) / denom
        eps = 1e-9
        if eps < t < 1.0 - eps and -eps <= u <= 1.0 + eps:
            ix = p1[0] + t * dx1
            iy = p1[1] + t * dy1
            return t, u, ix, iy
        return None

    @staticmethod
    def _nearest_a_index(pt, a_pts, tol):
        """Return the index of the nearest point in a_pts to pt within tol,
        or None if no point is within tol."""
        best_d = tol * tol   # compare squared distances — no sqrt needed
        best_i = None
        px, py = pt[0], pt[1]
        for i, ap in enumerate(a_pts):
            dx = ap[0] - px
            dy = ap[1] - py
            d2 = dx * dx + dy * dy
            if d2 < best_d:
                best_d = d2
                best_i = i
        return best_i

    @staticmethod
    def _detect_shared_boundary(a_pts, b_pts, tol=1.0):
        """Detect whether B's boundary shares points with A's contour.

        A mining-cut polygon has its outer edge coinciding with a segment of
        A's contour line. B may have TWO separate ON-main runs — a long outer
        arc and a short closing segment — separated by the inner cut arc. This
        function finds the true left and right junction points across ALL
        ON-main runs, not just the longest one.

        Args:
            a_pts: flat list of (x, y, z, ...) for A's closed contour
            b_pts: flat list of (x, y, z, ...) for B's closed polygon
            tol:   maximum distance (map units) to consider two points coincident

        Returns a dict with keys:
            match    : list of matched a indices (or -1) for every b point
            j_right  : b index where match[j] == a_end (first occurrence) —
                       traversal starts here to collect the inner arc
            a_start  : min a index across all ON-main runs — left junction
            a_end    : max a index across all ON-main runs — right junction
            reversed : True if B traverses A in reverse direction
        or None if total ON-main point count < 3.
        """
        n_b = len(b_pts)

        # For each b point record the nearest a index (or -1 if none within tol)
        match = []
        for bp in b_pts:
            mi = i3model._nearest_a_index(bp, a_pts, tol)
            match.append(mi if mi is not None else -1)

        # Count total shared points and find true junction indices across
        # ALL ON-main runs (not just the longest single run).
        on_indices = [mi for mi in match if mi != -1]
        if len(on_indices) < 3:
            return None

        a_start = min(on_indices)   # left junction in A
        a_end   = max(on_indices)   # right junction in A

        # Find j_right: first b index where match[j] == a_end.
        # The inner arc begins immediately after j_right in B's traversal.
        j_right = next((j for j in range(n_b) if match[j] == a_end), None)
        if j_right is None:
            return None

        # Traversal direction: forward if B goes a_start → a_end along the
        # shared arc (i.e. a_end appears after a_start in B's sequence).
        j_start_candidates = [j for j in range(n_b) if match[j] == a_start]
        if not j_start_candidates:
            return None

        # For forward detection: check if going forward from j_right
        # eventually hits a_start before cycling back to j_right.
        forward = (a_end > a_start)

        return {
            'match':    match,
            'j_right':  j_right,
            'a_start':  a_start,
            'a_end':    a_end,
            'reversed': not forward,
        }

    @staticmethod
    def _splice_shared_boundary(a_pts, b_pts, shared, z):
        """Boundary substitution for Type-2 cuts (B straddles A's boundary).

        Replaces the shared segment of A's contour with B's inner arc, producing
        a single continuous closed result contour with the notch cut correctly
        substituted.

        Args:
            a_pts:  flat list of (x, y, z, ...) for A's closed contour
            b_pts:  flat list of (x, y, z, ...) for B's closed polygon
            shared: dict returned by _detect_shared_boundary
            z:      Z coordinate for all output points

        Returns:
            (arc_segments, gap_fills) in the same format as _clip_contour_2d.
            arc_segments: [one_list_of_pts] — the spliced result contour
            gap_fills:    [inner_arc_pts]   — B's inner arc (for display + Delaunay)
        """
        match   = shared['match']
        j_right = shared['j_right']
        a_start = shared['a_start']
        a_end   = shared['a_end']
        is_rev  = shared['reversed']

        n_b = len(b_pts)

        # ------------------------------------------------------------------
        # Extract the inner arc: traverse B forward from j_right+1, collecting
        # points until we reach a point matched to a_start (left junction).
        #
        # Rules for each visited B point:
        #   • matched to a_start → stop (this IS the left junction, already in A)
        #   • matched to a_end   → skip (the right junction, already in A)
        #   • OFF-main (match=-1) → include — these are the true cut-face points
        #   • ON-main but not a junction → include as A point (intermediate pivot)
        #
        # This correctly collects cut1[94..102] + main[1138] for the data at hand,
        # and excludes the short closing ON-main run cut1[103..107] which is the
        # second shared segment (not part of the inner cut face).
        # ------------------------------------------------------------------
        inner_arc_raw = []
        idx   = (j_right + 1) % n_b
        steps = 0
        while steps < n_b:
            mi = match[idx]
            if mi == a_start:
                break                    # reached left junction — stop
            if mi != a_end:              # skip right-junction duplicates
                if mi == -1:
                    inner_arc_raw.append(b_pts[idx])          # OFF-main cut pt
                else:
                    inner_arc_raw.append(a_pts[mi])           # intermediate pivot
            idx   = (idx + 1) % n_b
            steps += 1

        # inner_arc_raw currently goes from a_end side toward a_start side.
        # For the splice we need it going a_end → a_start (same as A's direction)
        # which is already the case when B is forward (a_start < a_end).
        # When B is reversed the shared arc was traversed backwards in B, so
        # reverse the inner arc to restore the correct a_end → a_start order.
        if is_rev:
            inner_arc_raw = list(reversed(inner_arc_raw))

        inner_arc = [(pt[0], pt[1], z) for pt in inner_arc_raw]

        # ------------------------------------------------------------------
        # Build the spliced result contour:
        #   A[0 .. a_start] + inner_arc + A[a_end ..]
        # The junction points a_start and a_end are kept from A so there is
        # no floating-point gap at either splice point.
        # ------------------------------------------------------------------
        before_cut = [(pt[0], pt[1], z) for pt in a_pts[:a_start + 1]]
        after_cut  = [(pt[0], pt[1], z) for pt in a_pts[a_end:]]

        result = before_cut + inner_arc + after_cut

        # Gap fill = the inner arc bookended by the junction A points.
        # Used for (1) displaying the cut face and (2) constraining Delaunay.
        gap_fill = ([(a_pts[a_start][0], a_pts[a_start][1], z)] +
                    inner_arc +
                    [(a_pts[a_end][0], a_pts[a_end][1], z)])

        arc_segments = [result]    if len(result)    >= 2 else []
        gap_fills    = [gap_fill]  if len(gap_fill)  >= 2 else []

        return arc_segments, gap_fills

    @staticmethod
    def _clip_contour_2d(a_pts, b_pts, z):
        """Clip A contour by B polygon boundary using 2D geometry.

        Handles two topologies automatically:
          Type 1 — B is fully interior to A's closed polygon (no shared boundary).
                   Uses segment intersection + ray casting to keep outside arcs.
          Type 2 — B straddles A's boundary (B's outer edge coincides with a
                   segment of A's contour line — the mining-cut case).
                   Uses boundary substitution: replaces the shared segment with
                   B's inner arc.

        a_pts is either the original closed loop [(x,y,z)...] or a list of
        open arc segment lists [[...], [...]] from a previous clip pass.

        Returns:
            arc_segments : list of point lists — surviving arcs of A outside B
            gap_fills    : list of point lists — B boundary points between each
                           pair of intersection points (one list per gap, for
                           filling the gap in the contour display and for
                           constraining the Delaunay triangulation)
        """
        # Normalise input: always work with a list of arc point-lists.
        # A closed loop is a single arc; previous clip output is already a list.
        if a_pts and isinstance(a_pts[0], (list, tuple)) and \
                isinstance(a_pts[0][0], (list, tuple)):
            input_arcs = a_pts
        else:
            input_arcs = [list(a_pts)]

        # Flatten to a single pts list for shared-boundary detection.
        # For a single arc this is itself; for multiple arcs we check the
        # first arc only (subsequent arcs from a previous clip pass are open
        # segments that will not share a boundary with B).
        flat_a = input_arcs[0] if input_arcs else []

        # -----------------------------------------------------------------------
        # Dispatch: detect Type-2 (shared boundary) and splice instead of clip.
        # Only meaningful for a single closed input arc (first call per sid).
        # -----------------------------------------------------------------------
        if len(input_arcs) == 1:
            shared = i3model._detect_shared_boundary(flat_a, b_pts, tol=1.0)
            if shared is not None:
                return i3model._splice_shared_boundary(flat_a, b_pts, shared, z)

        # Ensure b_pts is closed (last point == first point)
        b_closed = list(b_pts)
        if b_closed[0][:2] != b_closed[-1][:2]:
            b_closed.append(b_closed[0])

        all_arc_segments = []
        all_gap_fills    = []

        for arc in input_arcs:
            if len(arc) < 2:
                continue

            # Ensure arc is not accidentally self-closed for open arcs
            pts = list(arc)

            # ---------------------------------------------------------------
            # Step 1: find all intersections of this arc with B edges
            # ---------------------------------------------------------------
            events = []  # (arc_seg_idx, t, ix, iy, b_edge_idx, u)
            n_arc = len(pts)
            n_b   = len(b_closed)
            for i in range(n_arc - 1):
                p1 = pts[i][:2]
                p2 = pts[i + 1][:2]
                for j in range(n_b - 1):
                    p3 = b_closed[j][:2]
                    p4 = b_closed[j + 1][:2]
                    r = i3model._segment_intersect_2d(p1, p2, p3, p4)
                    if r is not None:
                        t, u, ix, iy = r
                        events.append((i, t, ix, iy, j, u))

            # Sort events in traversal order along this arc
            events.sort(key=lambda e: (e[0], e[1]))

            # ---------------------------------------------------------------
            # Step 2: build augmented point list with intersections inserted
            # ---------------------------------------------------------------
            # Each entry: (x, y, z, is_intersection, b_edge_idx, u_along_B)
            augmented = []
            ev_idx = 0
            for i in range(n_arc - 1):
                augmented.append(
                    (pts[i][0], pts[i][1], z, False, -1, 0.0))
                while ev_idx < len(events) and events[ev_idx][0] == i:
                    e = events[ev_idx]
                    augmented.append(
                        (e[2], e[3], z, True, e[4], e[5]))
                    ev_idx += 1
            # Last point of arc
            augmented.append(
                (pts[-1][0], pts[-1][1], z, False, -1, 0.0))

            # ---------------------------------------------------------------
            # Step 3: walk augmented list, collecting outside arcs
            # ---------------------------------------------------------------
            # Determine initial inside/outside state using the midpoint of the
            # first segment rather than the first vertex, to avoid ambiguity
            # when the first point lies exactly on B's boundary.
            if len(pts) >= 2:
                mid_x = (pts[0][0] + pts[1][0]) / 2
                mid_y = (pts[0][1] + pts[1][1]) / 2
                started_inside = i3model._point_in_polygon_2d(
                    mid_x, mid_y, b_closed)
            else:
                started_inside = i3model._point_in_polygon_2d(
                    pts[0][0], pts[0][1], b_closed)
            is_inside = started_inside

            # (b_edge_idx, u, x, y) for each transition point
            transitions = []  # all intersections in order
            current_arc = []
            arc_segments = []

            for pt in augmented:
                x, y, z_val, is_int, b_edge, u = pt
                if is_int:
                    transitions.append((b_edge, u, x, y))
                    if is_inside:
                        # Coming OUT of B — start collecting
                        current_arc = [(x, y, z_val)]
                        is_inside = False
                    else:
                        # Going INTO B — end current arc
                        current_arc.append((x, y, z_val))
                        if len(current_arc) >= 2:
                            arc_segments.append(current_arc)
                        current_arc = []
                        is_inside = True
                else:
                    if not is_inside:
                        current_arc.append((x, y, z_val))

            # Flush trailing arc (arc started outside B and never re-entered,
            # OR arc started inside B and the final outside run wraps around to
            # the beginning — prepend it to the first arc segment).
            if len(current_arc) >= 2:
                if started_inside and arc_segments:
                    # Wraparound: the trailing outside run connects to the
                    # first arc found earlier; merge them into one arc.
                    arc_segments[0] = current_arc + arc_segments[0]
                else:
                    arc_segments.append(current_arc)

            # ---------------------------------------------------------------
            # Step 4: gap fill — traverse B boundary between each pair of
            # consecutive out→in and in→out transitions.
            # transitions alternates: in→out, out→in, in→out, out→in ...
            # (depending on initial state).
            # Each gap corresponds to one in-to-out transition followed by
            # the next out-to-in transition (or the last in-to-out wraps to
            # the first out-to-in when the arc starts outside B).
            # ---------------------------------------------------------------
            gap_fills = []
            # Pair up transitions: we need pairs (enter_B, exit_B) to find
            # the B boundary between them.
            # transitions[0] is the first crossing. If arc started OUTSIDE B,
            # transitions[0] = going-in, transitions[1] = going-out etc.
            # If arc started INSIDE B, transitions[0] = going-out etc.
            # In either case the B boundary to traverse is BETWEEN a going-in
            # event and the NEXT going-out event.
            enter_transitions = []  # (b_edge, u, x, y) where arc enters B
            exit_transitions  = []  # (b_edge, u, x, y) where arc exits B

            # For gap-fill pairing, re-derive started_inside consistently
            if len(pts) >= 2:
                mid_x = (pts[0][0] + pts[1][0]) / 2
                mid_y = (pts[0][1] + pts[1][1]) / 2
                started_inside = i3model._point_in_polygon_2d(
                    mid_x, mid_y, b_closed)
            else:
                started_inside = i3model._point_in_polygon_2d(
                    pts[0][0], pts[0][1], b_closed)
            currently_inside = started_inside
            for tr in transitions:
                if currently_inside:
                    exit_transitions.append(tr)   # coming out of B
                    currently_inside = False
                else:
                    enter_transitions.append(tr)  # going into B
                    currently_inside = True

            # For each entry into B, find the next exit from B.
            # The B boundary between entry and exit is the gap fill.
            for enter_tr, exit_tr in zip(enter_transitions, exit_transitions):
                b_edge_enter, u_enter, ex, ey = enter_tr
                b_edge_exit,  u_exit,  fx, fy = exit_tr

                gap = [(ex, ey, z)]

                # Traverse B boundary from enter point to exit point.
                # Determine direction: go in the direction where we stay
                # inside B (i.e. traverse the shorter path that stays
                # inside the B polygon between the two intersection points).
                # We always go forward along B edges: from b_edge_enter
                # to b_edge_exit in increasing edge index (wrapping).
                n_b_edges = len(b_closed) - 1

                # Forward path: enter_edge -> exit_edge (increasing index)
                forward_pts = []
                idx = b_edge_enter
                # Add remaining portion of the enter edge corner if needed
                # Move to the NEXT corner after the enter intersection
                idx = (b_edge_enter + 1) % n_b_edges
                while idx != b_edge_exit:
                    corner = b_closed[idx]
                    forward_pts.append((corner[0], corner[1], z))
                    idx = (idx + 1) % n_b_edges
                # Append exit point
                forward_pts.append((fx, fy, z))

                # Backward path: enter_edge -> exit_edge (decreasing index)
                backward_pts = []
                idx = b_edge_enter
                while idx != b_edge_exit:
                    corner = b_closed[idx]
                    backward_pts.append((corner[0], corner[1], z))
                    idx = (idx - 1) % n_b_edges
                backward_pts.append((fx, fy, z))

                # Choose the path with fewer corners — this is always the
                # short path between the two intersection points along B's
                # boundary, which correctly follows the local cut edge
                # regardless of B's shape (convex, concave, or elongated).
                # The midpoint-inside-B test fails for elongated B polygons
                # because both paths' midpoints can lie inside B.
                if len(forward_pts) <= len(backward_pts):
                    chosen = forward_pts
                else:
                    chosen = backward_pts

                gap.extend(chosen)
                if len(gap) >= 2:
                    gap_fills.append(gap)

            all_arc_segments.extend(arc_segments)
            all_gap_fills.extend(gap_fills)

        return all_arc_segments, all_gap_fills

    # -------------------------------------------------------------------------
    # Surfaces — Difference
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Contour Difference — small focused methods
    # -------------------------------------------------------------------------

    @staticmethod
    def contour_difference_affected_zs(surfaces_a_by_z, surfaces_b_by_z):
        """Return the set of Z levels present in both A and B."""
        return set(surfaces_b_by_z.keys()) & set(surfaces_a_by_z.keys())

    @staticmethod
    def contour_difference_clip_one_sid(a_pts, b_sid_dict, z):
        """Clip one A surface_id's contour against all B surface_ids at this Z.

        Tries boundary-substitution first (for notch-style cuts whose outer
        edge coincides with A). Falls back to polygon clipping for cuts that
        lie entirely inside A.

        Args:
            a_pts:      [(x,y,z)...] for this A surface_id
            b_sid_dict: {b_sid: [(x,y,z)...]} — all B surface_ids at this Z
            z:          the Z coordinate

        Returns:
            (arc_segments, gap_fills) where arc_segments is a list of point-lists
            and gap_fills is a list of point-lists (B boundary arcs to display).
            Returns (None, []) if A is unaffected, ([], []) if fully consumed.
        """
        combined_arcs = None
        combined_fills = []

        for pts_b in b_sid_dict.values():
            if len(pts_b) < 3:
                continue

            a_input = combined_arcs if combined_arcs is not None else a_pts

            # Try boundary-substitution first
            shared = i3model._detect_shared_boundary(a_input, pts_b)
            if shared is not None:
                arcs, fills = i3model._splice_shared_boundary(
                    a_input, pts_b, shared, z)
            else:
                arcs, fills = i3model._clip_contour_2d(a_input, pts_b, z)

            if not arcs:
                return [], []         # A sid fully consumed by this B sid

            combined_arcs = arcs
            combined_fills.extend(fills)

        return combined_arcs, combined_fills  # None if no B sids processed

    @staticmethod
    def contour_difference_build_polydata(arc_state, gap_fills, z):
        """Build a vtkPolyData from arc segments and gap fills for one Z level.

        Each arc segment and each gap fill becomes its own vtkPolyLine cell —
        no false connections between separate segments.

        Args:
            arc_state:  flat [(x,y,z)...] or list-of-lists of point-lists
            gap_fills:  list of point-lists (B boundary arcs)
            z:          Z coordinate (for normalisation)

        Returns a vtkPolyData, or None if there are no valid segments.
        """
        if arc_state and not isinstance(arc_state[0], list):
            arcs = [arc_state]
        else:
            arcs = arc_state or []

        vtk_pts   = vtk.vtkPoints()
        vtk_cells = vtk.vtkCellArray()
        has_pts   = False

        for seg in arcs:
            if len(seg) < 2:
                continue
            pl = vtk.vtkPolyLine()
            pl.GetPointIds().SetNumberOfIds(len(seg))
            for i, pt in enumerate(seg):
                pid = vtk_pts.InsertNextPoint(pt[0], pt[1], z)
                pl.GetPointIds().SetId(i, pid)
            vtk_cells.InsertNextCell(pl)
            has_pts = True

        for gap in gap_fills:
            if len(gap) < 2:
                continue
            pl = vtk.vtkPolyLine()
            pl.GetPointIds().SetNumberOfIds(len(gap))
            for i, pt in enumerate(gap):
                pid = vtk_pts.InsertNextPoint(pt[0], pt[1], z)
                pl.GetPointIds().SetId(i, pid)
            vtk_cells.InsertNextCell(pl)
            has_pts = True

        if not has_pts:
            return None

        poly = vtk.vtkPolyData()
        poly.SetPoints(vtk_pts)
        poly.SetLines(vtk_cells)
        return poly

    @staticmethod
    def contour_difference_build_actor(poly, color):
        """Build a vtkActor from a vtkPolyData with the given line colour.

        Args:
            poly:  vtkPolyData with line cells
            color: [r, g, b] floats 0–1

        Returns a vtkActor, or None if poly is None.
        """
        if poly is None:
            return None
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(2)
        return actor

    def contour_difference(self, surfaces_a_by_z, surfaces_b_by_z, color):
        """Compute the contour difference A minus B for matching Z levels.

        Operates on one B file at a time against the current live state of A
        (surfaces_a_by_z is already the result of any previous differences).
        Builds one actor per surviving A surface_id at each affected Z.

        Args:
            surfaces_a_by_z: {z: {sid: [(x,y,z)...]}} — current A contours
            surfaces_b_by_z: {z: {sid: [(x,y,z)...]}} — B file contours
            color:           [r, g, b] for new contour actors

        Returns:
            {sid: actor} dict of new actors for affected A surface_ids.
            Unaffected sids are NOT included — caller keeps their old actors.
            Also updates surfaces_a_by_z in-place with the new arc geometry
            so subsequent difference calls operate on the clipped state.
        """
        affected_zs = i3model.contour_difference_affected_zs(
            surfaces_a_by_z, surfaces_b_by_z)

        new_actors = {}   # {sid: actor}

        for z in affected_zs:
            a_sid_dict = surfaces_a_by_z.get(z, {})
            b_sid_dict = surfaces_b_by_z.get(z, {})

            for a_sid, a_pts in list(a_sid_dict.items()):
                arcs, fills = i3model.contour_difference_clip_one_sid(
                    a_pts, b_sid_dict, z)

                if arcs is None:
                    # A sid unaffected by all B sids at this Z — skip
                    continue

                if not arcs:
                    # A sid fully consumed — remove from live state
                    del surfaces_a_by_z[z][a_sid]
                    new_actors[a_sid] = None
                    continue

                # Build polydata and actor for the clipped result
                poly = i3model.contour_difference_build_polydata(arcs, fills, z)
                actor = i3model.contour_difference_build_actor(poly, color)
                new_actors[a_sid] = actor

                # Update live state so next difference call sees the clipped pts
                if arcs and not isinstance(arcs[0], list):
                    surfaces_a_by_z[z][a_sid] = list(arcs)
                else:
                    # Flatten first surviving arc as the new pts list
                    surfaces_a_by_z[z][a_sid] = arcs[0] if arcs else []

        return new_actors

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
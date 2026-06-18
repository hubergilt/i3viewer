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
        self.surface_file_id = 1
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

        z = vertices[0][2]      # all points share the same Z in 2.5D data
        for i, (x, y, z_pt, *_) in enumerate(vertices):
            pid = points.InsertNextPoint(x, y, z_pt)
            polyline.GetPointIds().SetId(i, pid)

        cells.InsertNextCell(polyline)
        return self.surfaces_build_actor(points, cells, color, surface_id, z)

    def surfaces_build_actor(self, points, cells, color, surface_id, z):
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
        setattr(actor, "z", z)
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
    def _boundary_substitution(a_pts, b_pts, tol=0.4):
        """Boundary substitution algorithm — 2.5D.

        Replaces the outer arc (shared boundary) of the main open polyline
        actor_a with the inner arc of the notch closed polygon actor_b,
        effectively cutting a notch out of the original contour.

        All geometry is 3D (x, y, z).  All intersection tests are performed
        in projected 2D (x, y); Z is interpolated from the originating 3D
        edge at parameter t so new intersection points carry the correct
        altitude.

        This is a thin orchestrator over four steps, each implemented as its
        own static method so they can be tested / debugged independently:
            Step 1 — i3model._bsub_step1_find_intersections
            Step 2 — i3model._bsub_step2_find_start_end
            Step 3 — i3model._bsub_step3_build_arcs
            Step 4 — i3model._bsub_step4_rebuild_a

        Args:
            a_pts: ordered list of (x, y, z) — open polyline (A)
            b_pts: ordered list of (x, y, z) — closed polygon (B), last
                   vertex implicitly connects back to first
            tol:   tolerance for vertex matching (default 0.4).
                   Must cover float32 rounding at the coordinate scale in use
                   (~0.25–0.5 units at scale ~8e6) while staying below the
                   minimum separation between genuinely distinct B vertices
                   (~1.0 units in practice). 0.4 satisfies both constraints.

        Returns:
            (arc_pts, inner_arc) where
                arc_pts   — rebuilt A polyline with the notch cut in
                inner_arc — B's inner arc (for gap fill / Delaunay)
            or None if fewer than 2 intersection points exist (no substitution),
            or if Start/End cannot be located, or rebuild fails.
        """
        intersections = i3model._bsub_step1_find_intersections(a_pts, b_pts, tol)
        if intersections is None:
            return None

        start_end = i3model._bsub_step2_find_start_end(b_pts, intersections, tol)
        if start_end is None:
            return None
        start_pt, end_pt = start_end

        arcs = i3model._bsub_step3_build_arcs(
            b_pts, start_pt, end_pt, intersections, tol)
        if arcs is None:
            return None
        outer_arc, inner_arc = arcs

        rebuilt = i3model._bsub_step4_rebuild_a(
            a_pts, start_pt, end_pt, outer_arc, tol)
        if rebuilt is None:
            return None

        return rebuilt, inner_arc

    @staticmethod
    def _bsub_step1_find_intersections(a_pts, b_pts, tol=0.4):
        """Step 1 — Compute all A-vertex × B-vertex coincidence points.

        Compares each unique A vertex directly against every B vertex in 2D
        (x, y); Z is taken from the matching A vertex. A hit is recorded
        only when both vertices coincide within tol. No edge projection, no
        t_b ambiguity. seen_a_vertices / seen_b_vertices guard against
        recording duplicate hits when two distinct A (or B) vertices both
        land within tol of the same counterpart vertex.

        Args:
            a_pts: ordered list of (x, y, z) — open polyline (A)
            b_pts: ordered list of (x, y, z) — closed polygon (B)
            tol:   vertex-matching tolerance

        Returns:
            list of (x, y, z, a_idx, t_a, b_idx, t_b) intersection tuples,
            or None if fewer than 2 are found (substitution not applicable).
        """
        n_a = len(a_pts)
        n_b = len(b_pts)

        def _find_b_vertex_for_vertex(px, py):
            """Return b_vertex_idx j if b_pts[j] coincides with (px, py) within tol, else None."""
            for j in range(n_b):
                bx, by = b_pts[j][0], b_pts[j][1]
                if (bx - px) ** 2 + (by - py) ** 2 < tol * tol:
                    return j
            return None

        raw_intersections = []   # (x, y, z, a_edge_idx, t_a, b_edge_idx, t_b)

        # Guard against two distinct A vertices both matching the same B vertex
        # (e.g. a_pts[1145] and a_pts[1146] both within tol of b_pts[1]).
        # seen_a_vertices prevents re-recording the same A vertex; seen_b_vertices
        # prevents re-recording the same B vertex from a different A vertex.
        seen_a_vertices = set()
        seen_b_vertices = set()
        for i in range(n_a):
            vx, vy, vz = a_pts[i][0], a_pts[i][1], a_pts[i][2]
            key_a = (round(vx, 6), round(vy, 6))
            if key_a in seen_a_vertices:
                continue
            seen_a_vertices.add(key_a)
            j_b = _find_b_vertex_for_vertex(vx, vy)
            if j_b is None:
                continue
            if j_b in seen_b_vertices:
                continue   # another A vertex already claimed this B vertex
            seen_b_vertices.add(j_b)
            raw_intersections.append((vx, vy, vz, i, 0.0, j_b, 0.0))

        intersections = list(raw_intersections)

        if len(intersections) < 2:
            return None   # not enough crossings — substitution not applicable

        # --- DEBUG: intersection points (csv format) ---
        print(f"[_boundary_substitution] Step 1: {len(intersections)} intersection(s) after dedup")
        for pt in intersections:
            print(f"{pt[0]},{pt[1]},{pt[2]},,,,")

        return intersections

    @staticmethod
    def _bsub_step2_find_start_end(b_pts, intersections, tol=0.4):
        """Step 2 — Find Start Point and End Point on actor_b.

        Walk b edges from index 0. For each edge, check whether any
        intersection point lies on it (within tol).  Detect transitions:
            first  true→false  →  Start Point (on the leaving edge)
            last   false→true  →  End Point   (on the entering edge)
        The last edge wraps back to the first for circular comparison.

        Args:
            b_pts:         ordered list of (x, y, z) — closed polygon (B)
            intersections: list of intersection tuples from Step 1
            tol:           vertex-matching tolerance

        Returns:
            (start_pt, end_pt) each as (x, y, z), or None if not found.
        """
        n_b = len(b_pts)

        def _dist2(p, q):
            return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2

        def _pt_on_b_edge(ix, iy, j):
            """True when (ix,iy) lies on b edge j within tol."""
            p3, p4 = b_pts[j][:2], b_pts[(j + 1) % n_b][:2]
            dx, dy = p4[0] - p3[0], p4[1] - p3[1]
            seg_len2 = dx * dx + dy * dy
            if seg_len2 < 1e-20:
                return _dist2((ix, iy, 0), (p3[0], p3[1], 0)) < tol * tol
            t = ((ix - p3[0]) * dx + (iy - p3[1]) * dy) / seg_len2
            if t < -tol or t > 1.0 + tol:
                return False
            cx = p3[0] + t * dx
            cy = p3[1] + t * dy
            return (cx - ix) ** 2 + (cy - iy) ** 2 < tol * tol

        # Boolean sequence: does any intersection point lie on b edge j?
        edge_has_intersection = []
        for j in range(n_b):
            has = any(_pt_on_b_edge(pt[0], pt[1], j) for pt in intersections)
            edge_has_intersection.append(has)

        # ------------------------------------------------------------------
        # Find the LARGEST contiguous (circular) run of B-edges that have NO
        # intersection with A. This run represents the genuine "gap" between
        # the start and end of the shared boundary — the real notch.
        #
        # Real-world A/B pairs often have many small scattered gaps (single
        # mismatched vertices, float rounding, short non-coincident stretches)
        # in addition to the one large gap that represents the actual notch.
        # Picking "the last transition seen while scanning j=0..n_b-1" (the
        # naive approach) is unreliable here: whichever small scattered gap
        # happens to be last in scan order wins, even though it has nothing
        # to do with the real notch. Picking the LARGEST gap instead reliably
        # identifies the real notch regardless of how many small spurious
        # gaps exist elsewhere on the boundary.
        #
        #   Start Point — on the edge just BEFORE the gap (last edge with
        #                  an intersection before the gap begins)
        #   End Point   — on the edge just AFTER the gap (first edge with
        #                  an intersection after the gap ends)
        # ------------------------------------------------------------------
        if not any(edge_has_intersection) or all(edge_has_intersection):
            return None

        # Rotate so we start scanning from an edge that HAS an intersection,
        # guaranteeing any run of "no intersection" edges is fully contained
        # (doesn't wrap past the end of the rotated order).
        scan_start = next(k for k in range(n_b) if edge_has_intersection[k])
        order = [(scan_start + k) % n_b for k in range(n_b)]

        best_len = 0
        best_run_start_idx = None  # index into `order`
        best_run_end_idx = None    # index into `order`

        idx = 0
        while idx < n_b:
            j = order[idx]
            if not edge_has_intersection[j]:
                run_start_idx = idx
                while idx < n_b and not edge_has_intersection[order[idx]]:
                    idx += 1
                run_len = idx - run_start_idx
                if run_len > best_len:
                    best_len = run_len
                    best_run_start_idx = run_start_idx
                    best_run_end_idx = idx - 1
            else:
                idx += 1

        start_edge = order[(best_run_start_idx - 1) % n_b]
        end_edge   = order[(best_run_end_idx + 1) % n_b]

        start_pt = None   # (x, y, z)
        end_pt   = None   # (x, y, z)

        for pt in intersections:
            if _pt_on_b_edge(pt[0], pt[1], start_edge):
                start_pt = (pt[0], pt[1], pt[2])
                break

        for pt in intersections:
            if _pt_on_b_edge(pt[0], pt[1], end_edge):
                end_pt = (pt[0], pt[1], pt[2])
                break

        if start_pt is None or end_pt is None:
            return None

        # --- DEBUG: start and end points (csv format) ---
        print(f"[_boundary_substitution] start_pt: {start_pt[0]},{start_pt[1]},{start_pt[2]},,,,")
        print(f"[_boundary_substitution] end_pt:   {end_pt[0]},{end_pt[1]},{end_pt[2]},,,,")

        return start_pt, end_pt

    @staticmethod
    def _bsub_step3_build_arcs(b_pts, start_pt, end_pt, intersections, tol=0.4):
        """Step 3 — Build two arcs from actor_b (walk in 3D).

        Walk b vertices from index 0.  Insert Start Point and End Point
        when the edge they lie on is traversed.  Split at those two points
        to form Arc 1 (first half) and Arc 2 (second half + wrap-around).
        Count how many intersections from Step 1 belong to each arc.
            Arc with more intersections → inner arc.
            Arc with fewer intersections → outer arc.

        Args:
            b_pts:         ordered list of (x, y, z) — closed polygon (B)
            start_pt:      (x, y, z) from Step 2
            end_pt:        (x, y, z) from Step 2
            intersections: list of intersection tuples from Step 1
            tol:           vertex-matching tolerance

        Returns:
            (outer_arc, inner_arc), each a list of (x, y, z) points,
            or None if Start/End could not be spliced into B's boundary.
        """
        n_b = len(b_pts)

        def _dist2(p, q):
            return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2

        def _close_to(p2d, q2d):
            return (p2d[0] - q2d[0]) ** 2 + (p2d[1] - q2d[1]) ** 2 < tol * tol

        # Ordered b vertices with Start/End inserted.
        #
        # start_pt / end_pt always coincide with an actual B VERTEX (Step 1
        # only records vertex-to-vertex coincidences), so insertion is keyed
        # on exact vertex match (_close_to(v, start_pt)) rather than fuzzy
        # edge-projection (_pt_on_b_edge). Using edge-projection here was the
        # bug: short, nearly-collinear consecutive B edges can all satisfy
        # "start_pt projects onto this edge within tol", causing start_pt to
        # be spliced in one (or more) edges too early and leaving the real
        # vertex it replaced as a stray leftover point in the rebuilt arc.
        b_augmented = []    # list of (x, y, z, tag)  tag ∈ {'v','start','end'}
        start_inserted = False
        end_inserted   = False

        for j in range(n_b):
            v = b_pts[j]
            is_start = not start_inserted and _close_to(start_pt[:2], v[:2])
            is_end   = not end_inserted   and _close_to(end_pt[:2],   v[:2])

            if is_start and is_end:
                # Degenerate: start_pt and end_pt coincide with the same
                # vertex (shouldn't normally happen, but guard against it).
                b_augmented.append((*start_pt, 'start'))
                b_augmented.append((*end_pt, 'end'))
                start_inserted = True
                end_inserted   = True
                continue

            if is_start:
                b_augmented.append((*start_pt, 'start'))
                start_inserted = True
                continue

            if is_end:
                b_augmented.append((*end_pt, 'end'))
                end_inserted = True
                continue

            b_augmented.append((*v[:3], 'v'))

        # Handle case where start/end fall on the wrap-around (last→first) edge
        if not start_inserted:
            b_augmented.append((*start_pt, 'start'))
        if not end_inserted:
            b_augmented.append((*end_pt, 'end'))

        # Split augmented list into Arc1 (start→end) and Arc2 (end→start+wrap)
        sp_idx = next((i for i, p in enumerate(b_augmented) if p[3] == 'start'),
                      None)
        ep_idx = next((i for i, p in enumerate(b_augmented) if p[3] == 'end'),
                      None)

        if sp_idx is None or ep_idx is None:
            return None

        def _to_xyz(entries):
            return [(e[0], e[1], e[2]) for e in entries]

        if sp_idx < ep_idx:
            arc1 = _to_xyz(b_augmented[sp_idx: ep_idx + 1])
            arc2 = _to_xyz(b_augmented[ep_idx:] + b_augmented[:sp_idx + 1])
        else:
            arc1 = _to_xyz(b_augmented[sp_idx:] + b_augmented[:ep_idx + 1])
            arc2 = _to_xyz(b_augmented[ep_idx: sp_idx + 1])

        # Count intersections belonging to each arc (by 2D proximity)
        def _count_intersections_on_arc(arc, ixs):
            count = 0
            for pt in ixs:
                for k in range(len(arc) - 1):
                    dx = arc[k + 1][0] - arc[k][0]
                    dy = arc[k + 1][1] - arc[k][1]
                    seg2 = dx * dx + dy * dy
                    if seg2 < 1e-20:
                        if _dist2(pt[:2] + (0,), arc[k][:2] + (0,)) < tol * tol:
                            count += 1
                            break
                        continue
                    t = ((pt[0] - arc[k][0]) * dx +
                         (pt[1] - arc[k][1]) * dy) / seg2
                    if t < -tol or t > 1.0 + tol:
                        continue
                    cx = arc[k][0] + t * dx
                    cy = arc[k][1] + t * dy
                    if (cx - pt[0]) ** 2 + (cy - pt[1]) ** 2 < tol * tol:
                        count += 1
                        break
            return count

        count1 = _count_intersections_on_arc(arc1, intersections)
        count2 = _count_intersections_on_arc(arc2, intersections)

        if count1 >= count2:
            inner_arc = arc1
            outer_arc = arc2
        else:
            inner_arc = arc2
            outer_arc = arc1

        # --- DEBUG: outer arc (xyzs format) ---
        print(f"[_boundary_substitution] outer_arc ({len(outer_arc)} pts):")
        for p in outer_arc:
            print(f"{p[0]} {p[1]} {p[2]}")
        print("$")

        # --- DEBUG: inner arc (xyzs format) ---
        print(f"[_boundary_substitution] inner_arc ({len(inner_arc)} pts):")
        for p in inner_arc:
            print(f"{p[0]} {p[1]} {p[2]}")
        print("$")

        return outer_arc, inner_arc

    @staticmethod
    def _bsub_step4_rebuild_a(a_pts, start_pt, end_pt, outer_arc, tol=0.4):
        """Step 4 — Rebuild actor_a.

        Walk a_pts in 3D applying:
            • before start edge  → keep
            • start on vertex    → keep vertex, mark as start
            • start on edge      → keep vertices up to and incl. start edge
                                    start, insert interpolated start point
            • between start/end  → skip
            • end on vertex      → mark as end, keep
            • end on edge        → insert interpolated end point
            • after end edge     → keep
        Insert outer_arc between start and end (reverse if needed).

        Args:
            a_pts:     ordered list of (x, y, z) — open polyline (A)
            start_pt:  (x, y, z) from Step 2 (order vs end_pt not assumed)
            end_pt:    (x, y, z) from Step 2
            outer_arc: list of (x, y, z) from Step 3
            tol:       vertex-matching tolerance

        Returns:
            rebuilt A polyline as list of (x, y, z), or None on failure.
        """
        n_a = len(a_pts)

        def _dist2(p, q):
            return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2

        def _close_to(p2d, q2d):
            return (p2d[0] - q2d[0]) ** 2 + (p2d[1] - q2d[1]) ** 2 < tol * tol

        def _find_on_a_edge(pt2d, idx_a):
            """Return t if pt2d lies on edge idx_a of a_pts."""
            p1, p2 = a_pts[idx_a][:2], a_pts[idx_a + 1][:2]
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            seg2 = dx * dx + dy * dy
            if seg2 < 1e-20:
                return None
            t = ((pt2d[0] - p1[0]) * dx + (pt2d[1] - p1[1]) * dy) / seg2
            if t < -tol or t > 1.0 + tol:
                return None
            cx = p1[0] + t * dx
            cy = p1[1] + t * dy
            if (cx - pt2d[0]) ** 2 + (cy - pt2d[1]) ** 2 < tol * tol:
                return t
            return None

        # Locate start_pt and end_pt on A
        a_start_edge = None; a_start_t = None; a_start_on_vertex = None
        a_end_edge   = None; a_end_t   = None; a_end_on_vertex   = None

        for i in range(n_a - 1):
            if a_start_edge is None:
                # Check if start_pt coincides with vertex i or i+1 within tol
                if _dist2(start_pt[:2], a_pts[i][:2]) < tol * tol:
                    a_start_edge = i; a_start_t = 0.0; a_start_on_vertex = i
                elif _dist2(start_pt[:2], a_pts[i + 1][:2]) < tol * tol:
                    a_start_edge = i; a_start_t = 1.0; a_start_on_vertex = i + 1
                else:
                    t = _find_on_a_edge(start_pt[:2], i)
                    if t is not None:
                        a_start_edge = i; a_start_t = t; a_start_on_vertex = None

            if a_end_edge is None:
                if _dist2(end_pt[:2], a_pts[i][:2]) < tol * tol:
                    a_end_edge = i; a_end_t = 0.0; a_end_on_vertex = i
                elif _dist2(end_pt[:2], a_pts[i + 1][:2]) < tol * tol:
                    a_end_edge = i; a_end_t = 1.0; a_end_on_vertex = i + 1
                else:
                    t = _find_on_a_edge(end_pt[:2], i)
                    if t is not None:
                        a_end_edge = i; a_end_t = t; a_end_on_vertex = None

        if a_start_edge is None or a_end_edge is None:
            print(f"[_boundary_substitution] Step 4 ERROR: could not locate start/end on A "
                  f"(a_start_edge={a_start_edge}, a_end_edge={a_end_edge})")
            return None

        # Ensure start comes before end along A
        if a_start_edge > a_end_edge or (
                a_start_edge == a_end_edge and a_start_t > a_end_t):
            start_pt, end_pt = end_pt, start_pt
            a_start_edge, a_end_edge = a_end_edge, a_start_edge
            a_start_t,    a_end_t    = a_end_t,    a_start_t
            a_start_on_vertex, a_end_on_vertex = a_end_on_vertex, a_start_on_vertex
            print(f"[_boundary_substitution] Step 4: swapped start/end so start comes first on A")

        print(f"[_boundary_substitution] Step 4: a_start_edge={a_start_edge} t={a_start_t:.4f} "
              f"on_vertex={a_start_on_vertex}")
        print(f"[_boundary_substitution] Step 4: a_end_edge={a_end_edge}   t={a_end_t:.4f} "
              f"on_vertex={a_end_on_vertex}")

        # Build result A polyline
        result = []

        # Vertices strictly before the start edge
        result.extend((p[0], p[1], p[2]) for p in a_pts[:a_start_edge + 1])

        # Insert start point (or use the coincident vertex)
        if a_start_on_vertex is not None:
            if result and _close_to(result[-1][:2], a_pts[a_start_on_vertex][:2]):
                pass  # already appended as part of the prefix above
            else:
                result.append((a_pts[a_start_on_vertex][0],
                                a_pts[a_start_on_vertex][1],
                                a_pts[a_start_on_vertex][2]))
        else:
            # Split: append interpolated start point
            if not result or not _close_to(result[-1][:2], start_pt[:2]):
                result.append(start_pt)

        # Outer arc goes between start_pt and end_pt
        # Check orientation: if outer_arc[-1] is closer to start_pt than to
        # end_pt, reverse it so it flows start→end correctly.
        if len(outer_arc) >= 2:
            d_fwd = _dist2(outer_arc[-1][:2], end_pt[:2])
            d_rev = _dist2(outer_arc[0][:2],  end_pt[:2])
            if d_rev < d_fwd:
                outer_arc = list(reversed(outer_arc))
        # Append arc (skip first/last if already equal to start/end)
        for k, op in enumerate(outer_arc):
            if k == 0 and _close_to(op[:2], start_pt[:2]):
                continue
            if k == len(outer_arc) - 1 and _close_to(op[:2], end_pt[:2]):
                continue
            result.append((op[0], op[1], op[2]))

        # Insert end point
        if a_end_on_vertex is not None:
            ep = (a_pts[a_end_on_vertex][0],
                  a_pts[a_end_on_vertex][1],
                  a_pts[a_end_on_vertex][2])
            if not result or not _close_to(result[-1][:2], ep[:2]):
                result.append(ep)
        else:
            if not result or not _close_to(result[-1][:2], end_pt[:2]):
                result.append(end_pt)

        # Vertices strictly after the end edge
        after_start = a_end_edge + 1 if a_end_on_vertex is None \
            else (a_end_on_vertex + 1 if a_end_t == 1.0 else a_end_edge + 1)
        result.extend((p[0], p[1], p[2]) for p in a_pts[after_start:])

        if len(result) < 2:
            print(f"[_boundary_substitution] Step 4 ERROR: result has only {len(result)} point(s)")
            return None

        print(f"[_boundary_substitution] Step 4: result polyline has {len(result)} pts "
              f"(prefix={a_start_edge + 1}, outer_arc={len(outer_arc)}, "
              f"suffix={len(result) - a_start_edge - 1 - len(outer_arc)} approx)")

        return result

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
    def actor_pts(actor):
        """Extract the ordered list of (x, y, z) vertices from a vtkActor.

        Reads the first polyline cell from the actor's vtkPolyData.  All
        contour actors produced by this module store exactly one vtkPolyLine
        cell, so this is the correct extraction path.

        Returns a list of (x, y, z) tuples, or an empty list if the actor
        carries no usable geometry.
        """
        mapper = actor.GetMapper()
        if mapper is None:
            return []
        poly = mapper.GetInput()
        if poly is None:
            return []
        pts = poly.GetPoints()
        if pts is None:
            return []

        lines = poly.GetLines()
        if lines is None or lines.GetNumberOfCells() == 0:
            # Fall back: return all points in index order
            return [(pts.GetPoint(i)[0],
                     pts.GetPoint(i)[1],
                     pts.GetPoint(i)[2])
                    for i in range(pts.GetNumberOfPoints())]

        lines.InitTraversal()
        id_list = vtk.vtkIdList()
        lines.GetNextCell(id_list)
        return [(pts.GetPoint(id_list.GetId(i))[0],
                 pts.GetPoint(id_list.GetId(i))[1],
                 pts.GetPoint(id_list.GetId(i))[2])
                for i in range(id_list.GetNumberOfIds())]

    @staticmethod
    def contour_difference_clip_one_sid(actor_a, actor_b, z):
        """Clip one A surface_id's contour against one B contour at this Z.

        Extracts geometry from both actors and runs the boundary
        substitution algorithm (intersection-based). Interior-cut polygon
        clipping (_clip_contour_2d) is not used.

        Args:
            actor_a: vtkActor whose contour is being clipped (A)
            actor_b: vtkActor clipping against (B)
            z:       the Z coordinate

        Returns:
            (arc_segments, gap_fills) where arc_segments is a list of point-lists
            and gap_fills is a list of point-lists (B boundary arcs to display).
            Returns (None, []) if A is unaffected, ([], []) if fully consumed.
        """
        a_pts = i3model.actor_pts(actor_a)
        b_pts = i3model.actor_pts(actor_b)

        if len(a_pts) < 2 or len(b_pts) < 3:
            return None, []

        # Intersection-based boundary substitution only
        result = i3model._boundary_substitution(a_pts, b_pts)
        if result is None:
            # No usable substitution — A is unaffected
            return None, []

        arc_pts, inner_arc = result
        arcs  = [arc_pts]
        fills = [inner_arc] if len(inner_arc) >= 2 else []

        if not arcs:
            return [], []

        return arcs, fills

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
    def contour_difference_build_actor(poly, color, z):
        """Build a vtkActor from a vtkPolyData with the given line colour.

        Args:
            poly:  vtkPolyData with line cells
            color: [r, g, b] floats 0–1
            z:     Z altitude to store as an attribute on the actor

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
        setattr(actor, "z", z)
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

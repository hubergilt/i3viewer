from enum import Enum


class FileType(Enum):
    """Represents the possible types of files"""

    XYZ = "xyz"
    XYZS = "xyzs"
    SRG = "srg"
    DB = "db"
    CSV = "csv"
    TXT = "txt"

    @staticmethod
    def get_fileType(file_path):
        if file_path:
            if file_path.endswith(".xyz"):
                return FileType.XYZ
            elif file_path.endswith(".xyzs"):
                return FileType.XYZS
            elif file_path.endswith(".srg"):
                return FileType.SRG
            elif file_path.endswith(".db"):
                return FileType.DB
            elif file_path.endswith(".csv"):
                return FileType.CSV
            elif file_path.endswith(".txt"):
                return FileType.TXT
            else:
                return None


class HeatMapCfg(Enum):
    """Represents the possible configuration for HeatMap"""

    INIT = "init"
    OPEN = "open"
    CONF = "conf"
    CLEAR = "clear"
    PERIOD = "period"


class DelaunayCfg:
    """
    A class to configure, run and save parameters for Delaunay-based surface reconstruction
    from contour lines.

    This class encapsulates the parameters and process of creating a terrain mesh
    from elevation contours using VTK's Delaunay triangulation algorithm.
    """

    def __init__(
        self,
        cleaner_tolerance=0.001,
        delaunay_alpha=0.0,
        delaunay_tolerance=0.001,
        delaunay_offset=5.0,
        feature_angle=60.0,
        projection_plane_mode=0,
    ):
        """
        Initialize the reconstruction parameters with default values.

        Args:
            cleaner_tolerance (float): Controls point merging during data cleaning.
                                      Points closer than this distance are merged.
                                      Range: 0.0001 to 0.1, default: 0.001

            delaunay_alpha (float): Controls the shape of triangulation.
                                   0.0 = standard Delaunay (convex hull),
                                   higher values = more concave boundary.
                                   Range: 0.0 to 100.0, default: 0.0

            delaunay_tolerance (float): Numerical tolerance during triangulation.
                                       Range: 0.0001 to 0.1, default: 0.001

            delaunay_offset (float): Controls size of super triangle during triangulation.
                                    Range: 1.0 to 20.0, default: 5.0

            feature_angle (float): Angle in degrees to determine sharp edges when computing normals.
                                  Range: 0.0 to 180.0, default: 60.0

            projection_plane_mode (int): Controls how points are projected for triangulation.
                                        0 = best fitting plane
                                        1 = XY plane
                                        2 = YZ plane
                                        3 = XZ plane
                                        Default: 0
        """
        # Store parameters
        self.cleaner_tolerance = cleaner_tolerance
        self.delaunay_alpha = delaunay_alpha
        self.delaunay_tolerance = delaunay_tolerance
        self.delaunay_offset = delaunay_offset
        self.feature_angle = feature_angle
        self.projection_plane_mode = projection_plane_mode

    @staticmethod
    def min_max_range():
        """
        Get the valid ranges for each parameter.

        Returns:
            Dict[str, Tuple[float, float]]: Dictionary of parameter names and their min/max values
        """
        return {
            "cleaner_tolerance": (0.0001, 0.1),
            "delaunay_alpha": (0.0, 100.0),
            "delaunay_tolerance": (0.0001, 0.1),
            "delaunay_offset": (1.0, 20.0),
            "feature_angle": (0.0, 180.0),
            "projection_plane_mode": (0, 3),
        }

    def config_high_resolution(self):
        self.cleaner_tolerance = 0.0001
        self.delaunay_alpha = 0.0
        self.delaunay_tolerance = 0.0001
        self.delaunay_offset = 2.0
        self.feature_angle = 45.0
        self.projection_plane_mode = 0

    def config_typical_gis(self):
        self.cleaner_tolerance = 0.001
        self.delaunay_alpha = 0.5
        self.delaunay_tolerance = 0.001
        self.delaunay_offset = 5.0
        self.feature_angle = 60.0
        self.projection_plane_mode = 0

    def config_noise_data(self):
        self.cleaner_tolerance = 0.01
        self.delaunay_alpha = 2.0
        self.delaunay_tolerance = 0.01
        self.delaunay_offset = 10.0
        self.feature_angle = 90.0
        self.projection_plane_mode = 0

    def config_contour_preserving(self):
        self.cleaner_tolerance = 0.0005
        self.delaunay_alpha = 1.0
        self.delaunay_tolerance = 0.001
        self.delaunay_offset = 5.0
        self.feature_angle = 30.0
        self.projection_plane_mode = 0


class SurfaceCfg:
    """
    A class to manage visualization parameters for 3D surface meshes in VTK.

    This class handles settings related to surface appearance, including:
    - Surface colors
    - Wireframe colors
    - Surface opacity
    - Edge thickness

    """

    def __init__(
        self,
        surface_color=(0.8, 0.8, 1.0),
        wireframe_color=(0.0, 0.0, 0.0),
        surface_opacity=1.0,
        edge_thickness=1.0,
    ):
        """
        Initialize the visualization parameters with default values.

        Args:
            surface_color (Tuple[float, float, float]): RGB color for the surface (0-1 range)
            wireframe_color (Tuple[float, float, float]): RGB color for edges (0-1 range)
            surface_opacity (float): Surface transparency (0-1, where 1 is opaque)
            edge_thickness (float): Width of edge lines
        """
        # Basic visualization parameters
        self.surface_color = surface_color
        self.wireframe_color = wireframe_color
        self.surface_opacity = surface_opacity
        self.edge_thickness = edge_thickness

    @staticmethod
    def min_max_range():
        """
        Get the valid ranges for each parameter.

        Returns:
            Dict[str, Tuple[float, float]]: Dictionary of parameter names and their min/max values
        """
        return {
            "surface_opacity": (0.0, 1.0),
            "edge_thickness": (1, 10),
        }

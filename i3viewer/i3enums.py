from enum import Enum


class FileType(Enum):
    """Represents the possible types of files"""

    XYZ = "xyz"
    SRG = "srg"
    DB = "db"
    CSV = "csv"
    TXT = "txt"

    @staticmethod
    def get_fileType(file_path):
        if file_path:
            if file_path.endswith(".xyz"):
                return FileType.XYZ
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

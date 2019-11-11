from typing import TYPE_CHECKING, Iterable, Optional

from exiftool import ExifTool  # type: ignore
from exiftool import executable as exiftool_default_exe  # type: ignore

from .get_thermal import get_thermal, get_thermal_batch
from .pathutils import Path

if TYPE_CHECKING:
    import numpy as np  # type: ignore


class FlirExtractor:
    """Extracts thermal data from FLIR images using ExifTool.

    Attributes:
        exiftoolpath: The path to the ExifTool executable.

    Example:
        with FlirExtractor(exiftoolpath="/usr/bin/exiftool") as extractor:
            # get a single thermal data point
            thermal_data = extractor.get_thermal("./path/to/FLIR.jpg")
            # get multiple thermal data
            thermal_d_list = extractor.get_thermal_batch(
                ["./FLIR1.jpg", "./FLIR2.jpg"]
            )
    """

    exiftoolpath: Optional[Path]
    _exiftool: Optional[ExifTool]

    def __init__(self, exiftoolpath: Path = exiftool_default_exe):
        self.exiftoolpath = exiftoolpath
        self._exiftool = None

    @property
    def exiftool(self) -> ExifTool:
        _exiftool = self._exiftool
        if _exiftool is None:
            raise AttributeError(
                "ExifTool was not initialized. "
                "Use FlirExtractor in a context manager, e.g. \n"
                "with FlirExtractor() as e:\n"
                "    e.do_magic()"
            )
        return _exiftool

    def open(self):
        """Creates an Exiftool process.

        Not recommended, use `with:` context manager instead.
        """
        if self._exiftool is not None:
            raise Exception("ExifTool was already initialized.")
        self._exiftool = ExifTool(executable_=str(self.exiftoolpath))
        self._exiftool.start()

    def close(self):
        """Closes the Exiftool process.

        Not recommended, use `with:` context manager instead.
        """
        if self._exiftool is None:
            return  # already closed, do nothing
        self._exiftool.terminate()
        self._exiftool = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    def get_thermal(self, filepath: Path) -> "np.ndarray":
        """Gets a thermal image from a FLIR file.

        Parameters:
            filepath: The path to the FLIR file.

        Returns:
            The thermal data in Celcius as a 2-D numpy array.
        """
        return get_thermal(self.exiftool, filepath)

    def get_thermal_batch(
        self, filepaths: Iterable[Path]
    ) -> Iterable["np.ndarray"]:
        """Gets thermal images from a list of FLIR files.

        Parameters:
            filepaths: The paths to the FLIR files.

        Returns:
            A list of the thermal data in Celcius as 2-D numpy arrays.
        """
        return get_thermal_batch(self.exiftool, filepaths)

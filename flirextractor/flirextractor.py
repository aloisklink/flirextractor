from typing import TYPE_CHECKING, Iterable, Optional

from exiftool import ExifTool

from .get_thermal import get_thermal_batch, get_thermal
from .pathutils import Path

if TYPE_CHECKING:
    import numpy as np

class FlirExtractor:
    exiftoolpath: Optional[Path]
    _exiftool: Optional[ExifTool]

    def __init__(self, exiftoolpath: Path = None):
        self.exiftoolpath = exiftoolpath
        self._exiftool = None

    @property
    def exiftool(self) -> ExifTool:
        _exiftool = self._exiftool
        if _exiftool is None:
            raise AttributeError(
                "ExifTool was not initialized. "
                "Did you use FlirExtractor in a context manager, e.g. \n"
                "with FlirExtractor() as e:\n"
                "    e.do_magic()")
        return _exiftool

    def open(self):
        self._exiftool = ExifTool(executable_=self.exiftoolpath)
        self._exiftool.start()

    def close(self):
        self._exiftool.terminate()
        self._exiftool = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    def get_thermal(self, filepath: Path) -> "np.ndarray":
        return get_thermal(self.exiftool, filepath)

    def get_thermal_batch(
        self, filepaths: Iterable[Path]) -> Iterable["np.ndarray"]:
        return get_thermal_batch(self.exiftool, filepaths)

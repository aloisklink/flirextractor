"""Used to load the thermal image from a FLIR JPG.

This is based of the algorithm used in
https://github.com/gtatters/Thermimage/blob/master/R/raw2temp.R
"""
import typing
import io

import numpy as np
from PIL import Image

from exiftool import ExifTool, fsencode

from .raw_temp_to_celcius import raw_temp_to_celcius
from .pathutils import Path, get_str_filepath

def _get_tag_bytes(
    exiftool: ExifTool,
    tag: typing.Text,
    filepath: Path,
) -> bytes:
    """Gets the data of a tag in a file in bytes using exiftool.

    No batch version is possible, as there is no way to seperate the bytes
    output by exiftool.

    Parameters:
        exiftool: The ExifTool process to use.
        tag: The metadata tag to load.
        filepath: The path to the file to load.

    Returns:
        The loaded metadata for the tag in `bytes`.
    """
    params = ["-b", f"-{tag}", str(filepath)]
    params_as_bytes = map(fsencode, params)
    return exiftool.execute(*params_as_bytes)

def _get_raw_np(exiftool: ExifTool, filepath: Path) -> np.ndarray:
    """Gets the raw thermal data from a FLIR image.

    These needed to be converted using the calibration constants into a
    useable form.

    Parameters:
        exiftool: The ExifTool process to use.
        filepath: The path to the file to load.

    Returns:
        The raw data as a 2-D numpy array.
    """
    raw_image_bytes = _get_tag_bytes(exiftool, "RawThermalImage", filepath)
    # we can't use Image.frombytes(), since bytes is not just the pixel data
    fp = io.BytesIO(raw_image_bytes)
    image = Image.open(fp)
    return np.array(image)

def get_thermal(exiftool: ExifTool, filepath: Path) -> np.ndarray:
    """Loads the thermal image from a single FLIR image.

    Please use `get_thermal_batch` for efficiency if you are loading
    multiple FLIR images.

    Parameters:
        exiftool: The ExifTool process to use.
        filepath: The path to the file to load.

    Returns:
        The thermal data in Celcius as a 2-D numpy array.
    """
    filepaths = (filepath,)
    # get first result from get_thermal_batch
    return next(iter(get_thermal_batch(exiftool, filepaths)))


exif_var_tags = dict(
    emissivity = "Emissivity",
    subject_distance = "SubjectDistance",
    reflected_temp = "ReflectedApparentTemperature",
    atmospheric_temp = "AtmosphericTemperature",
    ir_window_temp = "IRWindowTemperature",
    ir_window_transmission = "IRWindowTransmission",
    humidity = "RelativeHumidity",
    planck_r1 = "PlanckR1",
    planck_b = "PlanckB",
    planck_f = "PlanckF",
    planck_0 = "PlanckO",
    planck_r2 = "PlanckR2",
)
"""A mapping of Python variable names to EXIF metadata tag name"""
_inv_exif_var_tags = {exif: py for py, exif in exif_var_tags.items()}
"""A reverse mapping of exif_var_tags"""

def convert_image(
    metadata: typing.Mapping[typing.Text, typing.Text],
    raw_np: np.ndarray,
) -> np.ndarray:
    """Converts raw FLIR thermal data into Celcius using metadata.

    Parameters:
        metadata: A list of metadata tags with calibration values.
        raw_np: The raw thermal data as a 2-D numpy array.

    Returns:
        The thermal data in Celcius as a 2-D numpy array.
    """
    converted_metadata = {
        # convert {EXIFNAME: val} to {python_name: val}
        _inv_exif_var_tags[mdname]: float(val)
        for mdname, val in metadata.items()
        if mdname in _inv_exif_var_tags
    }
    return raw_temp_to_celcius(raw_np, **converted_metadata)

def get_thermal_batch(
    exiftool: ExifTool, filepaths: typing.Iterable[Path],
) -> typing.Iterable[np.ndarray]:
    """Loads the thermal images from multiple FLIR images.

    Parameters:
        exiftool: The ExifTool process to use.
        filepaths: A list of paths to the files to load.

    Returns:
        A list of thermal data in Celcius as 2-D numpy arrays.
    """
    str_paths = [get_str_filepath(filepath) for filepath in filepaths]
    metadata = exiftool.get_tags_batch(exif_var_tags.values(), str_paths)
    raw_images = [_get_raw_np(exiftool, filepath) for filepath in str_paths]
    return [
        convert_image(image_metadata, raw_image)
        for image_metadata, raw_image in zip(metadata, raw_images)
    ]
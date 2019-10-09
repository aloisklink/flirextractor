"""Used to load the thermal image from a FLIR JPG.

This is based of the algorithm used in
https://github.com/gtatters/Thermimage/blob/master/R/raw2temp.R
"""
import typing
import io

import numpy as np
from PIL import Image

from exiftool import ExifTool, fsencode

if typing.TYPE_CHECKING:
    import os

from .raw_temp_to_celcius import raw_temp_to_celcius

Path = typing.Union["os.PathLike", typing.Text]

def _get_tag_bytes(
    exiftool: ExifTool,
    tag: typing.Text,
    filepath: Path,
) -> bytes:
    params = ["-b", f"-{tag}", str(filepath)]
    params_as_bytes = map(fsencode, params)
    return exiftool.execute(*params_as_bytes)

def _get_raw_np(exiftool: ExifTool, filepath: Path) -> np.ndarray:
    raw_image_bytes = _get_tag_bytes(exiftool, "RawThermalImage", filepath)
    # we can't use Image.frombytes(), since bytes is not just the pixel data
    fp = io.BytesIO(raw_image_bytes)
    image = Image.open(fp)
    return np.array(image)

def get_thermal(exiftool: ExifTool, filepath: Path) -> np.ndarray:
    filepaths = (filepath,)
    return get_thermal_batch(exiftool, filepaths)[0]

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
inv_exif_var_tags = {exif: py for py, exif in exif_var_tags.items()}

def convert_image(
    metadata: typing.Mapping[typing.Text, typing.Text],
    raw_np: np.ndarray,
) -> np.ndarray:
    converted_metadata = {
        # convert {EXIFNAME: val} to {python_name: val}
        inv_exif_var_tags[mdname]: float(val)
        for mdname, val in metadata.items()
        if mdname in inv_exif_var_tags
    }
    return raw_temp_to_celcius(raw_np, **converted_metadata)

def get_thermal_batch(
    exiftool: ExifTool, filepaths: typing.Iterable[Path],
) -> typing.Iterable[np.ndarray]:
    raw_paths = [str(filepath) for filepath in filepaths]
    metadata = exiftool.get_tags_batch(exif_var_tags.values(), raw_paths)
    raw_images = [_get_raw_np(exiftool, filepath) for filepath in raw_paths]
    return [
        convert_image(image_metadata, raw_image)
        for image_metadata, raw_image in zip(metadata, raw_images)
    ]

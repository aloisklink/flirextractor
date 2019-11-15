"""Used to load the thermal image from a FLIR JPG.

Calls exiftool to extract the embedded image and metadata from the FLIR file.
"""
import io
import typing

import numpy as np  # type: ignore
from exiftool import ExifTool, fsencode  # type: ignore
from PIL import Image  # type: ignore

from .pathutils import Path, get_str_filepath
from .raw_temp_to_celcius import (
    AtmosphericTransConsts,
    CameraPlanckConsts,
    raw_temp_to_celcius,
)
from .utils import split_dict


def _get_tag_bytes(
    exiftool: ExifTool, tag: typing.Text, filepath: Path
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
    as_array = np.array(image)
    if image.format == "PNG":
        # bug in FLIR cameras -> they sometimes save in little-endian format
        as_array = as_array.astype("uint16").newbyteorder()
    return as_array


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


atmos_exif_var_tags = dict(
    alpha_1="AtmosphericTransAlpha1",
    alpha_2="AtmosphericTransAlpha2",
    beta_1="AtmosphericTransBeta1",
    beta_2="AtmosphericTransBeta2",
    x="AtmosphericTransX",
)


planck_exif_var_tags = dict(
    r1="PlanckR1", b="PlanckB", f="PlanckF", zero="PlanckO", r2="PlanckR2",
)
MetadataWithConstants = typing.Dict[
    str, typing.Union[float, CameraPlanckConsts, AtmosphericTransConsts]
]


def _extract_metadata_constants(
    input_dict: typing.Mapping[str, float]
) -> typing.Tuple[
    CameraPlanckConsts, AtmosphericTransConsts, typing.Mapping[str, float],
]:
    """Extracts any constant values into their objects

    Parameters:
        input_dict: All metadata values as floats.

    Returns:
        The planck constants, the atmospheric constants,
        nd the remaining values.
    """
    atmos_vars, remainder = split_dict(input_dict, atmos_exif_var_tags)
    atmos_consts = AtmosphericTransConsts(**atmos_vars)
    planck_vars, remainder = split_dict(remainder, planck_exif_var_tags)
    planck_consts = CameraPlanckConsts(**planck_vars)
    return planck_consts, atmos_consts, remainder


exif_var_tags = dict(
    emissivity="Emissivity",
    subject_distance="SubjectDistance",
    reflected_temp="ReflectedApparentTemperature",
    atmospheric_temp="AtmosphericTemperature",
    ir_window_temp="IRWindowTemperature",
    ir_window_transmission="IRWindowTransmission",
    humidity="RelativeHumidity",
    peak_spectral_sensitivity="PeakSpectralSensitivity",
    **atmos_exif_var_tags,
    **planck_exif_var_tags,
)
"""A mapping of Python variable names to EXIF metadata tag name"""
_inv_exif_var_tags = {exif: py for py, exif in exif_var_tags.items()}
"""A reverse mapping of exif_var_tags"""


def convert_exif_tag_to_py(full_exif_tag: str) -> str:
    for substr_exif_tag in _inv_exif_var_tags:
        if substr_exif_tag in full_exif_tag:
            return _inv_exif_var_tags[substr_exif_tag]
    raise KeyError(
        f"Could not find exif_tag {full_exif_tag} "
        f"in {_inv_exif_var_tags.keys()}."
    )


def convert_image(
    metadata: typing.Mapping[typing.Text, typing.Any], raw_np: np.ndarray
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
        convert_exif_tag_to_py(mdname): float(val)  # should already be float
        for mdname, val in metadata.items()
        if mdname != "SourceFile"  # exiftool also returns this for some reason
    }
    planck_consts, atmos_consts, remainder = _extract_metadata_constants(
        converted_metadata
    )
    return raw_temp_to_celcius(
        raw_np, planck=planck_consts, atmos_consts=atmos_consts, **remainder
    )


def get_thermal_batch(
    exiftool: ExifTool, filepaths: typing.Iterable[Path]
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

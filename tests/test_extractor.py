import pathlib
from typing import NamedTuple, Tuple

import numpy as np
import pytest

from flirextractor import FlirExtractor
from flirextractor.errors import UnsupportedImageError


class Image(NamedTuple):
    path: str
    shape: Tuple[int, int]


class AbsImage(NamedTuple):
    path: pathlib.Path
    shape: Tuple[int, int]


TEST_IMAGES = [Image("./IR_2412.jpg", (480, 640))]


@pytest.fixture(scope="module", params=TEST_IMAGES)
def image(request) -> AbsImage:
    test_image = request.param
    absolute_path = pathlib.Path(__file__).parent / test_image.path
    vals = test_image._asdict()
    vals["path"] = absolute_path
    return AbsImage(**vals)


def test_get_thermal(image: AbsImage):
    with FlirExtractor() as flir_extractor:
        thermal_a = flir_extractor.get_thermal(image.path)
        # should work when loading a str variable
        thermal_b = flir_extractor.get_thermal(str(image.path))
        # loading the same file twice should get the same result
        assert np.allclose(thermal_a, thermal_b, equal_nan=True)

        assert thermal_a.shape == image.shape

        with pytest.raises(TypeError):
            # should raise typeError with incorrect type
            flir_extractor.get_thermal(tuple())

        with pytest.raises(FileNotFoundError):
            flir_extractor.get_thermal("not existant file.jpg")

        with pytest.raises(UnsupportedImageError):
            # baboons file is from
            # https://github.com/LJMUAstroecology/flirpy/blob/master/examples/baboons.jpg # noqa: E501
            # and used under an MIT license.
            flir_extractor.get_thermal("./tests/baboons.jpg")

        with pytest.raises(IsADirectoryError):
            flir_extractor.get_thermal(pathlib.Path(__file__).parent)


def test_get_thermal_batch(image: AbsImage):
    with FlirExtractor() as flir_extractor:
        flir_extractor.get_thermal_batch((image.path, str(image.path)))

import pathlib

import pytest

from flirextractor import FlirExtractor

TEST_IMAGE_RELATIVE_PATH = pathlib.Path("./IR_2412.jpg")

TEST_IMAGE_PATH = pathlib.Path(__file__).parent / TEST_IMAGE_RELATIVE_PATH


def test_get_thermal():
    with FlirExtractor() as flir_extractor:
        thermal_a = flir_extractor.get_thermal(TEST_IMAGE_PATH)
        # should work when loading a str variable
        thermal_b = flir_extractor.get_thermal(str(TEST_IMAGE_PATH))
        # loading the same file twice should get the same result
        assert (thermal_a == thermal_b).all()

        with pytest.raises(TypeError):
            # should raise typeError with incorrect type
            flir_extractor.get_thermal(tuple())

        with pytest.raises(FileNotFoundError):
            flir_extractor.get_thermal("not existant file.jpg")

        with pytest.raises(IsADirectoryError):
            flir_extractor.get_thermal(pathlib.Path(__file__).parent)


def test_get_thermal_batch():
    with FlirExtractor() as flir_extractor:
        flir_extractor.get_thermal_batch(
            (TEST_IMAGE_PATH, str(TEST_IMAGE_PATH))
        )

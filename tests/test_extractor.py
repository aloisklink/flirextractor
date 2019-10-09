import pathlib

import pytest

from flirextractor import FlirExtractor

TEST_IMAGE_RELATIVE_PATH = pathlib.Path("./IR_2412.jpg")

TEST_IMAGE_PATH = pathlib.Path(__file__).parent / TEST_IMAGE_RELATIVE_PATH

def test_get_thermal():
    with FlirExtractor() as flir_extractor:
        flir_extractor.get_thermal(TEST_IMAGE_PATH)

# flirextractor

<p align="center">
<a href="https://pypi.org/project/flirextractor/"><img alt="PyPI" src="https://img.shields.io/pypi/v/flirextractor"></a>
<a href="https://pypi.org/project/flirextractor/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/flirextractor"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/aloisklink/flirextractor/blob/master/LICENSE.md"><img alt="GitHub: License" src="https://img.shields.io/github/license/aloisklink/flirextractor"></a>
</p>

An efficient GPLv3 Python package for extracting temperature data from FLIR IRT images.

## Differences from existing libraries

There is an existing Python package for extracting temperature
values from raw IRT images, see
[nationaldronesau/FlirImageExtractor](https://github.com/nationaldronesau/FlirImageExtractor).
However, it has some issues that I didn't like:

  - Most importantly, it is forked from the UNLICENSED
    [Nervengift/read_thermal.py](https://github.com/Nervengift/read_thermal.py),
    so until
    [Nervengift/read_thermal.py#4](https://github.com/Nervengift/read_thermal.py/issues/4)
    is answered, this package cannot be legally used.
  - Secondly, it is quite inefficient, as it runs a new exiftool process
    for each image, and it converts the temperature for each pixel, instead
    of using numpy's vectorized math.

## Installing

You can install flirextractor from pip.

```bash
pip3 install flirextractor
```

Make sure you install exiftool as well.

On RHEL, this can be installed via:

```bash
sudo yum install perl-Image-ExifTool
```

On Debian, this can be installed via:

```bash
sudo apt update && sudo apt install libimage-exiftool-perl -y
```

## Usage

Data is loaded in Celsius as 2-dimensional
[`numpy.ndarray`s](https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html).

To load data from a single FLIR file, run:

```python3
from flirextractor import FlirExtractor
with FlirExtractor() as extractor:
    thermal_data = extractor.get_thermal("path/to/FLIRimage.jpg")
```

Data can also be loaded from multiple FLIR files at once in batch mode,
which is slightly more efficient:

```python3
from flirextractor import FlirExtractor
with FlirExtractor() as extractor:
    list_of_thermal_data = extractor.get_thermal_batch(
        ["path/to/FLIRimage.jpg", "path/to/another/FLIRimage.jpg"])
```

## Testing

Use the Python package manager `poetry` to install test dependencies:

```bash
poetry install
```

Then run pytest to run tests.

```bash
poetry run pytest
```

Run mypy to run type tests:

```bash
poetry run -- mypy -p flirextractor
```

Run isort to sort imports:

```bash
poetry run isort **/*.py
```

Run black to auto-format code:

```bash
poetry run black .
```

And run flake8 to test for anything black missed:

```bash
poetry run flake8 tests/ flirextractor/
```

# flirextractor

<p align="center">
<a href="https://pypi.org/project/flirextractor/"><img alt="PyPI" src="https://img.shields.io/pypi/v/flirextractor"></a>
<a href="https://github.com/aloisklink/flirextractor/workflows/Tests/badge.svg"><img alt="GitHub Actions Status" src="https://github.com/aloisklink/flirextractor/workflows/Tests/badge.svg"></a>
<a href="https://pypi.org/project/flirextractor/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/flirextractor"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/aloisklink/flirextractor/blob/master/LICENSE.md"><img alt="GitHub: License" src="https://img.shields.io/github/license/aloisklink/flirextractor"></a>
</p>

An efficient GPLv3-licensed Python package for extracting temperature data from FLIR IRT images.

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

Or, using the python package manger [poetry](https://poetry.eustace.io/)
(recommended):

```bash
poetry add flirextractor
```

**Make sure you install exiftool as well.**

On RHEL, this can be installed via:

```bash
sudo yum install perl-Image-ExifTool
```

On Debian, this can be installed via:

```bash
sudo apt update && sudo apt install libimage-exiftool-perl -y
```

## Usage

Each FLIR infrared image is loaded in Celsius as a 2-dimensional
[`numpy.ndarray`](https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html).

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

Once you have the `numpy.ndarray`, you can export the data as a csv with:

```python3
import numpy as np
np.savetxt("output.csv", thermal_data, delimiter=",")
```

You can display the image for debugging by doing:

```python3
from PIL import Image
thermal_image = Image.fromarray(thermal_data)
thermal_image.show()
```

See [./scripts/example.py](./scripts/example.py) for more example usage.

## Testing

Use the Python package manager `poetry` to install test dependencies:

```bash
poetry install
```

Then run pytest to run tests.

```bash
poetry run pytest
```

You can run linters with pre-commit:

```bash
poetry run pre-commit run --all-files
```

## Acknowledgements

This work was supported by the
Engineering and Physical Sciences Research Council
[Doctoral Training Partnership Grant EP/R513325/1].

Additionally, many thanks to Glenn J. Tattersall, for their
[gtatters/Thermimage](https://github.com/gtatters/Thermimage) R package.
This work uses an image and adapts part of
[gtatters/Thermimage](https://github.com/gtatters/Thermimage)
under the GPLv3.0 License.

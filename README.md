# flirextractor

A library from extracting temperature values from FLIR IRT Images.

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
    each time, and it does not use numpy's vectorized math.

## Testing

Use the Python package manager `poetry` to install test dependecies:


```bash
poetry install
```

Then run pytest to run tests.

```bash
poetry run pytest
```

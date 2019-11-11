"""Extracts thermal data from FLIR images using ExifTool.

Example:
    from flirextractor import FlirExtractor
    with FlirExtractor() as extractor:
        thermal_data = extractor.get_thermal("path/to/FLIRimage.jpg")

License:
    flirextractor is a free software, licensed under GPL 3.0.
    flirextractor's source code is MIT Licensed, but as adapts
    gtatters/Thermimage GPL 3.0 code, the whole work can only be licensed
    under the GPL 3.0.

    aloisklink/flirextractor has Copyright (C) 2019 Alois Klink

    flirextractor adapts gtatters/Thermimage under the terms of the
    GPL-3.0 License, Copyright (C) 2017 Glenn J Tattersall

    flirextractor uses smarnach/pyexiftool under the terms of the
    BSD 3-clause License:
    Copyright 2012 Sven Marnach
    All rights reserved.
"""

from .__version__ import __version__  # noqa: F401
from .flirextractor import FlirExtractor  # noqa: F401

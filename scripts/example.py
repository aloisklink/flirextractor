"""Example code for using FlirExtractor

To run this, first install exiftool.
Follow your OS's instructions.

Next, install this library. You can either use pip or poetry (recommended).

Finally, run this script, with

```bash
# if you used pip
python3 scripts/example.py
# if you used poetry
poetry run python3 scripts/example.py
```
"""

# load the thermal data
from flirextractor import FlirExtractor
with FlirExtractor() as extractor:
    thermal_data = extractor.get_thermal("tests/IR_2412.jpg")

# save the thermal data as a csv
import numpy as np
np.savetxt("example.csv", thermal_data, delimiter=",")

# open the thermal data as an image
from PIL import Image
from PIL.ImageOps import autocontrast, colorize
thermal_image = Image.fromarray(thermal_data)
thermal_image.show()  # warning, might be quite dark

# use matplotlib to colorize the image
# Make sure you install matplotlib first
import matplotlib.pyplot as plt
plt.matshow(thermal_data)
colorbar = plt.colorbar()
colorbar.set_label("Temperature in Degrees Celcius")
plt.savefig("example.png")

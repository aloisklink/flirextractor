import typing

import numpy as np
import pytest
from flirextractor.raw_temp_to_celcius import (
    raw_temp_to_celcius,
    water_vapor_pressure,
)

temp_to_pressure = {
    0: 0.6113,
    5: 0.8726,
    10: 1.2281,
    15: 1.7056,
    20: 2.3388,
    25: 3.1690,
}
"""Map of Water Vapor Pressure in kPa at a given temp in C.

Data taken from CRC Handbook of Chemistry and Physics, 85th Edition
by David R. Lide

https://books.google.co.uk/books?id=WDll8hA006AC&pg=SA6-PA10&redir_esc=y#v=onepage&q&f=false
"""

PASCALS_IN_MMHG = 133.322_387_415
"""Number of Pascals in a mmHg"""


def kPa_to_mmHg(pressure_in_kPa):
    return pressure_in_kPa * 1000 / PASCALS_IN_MMHG


@pytest.mark.parametrize("temperature,pressure", temp_to_pressure.items())
def test_water_vapor_pressure(temperature, pressure):
    pressure_in_mmHg = kPa_to_mmHg(pressure)
    estimated_pressure_in_mmHg = water_vapor_pressure(temperature)
    tolerance = 0.05
    expected = pytest.approx(pressure_in_mmHg, rel=tolerance)
    assert expected == estimated_pressure_in_mmHg


class RawTempToCelciusInputVars(typing.NamedTuple):
    raw: float
    emissivity: float
    subject_distance: float
    reflected_temp: float
    atmospheric_temp: float
    ir_window_temp: float
    ir_window_transmission: float
    humidity: float
    planck_r1: float
    planck_b: float
    planck_f: float
    planck_0: float
    planck_r2: float
    peak_spectral_sensitivity: float


expected_raw_temp_to_celcius = {
    # data taken from first pixel of IR_2412.jpg
    RawTempToCelciusInputVars(
        raw=18090,
        **{
            "emissivity": 0.949999988079071,
            "subject_distance": 1.0,
            "reflected_temp": 19.9999938964844,
            "atmospheric_temp": 19.9999938964844,
            "ir_window_temp": 19.9999938964844,
            "ir_window_transmission": 1.0,
            "humidity": 0.5,
            "planck_r1": 21106.76953125,
            "planck_b": 1501.0,
            "planck_f": 1.0,
            "planck_0": -7340.0,
            "planck_r2": 0.012545257806778,
            "peak_spectral_sensitivity": 9.58537741505663,
        },
    ): 23.73440586671677
}


@pytest.mark.parametrize(
    "input_vals, expected_output_val", expected_raw_temp_to_celcius.items()
)
def test_raw_temp_to_celcius(input_vals, expected_output_val):

    input_vals = input_vals._replace(raw=np.array([input_vals.raw]))
    out_array = raw_temp_to_celcius(**input_vals._asdict())
    output_val = out_array[0]
    assert pytest.approx(output_val) == expected_output_val

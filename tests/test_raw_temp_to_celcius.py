import pytest
from flirextractor.raw_temp_to_celcius import water_vapor_pressure

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

https://books.google.co.uk/books?id=WDll8hA006AC&pg=SA6-PA10&redir_esc=y#v=onepage&q&f=false"""

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

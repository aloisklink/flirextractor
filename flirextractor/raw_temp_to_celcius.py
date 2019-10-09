"""Converts FLIR raw data into temperature data.

Adapted from Glenn J. Tattersall's Thermimage program in R:
[gtatters/Thermimage](https://github.com/gtatters/Thermimage) under
GPL-3.0.

License:
    Modifications have Copyright (C) 2019 Alois Klink

    Original work Copyright (C) 2017 Glenn J Tattersall

    This program is free software:
    you can redistribute it and/or modify it under the terms of the
    GNU General Public License as published by the Free Software Foundation,
    either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY;
    without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program. If not, see <https://www.gnu.org/licenses/>.
"""


import math

import numpy as np

CELCIUS_KELVIN_DIFF = 273.15
"""Offset between 0 Celcius and 0 Kelvin"""

def water_vapor_pressure(temp: float) -> float:
    """Calculates the saturated vapour pressure for a given temperature.

    Parameters:
        temp: The temperature in Celcius.

    Returns:
        The saturated water vapour pressure in a mystery unit.
    """
    # eh? what is this?
    # shouldn't we be using one of these?
    # https://en.wikipedia.org/wiki/Vapour_pressure_of_water
    return math.exp(math.fsum((
        1.5587,
        0.06939*temp,
        -0.00027816*(temp)**2,
        0.00000068455*(temp)**3,
    )))

def raw_temp_to_celcius(
    raw: np.ndarray,
    emissivity: float = 1,
    subject_distance: float = 1,
    reflected_temp: float = 20,
    atmospheric_temp: float = None,
    ir_window_temp: float = None,
    ir_window_transmission: float = 1,
    humidity: float = 0.5,
    planck_r1: float = 21106.77,
    planck_b: float = 1501,
    planck_f: float = 1,
    planck_0: float = -7340,
    planck_r2: float = 0.012545258,
    *, # kwargs only from now on
    peak_spectral_sensitivity: float = 9.8e-9, # default is 9.8 μm
    atmospheric_trans_a1: float = 6.569e-3,
    atmospheric_trans_a2: float = 12.62e-3,
    atmospheric_trans_b1: float = -2.276e-3,
    atmospheric_trans_b2: float = -6.67e-3,
    atmospheric_trans_x: float = -1.9,
) -> np.ndarray:
    """Loads temperature data from raw FLIR ADC data into Celcius.

    Parameters:
        raw: The raw ADC FLIR data.
        emissivity: ratio between 0 and 1, depends on subject material
        subject_distance: distance from camera to subject in meters
        reflected_temp: temperature reflected by the subject in Celcius
        atmospheric_temp:
          temperature of the atmosphere (default: reflected_temperature)
        ir_window_temp:
          the temperature of the IR window in Celcius
          (default: reflected_temperature)
        ir_window_transmission:
          the ratio of IR transmitted throught the window
        humidity: relative_humidity
        planck_r1: calibration constant
        planck_b: calibration constant
        planck_f: calibration constant
        planck_0: calibration constant
        planck_r2: calibration constant
        peak_spectral_sensitivity: wavelength of highest sensitivity in meters
        atmospheric_trans_a1: constant for calculating humidity
        atmospheric_trans_a2: constant for calculating humidity
        atmospheric_trans_b1: constant for calculating humidity
        atmospheric_trans_b2: constant for calculating humidity
        atmospheric_trans_x: constant for calculating humidity

    Returns:
        A 2D array of the image, with each pixel showing the temperature
        in Celcius.

    References:
        Glenn J. Tattersall. (2017, December 3).
        Thermimage: Thermal Image Analysis.
        doi:
        10.5281/zenodo.1069704 (URL: http://doi.org/10.5281/zenodo.1069704),
        R package, <URL: https://CRAN.R-project.org/package=Thermimage>.
    """
    if atmospheric_temp is None:
        atmospheric_temp = reflected_temp
    if ir_window_temp is None:
        ir_window_temp = reflected_temp
    # Equations to convert to temperature
    # See http://130.15.24.88/exiftool/forum/index.php/topic,4898.60.html
    # Standard equation: temperature<-PB/log(PR1/(PR2*(raw+PO))+PF)-273.15
    # Other source of information:
    # Minkina and Dudzik's Infrared Thermography: Errors and Uncertainties
    
    window_emissivity = 1 - ir_window_transmission
    window_reflection = 0 # anti-reflective coating on window
    water_partial_pressure = humidity * water_vapor_pressure(atmospheric_temp)

    # transmission through atmosphere - equations from
    # Minkina and Dudzik's Infrared Thermography Book
    # Note: for this script,
    # we assume the thermal window is at the mid-point (OD/2)
    # between the source and the camera sensor
    # TODO: use actual thermal window distance
    antenuation_b4_window = math.fsum((
        atmospheric_trans_x * math.exp(
            -math.sqrt(subject_distance/2) * math.fsum((
                atmospheric_trans_a1,
                atmospheric_trans_b1 * math.sqrt(water_partial_pressure),
            ))
        ),
        (1 - atmospheric_trans_x) * math.exp(
            -math.sqrt(subject_distance/2) * math.fsum((
                atmospheric_trans_a2,
                atmospheric_trans_b2 * math.sqrt(water_partial_pressure),
            ))
        ),
    ))
    antenuation_after_window = antenuation_b4_window

    def radiance(temperature: float) -> float:
        kelvin = temperature + CELCIUS_KELVIN_DIFF
        return math.fsum((
            - planck_0,
            - planck_r1 / planck_r2 / (math.exp(planck_b / kelvin) - planck_f),
        ))

    divisor = 1.0
    # attenuated radiance reflecting off the object before the window
    divisor *= emissivity
    reflected_b4_window = (
        (1 - emissivity) / divisor * radiance(reflected_temp))

    # attenuated radiance from the atmosphere (before the window)
    divisor *= antenuation_b4_window
    atmosphere_b4_window = (
        (1 - antenuation_b4_window)/divisor * radiance(atmospheric_temp)
    )
    # attenuated radiance from the window
    divisor *= ir_window_transmission
    radiance_window = window_emissivity/divisor * radiance(ir_window_temp)

    # attenuated reflection from the window
    reflected_after_window = (
        window_reflection/divisor * radiance(reflected_temp)
    )

    # attenuated radiance from the atmosphere (after the window)
    divisor *= antenuation_after_window
    atmosphere_after_window = (
        (1 - antenuation_after_window)/divisor * radiance(atmospheric_temp)
    )

    non_object_radiance = math.fsum((
        reflected_b4_window, atmosphere_b4_window, radiance_window,
        reflected_after_window, atmosphere_after_window))

    raw_object_radiance = raw/divisor - non_object_radiance

    raw_object_temperature_k = planck_b / np.log(np.sum(
            planck_r1/planck_r2/(raw_object_radiance + planck_0),
            planck_f,
        )
    )
    raw_object_temperature_c = raw_object_temperature_k - CELCIUS_KELVIN_DIFF
    return raw_object_temperature_c

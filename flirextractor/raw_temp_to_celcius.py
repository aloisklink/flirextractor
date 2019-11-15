"""Converts FLIR raw data into temperature data.

Adapted from Glenn J. Tattersall's Thermimage program in R:
[gtatters/Thermimage](https://github.com/gtatters/Thermimage) under
GPL-3.0.

License:
    Python port has Copyright (C) 2019 Alois Klink

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

References:
    Glenn J. Tattersall. (2017, December 3).
    Thermimage: Thermal Image Analysis.
    doi:
    10.5281/zenodo.1069704 (URL: http://doi.org/10.5281/zenodo.1069704),
    R package, <URL: https://CRAN.R-project.org/package=Thermimage>.
"""

import math
import typing

import numpy as np  # type: ignore

CELCIUS_KELVIN_DIFF = 273.15
"""Offset between 0 Celcius and 0 Kelvin"""


def water_vapor_pressure(temp: float) -> float:
    """Calculates the saturated vapour pressure for a given temperature.

    Parameters:
        temp: The temperature in Celcius.

    Returns:
        The saturated water vapour pressure in mmHg (milimeters of mercury).
    """
    # seems to pretty inaccurate, switch to Goff-Gratch?
    # shouldn't we be using one of these?
    # https://en.wikipedia.org/wiki/Vapour_pressure_of_water
    return math.exp(
        math.fsum(
            (
                1.5587,
                0.06939 * temp,
                -0.00027816 * (temp ** 2),
                0.00000068455 * (temp ** 3),
            )
        )
    )


class AtmosphericTransConsts(typing.NamedTuple):
    """Used to calculate atmospheric transmission.

    Default values are taken from FLIR image metadata"""

    alpha_1: float = 6.569e-3
    alpha_2: float = 12.62e-3
    beta_1: float = -2.276e-3
    beta_2: float = -6.67e-3
    x: float = 1.9


class CameraPlanckConsts(typing.NamedTuple):
    """Used to calculate radience from a temperature.

    Based of factory calibration and are stored in FLIR image metadata.
    """

    r1: float = 21106.77
    r2: float = 0.012545258
    b: float = 1501
    zero: float = -7340
    f: float = 1


def atmosphere_attenuation(
    relative_humidity: float,
    temperature: float,
    altitude: float,
    distance: float,
    peak_spectral_wavelength: float,
    atmos_consts: AtmosphericTransConsts = AtmosphericTransConsts(),
) -> float:
    """Calculates the transmittance of the IR signal in the atmosphere.

    Parameters:
        relative_humidity: The relative humidity between 0 and 1.
        temperature: The temperature of the atmosphere in Celcius.
        altitude: The altitude in meters above sea level (unused).
        distance: The distance the signal moves in the atmosphere in meters.
        peak_spectral_wavelength:
            The wavelength of the peak spectral power in meters (unused).
        atmos_trans_consts: constants taken from FLIR image metadata.

    Returns:
        The transmittance factor of the atmosphere.

    References:
        Sebastian Dudzik and Waldemar Minkina's
        Infrared Thermography: Errors and Uncertainties
    """
    if not 0 <= relative_humidity <= 1:
        raise ValueError("Relative humidity should be between 0 and 1")

    # TODO: Replace this mystery code with something from
    # http://www.control.isy.liu.se/student/exjobb/xfiles/1909.pdf

    water_saturated_pressure = water_vapor_pressure(temperature)
    water_partial_pressure = relative_humidity * water_saturated_pressure

    def exponential_term(alpha, beta):
        sqrt_water_pressure = math.sqrt(water_partial_pressure)
        return -math.sqrt(distance) * (alpha + beta * sqrt_water_pressure)

    exponential_1 = exponential_term(
        alpha=atmos_consts.alpha_1, beta=atmos_consts.beta_1,
    )
    exponential_2 = exponential_term(
        alpha=atmos_consts.alpha_2, beta=atmos_consts.beta_2,
    )
    part_1 = atmos_consts.x * math.exp(exponential_1)
    part_2 = (1 - atmos_consts.x) * math.exp(exponential_2)
    return part_1 + part_2


def raw_temp_to_celcius(
    raw: np.ndarray,
    emissivity: float = 1,
    subject_distance: float = 1,
    reflected_temp: float = 20,
    atmospheric_temp: float = None,
    ir_window_temp: float = None,
    ir_window_transmission: float = 1,
    humidity: float = 0.5,
    planck: CameraPlanckConsts = CameraPlanckConsts(),
    atmos_consts: AtmosphericTransConsts = AtmosphericTransConsts(),
    *,  # kwargs only from now on
    peak_spectral_sensitivity: float = 9.8,  # default is 9.8 μm
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
        planck: calibration constants
        atmos_trans_consts: atmospheric transmission constants from metadata
        peak_spectral_sensitivity:
            wavelength of highest sensitivity in micrometers

    Returns:
        A 2D array of the image, with each pixel showing the temperature
        in Celcius.
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
    window_reflection = 0  # anti-reflective coating on window

    # Note: for this script,
    # we assume the thermal window is at the mid-point (OD/2)
    # between the source and the camera sensor
    # TODO: use actual thermal window distance
    subject_distance_to_window = subject_distance / 2
    sensor_distance_to_window = subject_distance - subject_distance_to_window

    antenuation_b4_window = atmosphere_attenuation(
        relative_humidity=humidity,
        temperature=atmospheric_temp,
        altitude=0,
        distance=subject_distance_to_window,
        peak_spectral_wavelength=peak_spectral_sensitivity,
    )

    antenuation_after_window = atmosphere_attenuation(
        relative_humidity=humidity,
        temperature=atmospheric_temp,
        altitude=0,
        distance=sensor_distance_to_window,
        peak_spectral_wavelength=peak_spectral_sensitivity,
        atmos_consts=atmos_consts,
    )

    def radiance(temperature: float) -> float:
        kelvin = temperature + CELCIUS_KELVIN_DIFF
        denominator = planck.r2 * (math.exp(planck.b / kelvin) - planck.f)
        return planck.r1 / denominator - planck.zero

    divisor = 1.0
    # attenuated radiance reflecting off the object before the window
    divisor *= emissivity
    reflected_b4_window = (1 - emissivity) / divisor * radiance(reflected_temp)

    # attenuated radiance from the atmosphere (before the window)
    divisor *= antenuation_b4_window
    atmosphere_b4_window = (
        (1 - antenuation_b4_window) / divisor * radiance(atmospheric_temp)
    )
    # attenuated radiance from the window
    divisor *= ir_window_transmission
    radiance_window = window_emissivity / divisor * radiance(ir_window_temp)

    # attenuated reflection from the window
    reflected_after_window = (
        window_reflection / divisor * radiance(reflected_temp)
    )

    # attenuated radiance from the atmosphere (after the window)
    divisor *= antenuation_after_window
    atmosphere_after_window = (
        (1 - antenuation_after_window) / divisor * radiance(atmospheric_temp)
    )

    non_object_radiance = math.fsum(
        (
            reflected_b4_window,
            atmosphere_b4_window,
            radiance_window,
            reflected_after_window,
            atmosphere_after_window,
        )
    )

    raw_obj_radiance = raw / divisor - non_object_radiance

    raw_object_temperature_k = planck.b / np.log(
        planck.r1 / planck.r2 / (raw_obj_radiance + planck.zero) + planck.f
    )
    raw_object_temperature_c = raw_object_temperature_k - CELCIUS_KELVIN_DIFF
    return raw_object_temperature_c

from tudatpy.kernel.astro.fundamentals import compute_shadow_function
import numpy as np


def compute_shadow_vector(satellite_position, sun_position, earth_position, sun_radius, earth_radius):
    satellite_shadow_function = np.empty(len(satellite_position))
    satellite_shadow_function[:] = np.NaN
    for ii in range(len(satellite_position)):
        satellite_shadow_function[ii] = compute_shadow_function(sun_position[ii], sun_radius, earth_position[ii],
                                                                earth_radius, satellite_position[ii])
    return satellite_shadow_function

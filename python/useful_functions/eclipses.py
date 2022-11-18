from tudatpy.kernel.astro.fundamentals import compute_shadow_function
import numpy as np
import pandas as pd
from dataclasses import make_dataclass


def compute_shadow_vector(satellite_position, sun_position, earth_position, sun_radius, earth_radius):
    satellite_shadow_function = np.empty(len(satellite_position))
    satellite_shadow_function[:] = np.NaN
    for ii in range(len(satellite_position)):
        satellite_shadow_function[ii] = compute_shadow_function(sun_position[ii], sun_radius, earth_position[ii],
                                                                earth_radius, satellite_position[ii])
    return satellite_shadow_function


def compute_eclipses(satellite_position, sun_position, sun_radius, earth_position, earth_radius, epochs, fixed_step_size) :

    satellite_shadow_function = compute_shadow_vector(satellite_position, sun_position,
                                                      earth_position, sun_radius, earth_radius)
    all_eclipses = []

    eclipse = make_dataclass("Eclipse",
                             [("start",float),("end",float),("duration",float),
                              ("partial_eclipse",bool)])

    for ii in range(len(epochs)):
        if satellite_shadow_function[ii]:
            if ii == 0:
                partial_eclipse = True
            else :
                partial_eclipse = False
            t_start = epochs[ii]
            duration = 0
            j = 1
            while satellite_shadow_function[ii + j]:
                if ii + j == len(epochs):
                    partial_eclipse = True
                else:
                    partial_eclipse = False

                duration += fixed_step_size
                j += 1
            ii += j
            t_end = epochs[ii + j]
            eclipse_i = pd.DataFrame([eclipse(t_start,t_end,duration,partial_eclipse)])
            all_eclipses.append(eclipse_i)
        else:
            ii+=1
    return all_eclipses


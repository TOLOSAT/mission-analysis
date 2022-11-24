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


def find_next_eclipse(epoch_index, epochs, step_size, shadow_vector, eclipses_df):
    continue_browsing_ = True
    duration_ = None
    eclipse = {}
    while continue_browsing_:
        if shadow_vector[epoch_index]:
            eclipse["start"] = epoch_index
            duration_ = 0
            while shadow_vector[epoch_index]:
                duration_ += step_size
                epoch_index += 1
            eclipse["end"] = epoch_index - 1
            continue_browsing_ = False
        else:
            epoch_index += 1
    if duration_:
        eclipse["duration"] = duration_
    if epoch_index == (len(epochs) - 1):
        continue_browsing_ = False
    else:
        continue_browsing_ = True
    if eclipse:
        eclipses_df.append(eclipse)
    return epoch_index, continue_browsing_


def compute_eclipses(satellite_position, sun_position, sun_radius, earth_position, earth_radius, epochs,
                     step_size):
    shadow_vector = compute_shadow_vector(satellite_position, sun_position,
                                          earth_position, sun_radius, earth_radius)

    eclipses_df = pd.DataFrame(columns=["start", "end", "duration", "partial_eclipse"])

    eclipse = make_dataclass("Eclipse",
                             [("start", float), ("end", float), ("duration", float),
                              ("partial_eclipse", bool)])

    browsing_epochs = True
    epoch_index = 0
    while browsing_epochs == True:
        eclipse = {}
        if epoch_index == 0 and shadow_vector[epoch_index]:
            eclipse["partial_eclipse"] = True
        else:
            eclipse["partial_eclipse"] = False
        start, end, duration, next_epoch, continue_browsing = find_next_eclipse(epoch_index, shadow_vector)

        if satellite_shadow_function[epoch]:

            if epoch == 0:

            else:
                eclipse["partial_eclipse"] = False
            eclipse["start"] = epochs[epoch]
            duration = 0
            j = 0
            while satellite_shadow_function[epoch + j]:
                if epoch + j == len(epochs):
                    eclipse["partial_eclipse"] = True
                else:
                    eclipse["partial_eclipse"] = False
                duration += fixed_step_size
                j += 1
            epoch += j
            t_end = epochs[epoch + j]
            eclipse_i = pd.DataFrame([eclipse(t_start, t_end, duration, partial_eclipse)])
            all_eclipses.append(eclipse_i)
        else:
            epoch += 1


return all_eclipses

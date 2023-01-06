from tudatpy.kernel.astro.fundamentals import compute_shadow_function
import numpy as np
import pandas as pd


def compute_shadow_vector(satellite_position, sun_position, earth_position, sun_radius, earth_radius):
    """
    Parameters
    ----------
    satellite_position : ndarray
        Array of satellite positions in ECI frame
    sun_position : ndarray
        Array of sun positions in ECI frame
    earth_position : ndarray
        Array of earth positions in ECI frame
    sun_radius : float
        Sun radius in meters
    earth_radius : float
        Earth radius in meters

    Returns
    -------
    shadow_vector : ndarray
         Returns a vector with the value of the shadow function at each epoch :
         - 0 if the satellite is in umbra
         - 1 if the satellite is fully sunlit
         - a value between 0 and 1 if the satellite is in penumbra
    """
    shadow_vector = np.empty(len(satellite_position))
    shadow_vector[:] = np.NaN
    for ii in range(len(satellite_position)):
        shadow_vector[ii] = compute_shadow_function(sun_position[ii], sun_radius, earth_position[ii],
                                                    earth_radius, satellite_position[ii])
    return shadow_vector


def compute_eclipses(satellite_position, sun_position, sun_radius, earth_position, earth_radius, epochs,
                     eclipse_type="Umbra"):
    shadow_vector = compute_shadow_vector(satellite_position, sun_position,
                                          earth_position, sun_radius, earth_radius)

    shadow_df = pd.DataFrame({"epochs": epochs, "shadow": shadow_vector})
    if eclipse_type == "Umbra":
        shadow_df["bool"] = shadow_df['shadow'] == 0
    elif eclipse_type == "Penumbra":
        shadow_df["bool"] = shadow_df['shadow'] < 1
    else:
        raise ValueError("Type must be Umbra or Penumbra")

    # Code steps from https://joshdevlin.com/blog/calculate-streaks-in-pandas/
    shadow_df['start_bool'] = shadow_df["bool"].ne(shadow_df["bool"].shift(1))
    shadow_df['end_bool'] = shadow_df["bool"].ne(shadow_df["bool"].shift(-1))
    shadow_df['streak_id'] = shadow_df['start_bool'].cumsum()

    shadow_df.loc[shadow_df['start_bool'], 'start'] = shadow_df['epochs']
    shadow_df['start'] = shadow_df['start'].fillna(method="ffill")
    shadow_df = shadow_df[shadow_df['end_bool']]
    shadow_df = shadow_df.rename({
        "epochs": "end",
        "bool": "eclipse"
    }, axis=1)
    shadow_df = shadow_df[["eclipse", "start", "end"]]
    shadow_df = shadow_df[shadow_df['eclipse']].drop("eclipse", axis=1)
    shadow_df['duration'] = shadow_df['end'] - shadow_df['start']
    shadow_df = shadow_df.reset_index(drop=True)

    shadow_df['partial'] = False
    if shadow_df.loc[0, "start"] == epochs[0]:
        shadow_df.loc[0, 'partial'] = True
    if shadow_df.loc[shadow_df.index[-1], "end"] == epochs[-1]:
        shadow_df.loc[shadow_df.index[-1], 'partial'] = True
    return shadow_df

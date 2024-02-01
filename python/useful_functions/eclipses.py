from tudatpy.kernel.astro.fundamentals import compute_shadow_function
import numpy as np
import pandas as pd

from useful_functions.date_transformations import epoch_to_datetime


def compute_shadow_vector(satellite_position, sun_position, sun_radius, earth_radius):
    """
    Compute the shadow vector of the spacecraft at each epoch.
    Parameters
    ----------
    satellite_position : ndarray
        Array of satellite positions in ECI frame
    sun_position : ndarray
        Array of sun positions in ECI frame
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
        shadow_vector[ii] = compute_shadow_function(
            sun_position[ii],
            sun_radius,
            np.zeros(3),
            earth_radius,
            satellite_position[ii],
        )
    return shadow_vector


def compute_eclipses(
    satellite_position: np.ndarray,
    sun_position: np.ndarray,
    sun_radius: float,
    earth_radius: float,
    epochs: np.ndarray,
    eclipse_type="Umbra",
) -> pd.DataFrame:
    """
    Compute the communications of the spacecraft for a given ground station.

    Parameters
    ----------
    satellite_position : ndarray
        Array of satellite positions in ECI frame
    sun_position : ndarray
        Array of sun positions in ECI frame
    sun_radius : float
        Sun radius in meters
    earth_radius : float
        Earth radius in meters
    epochs : np.ndarray
        Array of epochs in seconds since J2000
    eclipse_type : string
        Type of eclipse to compute. Can be Umbra or Penumbra. Optional, default is Umbra.

    Returns
    -------
    shadow_df: pd.DataFrame
        Returns a data frame containing the following information about the eclipses
         - 'start' : start date of the communication window
         - 'end' : end date of the communication window
         - 'start_epoch' : start epoch of the communication window
         - 'end_epoch' : end epoch of the communication window
         - 'duration' : duration of the communication window
         - 'partial' : True if it is a partial communication window, False if not
    """

    shadow_vector = compute_shadow_vector(
        satellite_position, sun_position, sun_radius, earth_radius
    )

    shadow_df = pd.DataFrame({"epochs": epochs, "shadow": shadow_vector})
    if eclipse_type == "Umbra":
        shadow_df["bool"] = shadow_df["shadow"] == 0
    elif eclipse_type == "Penumbra":
        shadow_df["bool"] = shadow_df["shadow"] < 1
    else:
        raise ValueError("Type must be Umbra or Penumbra")

    # Code steps from https://joshdevlin.com/blog/calculate-streaks-in-pandas/
    shadow_df["start_bool"] = shadow_df["bool"].ne(shadow_df["bool"].shift(1))
    shadow_df["end_bool"] = shadow_df["bool"].ne(shadow_df["bool"].shift(-1))
    shadow_df["streak_id"] = shadow_df["start_bool"].cumsum()

    shadow_df.loc[shadow_df["start_bool"], "start"] = shadow_df["epochs"]
    shadow_df["start"] = shadow_df["start"].fillna(method="ffill")
    shadow_df = shadow_df[shadow_df["end_bool"]]
    shadow_df = shadow_df.rename({"epochs": "end", "bool": "eclipse"}, axis=1)
    shadow_df = shadow_df[["eclipse", "start", "end"]]
    shadow_df = shadow_df[shadow_df["eclipse"]].drop("eclipse", axis=1)
    shadow_df["duration"] = shadow_df["end"] - shadow_df["start"]
    shadow_df = shadow_df.reset_index(drop=True)

    shadow_df["partial"] = False
    if shadow_df.shape[0] == 0:
        return shadow_df
    if shadow_df.loc[0, "start"] == epochs[0]:
        shadow_df.loc[0, "partial"] = True
    if shadow_df.loc[shadow_df.index[-1], "end"] == epochs[-1]:
        shadow_df.loc[shadow_df.index[-1], "partial"] = True

    shadow_df.rename({"start": "start_epoch", "end": "end_epoch"}, axis=1, inplace=True)
    print(type(shadow_df["start_epoch"]))
    print(type(shadow_df["end_epoch"]))

    # shadow_df["start"] = epoch_to_datetime(shadow_df["start_epoch"])
    # shadow_df["end"] = epoch_to_datetime(shadow_df["end_epoch"])
    #
    # shadow_df = shadow_df[
    #     ["start", "end", "start_epoch", "end_epoch", "duration", "partial"]
    # ]
    return shadow_df

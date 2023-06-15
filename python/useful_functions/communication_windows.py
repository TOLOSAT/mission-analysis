import numpy as np
import pandas as pd
from pyproj import Transformer
from useful_functions.get_input_data import get_station
from useful_functions.date_transformations import epoch_to_datetime


def compute_visibility_vector(pos_ecf: np.ndarray, groundstation_name: str) -> pd.DataFrame:
    """
    Compute the visibility vector of the spacecraft from a given ground station.

    Parameters
    ----------
    pos_ecf : np.ndarray
        Array of satellite positions in ECEF frame
    groundstation_name : string
        Name of a csv file containing the longitude, latitude, altitude, and minimum elevation of the groundstation.

    Returns
    -------
    communication_windows: dataframe
        Returns a data frame containing the following information about the communication windows
         - 'start' : start date of the communication window
         - 'end' : end date of the communication window
         - 'duration' : duration of the communication window
         - 'partial' : True if it is a partial communication window, False if not
    """
    transformer = Transformer.from_crs(
        {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'},
        {"proj": 'geocent', "ellps": 'WGS84', "datum": 'WGS84'},
    )
    station = get_station(groundstation_name)
    station_ecf = transformer.transform(station["longitude"], station["latitude"], station["altitude"], radians=False)
    station_sat_vector = pos_ecf - station_ecf
    station_ecf_unit = station_ecf / np.linalg.norm(station_ecf)
    station_sat_vector_unit = station_sat_vector.T / np.apply_along_axis(np.linalg.norm, 1, station_sat_vector)
    dot_product = np.dot(station_ecf_unit, station_sat_vector_unit)
    elevation = 90 - np.arccos(dot_product) * 180 / np.pi

    visibility_vector = elevation >= station["minimum_elevation"]
    return visibility_vector


def compute_communication_windows(pos_ecf: np.ndarray, groundstation_name: str, epochs: np.ndarray) -> pd.DataFrame:
    """
    Compute the communications of the spacecraft for a given ground station.

    Parameters
    ----------
    pos_ecf : np.ndarray
        Array of satellite positions in ECEF frame
    groundstation_name : string
        Name of a csv file containing the longitude, latitude, altitude, and minimum elevation of the groundstation.
    epochs : np.ndarray
        Array of epochs in seconds since J2000

    Returns
    -------
    communication_windows: dataframe
        Returns a data frame containing the following information about the communication windows
         - 'start' : start date of the communication window
         - 'end' : end date of the communication window
         - 'duration' : duration of the communication window
         - 'partial' : True if it is a partial communication window, False if not
    """
    time = epoch_to_datetime(epochs)
    visibility_vector = compute_visibility_vector(pos_ecf, groundstation_name)
    visibility_df = pd.DataFrame({"time": time, "visibility": visibility_vector})

    # Define the start and end of a communication window
    visibility_df['start_of_streak'] = visibility_df.visibility.ne(visibility_df['visibility'].shift(1))
    visibility_df['end_of_streak'] = visibility_df.visibility.ne(visibility_df['visibility'].shift(-1))

    # vis = []
    # t=[]
    # start=[]
    # end=[]
    #
    # for i in range(len(visibility_vector)):
    #     if visibility_vector[i]:
    #         vis.append(visibility_vector[i])
    #         t.append(time[i])
    #         start.append(visibility_df['start_of_streak'][i])
    #         end.append(visibility_df['end_of_streak'][i])
    # visibility_df = pd.DataFrame({"time": t, "visibility": vis, "start_streak": start, "end_streak": end})
    visibility_df.loc[visibility_df['start_of_streak'], 'start'] = visibility_df['time']
    visibility_df['start'] = visibility_df['start'].fillna(method="ffill")
    visibility_df = visibility_df[visibility_df['end_of_streak']]
    visibility_df = visibility_df.rename({
        "time": "end",
    }, axis=1)
    visibility_df = visibility_df[["start", "end"]]
    visibility_df['duration'] = visibility_df['end'] - visibility_df['start']
    visibility_df = visibility_df.reset_index(drop=True)

    visibility_df['partial'] = False
    if visibility_df.loc[0, "start"] == time[0]:
        visibility_df.loc[0, 'partial'] = True
    if visibility_df.loc[visibility_df.index[-1], "end"] == time[-1]:
        visibility_df.loc[visibility_df.index[-1], 'partial'] = True

    return visibility_df

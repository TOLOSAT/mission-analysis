from datetime import timedelta, datetime
from typing import Dict

import numpy as np
import pandas as pd
from pyproj import Transformer
from tudatpy.kernel.astro import time_conversion
from tudatpy.kernel.astro.time_conversion import julian_day_to_calendar_date, seconds_since_epoch_to_julian_day
from useful_functions import get_input_data


def compute_visibility(pos_ecf, groundstation_name, dates_name):
    """
    Compute the visibility of the spacecraft from a given ground station.

    Parameters
    ----------
    pos_ecf : ndarray
        Array of satellite positions in ECEF frame
    groundstation_name : string
        Name of a csv file containing the longitude, latitude, altitude, and minimum elevation of the groundstation.
    dates_name : string
        String of the name of a csv file containing the start date, the end date, and the step size of the simulation

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
    # Set simulation start and end epochs (in seconds since J2000 = January 1, 2000 at 00:00:00)
    dates: dict[str, timedelta | datetime] = get_input_data.get_dates(dates_name)
    dates_new = get_input_data.get_dates(dates_name)  # calendar date
    simulation_start_epoch = time_conversion.julian_day_to_seconds_since_epoch(
        time_conversion.calendar_date_to_julian_day(dates_new["start_date"]))  # seconds since epoch
    simulation_end_epoch = time_conversion.julian_day_to_seconds_since_epoch(
        time_conversion.calendar_date_to_julian_day(dates_new["end_date"]))  # seconds since epoch
    simulation_step_epoch = dates_new["step_size"].seconds  # seconds
    tm = np.arange(simulation_start_epoch, simulation_end_epoch + simulation_step_epoch, simulation_step_epoch)
    time = []
    for i in tm:
        time.append(time_conversion.julian_day_to_calendar_date(
            time_conversion.seconds_since_epoch_to_julian_day(i)))  # calendar date

    station = get_input_data.get_station(groundstation_name)
    station_ecf = transformer.transform(station["longitude"], station["latitude"], station["altitude"], radians=False)
    station_sat_vector = pos_ecf - station_ecf
    station_ecf_unit = station_ecf / np.linalg.norm(station_ecf)
    station_sat_vector_unit = station_sat_vector.T / np.apply_along_axis(np.linalg.norm, 1, station_sat_vector)
    dot_product = np.dot(station_ecf_unit, station_sat_vector_unit)
    elevation = 90 - np.arccos(dot_product) * 180 / np.pi
    visibility = elevation >= station["minimum_elevation"]

    visibility_windows = pd.DataFrame({"time": time, "visibility": visibility})
    visibility_windows['start_of_streak'] = visibility_windows.visibility.ne(visibility_windows['visibility'].shift())  # we define the initial points of a communication window
    visibility_windows['end_of_streak'] = visibility_windows.visibility.ne(visibility_windows['visibility'].shift(-1))  # we define the initial points of a communication window

    vis = []
    t=[]
    start=[]
    end=[]

    for i in range(len(visibility)):
        if visibility[i]:
            vis.append(visibility[i])
            t.append(time[i])
            start.append(visibility_windows['start_of_streak'][i])
            end.append(visibility_windows['end_of_streak'][i])
    communication_windows = pd.DataFrame({"time": t, "visibility": vis, "start_streak": start, "end_streak": end})
    communication_windows.loc[communication_windows['start_streak'], 'start'] = communication_windows['time']
    communication_windows['start'] = communication_windows['start'].fillna(method="ffill")
    communication_windows = communication_windows[communication_windows['end_streak']]
    communication_windows = communication_windows.rename({
        "time": "end",
    }, axis=1)
    communication_windows = communication_windows[["start", "end"]]
    communication_windows['duration'] = communication_windows['end'] - communication_windows['start']
    communication_windows = communication_windows.reset_index(drop=True)

    communication_windows['partial'] = False
    if communication_windows.loc[0, "start"] == time[0]:
        communication_windows.loc[0, 'partial'] = True
    if communication_windows.loc[communication_windows.index[-1], "end"] == time[-1]:
        communication_windows.loc[communication_windows.index[-1], 'partial'] = True

    return communication_windows

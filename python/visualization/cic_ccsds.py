from useful_functions.date_transformations import epoch_to_astrotime, astrotime_to_epoch
from astropy.time import Time
import pandas as pd
from attitude import nadir_pointing, sun_pointing_rotation

cic_reference_jd = 2400000.5
cic_reference_time = Time(cic_reference_jd, format="jd", scale="tai")


def generate_oem_dataframe(days, seconds, states):
    """
    Generate a dataframe with the OEM format

    Parameters
    ----------
    days : list of int or np.ndarray of shape (n,)
        Days since CIC reference time
    seconds : list of float or np.ndarray of shape (n,)
        Seconds in the day
    states : np.ndarray of shape (n, 6)
        States in the EME2000/J2000 frame in meters and meters per second

    Returns
    -------
    oem_dataframe : pd.DataFrame
        Dataframe with the OEM format
    """
    oem_dataframe = pd.DataFrame(
        columns=["days", "seconds", "x", "y", "z", "vx", "vy", "vz"]
    )
    oem_dataframe["days"] = days
    oem_dataframe["seconds"] = seconds
    oem_dataframe[["x", "y", "z", "vx", "vy", "vz"]] = states / 1e3
    return oem_dataframe


def generate_aem_dataframe(days, seconds, quaternions):
    """
    Generate a dataframe with the AEM format

    Parameters
    ----------
    days : list of int or np.ndarray of shape (n,)
        Days since CIC reference time
    seconds : list of float or np.ndarray of shape (n,)
        Seconds in the day
    quaternions : np.ndarray of shape (n, 4)
        Quaternions representing the attitude of the spacecraft with respect to the EME2000/J2000 frame

    Returns
    -------
    aem_dataframe : pd.DataFrame
        Dataframe with the AEM format
    """
    aem_dataframe = pd.DataFrame(columns=["days", "seconds", "q0", "q1", "q2", "q3"])
    aem_dataframe["days"] = days
    aem_dataframe["seconds"] = seconds
    aem_dataframe[["q0", "q1", "q2", "q3"]] = quaternions
    return aem_dataframe


def epochs_to_CIC_days_secs(epochs):
    """
    Convert epochs in seconds since J2000 to days and seconds since CIC reference time

    Parameters
    ----------
    epochs : list of float or np.ndarray of shape (n,)
        Epochs in seconds since J2000

    Returns
    -------
    days : list of int of length n
        Days since CIC reference time
    seconds : list of float of length n
        Seconds in the day

    """
    astrotimes = epoch_to_astrotime(epochs)
    timedeltas_since_cic = [astrotime - cic_reference_time for astrotime in astrotimes]
    julian_days_since_cic = [timedelta.jd for timedelta in timedeltas_since_cic]
    days = [int(julian_day) for julian_day in julian_days_since_cic]
    seconds = [
        round((julian_day.jd - int(julian_day.jd)) * 86400, 3)
        for julian_day in timedeltas_since_cic
    ]
    return days, seconds


def CIC_days_secs_to_epochs(days, seconds):
    """
    Convert days and seconds since CIC reference time to epochs in seconds since J2000

    Parameters
    ----------
    days : list of int or np.ndarray of shape (n,)
        Days since CIC reference time
    seconds : list of float or np.ndarray of shape (n,)
        Seconds in the day

    Returns
    -------
    epochs : list of float of length n
        Epochs in seconds since J2000
    """
    julian_days = [day + second / 86400 for day, second in zip(days, seconds)]
    astrotimes = [
        Time(julian_day, format="jd", scale="tai") for julian_day in julian_days
    ]
    epochs = [astrotime_to_epoch(astrotime) for astrotime in astrotimes]
    return epochs


def generate_cic_files(
    epochs,
    satellite_states,
    sun_directions,
    spacecraft_name="TOLOSAT",
    path="",
    mute=False,
):
    """
    Generate CIC files (OEM and AEM) from epochs, satellite states and sun directions

    Parameters
    ----------
    epochs : list of float or np.ndarray of shape (n,)
        Epochs in seconds since J2000
    satellite_states : np.ndarray of shape (n, 6)
        States in the EME2000/J2000 frame in meters and meters per second
    sun_directions : np.ndarray of shape (n, 3)
        Sun directions in the EME2000/J2000 frame from the satellite
    spacecraft_name : str, optional
        Name of the spacecraft, by default "TOLOSAT"
    path : str, optional
        Path to the folder where the files will be saved, by default ""
    mute : bool, optional
        If True, the function will not print anything, by default False
    """
    days, seconds = epochs_to_CIC_days_secs(epochs)
    oem_dataframe = generate_oem_dataframe(days, seconds, satellite_states)
    export_OEM_file(
        oem_dataframe,
        epochs[0],
        epochs[-1],
        path,
        spacecraft_name=spacecraft_name,
        mute=mute,
    )
    if spacecraft_name == "TOLOSAT":
        quaternions = sun_pointing_rotation.compute_attitude_quaternions(
            epochs, sun_directions
        )
    else:
        quaternions = nadir_pointing.compute_attitude_quaternions(
            satellite_states[:, :3]
        )
    aem_dataframe = generate_aem_dataframe(days, seconds, quaternions)
    export_AEM_file(
        aem_dataframe,
        epochs[0],
        epochs[-1],
        path,
        spacecraft_name=spacecraft_name,
        mute=mute,
    )
    if not mute:
        print("Successfully generated CIC files")


def get_OEM_header(start, end, spacecraft_name="TOLOSAT"):
    """
    Generate the header of an OEM file

    Parameters
    ----------
    start : astropy.time.Time
        Start time of the data
    end : astropy.time.Time
        End time of the data
    spacecraft_name : str, optional
        Name of the spacecraft, by default "TOLOSAT"

    Returns
    -------
    header : list of str
        Header of the OEM file
    """
    return [
        "CIC_OEM_VERS = 2.0",
        "CREATION_DATE  = " + Time.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "ORIGINATOR     = TOLOSAT",
        "",
        "META_START",
        "",
        "COMMENT days (MJD), sec (UTC), x (km), y (km), z (km), vx (km/s), vy (km/s), vz (km/s)",
        "",
        "OBJECT_NAME = " + spacecraft_name,
        "OBJECT_ID = " + spacecraft_name,
        "",
        "CENTER_NAME = EARTH",
        "REF_FRAME   = EME2000",
        "TIME_SYSTEM = TAI",
        "START_TIME = " + start.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "STOP_TIME = " + end.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "",
        "META_STOP",
        "",
    ]


def get_AEM_header(start, end, spacecraft_name="TOLOSAT"):
    """
    Generate the header of an AEM file

    Parameters
    ----------
    start : astropy.time.Time
        Start time of the data
    end : astropy.time.Time
        End time of the data
    spacecraft_name : str, optional
        Name of the spacecraft, by default "TOLOSAT"

    Returns
    -------
    header : list of str
        Header of the AEM file
    """
    return [
        "CIC_AEM_VERS = 2.0",
        "CREATION_DATE  = " + Time.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "ORIGINATOR     = TOLOSAT",
        "",
        "META_START",
        "",
        "COMMENT days (MJD), sec (UTC), q0: real part, q1, q2, q3",
        "",
        "OBJECT_NAME = " + spacecraft_name,
        "OBJECT_ID = " + spacecraft_name,
        "",
        "REF_FRAME_A = EME2000",
        "REF_FRAME_B = SC_BODY_1",
        "ATTITUDE_DIR = A2B",
        "TIME_SYSTEM = TAI",
        "START_TIME = " + start.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "STOP_TIME = " + end.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "ATTITUDE_TYPE = QUATERNION",
        "QUATERNION_TYPE = LAST",
        "",
        "META_STOP",
        "",
    ]


def export_OEM_file(
    oem_dataframe, start_epoch, end_epoch, path, spacecraft_name="TOLOSAT", mute=False
):
    """
    Export cartesian states of the satellite to an OEM file following the CIC/CCSDS format.

    Parameters
    ----------
    oem_dataframe : pandas.DataFrame
        Columns : day (MJD), elapsed seconds (UTC), x (km), y (km), z (km), vx (km/s), vy (km/s), vz (km/s)
    start_epoch : float
        Start time of the attitude data (in seconds since J2000)
    end_epoch : float
        End time of the attitude data (in seconds since J2000)
    path : str
        Path to the folder where the file will be exported
    spacecraft_name : str, optional
        Name of the spacecraft, by default "TOLOSAT"
    mute : bool, optional
        If True, no print is made, by default False
    """
    start = epoch_to_astrotime(start_epoch)
    end = epoch_to_astrotime(end_epoch)
    with open(f"{path}{spacecraft_name}_POSITION_VELOCITY.TXT", "w") as f:
        f.write("\n".join(get_OEM_header(start, end, spacecraft_name)))
        f.write(
            "\n".join(oem_dataframe.to_string(header=False, index=False).split("\n"))
        )
    if not mute:
        print(f"OEM file exported to {path}{spacecraft_name}_POSITION_VELOCITY.TXT")


def export_AEM_file(
    aem_dataframe,
    start_epoch,
    end_epoch,
    path,
    spacecraft_name="TOLOSAT",
    mute=False,
):
    """
    Export attitude quaternions of the satellite to an AEM file following the CIC/CCSDS format.

    Parameters
    ----------
    aem_dataframe : pandas.DataFrame
        Columns : day (MJD), elapsed seconds (UTC), q0: real part, q1, q2, q3
    start_epoch : float
        Start time of the attitude data (in seconds since J2000)
    end_epoch : float
        End time of the attitude data (in seconds since J2000)
    path : str
    spacecraft_name : str, optional
        Name of the spacecraft, by default "TOLOSAT"
    mute : bool, optional
        If True, no print is made, by default False
    """
    start = epoch_to_astrotime(start_epoch)
    end = epoch_to_astrotime(end_epoch)
    with open(f"{path}{spacecraft_name}_QUATERNION.TXT", "w") as f:
        f.write(
            "\n".join(
                get_AEM_header(
                    start,
                    end,
                    spacecraft_name=spacecraft_name,
                )
            )
        )
        f.write(
            "\n".join(
                aem_dataframe.to_string(
                    header=False,
                    index=False,
                    formatters={
                        "q0": lambda x: f"{x:.6f}",
                        "q1": lambda x: f"{x:.6f}",
                        "q2": lambda x: f"{x:.6f}",
                        "q3": lambda x: f"{x:.6f}",
                    },
                ).split("\n")
            )
        )
    if not mute:
        print(f"AEM file exported to {path}{spacecraft_name}_QUATERNION.TXT")

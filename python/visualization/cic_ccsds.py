from useful_functions.date_transformations import epoch_to_astrotime
from astropy.time import Time

cic_reference_jd = 2400000.5
cic_reference_time = Time(cic_reference_jd, format="jd", scale="tai")


def get_CIC_epochs(epochs):
    astrotimes = epoch_to_astrotime(epochs)
    timedeltas_since_cic = [astrotime - cic_reference_time for astrotime in astrotimes]
    julian_days_since_cic = [timedelta.jd for timedelta in timedeltas_since_cic]
    days = [int(julian_day) for julian_day in julian_days_since_cic]
    seconds = [
        round((julian_day.jd - int(julian_day.jd)) * 86400, 3)
        for julian_day in timedeltas_since_cic
    ]
    return days, seconds


def get_OEM_header(start, end, spacecraft_name="TOLOSAT"):
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
    oem_dataframe, start_epoch, end_epoch, path, spacecraft_name="TOLOSAT"
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
    """
    start = epoch_to_astrotime(start_epoch)
    end = epoch_to_astrotime(end_epoch)
    with open(f"{path}{spacecraft_name}_POSITION_VELOCITY.TXT", "w") as f:
        f.write("\n".join(get_OEM_header(start, end, spacecraft_name)))
        f.write(
            "\n".join(oem_dataframe.to_string(header=False, index=False).split("\n"))
        )
    print(f"OEM file exported to {path}{spacecraft_name}_POSITION_VELOCITY.TXT")


def export_AEM_file(
    aem_dataframe,
    start_epoch,
    end_epoch,
    path,
    spacecraft_name="TOLOSAT",
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
    print(f"AEM file exported to {path}{spacecraft_name}_QUATERNION.TXT")

from datetime import datetime


def get_OEM_header(start, end, spacecraft_name="TOLOSAT"):
    return [
        "CIC_MEM_VERS = ???",
        "CREATION_DATE  = " + datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
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
        "REF_FRAME   = ICRF",
        "TIME_SYSTEM = UTC",
        "START_TIME = " + start.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
        "STOP_TIME = " + end.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
        "",
        "META_STOP",
        "",
    ]


def get_AEM_header(
        start, end, reference_frame_a, reference_frame_b, spacecraft_name="TOLOSAT"
):
    return [
        "CIC_AEM_VERS = ???",
        "CREATION_DATE  = " + datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
        "ORIGINATOR     = TOLOSAT",
        "",
        "META_START",
        "",
        "COMMENT days (MJD), sec (UTC), q0: real part, q1, q2, q3",
        "",
        "OBJECT_NAME = " + spacecraft_name,
        "OBJECT_ID = " + spacecraft_name,
        "",
        "REF_FRAME_A = " + reference_frame_a,
        "REF_FRAME_B = " + reference_frame_b,
        "ATTITUDE_DIR = A2B",
        "TIME_SYSTEM = UTC",
        "START_TIME = " + start.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
        "STOP_TIME = " + end.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
        "ATTITUDE_TYPE = QUATERNION",
        "QUATERNION_TYPE = FIRST",
        "",
        "META_STOP",
        "",
    ]


def export_OEM_file(oem_dataframe, start, end, path, spacecraft_name="TOLOSAT"):
    """
    Export cartesian states of the satellite to an OEM file following the CIC/CCSDS format.

    Parameters
    ----------
    oem_dataframe : pandas.DataFrame
        Columns : day (MJD), elapsed seconds (UTC), x (km), y (km), z (km), vx (km/s), vy (km/s), vz (km/s)
    start : datetime.datetime
        Start time of the position and velocity data
    end : datetime.datetime
        End time of the position and velocity data
    path : str
        Path to the folder where the file will be exported
    spacecraft_name : str, optional
        Name of the spacecraft, by default "TOLOSAT"
    """
    with open(f"{path}/{spacecraft_name}_POSITION_VELOCITY.TXT", "w") as f:
        f.write("\n".join(get_OEM_header(start, end, spacecraft_name)))
        f.write(
            "\n".join(oem_dataframe.to_string(header=False, index=False, formatters=).split("\n"))
        )
    print(f"OEM file exported to {path}/{spacecraft_name}_POSITION_VELOCITY.TXT")


def export_AEM_file(
        aem_dataframe,
        start,
        end,
        reference_frame_a,
        reference_frame_b,
        path,
        spacecraft_name="TOLOSAT",
):
    """
    Export attitude quaternions of the satellite to an AEM file following the CIC/CCSDS format.

    Parameters
    ----------
    aem_dataframe : pandas.DataFrame
        Columns : day (MJD), elapsed seconds (UTC), q0: real part, q1, q2, q3
    start : datetime.datetime
        Start time of the attitude data
    end : datetime.datetime
        End time of the attitude data
    reference_frame_a : str
        Reference frame A
    reference_frame_b : str
        Reference frame B
    path : str
    spacecraft_name : str, optional
        Name of the spacecraft, by default "TOLOSAT"
    """
    with open(f"{path}/{spacecraft_name}_QUATERNION.TXT", "w") as f:
        f.write(
            "\n".join(
                get_AEM_header(
                    start,
                    end,
                    reference_frame_a,
                    reference_frame_b,
                    spacecraft_name=spacecraft_name,
                )
            )
        )
        f.write(
            "\n".join(aem_dataframe.to_string(header=False, index=False, formatters=).split("\n"))
        )
    print(f"AEM file exported to {path}/{spacecraft_name}_QUATERNION.TXT")

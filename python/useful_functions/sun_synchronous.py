from useful_functions.date_transformations import epoch_to_astrotime
import numpy as np


def get_sso_raan(mean_local_time, epoch):
    """
    Get the right ascension of the ascending node of a sun-synchronous orbit for a given mean local time and epoch.
    Inspired by the "CL_op_locTime" function of the CelestLab toolbox.

    Parameters
    ----------
    mean_local_time : float
        Mean local time of the ascending node of the orbit (in hours)
    epoch : float
        Epoch of the orbit (in seconds since J2000)

    Returns
    -------
    right_ascension : float
        Right ascension of the ascending node of the orbit (in radians)

    """
    astrotime = epoch_to_astrotime(epoch)
    julian_day = [
        np.floor(astrotime.jd),
        astrotime.jd - np.floor(astrotime.jd),
    ]
    sidereal_time = np.mod(
        2 * np.pi * (julian_day[1] + 0.7790572732640 + 0.00273781191135448 * epoch / 86400), 2 * np.pi
    )
    mean_right_ascension = sidereal_time + np.pi - (julian_day[1] - 0.5) * 2 * np.pi
    right_ascension = np.mod(mean_right_ascension + (mean_local_time - 12) * np.pi / 12, 2 * np.pi)
    return right_ascension

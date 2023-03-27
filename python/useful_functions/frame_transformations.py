import numpy as np
from astropy import units as u
from astropy.coordinates import (
    TEME,
    GCRS,
    CartesianDifferential,
    CartesianRepresentation,
)
from pyproj import Transformer

from useful_functions.date_transformations import epoch_to_astrotime


def ecf2lla(pos_ecf):
    """
    Convert ECF coordinates to LLA coordinates.
    """
    transformer = Transformer.from_crs(
        {"proj": "geocent", "ellps": "WGS84", "datum": "WGS84"},
        {"proj": "latlong", "ellps": "WGS84", "datum": "WGS84"},
    )
    out_lla = transformer.transform(
        pos_ecf[:, 0], pos_ecf[:, 1], pos_ecf[:, 2], radians=False
    )
    return np.array(out_lla).T


def teme_to_j2000(state_teme, epoch):
    astrotime = epoch_to_astrotime(epoch)
    teme_p = CartesianRepresentation(state_teme[0:3] * u.m)
    teme_v = CartesianDifferential(state_teme[3:6] * u.m / u.s)
    teme = TEME(teme_p.with_differentials(teme_v), obstime=astrotime)

    gcrs = teme.transform_to(GCRS(obstime=astrotime)).cartesian
    x = gcrs.x.to_value(u.m)
    y = gcrs.y.to_value(u.m)
    z = gcrs.z.to_value(u.m)
    vx = gcrs.differentials["s"].d_x.to_value(u.m/u.s)
    vy = gcrs.differentials["s"].d_y.to_value(u.m/u.s)
    vz = gcrs.differentials["s"].d_z.to_value(u.m/u.s)
    return np.array([x, y, z, vx, vy, vz])

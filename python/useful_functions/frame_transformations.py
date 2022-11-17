import numpy as np
from pyproj import Transformer


def ecf2lla(pos_ecf):
    """
    Convert ECF coordinates to LLA coordinates.
    """
    transformer = Transformer.from_crs(
        {"proj": 'geocent', "ellps": 'WGS84', "datum": 'WGS84'},
        {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'}
    )
    out_lla = transformer.transform(pos_ecf[:, 0], pos_ecf[:, 1], pos_ecf[:, 2], radians=False)
    return np.array(out_lla).T

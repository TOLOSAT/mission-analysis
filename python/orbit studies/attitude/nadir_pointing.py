from scipy.spatial.transform.rotation import Rotation as R
import pandas as pd
import numpy as np


def compute_attitude_quaternions(satellite_positions):
    """
    Compute attitude quaternions for a satellite in a nadir pointing attitude.

    Parameters
    ----------
    satellite_positions : np.ndarray
        Satellite positions in EME2000 frame. Shape (N, 3)

    Returns
    -------
    quaternions_df : pd.DataFrame
        Attitude quaternions. Shape (N, 4)
    """
    satellite_positions = satellite_positions / np.linalg.norm(
        satellite_positions, axis=1, keepdims=True
    )
    nadir_directions = -satellite_positions

    nadir_pointing_rotation_axis = np.cross(np.array([0, 0, 1]), nadir_directions)
    nadir_pointing_rotation_axis = nadir_pointing_rotation_axis / np.linalg.norm(
        nadir_pointing_rotation_axis, axis=1, keepdims=True
    )

    nadir_pointing_rotation_angle = np.arccos(nadir_directions[:, 2])
    nadir_pointing_rotation_vector = (
        nadir_pointing_rotation_axis * nadir_pointing_rotation_angle[:, None]
    )
    nadir_pointing_rotation = R.from_rotvec(nadir_pointing_rotation_vector)

    quaternions = nadir_pointing_rotation.as_quat()
    quaternions_df = pd.DataFrame(quaternions, columns=["QX", "QY", "QZ", "QW"])
    return quaternions_df

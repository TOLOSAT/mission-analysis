from scipy.spatial.transform.rotation import Rotation as R
import pandas as pd
import numpy as np

ANGULAR_VELOCITY = 2  # deg/s

# Longitudinal axis of cubesat is Z axis


def compute_attitude_quaternions(epochs, sun_directions):
    sun_pointing_rotation_axis = np.cross(np.array([0, 0, 1]), sun_directions)
    sun_pointing_rotation_axis = sun_pointing_rotation_axis / np.linalg.norm(
        sun_pointing_rotation_axis, axis=1, keepdims=True
    )

    sun_pointing_rotation_angle = np.arccos(sun_directions[:, 2])
    sun_pointing_rotation_vector = (
        sun_pointing_rotation_axis * sun_pointing_rotation_angle[:, None]
    )
    sun_pointing_rotation = R.from_rotvec(sun_pointing_rotation_vector)

    elapsed_seconds = epochs - epochs[0]
    satellite_axis_rotation_angle = np.deg2rad(ANGULAR_VELOCITY * elapsed_seconds)
    satellite_axis_rotation_vector = (
        sun_directions * satellite_axis_rotation_angle[:, None]
    )
    satellite_axis_rotation = R.from_rotvec(satellite_axis_rotation_vector)

    full_rotation = R.concatenate([sun_pointing_rotation, satellite_axis_rotation])

    quaternions = full_rotation.as_quat()
    quaternions_df = pd.DataFrame(quaternions, columns=["QX", "QY", "QZ", "QW"])
    return quaternions_df

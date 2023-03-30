from scipy.spatial.transform.rotation import Rotation as R
import pandas as pd
import numpy as np

ANGULAR_VELOCITY = 2  # deg/s


# Longitudinal axis of cubesat is Z axis


def compute_attitude_rotation(epochs, sun_directions):
    """
    Compute the rotation from the EME2000 frame to the TOLOSAT frame at each epoch.

    Parameters
    ----------
    epochs : np.ndarray
        Array of epochs in seconds since J2000
    sun_directions : np.ndarray
        Array of sun directions in EME2000 frame from TOLOSAT

    Returns
    -------
    full_rotation : scipy.spatial.transform.rotation.Rotation
        Rotations from EME2000 to TOLOSAT frame
    """
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
    satellite_axis_rotation_Z_vector = (
        np.array([0, 0, 1]) * satellite_axis_rotation_angle[:, None]
    )
    satellite_axis_rotation_Z = R.from_rotvec(satellite_axis_rotation_Z_vector)

    full_rotation = sun_pointing_rotation * satellite_axis_rotation_Z
    return full_rotation


def compute_attitude_quaternions(epochs, sun_directions):
    """
    Compute the quaternions from the EME2000 frame to the TOLOSAT frame at each epoch.

    Parameters
    ----------
    epochs : np.ndarray
        Array of epochs in seconds since J2000
    sun_directions : np.ndarray
        Array of sun directions in EME2000 frame from TOLOSAT

    Returns
    -------
    quaternions_df : pd.DataFrame
        Quaternions from EME2000 to TOLOSAT frame
    """
    full_rotation = compute_attitude_rotation(epochs, sun_directions)
    quaternions = full_rotation.as_quat()
    quaternions_df = pd.DataFrame(quaternions, columns=["QX", "QY", "QZ", "QW"])
    return quaternions_df


def compute_body_vectors(epochs, sun_directions):
    """
    Compute the body vectors of TOLOSAT in the EME2000 frame at each epoch.

    Parameters
    ----------
    epochs : np.ndarray
        Array of epochs in seconds since J2000
    sun_directions : np.ndarray
        Array of sun directions in EME2000 frame from TOLOSAT

    Returns
    -------
    pX_vector : np.ndarray
        Vector of the X axis of TOLOSAT in EME2000 frame
    pY_vector : np.ndarray
        Vector of the Y axis of TOLOSAT in EME2000 frame
    pZ_vector : np.ndarray
        Vector of the Z axis of TOLOSAT in EME2000 frame
    """
    full_rotation = compute_attitude_rotation(epochs, sun_directions)
    pX_vector = full_rotation.apply(np.array([1, 0, 0]))
    pY_vector = full_rotation.apply(np.array([0, 1, 0]))
    pZ_vector = full_rotation.apply(np.array([0, 0, 1]))
    return pX_vector, pY_vector, pZ_vector

from results_processing import results
import numpy as np

c = 299792458  # m/s

for sat in results:
    if sat == "epochs" or sat == "Tolosat":
        continue
    else:
        dx = (results[sat]["x"] - results["Tolosat"]["x"]).to_numpy()
        dy = (results[sat]["y"] - results["Tolosat"]["y"]).to_numpy()
        dz = (results[sat]["z"] - results["Tolosat"]["z"]).to_numpy()
        results[sat]["dx"] = dx
        results[sat]["dy"] = dy
        results[sat]["dz"] = dz
        dv_x = (results[sat]["vx"] - results["Tolosat"]["vx"]).to_numpy()
        dv_y = (results[sat]["vy"] - results["Tolosat"]["vy"]).to_numpy()
        dv_z = (results[sat]["vz"] - results["Tolosat"]["vz"]).to_numpy()
        results[sat]["dv_x"] = dv_x
        results[sat]["dv_y"] = dv_y
        results[sat]["dv_z"] = dv_z
        dv = np.sqrt(dv_x ** 2 + dv_y ** 2 + dv_z ** 2)
        results[sat]["dv"] = dv
        theta_r = np.arccos(np.sum(np.array([dx, dy, dz])* np.array([dv_x, dv_y, dv_z]), axis=0) / (
                np.linalg.norm([dx, dy, dz]) * np.linalg.norm([dv_x, dv_y, dv_z])))
        results[sat]["theta_r_deg"] = np.deg2rad(theta_r)
        beta = dv / c
        gamma = 1 / np.sqrt(1 - beta ** 2)
        results[sat]["doppler"] = 1 / (gamma * (1 + beta * np.cos(theta_r)))

import numpy as np
import matplotlib.pyplot as plt
# import os

# ====================================
# INITIAL ORBIT DEFINITION
# ====================================

# Starting epochs
years = np.arange(2024, 2037)  # years from 2024 to 2036

# Earth parameters
Re = 6378137.0  # Earth's equatorial radius in meters
mu = 3.986004418e14  # Earth's gravitational parameter (m^3/s^2)
J2 = 1.08263e-3  # Earth's J2 constant
precession_rate_ss_orbit = 1.99096871*(10**7) # Sun-synchronous precession rate (rad/s)
n = np.sqrt(mu / sma ** 3)  # Mean motion (n) calculation (rad/s)

# Initial mean keplerian parameters corresponding to the Polar orbit
print("Initiating mean keplerian parameters")
sma = 6378137.0 + 500e3  # Semi-major axis [m] (Earth's radius + 500 km)
ecc = 2.e-3  # Eccentricity [-]

# Placeholder for CL_op_ssoJ2 function, replace with appropriate function
def CL_op_ssoJ2():
    # Inclination calculation (using radians)
    inclination = np.arccos(-(precession_rate_ss_orbit*2*sma**2*(1-(ecc**2))**2)/(2*n*(Re**2)*J2))
    return np.degrees(inclination)   # Example inclination for sun-synchronous orbit

inc = CL_op_ssoJ2()  # Inclination [rad]
pom = np.pi / 2  # Argument of perigee [rad]
mlh = 6  # MLTAN [hours]

anm = 0  # Mean anomaly [rad]
cjd0 = np.zeros(len(years))
kep_mean_ini = np.zeros((6, len(years)))

# Placeholder for CL_dat_cal2cjd function
def CL_dat_cal2cjd(year, month, day, hour, minute, second):
    # Conversion logic from calendar date to modified Julian day (since 1950.0)
    import datetime
    reference_date = datetime.datetime(1950, 1, 1)
    current_date = datetime.datetime(year, month, day, hour, minute, second) #Attributes: year, month, day, hour, minute, second, microsecond, and tzinfo.
    delta_days = (current_date - reference_date).days + (current_date - reference_date).seconds / 86400.0
    return delta_days #Returns the total difference in days

# Placeholder for CL_op_locTime function
def CL_op_locTime(cjd, mode, param, output_type):
    # Conversion logic based on the provided relationships
    # This is a placeholder implementation. Actual implementation may vary.
    pi = np.pi
    sidt = (2 * pi * (cjd % 1))  # Simplified sidereal time
    if output_type == "ra":
        ra = input_value + sidt
        return ra

for ii in range(len(years)):
    cjd0[ii] = CL_dat_cal2cjd(years[ii], 1, 2, 12, 0, 0)  # Julian date initial time [Julian days]
    gom = CL_op_locTime(cjd0[ii], "mlh", mlh, "ra")  # RAAN [rad]
    kep_mean_ini[:, ii] = [sma, ecc, inc, pom, gom, anm]

# ====================================
# NUMERICAL PROPAGATION WITH STELA
# ====================================

# Force model setup parameters (placeholder values)
params_stela = {
    'mass': 2.66,  # TOLOSAT's mass
    'drag_coef': 2.2,
    'drag_area': 0.025,  # m^2
    'srp_area': 0.025,  # m^2
    'srp_coef': 1.8,
    'zonal_maxDeg': 15,
    'tesseral_maxDeg': 15,
    'drag_solarActivityType': 'variable',
    'solarActivityFile': 'stela_solar_activity.txt'
}

# Placeholder for CL_mu, gravitational constant
CL_mu = 3.986004418e14  # Earth's gravitational parameter [m^3/s^2]

# Propagation step setup
params_stela['integrator_step'] = 2 * np.pi * np.sqrt(sma**3 / CL_mu)  # Exactly one orbit period
step_stela = params_stela['integrator_step'] / 86400  # Propagation step in days
cjd_stela = np.array([cjd0[ii] + np.arange(0, 3000, step_stela) for ii in range(len(years))])

# Placeholder for CL_stela_extrap function
def CL_stela_extrap(mode, cjd_init, kep_init, cjd_prop, params, frame):
    # Placeholder propagation method
    return np.tile(kep_init[:, None], (1, len(cjd_prop))) + np.random.randn(*kep_init[:, None].shape) * 1e-5

# STELA propagation
sma_stela = np.full((len(years), 50000), np.nan)
inc_stela = np.full_like(sma_stela, np.nan)
RAAN_stela = np.full_like(sma_stela, np.nan)
ecc_stela = np.full_like(sma_stela, np.nan)
pom_stela = np.full_like(sma_stela, np.nan)
mltan = np.full_like(sma_stela, np.nan)

for ii in range(len(years)):
    print(f"Beginning STELA propagation {ii+1}/{len(years)}")
    mean_kep_stela = CL_stela_extrap("kep", cjd0[ii], kep_mean_ini[:, ii], cjd_stela[ii, :], params_stela, 'm')
    sma_stela[ii, :mean_kep_stela.shape[1]] = mean_kep_stela[0, :]
    inc_stela[ii, :mean_kep_stela.shape[1]] = mean_kep_stela[2, :]
    RAAN_stela[ii, :mean_kep_stela.shape[1]] = mean_kep_stela[4, :]
    ecc_stela[ii, :mean_kep_stela.shape[1]] = mean_kep_stela[1, :]
    pom_stela[ii, :mean_kep_stela.shape[1]] = mean_kep_stela[3, :]
    mltan[ii, :mean_kep_stela.shape[1]] = CL_op_locTime(cjd_stela[ii, :], "ra", RAAN_stela[ii, :], "mlh")

print("Completed STELA propagation")

# ====================================
# PLOTS OF THE ORBIT EVOLUTION
# ====================================

colors = np.array([[0, 135, 108], [61, 154, 112], [100, 173, 115], [137, 191, 119],
                   [175, 209, 124], [214, 225, 132], [255, 241, 143], [253, 213, 118],
                   [251, 184, 98], [245, 155, 86], [238, 125, 79], [227, 94, 78],
                   [212, 61, 81]]) / 255

legend_strings = years.astype(str)

plt.figure(figsize=(20, 10))

plt.subplot(231)
for ii in range(len(years)):
    plt.plot(cjd_stela[ii, :] - cjd0[ii], sma_stela[ii, :] - 6378137.0, color=colors[ii, :])
plt.title('Altitude decay with STELA propagation')
plt.xlabel('Elapsed days since launch')
plt.ylabel('Altitude (m)')
plt.legend(legend_strings)

plt.subplot(232)
for ii in range(len(years)):
    plt.plot(cjd_stela[ii, :] - cjd0[ii], np.degrees(inc_stela[ii, :]), color=colors[ii, :])
plt.title('Inclination with STELA propagation')
plt.xlabel('Elapsed days since launch')
plt.ylabel('Inclination (deg)')

plt.subplot(233)
for ii in range(len(years)):
    plt.plot(cjd_stela[ii, :] - cjd0[ii], ecc_stela[ii, :], color=colors[ii, :])
plt.title('Eccentricity with STELA propagation')
plt.xlabel('Elapsed days since launch')
plt.ylabel('Eccentricity')

plt.subplot(234)
for ii in range(len(years)):
    plt.plot(cjd_stela[ii, :] - cjd0[ii], np.degrees(pom_stela[ii, :]), color=colors[ii, :])
plt.title('Argument of perigee with STELA propagation')
plt.xlabel('Elapsed days since launch')
plt.ylabel('Argument of perigee (deg)')

plt.subplot(235)
for ii in range(len(years)):
    plt.plot(cjd_stela[ii, :] - cjd0[ii], np.degrees(RAAN_stela[ii, :]), color=colors[ii, :])
plt.title('RAAN TOLOSAT with STELA propagation')
plt.xlabel('Elapsed days since launch')
plt.ylabel('RAAN (deg)')

plt.subplot(236)
for ii in range(len(years)):
    plt.plot(cjd_stela[ii, :] - cjd0[ii], mltan[ii, :], color=colors[ii, :])
plt.title('Evolution of the MLTAN during the TOLOSAT mission')
plt.ylabel('MLTAN [hours]')
plt.xlabel('Elapsed days since launch')

plt.tight_layout()
plt.savefig('launchYear_missionDuration.png')
plt.show()

# Save data to CSV files
np.savetxt('years_py.csv', years, delimiter=',')
np.savetxt('cjd_stela_py.csv', cjd_stela, delimiter=',')
np.savetxt('cjd0_py.csv', cjd0, delimiter=',')
np.savetxt('sma_py.csv', sma_stela, delimiter=',')
np.savetxt('inc_py.csv', inc_stela, delimiter=',')
np.savetxt('ecc_py.csv', ecc_stela, delimiter=',')
np.savetxt('pom_py.csv', pom_stela, delimiter=',')
np.savetxt('RAAN_py.csv', RAAN_stela,


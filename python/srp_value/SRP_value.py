# Import statements
from useful_functions import get_spacecraft

spacecraft_name = "Tolosat"
radiation_pressure_coefficient = get_spacecraft(spacecraft_name)[
    "reflectivity_coefficient"
]

SolarRadiationPressure = (
    1367 / 3e8 * radiation_pressure_coefficient * 1 * (np.cos(0)) ** 2
)
print(
    "Solar Radiation Pressure experienced by the satellite is "
    + str(SolarRadiationPressure)
    + " Pa"
)

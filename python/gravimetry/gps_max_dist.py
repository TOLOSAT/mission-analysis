import math
"""
Check polarization and atmospheric losses parameters for the uplink and downlink
Check worst case scenario and choose the right parameters,
they will probably depend on the altitude and distance between satellites
"""

def calculate_max_distance(EIRP, receiver_sensitivity, GT, system_losses, frequency):
    """
    Calculate the maximum communication distance between a satellite and a ground station.

    Parameters:
    EIRP (float): Effective Isotropic Radiated Power in dB.
    receiver_sensitivity (float): Receiver sensitivity in dBm.
    GT (float): Gain-to-Noise-Temperature ratio in dB/K.
    system_losses (float): System losses in dB.
    frequency (float): Frequency in Hz.

    Returns:
    float: Maximum distance in meters.
    """
    # Calculate the Maximum Allowable Path Loss (MAPL)
    MAPL = EIRP + GT - receiver_sensitivity - system_losses

    # Constants
    c = 3 * 10 ** 8  # Speed of light in meters per second
    four_pi_c = 4 * math.pi / c

    # Calculate log terms
    log_frequency = 20 * math.log10(frequency)
    log_four_pi_c = 20 * math.log10(four_pi_c)

    # Calculate the maximum distance
    log_distance = (MAPL - log_frequency - log_four_pi_c) / 20
    distance = 10 ** log_distance

    return distance


scenario = "typical"   # choose between typical or worst
if scenario == "typical":
    atm_loss = 0.04 # dB
    polarization_losses = 0.8 # dB
    system_losses = atm_loss + polarization_losses

elif scenario == "worst":
    atm_loss = 0.05 # dB
    polarization_losses = 2 # dB
    system_losses = atm_loss + polarization_losses
else:
    print("Scenario not well defined")

# Uplink parameters
frequency_up = 2.0675*10**9 # Hz
EIRP_up = 54 # dBm
receiver_sensitivity_up = -101.9 # dBm
GT_up = 17 # dB/K  # we need to get this parameter for the GS

# Downlink parameters
frequency_down = 2.245*10**9 # Hz
receiver_sensitivity_down = -101.9 # dBm  # we need to get this parameter for the GS
GT_down = 17 # dB/K
# Satellite hardware parameters
if scenario == "typical":
    transmission_power = 3  # dBW
    circuit_losses = 4  # dB
    gain = 3  # dBi
    reflection_coefficient = -17  # dB
elif scenario == "worst":
    transmission_power = 0  # dBW
    circuit_losses = 6  # dB
    gain = -7  # dBi
    reflection_coefficient = -15  # dB
else:
    print("Scenario not well defined")
missmatch_losses = -10 * math.log10(1 - 1 / (10 ** (-reflection_coefficient / 10)))  # dB
EIRP_down = transmission_power - circuit_losses - missmatch_losses + gain  # dBm


# Calculate the maximum distance
max_distance_up = calculate_max_distance(EIRP_up, receiver_sensitivity_up, GT_up, system_losses, frequency_up)
print(f"The maximum uplink communication distance is: {max_distance_up/1000:.2f} km")
max_distance_down = calculate_max_distance(EIRP_down, receiver_sensitivity_down, GT_down, system_losses, frequency_down)
print(f"The maximum downlink communication distance is: {max_distance_down/1000:.2f} km")
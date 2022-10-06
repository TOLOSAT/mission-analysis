import numpy as np
from tudatpy.kernel import numerical_simulation
from tudatpy.kernel.astro import time_conversion
from tudatpy.kernel.interface import spice
from tudatpy.kernel.numerical_simulation import environment_setup, propagation_setup
from tudatpy.util import result2array

from iridium_TLEs import iridium_all_data

# Create new synced Iridium DataFrame
iridium_all_data_synced = iridium_all_data.copy()

# Load spice kernels
spice.load_standard_kernels([])

# Define list of Iridium satellites and the acceleration model to be used
iridium_all_names = iridium_all_data["name"].to_list()
iridium_all_epochs = iridium_all_data["epoch"].to_list()

# Set simulation end epoch (in seconds since J2000 = January 1, 2000 at 00:00:00)
end_date = max(iridium_all_epochs).to_datetime()
simulation_end_epoch = time_conversion.julian_day_to_seconds_since_epoch(
    time_conversion.calendar_date_to_julian_day(end_date))

# Create default body settings and bodies system
bodies_to_create = ["Earth"]
global_frame_origin = "Earth"
global_frame_orientation = "J2000"
body_settings = environment_setup.get_default_body_settings(
    bodies_to_create, global_frame_origin, global_frame_orientation)
acceleration_settings_iridium = dict(
    Earth=[
        propagation_setup.acceleration.spherical_harmonic_gravity(10, 10)
    ]
)
bodies_to_propagate = ["Iridium"]
central_bodies = ["Earth"]
bodies = environment_setup.create_system_of_bodies(body_settings)
bodies.create_empty_body("Iridium")
acceleration_settings = {"Iridium": acceleration_settings_iridium}

# Create acceleration models
acceleration_models = propagation_setup.create_acceleration_models(
    bodies, acceleration_settings, bodies_to_propagate, central_bodies
)

# Create termination settings
termination_condition = propagation_setup.propagator.time_termination(simulation_end_epoch)

print("Starting sync of Iridium satellites...")
# Synchronise all Iridium spacecraft to the maximum epoch
for spacecraft in iridium_all_names:
    print("--------------------------------")
    print("Synchronising " + spacecraft + "...")
    # Set simulation start epoch (in seconds since J2000 = January 1, 2000 at 00:00:00)
    start_date = iridium_all_data[iridium_all_data["name"] == spacecraft]["epoch"].item().to_datetime()
    simulation_start_epoch = time_conversion.julian_day_to_seconds_since_epoch(
        time_conversion.calendar_date_to_julian_day(start_date))

    Delta_t = simulation_end_epoch - simulation_start_epoch

    # Create numerical integrator settings

    if Delta_t == 0:
        print("No need to synchronise " + spacecraft + ".")
        continue
    elif Delta_t < 10:
        step_size = Delta_t
    else:
        step_size = Delta_t / (10 ** np.floor(np.log10(Delta_t)))
    print(f"Start_epoch: {str(start_date)}, End_epoch: {str(end_date)}, Delta_t: {Delta_t}, Step_size: {step_size}")
    integrator_settings = propagation_setup.integrator.runge_kutta_4(
        simulation_start_epoch, step_size
    )

    # Set initial conditions for the satellite
    initial_state = iridium_all_data[iridium_all_data["name"] == spacecraft][
        ["x", "y", "z", "vx", "vy", "vz"]].to_numpy().tolist()[0]

    # Create propagation settings
    propagator_settings = propagation_setup.propagator.translational(
        central_bodies,
        acceleration_models,
        bodies_to_propagate,
        initial_state,
        termination_condition
    )

    # Create simulation object and propagate the dynamics
    dynamics_simulator = numerical_simulation.SingleArcSimulator(
        bodies, integrator_settings, propagator_settings, print_state_data=False
    )

    # Extract the resulting state history and convert it to a ndarray
    states = dynamics_simulator.state_history
    states_array = result2array(states)
    end_date_actual = states_array[-1, 0]
    end_epoch = time_conversion.julian_day_to_calendar_date(
        time_conversion.seconds_since_epoch_to_julian_day(end_date_actual))

    iridium_all_data_synced.loc[iridium_all_data_synced["name"] == spacecraft, ["x", "y", "z", "vx", "vy", "vz"]] = \
        states_array[-1, 1:7]
    iridium_all_data_synced.loc[iridium_all_data_synced["name"] == spacecraft, "epoch"] = end_epoch

    print(f"Done synchronising {spacecraft} to {end_epoch}.")
print("--------------------------------")
print("Done syncing Iridium satellites.")

import pandas as pd
from tudatpy.kernel import numerical_simulation
from tudatpy.kernel.astro import time_conversion
from tudatpy.kernel.interface import spice
from tudatpy.kernel.numerical_simulation import environment_setup, propagation_setup
from tudatpy.util import result2array

from iridium_TLEs import iridium_states, iridium_NEXT_states, iridium_names, iridium_NEXT_names
from useful_functions import get_dates

# Load spice kernels
spice.load_standard_kernels([])

dates_name = "1year"

# Set simulation start and end epochs (in seconds since J2000 = January 1, 2000 at 00:00:00)
dates = get_dates(dates_name)
simulation_start_epoch = time_conversion.julian_day_to_seconds_since_epoch(
    time_conversion.calendar_date_to_julian_day(dates["start_date"]))
simulation_end_epoch = time_conversion.julian_day_to_seconds_since_epoch(
    time_conversion.calendar_date_to_julian_day(dates["end_date"]))

# Create default body settings and bodies system
bodies_to_create = ["Earth"]
global_frame_origin = "Earth"
global_frame_orientation = "J2000"
body_settings = environment_setup.get_default_body_settings(
    bodies_to_create, global_frame_origin, global_frame_orientation)
bodies = environment_setup.create_system_of_bodies(body_settings)

# Define list of Iridium satellites and the acceleration model to be used
iridium_all_names = iridium_names + iridium_NEXT_names
acceleration_settings_iridium = dict(
    Earth=[
        propagation_setup.acceleration.spherical_harmonic_gravity(10, 10)
    ]
)
acceleration_settings = {}

# Create bodies to propagate and define their acceleration settings
for spacecraft in iridium_all_names:
    bodies.create_empty_body(spacecraft)
    acceleration_settings[spacecraft] = acceleration_settings_iridium

# Define bodies that are propagated and their respective central bodies
bodies_to_propagate = iridium_all_names
central_bodies = ["Earth"] * len(iridium_all_names)

# Create acceleration models
acceleration_models = propagation_setup.create_acceleration_models(
    bodies, acceleration_settings, bodies_to_propagate, central_bodies
)

# Set initial conditions for the satellite
initial_state = iridium_states.flatten().tolist() + iridium_NEXT_states.flatten().tolist()

# Create termination settings
termination_condition = propagation_setup.propagator.time_termination(simulation_end_epoch)

# Create propagation settings
propagator_settings = propagation_setup.propagator.translational(
    central_bodies,
    acceleration_models,
    bodies_to_propagate,
    initial_state,
    termination_condition
)

# Create numerical integrator settings
fixed_step_size = dates["step_size"].total_seconds()
integrator_settings = propagation_setup.integrator.runge_kutta_4(
    simulation_start_epoch, fixed_step_size
)

# Create simulation object and propagate the dynamics
dynamics_simulator = numerical_simulation.SingleArcSimulator(
    bodies, integrator_settings, propagator_settings
)

# Extract the resulting state history and convert it to a ndarray
states = dynamics_simulator.state_history
states_array = result2array(states)
states_dataframe = pd.DataFrame(states_array)

# Export results to files
states_dataframe.iloc[:, 0].to_pickle("iridium_states/epochs.pkl")
for sat in enumerate(iridium_all_names):
    states_dataframe.iloc[:, (sat[0] * 6 + 1):(sat[0] * 6 + 7)].to_pickle(f"iridium_states/{sat[1]}.pkl")

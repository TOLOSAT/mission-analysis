from matplotlib import pyplot as plt
from tudatpy.kernel import numerical_simulation
from tudatpy.kernel.astro import time_conversion
from tudatpy.kernel.interface import spice
from tudatpy.kernel.numerical_simulation import environment_setup, propagation_setup
from tudatpy.util import result2array
from iridium_states import *

# Load spice kernels
spice.load_standard_kernels([])

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

# Define list of Irinum satellites and the acceleration model to be used
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
iridium_states = np.concatenate((iridium_r, iridium_v), axis=1)
iridium_NEXT_states = np.concatenate((iridium_NEXT_r, iridium_NEXT_v), axis=1)
initial_state = iridium_states.flatten().tolist() + iridium_NEXT_states.flatten().tolist()

# Setup dependent variables to be save
sun_position_dep_var = propagation_setup.dependent_variable.relative_position("Sun", "Earth")
earth_position_dep_var = propagation_setup.dependent_variable.relative_position("Earth", "Earth")
keplerian_states_dep_var = propagation_setup.dependent_variable.keplerian_state("Spacecraft", "Earth")
ecef_pos_dep_var = propagation_setup.dependent_variable.central_body_fixed_cartesian_position("Spacecraft", "Earth")
dependent_variables_to_save = [sun_position_dep_var, earth_position_dep_var, keplerian_states_dep_var, ecef_pos_dep_var]

# Create termination settings
termination_condition = propagation_setup.propagator.time_termination(simulation_end_epoch)

# Create propagation settings
propagator_settings = propagation_setup.propagator.translational(
    central_bodies,
    acceleration_models,
    bodies_to_propagate,
    initial_state,
    termination_condition,
    output_variables=dependent_variables_to_save
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
dependent_variables_history = dynamics_simulator.dependent_variable_history
dependent_variables_history_array = result2array(dependent_variables_history)

sun_radius = bodies.get("Sun").shape_model.average_radius
earth_radius = bodies.get("Earth").shape_model.average_radius
states_array[:, 0] = states_array[:, 0] - states_array[0, 0]
satellite_position = states_array[:, 1:4]
sun_position = dependent_variables_history_array[:, 1:4]
earth_position = dependent_variables_history_array[:, 4:7]
keplerian_states = dependent_variables_history_array[:, 7:13]
ecef_position = dependent_variables_history_array[:, 13:16]

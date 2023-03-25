# Import statements
from tudatpy.kernel import numerical_simulation
from tudatpy.kernel.astro import element_conversion, time_conversion
from tudatpy.kernel.interface import spice
from tudatpy.kernel.numerical_simulation import environment_setup, propagation_setup
from tudatpy.util import result2array

from useful_functions import *
from visualization.cic_ccsds import (
    epochs_to_CIC_days_secs,
    export_OEM_file,
    export_AEM_file,
)
from attitude.sun_pointing_rotation import compute_attitude_quaternions

# Initial settings (independent of tudat)
orbit_name = "SSO6"
dates_name = "1day"
spacecraft_name = "Tolosat"
groundstation_name = "toulouse"

# Load spice kernels
spice.load_standard_kernels([])

# Set simulation start and end epochs (in seconds since J2000 = January 1, 2000 at 00:00:00)
dates = get_input_data.get_dates(dates_name)
simulation_start_epoch = time_conversion.julian_day_to_seconds_since_epoch(
    time_conversion.calendar_date_to_julian_day(dates["start_date"])
)
simulation_end_epoch = time_conversion.julian_day_to_seconds_since_epoch(
    time_conversion.calendar_date_to_julian_day(dates["end_date"])
)

# Create default body settings and bodies system
bodies_to_create = ["Earth", "Sun", "Moon", "Jupiter"]
global_frame_origin = "Earth"
global_frame_orientation = "J2000"
body_settings = environment_setup.get_default_body_settings(
    bodies_to_create, global_frame_origin, global_frame_orientation
)
bodies = environment_setup.create_system_of_bodies(body_settings)

# Add vehicle object to system of bodies
bodies.create_empty_body("Spacecraft")
bodies.get("Spacecraft").mass = get_input_data.get_spacecraft(spacecraft_name)["mass"]

# Create aerodynamic coefficient interface settings, and add to vehicle
reference_area = get_input_data.get_spacecraft(spacecraft_name)["drag_area"]
drag_coefficient = get_input_data.get_spacecraft(spacecraft_name)["drag_coefficient"]
aero_coefficient_settings = environment_setup.aerodynamic_coefficients.constant(
    reference_area, [drag_coefficient, 0, 0]
)
environment_setup.add_aerodynamic_coefficient_interface(
    bodies, "Spacecraft", aero_coefficient_settings
)

# Create radiation pressure settings, and add to vehicle
reference_area_radiation = get_input_data.get_spacecraft(spacecraft_name)["srp_area"]
radiation_pressure_coefficient = get_input_data.get_spacecraft(spacecraft_name)[
    "reflectivity_coefficient"
]
occulting_bodies = ["Earth"]
radiation_pressure_settings = environment_setup.radiation_pressure.cannonball(
    "Sun", reference_area_radiation, radiation_pressure_coefficient, occulting_bodies
)
environment_setup.add_radiation_pressure_interface(
    bodies, "Spacecraft", radiation_pressure_settings
)

# Define bodies that are propagated and their respective central bodies
bodies_to_propagate = ["Spacecraft"]
central_bodies = ["Earth"]

# Define accelerations acting on the spacecraft
acceleration_settings_spacecraft = dict(
    Sun=[
        propagation_setup.acceleration.cannonball_radiation_pressure(),
        propagation_setup.acceleration.point_mass_gravity(),
    ],
    Earth=[
        propagation_setup.acceleration.spherical_harmonic_gravity(10, 10),
        propagation_setup.acceleration.aerodynamic(),
    ],
    Moon=[propagation_setup.acceleration.point_mass_gravity()],
    Jupiter=[propagation_setup.acceleration.point_mass_gravity()],
)

acceleration_settings = {"Spacecraft": acceleration_settings_spacecraft}

# Create acceleration models
acceleration_models = propagation_setup.create_acceleration_models(
    bodies, acceleration_settings, bodies_to_propagate, central_bodies
)

# Set initial conditions for the satellite
earth_gravitational_parameter = bodies.get("Earth").gravitational_parameter
orbit = get_input_data.get_orbit(orbit_name)
initial_state = element_conversion.keplerian_to_cartesian_elementwise(
    gravitational_parameter=earth_gravitational_parameter,
    semi_major_axis=orbit["semi_major_axis"],
    eccentricity=orbit["eccentricity"],
    inclination=np.deg2rad(orbit["inclination"]),
    argument_of_periapsis=np.deg2rad(orbit["argument_of_periapsis"]),
    longitude_of_ascending_node=np.deg2rad(orbit["longitude_of_ascending_node"]),
    true_anomaly=np.deg2rad(orbit["true_anomaly"]),
)

# Setup dependent variables to be save
sun_direction_dep_var = propagation_setup.dependent_variable.relative_position(
    "Sun", "Spacecraft"
)
dependent_variables_to_save = [sun_direction_dep_var]

# Create termination settings
termination_condition = propagation_setup.propagator.time_termination(
    simulation_end_epoch
)

# Create propagation settings
propagator_settings = propagation_setup.propagator.translational(
    central_bodies,
    acceleration_models,
    bodies_to_propagate,
    initial_state,
    termination_condition,
    output_variables=dependent_variables_to_save,
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
epochs = states_array[:, 0]
satellite_position = states_array[:, 1:4]
sun_direction = dependent_variables_history_array[:, 1:4]
sun_direction = sun_direction / np.linalg.norm(sun_direction, axis=1, keepdims=True)

oem_dataframe = pd.DataFrame(
    columns=["days", "seconds", "x", "y", "z", "vx", "vy", "vz"]
)
days, seconds = epochs_to_CIC_days_secs(epochs)
oem_dataframe["days"] = days
oem_dataframe["seconds"] = seconds
oem_dataframe[["x", "y", "z", "vx", "vy", "vz"]] = states_array[:, 1:7] / 1e3

export_OEM_file(oem_dataframe, simulation_start_epoch, simulation_end_epoch, "")

quaternions = compute_attitude_quaternions(epochs, sun_direction)

aem_dataframe = pd.DataFrame(columns=["days", "seconds", "q0", "q1", "q2", "q3"])
aem_dataframe["days"] = days
aem_dataframe["seconds"] = seconds
aem_dataframe[["q0", "q1", "q2", "q3"]] = quaternions

export_AEM_file(aem_dataframe, simulation_start_epoch, simulation_end_epoch, "")

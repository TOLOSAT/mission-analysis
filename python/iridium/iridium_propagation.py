from tudatpy.kernel import numerical_simulation
from tudatpy.kernel.astro import element_conversion
from tudatpy.kernel.interface import spice
from tudatpy.kernel.numerical_simulation import environment_setup, propagation_setup
from tudatpy.util import result2array

from iridium_TLE_sync import iridium_states_synced, iridium_names
from useful_functions import *

# Load spice kernels
spice.load_standard_kernels([])

# Isolate states
iridium_all_states = iridium_states_synced[["x", "y", "z", "vx", "vy", "vz"]].to_numpy()

# Get input data
dates_name = "3days_1sec_iter"
spacecraft_name = "Tolosat"
orbit_name = "SSO6"

Tolosat = get_spacecraft(spacecraft_name)
Tolosat_orbit = get_orbit(orbit_name)

# Set simulation start and end epochs (in seconds since J2000 = January 1, 2000 at 00:00:00)
dates = get_dates(dates_name)
simulation_start_date = dates["start_date"]
simulation_end_date = dates["end_date"]
propagation_duration = dates["propagation_days"]

# Create default body settings and bodies system
bodies_to_create = ["Earth", "Sun", "Moon", "Jupiter"]
global_frame_origin = "Earth"
global_frame_orientation = "J2000"
body_settings = environment_setup.get_default_body_settings(
    bodies_to_create, global_frame_origin, global_frame_orientation
)
bodies = environment_setup.create_system_of_bodies(body_settings)

# Define list of Iridium satellites and the acceleration model to be used
all_spacecraft_names = ["Tolosat"] + iridium_names

acceleration_settings_iridium = dict(
    Earth=[propagation_setup.acceleration.spherical_harmonic_gravity(2, 0)]
)
acceleration_settings_tolosat = dict(
    Earth=[
        propagation_setup.acceleration.spherical_harmonic_gravity(10, 10),
        propagation_setup.acceleration.aerodynamic(),
    ],
    Sun=[
        propagation_setup.acceleration.point_mass_gravity(),
        propagation_setup.acceleration.cannonball_radiation_pressure(),
    ],
    Moon=[propagation_setup.acceleration.point_mass_gravity()],
    Jupiter=[propagation_setup.acceleration.point_mass_gravity()],
)
acceleration_settings = {"Tolosat": acceleration_settings_tolosat}

# Add vehicle object to system of bodies
bodies.create_empty_body("Tolosat")
bodies.get("Tolosat").mass = Tolosat["mass"]

# Create bodies to propagate and define their acceleration settings
for spacecraft in iridium_names:
    bodies.create_empty_body(spacecraft)
    acceleration_settings[spacecraft] = acceleration_settings_iridium

# Create aerodynamic coefficient interface settings, and add to vehicle
Tolosat_aero_settings = environment_setup.aerodynamic_coefficients.constant(
    Tolosat["drag_area"], [Tolosat["drag_coefficient"], 0, 0]
)
environment_setup.add_aerodynamic_coefficient_interface(
    bodies, "Tolosat", Tolosat_aero_settings
)

# Create radiation pressure settings, and add to vehicle
Tolosat_srp_settings = environment_setup.radiation_pressure.cannonball(
    "Sun", Tolosat["srp_area"], Tolosat["reflectivity_coefficient"], ["Earth"]
)
environment_setup.add_radiation_pressure_interface(
    bodies, "Tolosat", Tolosat_srp_settings
)

# Define bodies that are propagated and their respective central bodies
bodies_to_propagate = all_spacecraft_names
central_bodies = ["Earth"] * len(all_spacecraft_names)

# Create acceleration models
acceleration_models = propagation_setup.create_acceleration_models(
    bodies, acceleration_settings, bodies_to_propagate, central_bodies
)

# Set initial conditions for the satellite
earth_gravitational_parameter = bodies.get("Earth").gravitational_parameter
Tolosat_initial_state = element_conversion.keplerian_to_cartesian_elementwise(
    gravitational_parameter=earth_gravitational_parameter,
    semi_major_axis=Tolosat_orbit["semi_major_axis"],
    eccentricity=Tolosat_orbit["eccentricity"],
    inclination=np.deg2rad(Tolosat_orbit["inclination"]),
    argument_of_periapsis=np.deg2rad(Tolosat_orbit["argument_of_periapsis"]),
    longitude_of_ascending_node=get_sso_raan(
        Tolosat_orbit["mean_local_time"], datetime_to_epoch(simulation_start_date)
    ),
    true_anomaly=np.deg2rad(Tolosat_orbit["true_anomaly"]),
)

initial_state = Tolosat_initial_state.tolist() + iridium_all_states.flatten().tolist()

# Setup dependent variables
sun_direction_dep_var = propagation_setup.dependent_variable.relative_position(
    "Sun", "Tolosat"
)
dependent_variables_to_save = [sun_direction_dep_var]

# Set fixed step size
fixed_step_size = dates["step_size"].total_seconds()

# First iteration
propagation_start_date = simulation_start_date
propagation_end_date = propagation_start_date + propagation_duration

# Propagation loop
for propagation_number in tqdm(
    range(
        int((simulation_end_date - simulation_start_date) / propagation_duration) + 1
    ),
    desc="Propagation",
    ncols=80,
):
    # Convert to epochs
    propagation_start_epoch = datetime_to_epoch(propagation_start_date)
    propagation_end_epoch = datetime_to_epoch(propagation_end_date)

    # Create termination settings
    termination_time = propagation_setup.propagator.time_termination(
        propagation_end_epoch
    )
    termination_altitude = propagation_setup.propagator.dependent_variable_termination(
        dependent_variable_settings=propagation_setup.dependent_variable.altitude(
            "Tolosat", "Earth"
        ),
        limit_value=100.0e3,
        use_as_lower_limit=True,
        terminate_exactly_on_final_condition=False,
    )
    termination_settings = propagation_setup.propagator.hybrid_termination(
        [termination_time, termination_altitude], fulfill_single_condition=True
    )

    # Create propagation settings
    propagator_settings = propagation_setup.propagator.translational(
        central_bodies,
        acceleration_models,
        bodies_to_propagate,
        initial_state,
        termination_settings,
        output_variables=dependent_variables_to_save,
    )

    # Create numerical integrator settings
    integrator_settings = propagation_setup.integrator.runge_kutta_4(
        propagation_start_epoch, fixed_step_size
    )

    # Create simulation object and propagate the dynamics
    dynamics_simulator = numerical_simulation.SingleArcSimulator(
        bodies,
        integrator_settings,
        propagator_settings,
        print_state_data=False,
        print_dependent_variable_data=False,
    )

    # Extract the resulting state history and convert it to a ndarray
    states = dynamics_simulator.state_history
    states_array = result2array(states)
    states_dataframe = pd.DataFrame(states_array)

    dependent_variables_history = dynamics_simulator.dependent_variable_history
    sun_direction = result2array(dependent_variables_history)
    sun_direction = sun_direction / np.linalg.norm(sun_direction, axis=1, keepdims=True)
    sun_direction_dataframe = pd.DataFrame(sun_direction)

    # Export results to files
    makedirs(f"iridium_states/{propagation_number}", exist_ok=True)
    sun_direction_dataframe.iloc[:, 1:4].to_pickle(
        f"iridium_states/{propagation_number}/sun_direction.pkl"
    )
    states_dataframe.iloc[:, 0].to_pickle(
        f"iridium_states/{propagation_number}/epochs.pkl"
    )
    for sat in enumerate(all_spacecraft_names):
        states_dataframe.iloc[:, (sat[0] * 6 + 1) : (sat[0] * 6 + 7)].to_pickle(
            f"iridium_states/{propagation_number}/{sat[1]}.pkl"
        )

    # Update initial state
    initial_state = states_array[-1, 1:]

    # Update propagation dates
    propagation_start_date = propagation_end_date
    propagation_end_date = propagation_start_date + propagation_duration

print("Done with Iridium propagation.")

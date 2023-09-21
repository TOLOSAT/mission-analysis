# Import statements
from tudatpy.kernel import numerical_simulation
from tudatpy.kernel.astro import element_conversion
from tudatpy.kernel.interface import spice
from tudatpy.kernel.numerical_simulation import environment_setup, propagation_setup
from tudatpy.util import result2array

from useful_functions import *
from useful_functions import plot_functions as pf

# Initial settings (independent of tudat)
orbit_name = "SSO6"
dates_name = "10years_10sec_iter"
spacecraft_name = "Tolosat"
groundstation_name = "toulouse"

# Load spice kernels
spice.load_standard_kernels([])

# Set simulation start and end epochs (in seconds since J2000 = January 1, 2000 at 00:00:00)
dates = get_dates(dates_name)
simulation_start_date = dates["start_date"]
simulation_end_date = dates["end_date"]
propagation_duration = dates["propagation_days"]

# Create default body settings and bodies system
bodies_to_create = [
    "Earth",
    "Sun",
    "Moon",
    "Jupiter",
]
global_frame_origin = "Earth"
global_frame_orientation = "J2000"
body_settings = environment_setup.get_default_body_settings(
    bodies_to_create, global_frame_origin, global_frame_orientation
)
bodies = environment_setup.create_system_of_bodies(body_settings)

# Add vehicle object to system of bodies
bodies.create_empty_body("Spacecraft")
bodies.get("Spacecraft").mass = get_spacecraft(spacecraft_name)["mass"]

# Create aerodynamic coefficient interface settings, and add to vehicle
reference_area = get_spacecraft(spacecraft_name)["drag_area"]
drag_coefficient = get_spacecraft(spacecraft_name)["drag_coefficient"]
aero_coefficient_settings = environment_setup.aerodynamic_coefficients.constant(
    reference_area, [drag_coefficient, 0, 0]
)
environment_setup.add_aerodynamic_coefficient_interface(
    bodies, "Spacecraft", aero_coefficient_settings
)

# Create radiation pressure settings, and add to vehicle
reference_area_radiation = get_spacecraft(spacecraft_name)["srp_area"]
radiation_pressure_coefficient = get_spacecraft(spacecraft_name)[
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
)

acceleration_settings = {"Spacecraft": acceleration_settings_spacecraft}

# Create acceleration models
acceleration_models = propagation_setup.create_acceleration_models(
    bodies, acceleration_settings, bodies_to_propagate, central_bodies
)

# Set initial conditions for the satellite
earth_gravitational_parameter = bodies.get("Earth").gravitational_parameter
orbit = get_orbit(orbit_name)
initial_state = element_conversion.keplerian_to_cartesian_elementwise(
    gravitational_parameter=earth_gravitational_parameter,
    semi_major_axis=orbit["semi_major_axis"],
    eccentricity=orbit["eccentricity"],
    inclination=np.deg2rad(orbit["inclination"]),
    argument_of_periapsis=np.deg2rad(orbit["argument_of_periapsis"]),
    longitude_of_ascending_node=get_sso_raan(
        orbit["mean_local_time"], datetime_to_epoch(simulation_start_date)
    ),
    true_anomaly=np.deg2rad(orbit["true_anomaly"]),
)

# Setup dependent variables to be save
sun_position_dep_var = propagation_setup.dependent_variable.relative_position(
    "Sun", "Earth"
)

# Set fixed step size
fixed_step_size = dates["step_size"].total_seconds()

# First iteration
propagation_start_date = simulation_start_date
propagation_end_date = propagation_start_date + propagation_duration

# Initialize eclipses DataFrame
all_eclipses = pd.DataFrame(columns=["start", "end", "duration", "partial"])

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
            "Spacecraft", "Earth"
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
        output_variables=[sun_position_dep_var],
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
    dependent_variables_history = dynamics_simulator.dependent_variable_history
    dependent_variables_history_array = result2array(dependent_variables_history)

    sun_radius = bodies.get("Sun").shape_model.average_radius
    earth_radius = bodies.get("Earth").shape_model.average_radius
    satellite_position = states_array[:, 1:4]
    sun_position = dependent_variables_history_array[:, 1:4]
    epochs = states_array[:, 0]

    # Store the eclipses results
    eclipses = compute_eclipses(
        satellite_position,
        sun_position,
        sun_radius,
        earth_radius,
        epoch_to_datetime(epochs),
        eclipse_type="Umbra",
    )
    if all_eclipses.empty:
        if not eclipses.empty:
            all_eclipses = eclipses
    elif not all_eclipses.empty and not eclipses.empty:
        all_eclipses = pd.concat([all_eclipses, eclipses], ignore_index=True)

    # Update initial conditions
    initial_state = states_array[-1, 1:7]

    # Update propagation dates
    propagation_start_date = propagation_end_date
    propagation_end_date = propagation_start_date + propagation_duration
all_eclipses["partial"] = all_eclipses["partial"].astype("boolean")
print("Done!")

all_eclipses = all_eclipses[~all_eclipses["partial"]]
all_eclipses["start"] = pd.to_datetime(all_eclipses["start"], utc=True)
all_eclipses["timedelta"] = all_eclipses["start"] - simulation_start_date
all_eclipses["seconds"] = all_eclipses["timedelta"].dt.total_seconds()

all_eclipses.to_csv("all_eclipses.csv", index=False)

# To import results and plot again
# all_eclipses = pd.read_csv("all_eclipses.csv", parse_dates=["start", "end"], infer_datetime_format=True)
# all_eclipses['timedelta'] = pd.to_timedelta(all_eclipses['timedelta'])

fig, axes = pf.dark_figure()
axes[0].vlines(
    all_eclipses["seconds"] / 86400 / 365.25,
    0,
    all_eclipses["duration"].dt.total_seconds() / 60,
)
axes[0].set_title("Evolution of the eclipse duration over the entire mission")
axes[0].set_xlabel("Time since launch [years]")
axes[0].set_ylabel("Eclipse duration [mins]")
axes[0].set_ylim(0, all_eclipses["duration"].max().total_seconds() / 60)
axes[0].set_xlim(0, all_eclipses["seconds"].max() / 86400 / 365.25)
pf.finish_dark_figure(fig, "all_eclipses_dark.png", show=True, force_y_int=True)

fig, axes = pf.light_figure()
axes[0].vlines(
    all_eclipses["seconds"] / 86400 / 365.25,
    0,
    all_eclipses["duration"].dt.total_seconds() / 60,
)
axes[0].set_title("Evolution of the eclipse duration over the entire mission")
axes[0].set_xlabel("Time since launch [years]")
axes[0].set_ylabel("Eclipse duration [mins]")
axes[0].set_ylim(0, all_eclipses["duration"].max().total_seconds() / 60)
axes[0].set_xlim(0, all_eclipses["seconds"].max() / 86400 / 365.25)
pf.finish_light_figure(fig, "all_eclipses_light.png", show=True, force_y_int=True)

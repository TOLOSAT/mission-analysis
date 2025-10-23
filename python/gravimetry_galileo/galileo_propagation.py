# ------------------------------------------------------------------------------
# GALILEO + TOLOSAT ORBIT PROPAGATION SCRIPT (SEGMENTED)
# ------------------------------------------------------------------------------
# This script propagates Tolosat and GALILEO satellites using TudatPy in segments
# (~94.4 min/orbit) to improve long-term integration stability.
#
## Initial States:
# - GALILEO satellite states are extracted from TLEs (≤5 days old) via `galileo_TLE_sync.py`
#   and synchronized to a common epoch (`start_datetime`).
# - TOLOSAT is initialized from a Keplerian orbit (e.g., "SSO6").
# - The launch date is set to the same date as TLE extraction for simulation purposes,
#   allowing consistent propagation and visibility analysis.
#
# ------------------------------------------------------------------------------


from tudatpy.kernel import numerical_simulation
from tudatpy.kernel.astro import element_conversion
from tudatpy.kernel.interface import spice
from tudatpy.kernel.numerical_simulation import environment_setup, propagation_setup
from tudatpy.util import result2array

from galileo_TLE_sync import galileo_states_synced, galileo_names, start_datetime
from useful_functions import *

# =============================
# Configuration
# =============================
spacecraft_name = "Tolosat"
orbit_name = "SSO6"
step_size = 10  # seconds
segment_duration_days = 94.4 / 60 / 24  # 1 orbit ~94.4 min
mission_duration_days = 1   # total simulation duration in days

# =============================
# Setup
# =============================
spice.load_standard_kernels([])
Tolosat = get_spacecraft(spacecraft_name)
Tolosat_orbit = get_orbit(orbit_name)
simulation_start_date = start_datetime
simulation_end_date = simulation_start_date + datetime.timedelta(days=mission_duration_days)

# Create bodies
bodies_to_create = ["Earth", "Sun", "Moon", "Jupiter"]
global_frame_origin = "Earth"
global_frame_orientation = "J2000"
body_settings = environment_setup.get_default_body_settings(bodies_to_create, global_frame_origin, global_frame_orientation)
bodies = environment_setup.create_system_of_bodies(body_settings)

# Create spacecraft
bodies.create_empty_body("Tolosat")
bodies.get("Tolosat").mass = Tolosat["mass"]
aero_settings = environment_setup.aerodynamic_coefficients.constant(
    Tolosat["drag_area"], [Tolosat["drag_coefficient"], 0, 0]
)
environment_setup.add_aerodynamic_coefficient_interface(bodies, "Tolosat", aero_settings)
srp_settings = environment_setup.radiation_pressure.cannonball_radiation_target(
    reference_area=Tolosat["srp_area"],
    radiation_pressure_coefficient=Tolosat["reflectivity_coefficient"],
    per_source_occulting_bodies={"Sun": ["Earth"]},
)
environment_setup.add_radiation_pressure_target_model(bodies, "Tolosat", srp_settings)

# Create Galileo satellites
for gal in galileo_names:
    bodies.create_empty_body(gal)

# Acceleration settings
acceleration_settings = {
    "Tolosat": {
        "Sun": [propagation_setup.acceleration.point_mass_gravity(), propagation_setup.acceleration.radiation_pressure()],
        "Earth": [propagation_setup.acceleration.spherical_harmonic_gravity(5, 5), propagation_setup.acceleration.aerodynamic()],
        "Moon": [propagation_setup.acceleration.point_mass_gravity()],
        "Jupiter": [propagation_setup.acceleration.point_mass_gravity()],
    }
}
for gal in galileo_names:
    acceleration_settings[gal] = {"Earth": [propagation_setup.acceleration.spherical_harmonic_gravity(2, 0)]}

all_spacecraft = ["Tolosat"] + galileo_names
bodies_to_propagate = all_spacecraft
central_bodies = ["Earth"] * len(bodies_to_propagate)
acceleration_models = propagation_setup.create_acceleration_models(bodies, acceleration_settings, bodies_to_propagate, central_bodies)

# Initial state
mu_earth = bodies.get("Earth").gravitational_parameter
Tolosat_initial_state = element_conversion.keplerian_to_cartesian_elementwise(
    gravitational_parameter=mu_earth,
    semi_major_axis=Tolosat_orbit["semi_major_axis"],
    eccentricity=Tolosat_orbit["eccentricity"],
    inclination=np.deg2rad(Tolosat_orbit["inclination"]),
    argument_of_periapsis=np.deg2rad(Tolosat_orbit["argument_of_periapsis"]),
    longitude_of_ascending_node=get_sso_raan(Tolosat_orbit["mean_local_time"], datetime_to_epoch(simulation_start_date)),
    true_anomaly=np.deg2rad(Tolosat_orbit["true_anomaly"]),
)
galileo_states = galileo_states_synced[["x", "y", "z", "vx", "vy", "vz"]].to_numpy()
initial_state = np.concatenate(([Tolosat_initial_state], galileo_states)).flatten()

# =============================
# Segmented Propagation
# =============================
segment_td = datetime.timedelta(days=segment_duration_days)
num_segments = int(np.ceil(mission_duration_days / segment_duration_days))
current_start = simulation_start_date

all_results = []
all_sun_directions = []

dependent_variables_to_save = [
    propagation_setup.dependent_variable.relative_position("Sun", "Tolosat")
]

print("Propagating GALILEO + Tolosat in segments...")
for _ in tqdm(range(num_segments), desc="Propagation", ncols=80):
    current_end = min(current_start + segment_td, simulation_end_date)
    start_epoch = datetime_to_epoch(current_start)
    end_epoch = datetime_to_epoch(current_end)

    termination_time = propagation_setup.propagator.time_termination(end_epoch)
    termination_altitude = propagation_setup.propagator.dependent_variable_termination(
        dependent_variable_settings=propagation_setup.dependent_variable.altitude("Tolosat", "Earth"),
        limit_value=100e3,
        use_as_lower_limit=True,
        terminate_exactly_on_final_condition=False,
    )
    termination_settings = propagation_setup.propagator.hybrid_termination(
        [termination_time, termination_altitude], fulfill_single_condition=True
    )

    propagator_settings = propagation_setup.propagator.translational(
        central_bodies,
        acceleration_models,
        bodies_to_propagate,
        initial_state,
        termination_settings,
        output_variables=dependent_variables_to_save,
    )
    integrator_settings = propagation_setup.integrator.runge_kutta_4(start_epoch, step_size)

    simulator = numerical_simulation.SingleArcSimulator(
        bodies, integrator_settings, propagator_settings,
        print_state_data=False, print_dependent_variable_data=False
    )

    segment_result = result2array(simulator.state_history)
    all_results.append(segment_result)

    sun_direction = result2array(simulator.dependent_variable_history)
    sun_direction[:, 1:] /= np.linalg.norm(sun_direction[:, 1:], axis=1, keepdims=True)
    all_sun_directions.append(sun_direction)

    initial_state = segment_result[-1, 1:].flatten()
    current_start = current_end

# =============================
# Save data in ONE folder
# =============================
states_df = pd.DataFrame(np.vstack(all_results))
sun_df = pd.DataFrame(np.vstack(all_sun_directions))

# Create output folder
base_path = "galileo_states"
os.makedirs(base_path, exist_ok=True)
existing = sorted([int(f) for f in os.listdir(base_path) if f.isdigit()])
next_index = existing[-1] + 1 if existing else 0
output_folder = os.path.join(base_path, str(next_index))
os.makedirs(output_folder, exist_ok=True)

# Save data
states_df.iloc[:, 0].to_pickle(f"{output_folder}/epochs.pkl")
sun_df.iloc[:, 1:4].to_pickle(f"{output_folder}/sun_direction.pkl")
for i, sat in enumerate(all_spacecraft):
    states_df.iloc[:, (i * 6 + 1):(i * 6 + 7)].to_pickle(f"{output_folder}/{sat}.pkl")

print(f"Done! Saved segmented propagation in folder: galileo_states/{next_index}")

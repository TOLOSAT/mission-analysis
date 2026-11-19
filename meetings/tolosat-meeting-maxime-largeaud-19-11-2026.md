# Meeting 19/11/2026 

## Done during the meeting

Very productive meeting with Maxime Largeaud. Clarified lots of points regarding flight dynamics/operations and gravimetry.

Maxime LARGEAUD: Works for CS group. Worked on cubesat at USpace, worked on the sentinel system.

# Introduction

Telemetry data is first thing, range and doppler measurements (depends on the provider) gives the speed of the satellite and we put that in an orbit determination program, angular measurements could also be used. Ranging and doppler data as a first introduction.

Station data for when the GNSS chip is turned off. Depending on the satellite, you may want to make sure that you can access other types of data.

Expected injection report by the provider, but not very precise.
VEGA C and Ariane 6 are very precise (within 3 sigma which is around 10 km for the semi major axis).
Take and use new measurement early in the mission

(Batch) Least square, iterative process (depends on the data) but when converging rapidly takes around 2min→ estimated orbit. May converge to a local minimum (see source: Valado). Orekit is based on Valado.

From estimated orbit: flight dynamics product ->orbital propagation: (expected station passes) based on propagated ephemeris (Inertial frame) and orbital events

## Different phases:

- **LEOP:** Launch + 2-3 days (GNSS data from that point), manual operations
- **Commissioning phase:** few days-few months, auto
- **Routine operation:** flight dynamics operations are automated
- **End-of-life:** deorbiting and reentry ->maximum time for reentry/deorbit is ~5x the satellite mission life, capped at 25 years. Manual operations

## To do:

- [ ] Identify station provider (gives the core data to estimate orbits)
- [ ] Identify and contact the launch provider (and make sure there are no exportation problem)
- [ ] Make sure to be CCSDS compliant (sets standards for operations, aligned with providers and orekit generates files in that format)
- [ ] Think about operations automation for orbit determination DO IT EARLY (can we ask SUPAERO for a dedicated server spot (small) ?)
- [ ] Handle end-of-life (tools can switch manual<->automated easily)

## Orekit:

- Java version
- Python wrapper (more convenient, lots of automation processes are python based)

## Flight Dynamics:

- Which tool: Jenkins, Dagstaer, CNC?
- How are we going to store the data? What kind of database? How large? Its format?
  - Recommendation : keep archive of every data we got in the entire lifespan of the satellite for further analysis later on. Archiving data that is 3 month old (or maybe even less) (active data can be used to make up for lack of data during daily operations, and for potential analysis required by other subsystems)
- Choose the Sample Rate: how many position data arrays are we going to get per second?
- How are we getting the data
  - Which station providers
  - How we get the data from them (curl commands, APIs, etc…)
  - How to automate this data gathering process

## Flight Dynamics Process:

1. **Receive Data**(GNSS/GS information)
2. **Flight Dynamics System does : Orbit Determination, Estimated Orbit**
   - Will give us estimated orbit, covariance(uncertainty)
   - Recommend focusing on propagating orbit, propagating other stuff (?)
   - Not a priority. If we have time → maybe look into how to propagate the orbit covariance (Maxime will send Niels papers about it, no consensus on a method, very active research rn in the field) + cf. SSA companies (notes written lower in the page)
3. **Orbital Propagation**(Generate orbital and station events)→ orbital ephemeris from estimation date to 10 days in the future recommended (OEM (CCSDS)), Orbital Events. Best to make OEM calculation less than 15 min.

### Recommendations :

- Implement FDS via FastAPI and Docker
- Identify a few main containers → 1 for database, 1 for FastAPI, 1 for the core functions
- How often should we redo an FDS process (propagation, events calculation) → every 10-15h during routine operations

### If no contact for a few days due to issues with satellite or ground tracking ?

- SpaceTrack→ US radar based tracking system we can use to get informations about orbit (TLE's)  again
- Register the satellite to SpaceTrack

### SSA (Space Situational Awareness) -> Entities that calculate collision probabilities:

(Legally required to send OEM data to them)

- SpaceTrack -> TLE's (Two-line Elements) could take a while
- Aldoria
- Neurospace
- SSA can also provide covariance data


## Control station:

- Station manager
- Flight dynamics system
- Mission center→ payload data (where postprocessing is done)

---

## [Niels]

*I will be at TOLOSAT but maybe jumping all around several teams, so I added these questions to ensure they get asked :*

### The gravimetry team will need to determine external pertubrations :

- **How to determine atmospheric drag (air density at given altitude, friction…) ?**
- **How to determine the influence of other celestial bodies ? Which are the ones to absolutely take into account ?**
- **What are other perturbations we should consider ?**
  - In LEO you want to take into account atmospheric drag, Moon, Sun, solar radiation pressure, tidal forces, J2, J3, 64 parameters?, the Earth radiation pressure (albedo) but maybe a bit too much (might make model not as efficient or usable)
  - For the estimation of drag forces→ estimate drag factor → check on the orekit website
  - For the estimation of gravitational forces → Maxime will check if it's possible to estimate them (possible to implement in the force model, but the estimation is another matter) or maybe ask Niels too (might have ideas)
  - Can estimate solar radiation pressure coefficient with Orekit
  - Might want to check Precise Orbit Determination (OD is broader) which are more precise determination methods → problem with GNSS data is it comes from onboard system, for POD we might want to use RAW GNSS data which is Phase and Carrier which might give more precision (hence the POD)

### What's the order of precision we have to match to ensure good contact with the ground segment's antennas ? 100m, 1km, 10km ?

- Depends on performance of station providers. Using GNSS, precision is around 10m on the estimation date (plenty enough to have precise comm) BUT drift from position
- → Uspace estimated 10km drift over 7 days ~ 1.5s in LEO
- Ground stations should be able to handle that (we can check the CNES GS antenna's BeamWidth/RadiationPattern)

### Are we required to interface with Space Situational Awareness (SAA) providers ? If so, do you know one that's free to work with ?

- SpaceTrack, Aldoria, Neurospace (cf. notes above for more details)

### How regularly do you think our FDS should generate ephemeris ?

- Every 10-15h (cf. notes above)

### Are there any legal blockings that the FDS must pass before launch ?

- On the FDS itself not quite
- The regulations applied are the regulations applied on the whole program (for example "Loi sur les opérations spatiales" and other regulations)
- SpaceTrack (SSA) registering. To send our OEM data to get TLE's and collision probabilities

### In the absence of GNSS, what's the best method to determine our position ? What if the antennas do not provide angular velocities and/or doppler measurements ?

- Recommended checking services offered by the stations we will use
- Possibility of registering the satellite in SpaceTrack
- See notes above for more details

### Can you tell us about what's complicated when trying to implement a FDS for such a "simple" mission ?

- The main thing would be how we understand orbital mechanics : learn and familiarize ourselves with the force models (especially drag with the drag model) and where the forces come from and how they're computed, the inertial frames used (like Earth centric fixed). To be sure to have a good idea of the larger picture. Check out the batch least-squares method in Vallado (to understand what's behind the functions in Orekit, what's under the hood)
- How to automate is hard and takes a lot of trials, and how to prioritise things → sort priorities very early
- Least difficult is the coding

### You are somewhat an expert with Orekit. Can you give us some tips for working with it ? If I remember correctly, the Orekit forum is a great place to get help ?

### If our satellite dies early in its life in orbit, should the FDS still generate ephemeris reports until its reentry or can we shut the whole program down ?

- Opinion of Maxime is to get the most data possible until it's impossible to get them (altho might be impossible if transponder is down, or GNSS chip is broken). The data might be useful to analyse why the satellite failed. Make sure the database is working still because it will be the source of data for those potential analysis.

### Can you name important standards we should respect (e.g : ephemeris report formatting, API requests inputs…)

- CCSDS standard and other standards but they are implemented in Orekit


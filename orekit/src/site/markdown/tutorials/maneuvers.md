<!--- Copyright 2002-2021 CS GROUP
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->

# Maneuvers

The next tutorials detail some elementary usages of the maneuvers.
Both simple impulsive maneuvers and more complex continuous thrust
maneuvers are presented.

## Impulsive maneuvers

Impulsive maneuvers are very simple discrete changes to the velocity
of a spacecraft. They are mainly used in two cases:

  - for station-keeping, as they remain realistic models given the small
    size of the required maneuvers
  - for initialization of optimization or search algorithm that will
    internally use more realistic models for large maneuvers

This tutorial shows how to implement a series of maneuvers to change
progressively the inclination of an orbit.

Let's set up an initial state as:

    final Frame eme2000 = FramesFactory.getEME2000();
    final Orbit initialOrbit =
                    new KeplerianOrbit(8000000.0, 0.01,
                                       FastMath.toRadians(50.0), // ← this is initial inclination
                                       FastMath.toRadians(140.0),
                                       FastMath.toRadians(12.0),
                                       FastMath.toRadians(-60.0), PositionAngle.MEAN,
                                       eme2000,
                                       new AbsoluteDate(new DateComponents(2008, 6, 23),
                                                        new TimeComponents(14, 0, 0),
                                                        TimeScalesFactory.getUTC()),
                                       Constants.EIGEN5C_EARTH_MU);

The maneuver will be defined in spacecraft frame. We need to ensure the Z axis is
aligned with orbital momentum, so we select an attitude aligned with LVLH
Local Orbital frame

    final AttitudeProvider attitudeProvider = new LofOffset(eme2000, LOFType.LVLH);

We want to perform a series of 3 inclination reduction maneuvers. As they modify
only inclination, they must occur at node, but not all nodes are suitable, we want
ascending nodes, with a ΔV along -Z. The maneuvers are triggered when `Action.STOP`
events occur (and are filtered out)

    final NodeDetector ascendingNodeStopper =
                    new NodeDetector(FramesFactory.getEME2000()).
                    withMaxCheck(300.0).
                    withThreshold(1.0e-6).
                    withHandler(new StopOnIncreasing<>());

We allow only maneuvers on the first 3 orbits

    final AbsoluteDate lastAllowedDate =
                    initialOrbit.getDate().shiftedBy(3 * initialOrbit.getKeplerianPeriod());
    final EnablingPredicate<EventDetector> predicate =
                    (state, detector, g) -> state.getDate().isBefore(lastAllowedDate);
    final EventDetector trigger =
                    new EventEnablingPredicateFilter<>(ascendingNodeStopper, predicate);

Create the maneuver, using ascending node detector as a trigger

    final ImpulseManeuver<EventDetector> maneuver =
                    new ImpulseManeuver<>(trigger,
                                          new Vector3D(0.0, 0.0, -122.25), // ← 122.25 m/s along -Z
                                          350.0);

Wrap-up everything in a propagator. Note that ImpulseManeuver is a event detector,
not a force model! This allows it to be used for all propagators, including
analytical ones like the Keplerian propagator used here

    final KeplerianPropagator propagator = new KeplerianPropagator(initialOrbit, attitudeProvider);
    propagator.addEventDetector(maneuver);

Progress monitoring

    propagator.getMultiplexer().add(900.0, (state, isLast) -> {
        final Vector3D pos = state.getPVCoordinates(eme2000).getPosition();
        System.out.format(Locale.US, "%s %s hemisphere inclination = %5.3f%n",
                          state.getDate(),
                          pos.getZ() > 0 ? "Northern" : "Southern",
                          FastMath.toDegrees(state.getOrbit().getI()));
    });

Run simulation

    propagator.propagate(initialOrbit.getDate().shiftedBy(5 * initialOrbit.getKeplerianPeriod()));

The printed result is shown below. We see that inclination remains constant as
we cross descending nodes (i.e. switch from Northern to Southern hemisphere),
and changes as we cross the first three ascending nodes

    2008-06-23T14:00:00.000 Northern hemisphere inclination = 50.000
    2008-06-23T14:15:00.000 Northern hemisphere inclination = 50.000
    2008-06-23T14:30:00.000 Northern hemisphere inclination = 50.000
    2008-06-23T14:45:00.000 Southern hemisphere inclination = 50.000
    2008-06-23T15:00:00.000 Southern hemisphere inclination = 50.000
    2008-06-23T15:15:00.000 Southern hemisphere inclination = 50.000
    2008-06-23T15:30:00.000 Southern hemisphere inclination = 50.000
    2008-06-23T15:45:00.000 Northern hemisphere inclination = 49.000
    2008-06-23T16:00:00.000 Northern hemisphere inclination = 49.000
    2008-06-23T16:15:00.000 Northern hemisphere inclination = 49.000
    2008-06-23T16:30:00.000 Northern hemisphere inclination = 49.000
    2008-06-23T16:45:00.000 Southern hemisphere inclination = 49.000
    2008-06-23T17:00:00.000 Southern hemisphere inclination = 49.000
    2008-06-23T17:15:00.000 Southern hemisphere inclination = 49.000
    2008-06-23T17:30:00.000 Southern hemisphere inclination = 49.000
    2008-06-23T17:45:00.000 Northern hemisphere inclination = 48.001
    2008-06-23T18:00:00.000 Northern hemisphere inclination = 48.001
    2008-06-23T18:15:00.000 Northern hemisphere inclination = 48.001
    2008-06-23T18:30:00.000 Northern hemisphere inclination = 48.001
    2008-06-23T18:45:00.000 Southern hemisphere inclination = 48.001
    2008-06-23T19:00:00.000 Southern hemisphere inclination = 48.001
    2008-06-23T19:15:00.000 Southern hemisphere inclination = 48.001
    2008-06-23T19:30:00.000 Southern hemisphere inclination = 48.001
    2008-06-23T19:45:00.000 Northern hemisphere inclination = 47.001
    2008-06-23T20:00:00.000 Northern hemisphere inclination = 47.001
    2008-06-23T20:15:00.000 Northern hemisphere inclination = 47.001
    2008-06-23T20:30:00.000 Southern hemisphere inclination = 47.001
    2008-06-23T20:45:00.000 Southern hemisphere inclination = 47.001
    2008-06-23T21:00:00.000 Southern hemisphere inclination = 47.001
    2008-06-23T21:15:00.000 Southern hemisphere inclination = 47.001
    2008-06-23T21:30:00.000 Northern hemisphere inclination = 47.001
    2008-06-23T21:45:00.000 Northern hemisphere inclination = 47.001
    2008-06-23T22:00:00.000 Northern hemisphere inclination = 47.001
    2008-06-23T22:15:00.000 Northern hemisphere inclination = 47.001
    2008-06-23T22:30:00.000 Southern hemisphere inclination = 47.001
    2008-06-23T22:45:00.000 Southern hemisphere inclination = 47.001
    2008-06-23T23:00:00.000 Southern hemisphere inclination = 47.001
    2008-06-23T23:15:00.000 Southern hemisphere inclination = 47.001
    2008-06-23T23:30:00.000 Northern hemisphere inclination = 47.001
    2008-06-23T23:45:00.000 Northern hemisphere inclination = 47.001

The complete code for this example can be found in the source tree of the tutorials,
in file `src/main/java/org/orekit/tutorials/maneuvers/ImpulseAtNode.java`.

## Continuous maneuvers

Continuous maneuvers are realistic models that take into account
maneuver duration, attitude change during maneuver and mass depletion.
They can only be used with integration-based propagators.

This tutorial shows how to implement an apogee maneuver, using either
the attitude set up at propagator level itself or overriding it
for only the maneuver acceleration direction computation. We use
only date-based triggers and constant thrust propulsion system, but
it is possible to use different ones. As an example, we could
replace the `BasicConstantThrustPropulsionModel` with `ScaledConstantThrustPropulsionModel`
and to take into account some calibration factors (or estimate these
factors if instead of using this model in a simulation we use it in
an orbit determination and configure these scaling factors as estimated).
We could also replace the date-based triggers by event-based
triggers, which can model multi-burn maneuvers.

Let's set up an initial state with a GTO orbit and a 2500kg spacecraft:

    final Frame eme2000 = FramesFactory.getEME2000();
    final AbsoluteDate date = new AbsoluteDate(new DateComponents(2004, 01, 01),
                                               new TimeComponents(23, 30, 00.000),
                                               TimeScalesFactory.getUTC());
    final Orbit orbit =
                    new KeplerianOrbit(24396159, 0.72831215, FastMath.toRadians(7),
                                       FastMath.toRadians(180), FastMath.toRadians(261),
                                       FastMath.toRadians(0), PositionAngle.TRUE,
                                       eme2000, date,
                                       Constants.EIGEN5C_EARTH_MU);
    final SpacecraftState initialState = new SpacecraftState(orbit, 2500.0);

Prepare propagator, using an adaptive stepsize integrator. The propagator
will use an attitude mode aligned with VNC, i.e. its X axis is always
along orbital velocity

    final OrbitType orbitType = OrbitType.EQUINOCTIAL;
    final double[][] tol = NumericalPropagator.tolerances(1.0, orbit, orbitType);
    final AdaptiveStepsizeIntegrator integrator =
                    new DormandPrince853Integrator(0.001, 1000, tol[0], tol[1]);
    integrator.setInitialStepSize(60);
    final NumericalPropagator propagator = new NumericalPropagator(integrator);
    propagator.setOrbitType(orbitType);
    propagator.setInitialState(initialState);
    propagator.setAttitudeProvider(new LofOffset(eme2000, LOFType.VNC));

At first, we want to compute the maneuver as an inertial one, so we cannot
rely on the attitude mode configured above, we need an attitude overriding
law with the X axis pointing towards a specific direction

    final Vector3D direction = new Vector3D(FastMath.toRadians(-7.4978),
                                            FastMath.toRadians(351));
    final AttitudeProvider attitudeOverride =
                    new InertialProvider(new Rotation(direction, Vector3D.PLUS_I),
                                         eme2000);

Maneuver will start at a known date and stop after a known duration

   final AbsoluteDate firingDate = new AbsoluteDate(new DateComponents(2004, 1, 2),
                                                    new TimeComponents(4, 15, 34.080),
                                                    TimeScalesFactory.getUTC());
   final double duration = 3653.99;
   final ManeuverTriggers triggers = new DateBasedManeuverTriggers(firingDate, duration);

Maneuver has constant thrust

   final double thrust = 420;
   final double isp    = 318;
   final PropulsionModel propulsionModel =
                   new BasicConstantThrustPropulsionModel(thrust, isp,
                                                          Vector3D.PLUS_I,
                                                          "apogee-engine");

Build maneuver and add it to the propagator as a new force model

   propagator.addForceModel(new Maneuver(attitudeOverride, triggers, propulsionModel));

Progress monitoring

    propagator.getMultiplexer().add(120.0, (state, isLast) ->
        System.out.format(Locale.US, "%s a = %12.3f m, e = %11.9f, m = %8.3f kg%n",
                          state.getDate(), state.getA(), state.getE(), state.getMass())
    );

Propagate orbit, including maneuver

    propagator.propagate(fireDate.shiftedBy(-900), fireDate.shiftedBy(duration + 900));


The printed result is shown below. We see that semi-major axis, eccentricity
and inclination are constant before the maneuver, they change continuously
during the maneuver, and become constant again after maneuver

2004-01-02T04:00:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:02:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:04:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:06:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:08:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:10:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:12:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:14:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:16:34.080 a = 24442112.400 m, e = 0.725043403, m = 2491.919 kg
2004-01-02T04:18:34.080 a = 24536037.252 m, e = 0.718404119, m = 2475.758 kg
2004-01-02T04:20:34.080 a = 24632720.409 m, e = 0.711627339, m = 2459.596 kg
2004-01-02T04:22:34.080 a = 24732246.157 m, e = 0.704710905, m = 2443.435 kg
2004-01-02T04:24:34.080 a = 24834702.625 m, e = 0.697652633, m = 2427.273 kg
2004-01-02T04:26:34.080 a = 24940182.000 m, e = 0.690450311, m = 2411.112 kg
2004-01-02T04:28:34.080 a = 25048780.751 m, e = 0.683101699, m = 2394.950 kg
2004-01-02T04:30:34.080 a = 25160599.875 m, e = 0.675604529, m = 2378.788 kg
2004-01-02T04:32:34.080 a = 25275745.160 m, e = 0.667956507, m = 2362.627 kg
2004-01-02T04:34:34.080 a = 25394327.460 m, e = 0.660155308, m = 2346.465 kg
2004-01-02T04:36:34.080 a = 25516463.000 m, e = 0.652198582, m = 2330.304 kg
2004-01-02T04:38:34.080 a = 25642273.694 m, e = 0.644083951, m = 2314.142 kg
2004-01-02T04:40:34.080 a = 25771887.491 m, e = 0.635809009, m = 2297.981 kg
2004-01-02T04:42:34.080 a = 25905438.748 m, e = 0.627371325, m = 2281.819 kg
2004-01-02T04:44:34.080 a = 26043068.626 m, e = 0.618768440, m = 2265.658 kg
2004-01-02T04:46:34.080 a = 26184925.522 m, e = 0.609997872, m = 2249.496 kg
2004-01-02T04:48:34.080 a = 26331165.531 m, e = 0.601057114, m = 2233.335 kg
2004-01-02T04:50:34.080 a = 26481952.946 m, e = 0.591943638, m = 2217.173 kg
2004-01-02T04:52:34.080 a = 26637460.795 m, e = 0.582654892, m = 2201.012 kg
2004-01-02T04:54:34.080 a = 26797871.426 m, e = 0.573188310, m = 2184.850 kg
2004-01-02T04:56:34.080 a = 26963377.135 m, e = 0.563541304, m = 2168.688 kg
2004-01-02T04:58:34.080 a = 27134180.848 m, e = 0.553711279, m = 2152.527 kg
2004-01-02T05:00:34.080 a = 27310496.862 m, e = 0.543695627, m = 2136.365 kg
2004-01-02T05:02:34.080 a = 27492551.643 m, e = 0.533491736, m = 2120.204 kg
2004-01-02T05:04:34.080 a = 27680584.703 m, e = 0.523096997, m = 2104.042 kg
2004-01-02T05:06:34.080 a = 27874849.544 m, e = 0.512508806, m = 2087.881 kg
2004-01-02T05:08:34.080 a = 28075614.691 m, e = 0.501724576, m = 2071.719 kg
2004-01-02T05:10:34.080 a = 28283164.817 m, e = 0.490741747, m = 2055.558 kg
2004-01-02T05:12:34.080 a = 28497801.970 m, e = 0.479557796, m = 2039.396 kg
2004-01-02T05:14:34.080 a = 28719846.917 m, e = 0.468170253, m = 2023.235 kg
2004-01-02T05:16:34.080 a = 28937941.941 m, e = 0.457162297, m = 2007.882 kg
2004-01-02T05:18:34.080 a = 28937941.941 m, e = 0.457162297, m = 2007.882 kg
2004-01-02T05:20:34.080 a = 28937941.941 m, e = 0.457162297, m = 2007.882 kg
2004-01-02T05:22:34.080 a = 28937941.941 m, e = 0.457162297, m = 2007.882 kg
2004-01-02T05:24:34.080 a = 28937941.941 m, e = 0.457162297, m = 2007.882 kg
2004-01-02T05:26:34.080 a = 28937941.941 m, e = 0.457162297, m = 2007.882 kg
2004-01-02T05:28:34.080 a = 28937941.941 m, e = 0.457162297, m = 2007.882 kg
2004-01-02T05:30:34.080 a = 28937941.941 m, e = 0.457162297, m = 2007.882 kg

If instead of overriding the attitude we want to use the attitude configured
in the propagator (which here is VNC-aligned), then we simply set the
attitude overriding parameter to null when building the maneuver:

   propagator.addForceModel(new Maneuver(null, triggers, propulsionModel));

The results with this configuration would become:

2004-01-02T04:00:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:02:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:04:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:06:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:08:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:10:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:12:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:14:34.080 a = 24396159.000 m, e = 0.728312150, m = 2500.000 kg
2004-01-02T04:16:34.080 a = 24445841.001 m, e = 0.724984968, m = 2491.919 kg
2004-01-02T04:18:34.080 a = 24547017.613 m, e = 0.718218653, m = 2475.758 kg
2004-01-02T04:20:34.080 a = 24650693.763 m, e = 0.711301532, m = 2459.596 kg
2004-01-02T04:22:34.080 a = 24756972.407 m, e = 0.704231757, m = 2443.435 kg
2004-01-02T04:24:34.080 a = 24865960.944 m, e = 0.697007471, m = 2427.273 kg
2004-01-02T04:26:34.080 a = 24977771.472 m, e = 0.689626812, m = 2411.112 kg
2004-01-02T04:28:34.080 a = 25092521.078 m, e = 0.682087911, m = 2394.950 kg
2004-01-02T04:30:34.080 a = 25210332.139 m, e = 0.674388891, m = 2378.788 kg
2004-01-02T04:32:34.080 a = 25331332.649 m, e = 0.666527867, m = 2362.627 kg
2004-01-02T04:34:34.080 a = 25455656.575 m, e = 0.658502951, m = 2346.465 kg
2004-01-02T04:36:34.080 a = 25583444.233 m, e = 0.650312244, m = 2330.304 kg
2004-01-02T04:38:34.080 a = 25714842.703 m, e = 0.641953845, m = 2314.142 kg
2004-01-02T04:40:34.080 a = 25850006.270 m, e = 0.633425850, m = 2297.981 kg
2004-01-02T04:42:34.080 a = 25989096.901 m, e = 0.624726354, m = 2281.819 kg
2004-01-02T04:44:34.080 a = 26132284.765 m, e = 0.615853455, m = 2265.658 kg
2004-01-02T04:46:34.080 a = 26279748.789 m, e = 0.606805258, m = 2249.496 kg
2004-01-02T04:48:34.080 a = 26431677.269 m, e = 0.597579879, m = 2233.335 kg
2004-01-02T04:50:34.080 a = 26588268.522 m, e = 0.588175453, m = 2217.173 kg
2004-01-02T04:52:34.080 a = 26749731.602 m, e = 0.578590139, m = 2201.012 kg
2004-01-02T04:54:34.080 a = 26916287.072 m, e = 0.568822132, m = 2184.850 kg
2004-01-02T04:56:34.080 a = 27088167.851 m, e = 0.558869672, m = 2168.688 kg
2004-01-02T04:58:34.080 a = 27265620.125 m, e = 0.548731056, m = 2152.527 kg
2004-01-02T05:00:34.080 a = 27448904.347 m, e = 0.538404659, m = 2136.365 kg
2004-01-02T05:02:34.080 a = 27638296.331 m, e = 0.527888947, m = 2120.204 kg
2004-01-02T05:04:34.080 a = 27834088.441 m, e = 0.517182503, m = 2104.042 kg
2004-01-02T05:06:34.080 a = 28036590.891 m, e = 0.506284055, m = 2087.881 kg
2004-01-02T05:08:34.080 a = 28246133.176 m, e = 0.495192508, m = 2071.719 kg
2004-01-02T05:10:34.080 a = 28463065.636 m, e = 0.483906983, m = 2055.558 kg
2004-01-02T05:12:34.080 a = 28687761.178 m, e = 0.472426869, m = 2039.396 kg
2004-01-02T05:14:34.080 a = 28920617.165 m, e = 0.460751878, m = 2023.235 kg
2004-01-02T05:16:34.080 a = 29149754.286 m, e = 0.449481220, m = 2007.882 kg
2004-01-02T05:18:34.080 a = 29149754.286 m, e = 0.449481220, m = 2007.882 kg
2004-01-02T05:20:34.080 a = 29149754.286 m, e = 0.449481220, m = 2007.882 kg
2004-01-02T05:22:34.080 a = 29149754.286 m, e = 0.449481220, m = 2007.882 kg
2004-01-02T05:24:34.080 a = 29149754.286 m, e = 0.449481220, m = 2007.882 kg
2004-01-02T05:26:34.080 a = 29149754.286 m, e = 0.449481220, m = 2007.882 kg
2004-01-02T05:28:34.080 a = 29149754.286 m, e = 0.449481220, m = 2007.882 kg
2004-01-02T05:30:34.080 a = 29149754.286 m, e = 0.449481220, m = 2007.882 kg

As expected, we see that for the same fuel consumption, semi-major axis increases
more and eccentricity decreases more when the attitude is always kept aligned
with velocity than when attitude is inertial.

The complete code for this example can be found in the source tree of the tutorials,
in file `src/main/java/org/orekit/tutorials/maneuvers/ApogeeManeuver.java`.


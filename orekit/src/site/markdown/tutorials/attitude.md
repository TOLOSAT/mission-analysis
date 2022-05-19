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

# Attitude

This tutorial emphasizes a specific usage of the attitude package
described in the [attitudes section](https://www.orekit.org/site-orekit-latest/architecture/attitudes.html) of
the library architecture documentation.

## Attitudes Sequence

`AttitudesSequence` enables easy switching between attitude laws on
event occurrences when propagating some `SpacecraftState`.

Let's set up an initial state as:

* a date in UTC time scale
* an orbit defined by the position and the velocity of the spacecraft in
  the EME2000 inertial frame and an associated central attraction coefficient
  chosen among many physical constants available in Orekit.

The initial orbit is here defined as a `KeplerianOrbit`.

    AbsoluteDate initialDate = new AbsoluteDate(2004, 01, 01, 23, 30, 00.000, TimeScalesFactory.getUTC());
    Vector3D position  = new Vector3D(-6142438.668, 3492467.560, -25767.25680);
    Vector3D velocity  = new Vector3D(505.8479685, 942.7809215, 7435.922231);
    Orbit initialOrbit = new KeplerianOrbit(new PVCoordinates(position, velocity),
                                            FramesFactory.getEME2000(), initialDate,
                                            Constants.EIGEN5C_EARTH_MU);

More details on the orbit representation can be found
in the [orbits section](https://www.orekit.org/site-orekit-latest/architecture/orbits.html)
of the library architecture documentation.

We will put all switching events in a set.

    final SortedSet<String> output = new TreeSet<>();

Let's define a couple of `AttitudeProvider`, built upon `LofOffset` laws for instance.

    final AttitudeProvider dayObservationLaw = new LofOffset(initialOrbit.getFrame(), LOFType.VVLH,
                                                             RotationOrder.XYZ, FastMath.toRadians(20), FastMath.toRadians(40), 0);
    final AttitudeProvider nightRestingLaw   = new LofOffset(initialOrbit.getFrame(), LOFType.VVLH);

Let's also define some `EventDetector`. For this tutorial's requirements,
two `EclipseDetector`, each one using a customized implementation of `EventHandler`
with a dedicated `eventOccurred` method: `dayNightEvent`, to detect the day to night
transition, `nightDayEvent`, to detect the night to day transition:

    PVCoordinatesProvider sun   = CelestialBodyFactory.getSun();
    PVCoordinatesProvider earth = new OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                                                       0.0,
                                                       FramesFactory.getITRF(IERSConventions.IERS_2010, true));
    EventDetector dayNightEvent = new EclipseDetector(sun, 696000000., earth).
                                  withHandler(new ContinueOnEvent<EclipseDetector>());
    EventDetector nightDayEvent = new EclipseDetector(sun, 696000000., earth).
                                  withHandler(new ContinueOnEvent<EclipseDetector>());

More details on event detectors and event handlers can be found in the
[propagation section](https://www.orekit.org/site-orekit-latest/architecture/propagation.html)
of the library architecture documentation.

An `AttitudesSequence` is then defined, for the sake of this tutorial,
by adding two switching conditions acting as a simple loop:

* the first one enables the transition from `dayObservationLaw` to `nightRestingLaw`
  when a decreasing `dayNightEvent` occurs,
* the second one enables the transition from `nightRestingLaw` to `dayObservationLaw`
  when an increasing `nightDayEvent` occurs.

As the two conditions reverse each other effect, the combined `AttitudesSequence`
acts as a loop. We also define a handler to monitor attitude switches:

    AttitudesSequence attitudesSequence = new AttitudesSequence();
    AttitudesSequence.SwitchHandler switchHandler =
                (preceding, following, s) -> {
                    if (preceding == dayObservationLaw) {
                        output.add(s.getDate() + ": switching to night law");
                    } else {
                        output.add(s.getDate() + ": switching to day law");
                    }
                };
    attitudesSequence.addSwitchingCondition(dayObservationLaw, dayNightEvent,
                                            false, true, 10.0,
                                            AngularDerivativesFilter.USE_R, nightRestingLaw,   switchHandler);
    attitudesSequence.addSwitchingCondition(nightRestingLaw,   nightDayEvent,
                                            true, false, 10.0,
                                            AngularDerivativesFilter.USE_R, dayObservationLaw, switchHandler);

An `AttitudesSequence` needs at least one switching condition to be meaningful,
but there is no upper limit.

An active `AttitudeProvider` may have several switch events and next law settings,
leading to different activation patterns depending on which event is triggered first.

Don't forget to set the initial active law according to the initial state:

    if (dayNightEvent.g(new SpacecraftState(initialOrbit)) >= 0) {
        // initial position is in daytime
        attitudesSequence.resetActiveProvider(dayObservationLaw);
    } else {
        // initial position is in nighttime
        attitudesSequence.resetActiveProvider(nightRestingLaw);
    }

Now, let's choose some propagator to compute the spacecraft motion. We will use
an `EcksteinHechlerPropagator` based on the analytical Eckstein-Hechler model.
The propagator is built upon the initialOrbit, the attitudeSequence and
physical constants for the potential.

    Propagator propagator = new EcksteinHechlerPropagator(initialOrbit, attitudesSequence,
                                                          Constants.EIGEN5C_EARTH_EQUATORIAL_RADIUS,
                                                          Constants.EIGEN5C_EARTH_MU, Constants.EIGEN5C_EARTH_C20,
                                                          Constants.EIGEN5C_EARTH_C30, Constants.EIGEN5C_EARTH_C40,
                                                          Constants.EIGEN5C_EARTH_C50, Constants.EIGEN5C_EARTH_C60);

The `attitudeSequence` must register all the switching events before propagation.

    attitudesSequence.registerSwitchEvents(propagator);

The propagator operating mode is completed with a fixed step handler.
The implementation of the interface `OrekitFixedStepHandler` aims to define
the `handleStep` method called within the loop. For the purpose of this
tutorial, the `handleStep` method will print at the current date two angles,
the first one indicates if the spacecraft is eclipsed while the second informs
about the current attitude law.

    propagator.getMultiplexer().add(180.0, (currentState, isLast) -> {
            DecimalFormatSymbols angleDegree = new DecimalFormatSymbols(Locale.US);
            angleDegree.setDecimalSeparator('\u00b0');
            DecimalFormat ad = new DecimalFormat(" 00.000;-00.000", angleDegree);

            // the Earth position in spacecraft frame should be along spacecraft Z axis
            // during nigthtime and away from it during daytime due to roll and pitch offsets
            final Vector3D earthDir = currentState.toTransform().transformPosition(Vector3D.ZERO);
            final double pointingOffset = Vector3D.angle(earthDir, Vector3D.PLUS_K);

            // the g function is the eclipse indicator, it is an angle between Sun and Earth limb,
            // positive when Sun is outside of Earth limb, negative when Sun is hidden by Earth limb
            final double eclipseAngle = dayNightEvent.g(currentState);

            output.add(currentState.getDate() +
                       " " + ad.format(FastMath.toDegrees(eclipseAngle) +
                       " " + ad.format(FastMath.toDegrees(pointingOffset)));
        }
    });


More details on steps management can be found in the
[propagation section](https://www.orekit.org/site-orekit-latest/architecture/propagation.html)
of the library architecture documentation.

Finally, the propagator is just asked to propagate for a given duration, and we print
the results:

    SpacecraftState finalState = propagator.propagate(initialDate.shiftedBy(12600.));
    for (final String line : output) {
        System.out.println(line);
    }

Note that we use an intermediate `SortedSet` to first gather both the switching events
and the step outputs instead of just letting the event handler and step handler directly
print their results. The rationale is that as events handlers could truncate a step (if
their `eventOccurred` method returned `Action.STOP`), the library design is to always
call `eventOccurred` on the event handler first, and then to call `handleStep` on the
step handler afterwards, with the `isLast` boolean set up correctly if the event handler
decided to stop propagation. A side effect is that if both methods print something, then
the switch from the end of the step would be printed first and the step itself printed
afterwards, which would lead to out of order output. The `SortedSet` ensures the various
lines will be sorted in lexicographic order, which is chronological order here, despite
they will be generated slightly out of order near events occurrences.

As the propagation goes along, events occur switching from one attitude law to another.

The printed results are shown below:

    2004-01-01T23:30:00.000 -11°649  00°000
    2004-01-01T23:33:00.000 -17°804  00°000
    2004-01-01T23:36:00.000 -22°458  00°000
    2004-01-01T23:39:00.000 -25°045  00°000
    2004-01-01T23:42:00.000 -25°140  00°000
    2004-01-01T23:45:00.000 -22°726  00°000
    2004-01-01T23:48:00.000 -18°207  00°000
    2004-01-01T23:51:00.000 -12°146  00°000
    2004-01-01T23:54:00.000 -05°042  00°000
    2004-01-01T23:55:57.968: switching to day law
    2004-01-01T23:57:00.000  02°741  43°958
    2004-01-02T00:00:00.000  10°946  43°958
    2004-01-02T00:03:00.000  19°390  43°958
    2004-01-02T00:06:00.000  27°931  43°958
    2004-01-02T00:09:00.000  36°441  43°958
    2004-01-02T00:12:00.000  44°787  43°958
    2004-01-02T00:15:00.000  52°808  43°958
    2004-01-02T00:18:00.000  60°286  43°958
    2004-01-02T00:21:00.000  66°913  43°958
    2004-01-02T00:24:00.000  72°251  43°958
    2004-01-02T00:27:00.000  75°751  43°958
    2004-01-02T00:30:00.000  76°896  43°958
    2004-01-02T00:33:00.000  75°480  43°958
    2004-01-02T00:36:00.000  71°756  43°958
    2004-01-02T00:39:00.000  66°259  43°958
    2004-01-02T00:42:00.000  59°533  43°958
    2004-01-02T00:45:00.000  51°999  43°958
    2004-01-02T00:48:00.000  43°955  43°958
    2004-01-02T00:51:00.000  35°608  43°958
    2004-01-02T00:54:00.000  27°112  43°958
    2004-01-02T00:57:00.000  18°596  43°958
    2004-01-02T01:00:00.000  10°184  43°958
    2004-01-02T01:03:00.000  02°022  43°958
    2004-01-02T01:03:45.919: switching to night law
    2004-01-02T01:06:00.000 -05°706  00°000
    2004-01-02T01:09:00.000 -12°733  00°000
    2004-01-02T01:12:00.000 -18°680  00°000
    2004-01-02T01:15:00.000 -23°037  00°000
    2004-01-02T01:18:00.000 -25°240  00°000
    2004-01-02T01:21:00.000 -24°914  00°000
    2004-01-02T01:24:00.000 -22°122  00°000
    2004-01-02T01:27:00.000 -17°313  00°000
    2004-01-02T01:30:00.000 -11°051  00°000
    2004-01-02T01:33:00.000 -03°814  00°000
    2004-01-02T01:34:28.690: switching to day law
    2004-01-02T01:36:00.000  04°052  43°958
    2004-01-02T01:39:00.000  12°308  43°958
    2004-01-02T01:42:00.000  20°777  43°958
    2004-01-02T01:45:00.000  29°322  43°958
    2004-01-02T01:48:00.000  37°815  43°958
    2004-01-02T01:51:00.000  46°121  43°958
    2004-01-02T01:54:00.000  54°070  43°958
    2004-01-02T01:57:00.000  61°434  43°958
    2004-01-02T02:00:00.000  67°885  43°958
    2004-01-02T02:03:00.000  72°963  43°958
    2004-01-02T02:06:00.000  76°111  43°958
    2004-01-02T02:09:00.000  76°841  43°958
    2004-01-02T02:12:00.000  75°020  43°958
    2004-01-02T02:15:00.000  70°968  43°958
    2004-01-02T02:18:00.000  65°236  43°958
    2004-01-02T02:21:00.000  58°353  43°958
    2004-01-02T02:24:00.000  50°719  43°958
    2004-01-02T02:27:00.000  42°613  43°958
    2004-01-02T02:30:00.000  34°231  43°958
    2004-01-02T02:33:00.000  25°723  43°958
    2004-01-02T02:36:00.000  17°215  43°958
    2004-01-02T02:39:00.000  08°834  43°958
    2004-01-02T02:42:00.000  00°727  43°958
    2004-01-02T02:42:16.591: switching to night law
    2004-01-02T02:45:00.000 -06°907  00°000
    2004-01-02T02:48:00.000 -13°788  00°000
    2004-01-02T02:51:00.000 -19°515  00°000
    2004-01-02T02:54:00.000 -23°558  00°000
    2004-01-02T02:57:00.000 -25°366  00°000
    2004-01-02T03:00:00.000 -24°622  00°000
    Propagation ended at 2004-01-02T03:00:00.000

The complete code for this example can be found in the source tree of the tutorials,
in file `src/main/java/org/orekit/tutorials/attitude/EarthObservation.java`.

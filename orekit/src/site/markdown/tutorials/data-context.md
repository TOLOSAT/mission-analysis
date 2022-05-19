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

# Data context

This tutorial shows how to use different data contexts in one application.
It sets up two data contexts, a made-up one with a reduced set of leap
seconds and no Earth Orientation Parameters, and a complete one that uses
the files located in an `orekit-data` folder located in user home directory,
and compared dates and frames computed using both contexts.

The `DataContext` interfaces is the top-level interface for building physical
models that depend on external data. These models include time scales like
UTC (which needs UTC-TAI offsets data) or UT1 (which needs Earth Orientation
Parameters data), frames like ITRF (which also need Earth Orientation
Parameters data), celestial bodies (which need ephemerides). The `DataContext`
interface allows to retrieve the factories for all these models, and the
factories will build them.

## Default context

There is a default `DataContext` which loads models data lazily when they
are needed, using several `DataProvider` instances to locate this data,
for example by crawling a directory tree on disk storage and parsing the
files according to their names. For example it knows how to load UTC-TAI offsets
from a `tai-utc.dat` file that users would have downloaded from USNO and saved.

The default data context is configured by specifying the root directory
where data will be searched when needed:

    // configure the reference context
    final File home       = new File(System.getProperty("user.home"));
    final File orekitData = new File(home, "orekit-data");
    if (!orekitData.exists()) {
        System.err.format(Locale.US, "Failed to find %s folder%n",
                          orekitData.getAbsolutePath());
        System.err.format(Locale.US, "You need to download %s from %s, unzip it in %s and rename it 'orekit-data' for this tutorial to work%n",
                          "orekit-data-master.zip", "https://gitlab.orekit.org/orekit/orekit-data/-/archive/master/orekit-data-master.zip",
                          home.getAbsolutePath());
        System.exit(1);
    }
    DataContext.
        getDefault().
        getDataProvidersManager().
        addProvider(new DirectoryCrawler(orekitData));

## Custom context

The custom context is implemented by the application class itself:

    // create the local data context implemented by this class
    final DataContext context = new Context();
    
This works because the class defines the five methods that allow to get the five
model factories:

    /** {@inheritDoc} */
    @Override
    public TimeScales getTimeScales() {
        // set up only the offsets for years 2009 to 2017 and zero EOP
        return TimeScales.of(Arrays.asList(new OffsetModel(new DateComponents(2009, 1, 1), 34),
                                           new OffsetModel(new DateComponents(2012, 1, 1), 35),
                                           new OffsetModel(new DateComponents(2015, 1, 1), 36)),
            (convention, timescale) -> Collections.emptyList());
    }

    /** {@inheritDoc} */
    @Override
    public Frames getFrames() {
        return Frames.of(getTimeScales(), getCelestialBodies());
    }

    /** {@inheritDoc} */
    @Override
    public CelestialBodies getCelestialBodies() {
        // just us the lazy loaded bodies
        return DataContext.getDefault().getCelestialBodies();
    }

    /** {@inheritDoc} */
    @Override
    public GravityFields getGravityFields() {
        // just us the lazy loaded gravity fields
        return DataContext.getDefault().getGravityFields();
    }

    /** {@inheritDoc} */
    @Override
    public GeoMagneticFields getGeoMagneticFields() {
        // just us the lazy loaded geomagnetic fields
        return DataContext.getDefault().getGeoMagneticFields();
    }

The most important part, and probably the one most people will need to
implement corresponds to the `TimeScales` factory. Here we create it using
the static method `TimeScales.of(utcMinusTai, eopSupplier)`. For the tutorial,
the implementation is very limited: the `utcMinusTai` collection of offsets
is hard-coded and limited to the three leap seconds that occurred in 2009,
2012, and 2015. The `eopSupplier` function is even more basic as it always
returns an empty list.

That `Frames` factory is often closely linked to both the `TimeScales` and
`CelestialBodies`, as it needs the same data, so a recommended way to build
the factory is to refer to the other factories as shown in the tutorial.

All the remaining factories are in fact the same factories that are automatically
retrieved by the default context.

## Models comparison

We first want to check the offsets between dates converted from their calendar
representation to an Orekit `AbsoluteDate` in the two contexts. We will use
one date before the first leap second of the custom context, one date in
the range covered by both contexts, and one after the first leap second that is
missing in the custom context and present in the default context.

    // compare date conversions for the two contexts
    final TimeScale contextUTC   = context.getTimeScales().getUTC();
    final TimeScale referenceUTC = DataContext.getDefault().getTimeScales().getUTC();
    System.out.format(Locale.US, "time scales differences between made up data context and default data context%n");
    for (DateComponents day : days) {
        final AbsoluteDate contextDate   = new AbsoluteDate(day, TimeComponents.H00, contextUTC);
        final AbsoluteDate referenceDate = new AbsoluteDate(day, TimeComponents.H00, referenceUTC);
        System.out.format(Locale.US, "UTC offsets on %s: %8.5f%n",
                          day, contextDate.durationFrom(referenceDate));
    }

The output of this small loop reads:

    time scales differences between made up data context and default data context
    UTC offsets on 2003-11-23:  8.08645
    UTC offsets on 2010-07-11:  0.00000
    UTC offsets on 2017-08-21: -1.00000

The last two lines were expected. On 2010 both the custom and default context
consider there is a 35 seconds offset between TAI aund UTC, so they convert
the calendar date the same way. On 2017, the custom context missed a leap
second that occurred on 2017-01-01 so consider the offset is 36 seconds since
2015 on, whereas the default context knew the offset has changed to 37 seconds.
The first line looks probably strange, with a value that is not a whole number of
seconds. This is due to a side effect of the way Orekit creates the UTC time
scale. As it is cumbersome to parse the non-constant offsets used between 1961
and 1972 and some custom files don't even include them, Orekit looks at the offsets
provided (here the three offsets we hardcoded) and if the first one is later than
1968 (which corresponds to the last change in the linear model, which was in effect
from 1968-02-01 to 1971-12-31), then it automatically add them. This implies that
our custom context uses the last linear model from 1968-02-01 to 2008-12-31! This
is not a problem if the earliest date used is in 2009, though. So the lesson learned
from this example is that if one implements a custom context with a custom
`TimeScales`, then, it is better to implement all constants offsets starting from
1972 and not starting later.

Another comparison we want to do is to check ITRF frames. We will do this on
a day for which dates conversion works (i.e. between 2009 and 2015). We selected
2010-07-01. We build two times the ITRF frame, each time with a different context.
As the contexts do not use the same Earth Orientation Parameters, the frames
will not match. We compute the transformation between them during the day, extract
the rotation angle, and multiply it by the Earth equatorial radius to get a value
that is easier to understand:

     // compare frames conversions for the two contexts
     final Frame contextITRF   = context.getFrames().getITRF(IERSConventions.IERS_2010, false);
     final Frame referenceITRF = DataContext.getDefault().getFrames().getITRF(IERSConventions.IERS_2010, false);
     System.out.format(Locale.US, "%nframes differences between made up data context and default data context%n");
     final AbsoluteDate t0 = new AbsoluteDate(days.get(1), contextUTC);
     for (double dt = 0; dt < Constants.JULIAN_DAY; dt += 3600) {
         final AbsoluteDate date      = t0.shiftedBy(dt);
         final Transform    transform = contextITRF.getTransformTo(referenceITRF, date);
         System.out.format(Locale.US, "frames offsets on %s: %6.3f m%n",
                           date, transform.getRotation().getAngle() * Constants.WGS84_EARTH_EQUATORIAL_RADIUS);
     }

The output of this loop reads:

    frames differences between made up data context and default data context
    frames offsets on 2010-07-11T00:00:00.000: 29.393 m
    frames offsets on 2010-07-11T01:00:00.000: 29.385 m
    frames offsets on 2010-07-11T02:00:00.000: 29.378 m
    frames offsets on 2010-07-11T03:00:00.000: 29.371 m
    frames offsets on 2010-07-11T04:00:00.000: 29.364 m
    frames offsets on 2010-07-11T05:00:00.000: 29.357 m
    frames offsets on 2010-07-11T06:00:00.000: 29.350 m
    frames offsets on 2010-07-11T07:00:00.000: 29.344 m
    frames offsets on 2010-07-11T08:00:00.000: 29.337 m
    frames offsets on 2010-07-11T09:00:00.000: 29.331 m
    frames offsets on 2010-07-11T10:00:00.000: 29.325 m
    frames offsets on 2010-07-11T11:00:00.000: 29.318 m
    frames offsets on 2010-07-11T12:00:00.000: 29.312 m
    frames offsets on 2010-07-11T13:00:00.000: 29.305 m
    frames offsets on 2010-07-11T14:00:00.000: 29.299 m
    frames offsets on 2010-07-11T15:00:00.000: 29.293 m
    frames offsets on 2010-07-11T16:00:00.000: 29.286 m
    frames offsets on 2010-07-11T17:00:00.000: 29.280 m
    frames offsets on 2010-07-11T18:00:00.000: 29.274 m
    frames offsets on 2010-07-11T19:00:00.000: 29.268 m
    frames offsets on 2010-07-11T20:00:00.000: 29.262 m
    frames offsets on 2010-07-11T21:00:00.000: 29.257 m
    frames offsets on 2010-07-11T22:00:00.000: 29.251 m
    frames offsets on 2010-07-11T23:00:00.000: 29.246 m

What we see is the effect of EOP.

The complete code for this example can be found in the source tree of the tutorials,
in file `src/main/java/org/orekit/tutorials/data/Context.java`.

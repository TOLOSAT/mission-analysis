package quickTest;

import java.io.File;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

import org.hipparchus.ode.nonstiff.AdaptiveStepsizeIntegrator;
import org.hipparchus.ode.nonstiff.DormandPrince853Integrator;
import org.hipparchus.util.FastMath;
import org.orekit.bodies.CelestialBody;
import org.orekit.bodies.CelestialBodyFactory;
import org.orekit.bodies.OneAxisEllipsoid;
import org.orekit.data.DataContext;
import org.orekit.data.DataProvidersManager;
import org.orekit.data.DirectoryCrawler;
import org.orekit.errors.OrekitException;
import org.orekit.forces.ForceModel;
import org.orekit.forces.drag.DragForce;
import org.orekit.forces.drag.DragSensitive;
import org.orekit.forces.drag.IsotropicDrag;
import org.orekit.forces.gravity.HolmesFeatherstoneAttractionModel;
import org.orekit.forces.gravity.potential.GravityFieldFactory;
import org.orekit.forces.gravity.potential.NormalizedSphericalHarmonicsProvider;
import org.orekit.forces.radiation.IsotropicRadiationSingleCoefficient;
import org.orekit.forces.radiation.RadiationSensitive;
import org.orekit.forces.radiation.SolarRadiationPressure;
import org.orekit.frames.Frame;
import org.orekit.frames.FramesFactory;
import org.orekit.orbits.KeplerianOrbit;
import org.orekit.orbits.CircularOrbit;
import org.orekit.orbits.Orbit;
import org.orekit.orbits.OrbitType;
import org.orekit.orbits.PositionAngle;
import org.orekit.propagation.SpacecraftState;
import org.orekit.propagation.events.AltitudeDetector;
import org.orekit.propagation.events.EventDetector;
import org.orekit.propagation.numerical.NumericalPropagator;
import org.orekit.propagation.sampling.OrekitFixedStepHandler;
import org.orekit.time.AbsoluteDate;
import org.orekit.time.TimeScalesFactory;
import org.orekit.utils.Constants;
import org.orekit.utils.IERSConventions;
import org.orekit.models.earth.atmosphere.*;
import org.orekit.models.earth.atmosphere.data.MarshallSolarActivityFutureEstimation;



/** Based on the Orekit tutorial for numerical orbit propagation
 */
public class NumericalTest {

    /** Private constructor for utility class. */
    private NumericalTest() {
        // empty
    }

    /** Program entry point.
     * @param args program arguments (unused here)
     */
    static ArrayList<KeplerianOrbit> orbitList = new ArrayList<>();
    
    static AbsoluteDate initialDate = new AbsoluteDate();
    
    public static void main(final String[] args) {
        try {

            // configure Orekit
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
            final DataProvidersManager manager = DataContext.getDefault().getDataProvidersManager();
            manager.addProvider(new DirectoryCrawler(orekitData));

            // gravitation coefficient
            final double mu =  3.986004415e+14;

            // inertial frame
            final Frame inertialFrame = FramesFactory.getEME2000();
            
            // Load Celestial bodies
            // ---------------------
            final CelestialBody   sun   = CelestialBodyFactory.getSun();
          
            
            // Initial date
            initialDate = new AbsoluteDate(2024,07,02,12,0,0,TimeScalesFactory.getUTC());

            // Initial orbit
            final double RE = Constants.EIGEN5C_EARTH_EQUATORIAL_RADIUS;
            final double a = 6878.e3; // semi major axis in meters
            final double e = 2.e-2; // eccentricity
            final double i = 97.4009688*Math.PI/180; // inclination
            final double omega =Math.PI/2; // perigee argument
            final double raan = 0; // right ascention of ascending node
            final double lM = 0; // mean anomaly
            final Orbit initialOrbit = new KeplerianOrbit(a, e, i, omega, raan, lM, PositionAngle.MEAN,
                          inertialFrame, initialDate, mu);

            int datastep = 100; // Interval between recorded data points on output file
    		int duration = 1600*86400;// in seconds
            double  mass= 2.66;
    		
            // Initial state definition
            final SpacecraftState initialState = new SpacecraftState(initialOrbit, mass);
            final CircularOrbit initialCirc = (CircularOrbit) OrbitType.CIRCULAR.convertType(initialOrbit);
            // Adaptive step integrator with a minimum step of 0.01 and a maximum step of 1000
            final double minStep = 0.01;
            final double maxstep = 1000.0;
            final double positionTolerance = 10.0;
            final OrbitType propagationType = OrbitType.CIRCULAR;
            final double[][] tolerances =
                    NumericalPropagator.tolerances(positionTolerance, initialCirc, propagationType);
            final AdaptiveStepsizeIntegrator integrator =
                    new DormandPrince853Integrator(minStep, maxstep, tolerances[0], tolerances[1]);

            // Propagator
            final NumericalPropagator propagator = new NumericalPropagator(integrator);
            propagator.setOrbitType(propagationType);

            // Gravity Field Force Model
            final NormalizedSphericalHarmonicsProvider provider =
                    GravityFieldFactory.getNormalizedProvider(10, 10);
            final ForceModel holmesFeatherstone =
                    new HolmesFeatherstoneAttractionModel(FramesFactory.getITRF(IERSConventions.IERS_2010,true),provider);
            propagator.addForceModel(holmesFeatherstone);
            
            
            //Models
            final IERSConventions conventions = IERSConventions.IERS_2010;
            final Frame earthFrame = FramesFactory.getITRF(conventions, false);
            final OneAxisEllipsoid earth = new OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                    Constants.WGS84_EARTH_FLATTENING,
                    earthFrame);
            
            // Atmosphere
            //final HarrisPriester atmos = new HarrisPriester(sun,earth);
            
            final MarshallSolarActivityFutureEstimation parameters = new MarshallSolarActivityFutureEstimation(MarshallSolarActivityFutureEstimation.DEFAULT_SUPPORTED_NAMES, MarshallSolarActivityFutureEstimation.StrengthLevel.AVERAGE);
            final NRLMSISE00 atmos = new NRLMSISE00(parameters, sun, earth);
            
            // Drag
            double crossArea = 0.025;
            double Cd = 2.2;
            DragSensitive ssc = new IsotropicDrag(crossArea, Cd);
            propagator.addForceModel(new DragForce(atmos, ssc));
           
            // Solar Radiation Pressure
            double cR = 1.8;
            double srpArea = 0.025;
            final RadiationSensitive ssrc = new IsotropicRadiationSingleCoefficient(srpArea, cR);
            propagator.addForceModel(new SolarRadiationPressure(sun, RE, ssrc));
            
            
            // Set up initial state in the propagator
            propagator.setInitialState(initialState);

            // Set up a step handler
            propagator.getMultiplexer().add(8600, new TestStepHandler());
            
            
            // Stopping when altitude too low
            
            final double MinAlt = 140000;
            final EventDetector LowAlt = new AltitudeDetector(MinAlt, earth);
            propagator.addEventDetector(LowAlt);
            
            // Extrapolate from the initial to the final date
            propagator.propagate(initialDate.shiftedBy(duration));
            
            
            new WriteToFile("output/numericaltest.txt",datastep);
            
            BasicPlot plotter = new BasicPlot(); //creating plotter class
            List<AbsoluteDate> DateList = orbitList.stream().map(KeplerianOrbit::getDate).collect(Collectors.toList());
            
            List<Double> TimeList =  new ArrayList<>();
            
            for (AbsoluteDate D : DateList) {
             	TimeList.add(D.durationFrom(initialDate)/(24*3600));
             }
            
            List<Double> AList = orbitList.stream().map(KeplerianOrbit::getA).collect(Collectors.toList());
            plotter.plot(TimeList, AList, "Semi Major Axis" ,"NumericalA", "Numerical");	            
        
            ArrayList<Double> AltList = new ArrayList<>();
            for (double r : AList) {
            	AltList.add(r-RE);
            }
            plotter.plot(TimeList, AltList, "Altitude" ,"NumericalAlt", "Numerical");	
            
            List<Double> EList = orbitList.stream().map(KeplerianOrbit::getE).collect(Collectors.toList());
            plotter.plot(TimeList, EList, "Eccentricity" ,"NumericalE", "Numerical");	
            
            List<Double> IList = orbitList.stream().map(KeplerianOrbit::getI).collect(Collectors.toList());
            plotter.plot(TimeList, IList, "Inclination" ,"NumericalI", "Numerical");	
            
            List<Double> APList = orbitList.stream().map(KeplerianOrbit::getPerigeeArgument).collect(Collectors.toList());
            plotter.plot(TimeList, APList, "Argument of the Perigee" ,"NumericalAP", "Numerical");	

            List<Double> RaanList = orbitList.stream().map(KeplerianOrbit::getRightAscensionOfAscendingNode).collect(Collectors.toList());
            plotter.plot(TimeList, RaanList, "Right Ascension of Ascending Node" ,"NumericalRaan", "Numerical");	
            
        } catch (OrekitException oe) {
            System.err.println(oe.getLocalizedMessage());
        }
    }

    /* Step Handler
     * Introduces oscullating orbital elements into a list
     */
    private static class TestStepHandler implements OrekitFixedStepHandler {

        /** Simple constructor.
         */
        TestStepHandler() {
            //private constructor
        }

        /** {@inheritDoc} */
        @Override
        public void init(final SpacecraftState s0, final AbsoluteDate t, final double step) {
        }

        /** {@inheritDoc} */
        @Override
        public void handleStep(final SpacecraftState currentState) {
            final KeplerianOrbit o = (KeplerianOrbit) OrbitType.KEPLERIAN.convertType(currentState.getOrbit());
            orbitList.add(o);
        }

        /** {@inheritDoc} */
        @Override
        public void finish(final SpacecraftState finalState) {
            System.out.println("this was the last step ");
            System.out.println();
        }

    }

    private static class WriteToFile{
    	
     WriteToFile(String filename, int dataStep) {
    		 try {
    			 FileWriter myWriter = new FileWriter(filename);
    			 myWriter.write("Time ; Semi-Major Axis ; Eccentricity ; Inclination ; Argument of the perigee ; Right Ascension of the Ascending node\n");
    			 int i = -1;
    			 int previ = 0;
    			 for(KeplerianOrbit o : orbitList) {
    				 i += 1;
    				 if( i-previ == 0 || i-previ == dataStep) {
    					 myWriter.write( String.valueOf(o.getDate().durationFrom(initialDate)) + ";"
    						 +	String.valueOf(o.getA()) + ";"
    					     + String.valueOf(o.getE()) + ";" 
    					     + String.valueOf(FastMath.toDegrees(o.getI())) + ";" 
    					     + String.valueOf(FastMath.toDegrees(o.getPerigeeArgument())) + ";" 
    					     + String.valueOf(FastMath.toDegrees(o.getTrueAnomaly())) + "\n");
    					 previ = i;
    				 }
    			 }
    			 myWriter.close();
    			 
    		 }
    		 catch (IOException e) {
                 System.out.println("An error occurred.");
                 e.printStackTrace();
               }
    	    }
    	
    }
}

package quickTest;

import java.io.File;



import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

import org.hipparchus.ode.AbstractIntegrator;
import org.hipparchus.ode.nonstiff.ClassicalRungeKuttaIntegrator;
import org.hipparchus.util.FastMath;
import org.orekit.bodies.CelestialBody;
import org.orekit.bodies.CelestialBodyFactory;
import org.orekit.bodies.OneAxisEllipsoid;
import org.orekit.data.DataContext;
import org.orekit.data.DataProvidersManager;
import org.orekit.data.DirectoryCrawler;
import org.orekit.errors.OrekitException;
import org.orekit.forces.drag.DragSensitive;
import org.orekit.forces.drag.IsotropicDrag;
import org.orekit.forces.gravity.potential.GravityFieldFactory;
import org.orekit.forces.gravity.potential.UnnormalizedSphericalHarmonicsProvider;
import org.orekit.forces.radiation.IsotropicRadiationSingleCoefficient;
import org.orekit.forces.radiation.RadiationSensitive;
import org.orekit.frames.Frame;
import org.orekit.frames.FramesFactory;
import org.orekit.models.earth.atmosphere.HarrisPriester;
import org.orekit.orbits.KeplerianOrbit;
import org.orekit.orbits.Orbit;
import org.orekit.orbits.OrbitType;
import org.orekit.orbits.PositionAngle;
import org.orekit.propagation.PropagationType;
import org.orekit.propagation.SpacecraftState;
import org.orekit.propagation.events.EventDetector;
import org.orekit.propagation.sampling.OrekitFixedStepHandler;
import org.orekit.propagation.semianalytical.dsst.DSSTPropagator;
import org.orekit.time.AbsoluteDate;
import org.orekit.time.TimeScalesFactory;
import org.orekit.utils.Constants;
import org.orekit.utils.IERSConventions;


import org.orekit.propagation.semianalytical.dsst.forces.DSSTAtmosphericDrag;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTSolarRadiationPressure;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTTesseral;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTZonal;
import org.orekit.propagation.events.AltitudeDetector;
import org.orekit.models.earth.atmosphere.data.MarshallSolarActivityFutureEstimation;
import org.orekit.models.earth.atmosphere.NRLMSISE00;
import org.orekit.bodies.GeodeticPoint;
import org.orekit.utils.PVCoordinates;

import quickTest.PathCreator.AppFrame;

import org.orekit.frames.Transform;
import org.hipparchus.geometry.euclidean.threed.Vector3D;

import gov.nasa.worldwind.WorldWind;
import gov.nasa.worldwindx.examples.ApplicationTemplate;



public class DSSTPropagationMux {
	
	/** Private constructor for utility class. */
    private DSSTPropagationMux() {
        // empty
    }
    static ArrayList<KeplerianOrbit> orbitList = new ArrayList<>();
    
    static ArrayList<GeodeticPoint> listOfStates = new ArrayList<GeodeticPoint>();
    
    static OneAxisEllipsoid earth;
    
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
         final double ecc = 2.e-2; // eccentricity
         final double i = 97.4009688*Math.PI/180; // inclination
         final double omega =Math.PI/2; // perigee argument
         final double raan = 0; // right ascention of ascending node
         final double lM = 0; // mean anomaly
         final Orbit initialOrbit = new KeplerianOrbit(a, ecc, i, omega, raan, lM, PositionAngle.MEAN,
                       inertialFrame, initialDate, mu);

        final double fixedStepSize = 2*Math.PI*Math.sqrt((a*a*a)/mu);
        final int datastep = 1; // Interval between recorded data points on output file
 		final int duration = 160000*86400;// in seconds
        final double  mass= 2.66;
        final AbsoluteDate start = initialOrbit.getDate();

         final double rotationRate = Constants.WGS84_EARTH_ANGULAR_VELOCITY;
         
         
         
         // Defining the Propagator
         final AbstractIntegrator integrator = new ClassicalRungeKuttaIntegrator(fixedStepSize);
         
         final PropagationType outputType = PropagationType.MEAN; 
         
         final  DSSTPropagator propagator = new DSSTPropagator(integrator, outputType);
         propagator.setInitialState(new SpacecraftState(initialOrbit, mass), PropagationType.MEAN);
         
       //Models
         final IERSConventions conventions = IERSConventions.IERS_2010;
         final Frame earthFrame = FramesFactory.getITRF(conventions, false);
         earth = new OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                 Constants.WGS84_EARTH_FLATTENING,
                 earthFrame);
         
         
         // Gravity Field Force Model
         
         
         final int ZonalMaxDegree = 15;
         final int ZonalMaxOrder = 15;
         final UnnormalizedSphericalHarmonicsProvider unnormalized =
                 GravityFieldFactory.getConstantUnnormalizedProvider(ZonalMaxDegree,  ZonalMaxOrder);
         propagator.addForceModel(new DSSTZonal(unnormalized));
         propagator.addForceModel(new DSSTTesseral(earthFrame, rotationRate, unnormalized));
         
         
         // Atmosphere
         //final HarrisPriester atmos = new HarrisPriester(sun,earth);
         
         final MarshallSolarActivityFutureEstimation parameters = new MarshallSolarActivityFutureEstimation(MarshallSolarActivityFutureEstimation.DEFAULT_SUPPORTED_NAMES, MarshallSolarActivityFutureEstimation.StrengthLevel.AVERAGE);
         final NRLMSISE00 atmos = new NRLMSISE00(parameters, sun, earth);
         
         // Drag
         double crossArea = 0.025;
         double Cd = 2.2;
         DragSensitive ssc = new IsotropicDrag(crossArea, Cd);
         propagator.addForceModel(new DSSTAtmosphericDrag(atmos, ssc, mu));
        
         // Solar Radiation Pressure
         double cR = 1.8;
         double srpArea = 0.025;
         final RadiationSensitive ssrc = new IsotropicRadiationSingleCoefficient(srpArea, cR);
         propagator.addForceModel(new DSSTSolarRadiationPressure(sun, RE, ssrc, mu));
         
         
         // Stopping when altitude too low
         
         final double MinAlt = 140000;
         final EventDetector LowAlt = new AltitudeDetector(MinAlt, earth);
         propagator.addEventDetector(LowAlt);
         
         //Propagation
         
         propagator.getMultiplexer().add(8600, new TestStepHandler());
         
         final double dsstOn = System.currentTimeMillis();
         propagator.propagate(start, start.shiftedBy(duration));
         final double dsstOff = System.currentTimeMillis();
         System.out.println("DSST execution time (without large file write) : " + (dsstOff - dsstOn) / 1000.);
         

         //Writing the results to a text file         
         new WriteToFile("output/DSSTPropagation.txt",datastep);
         
         BasicPlot plotter = new BasicPlot(); //creating plotter class
         List<AbsoluteDate> DateList = orbitList.stream().map(KeplerianOrbit::getDate).collect(Collectors.toList());
         
         List<Double> TimeList =  new ArrayList<>();
         
         for (AbsoluteDate D : DateList) {
          	TimeList.add(D.durationFrom(initialDate)/(24*3600));
          }
         
         List<Double> AList = orbitList.stream().map(KeplerianOrbit::getA).collect(Collectors.toList());
         plotter.plot(TimeList, AList, "Semi Major Axis" ,"DSSTA", "Semi-Analytical");	

         ArrayList<Double> AltList = new ArrayList<>();
         for (double r : AList) {
         	AltList.add(r-RE);
         }
         plotter.plot(TimeList, AltList, "Altitude" ,"DSSTAlt", "Semi-Analytical");	
         
         List<Double> EList = orbitList.stream().map(KeplerianOrbit::getE).collect(Collectors.toList()); //Eccentricity
         plotter.plot(TimeList, EList, "Eccentricity" ,"DSSTE", "Semi-Analytical");	
         
         List<Double> IList = orbitList.stream().map(KeplerianOrbit::getI).collect(Collectors.toList()); //Inclination
         plotter.plot(TimeList, IList, "Inclination" ,"DSSTI", "Semi-Analytical");	

         List<Double> APList = orbitList.stream().map(KeplerianOrbit::getPerigeeArgument).collect(Collectors.toList());
         plotter.plot(TimeList, APList, "Argument of the Perigee" ,"DSSTAP", "Semi-Analytical");	

         List<Double> RaanList = orbitList.stream().map(KeplerianOrbit::getRightAscensionOfAscendingNode).collect(Collectors.toList());
         plotter.plot(TimeList, RaanList, "Right Ascension of Ascending Node" ,"DSSTRaan", "Semi-Analytical");				
         
         System.out.println("Successfully wrote to the file.");
      
         //new PathCreator(listOfStates);
         //System.setProperty("http.proxyHost", "proxy.isae.fr");
         //System.setProperty("http.proxyPort", "3128");
         //WorldWind.setOfflineMode(true);
         //ApplicationTemplate.start("WorldWind Paths", AppFrame.class);
         
}catch (OrekitException oe) {
    System.err.println(oe.getLocalizedMessage());
}
}	 

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
        
       /* // compute sub-satellite track
        AbsoluteDate  date    = currentState.getDate();
        PVCoordinates pvInert = currentState.getPVCoordinates();
        Transform t;
			t = currentState.getFrame().getTransformTo(earth.getBodyFrame(), date);
            Vector3D p = t.transformPosition(pvInert.getPosition());
            GeodeticPoint center = earth.transform(p, earth.getBodyFrame(), date);
            listOfStates.add(center); */
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
   						 + String.valueOf(o.getA()) + ";"
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
	 




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
import org.orekit.forces.gravity.potential.NormalizedSphericalHarmonicsProvider;
import org.orekit.forces.gravity.potential.UnnormalizedSphericalHarmonicsProvider;
import org.orekit.forces.radiation.IsotropicRadiationSingleCoefficient;
import org.orekit.forces.radiation.RadiationSensitive;
import org.orekit.frames.Frame;
import org.orekit.frames.FramesFactory;
import org.orekit.models.earth.atmosphere.HarrisPriester;
import org.orekit.orbits.KeplerianOrbit;
import org.orekit.orbits.Orbit;
import org.orekit.orbits.PositionAngle;
import org.orekit.propagation.BoundedPropagator;
import org.orekit.propagation.EphemerisGenerator;
import org.orekit.propagation.PropagationType;
import org.orekit.propagation.SpacecraftState;
import org.orekit.propagation.semianalytical.dsst.DSSTPropagator;
import org.orekit.time.AbsoluteDate;
import org.orekit.time.TimeScale;
import org.orekit.time.TimeScalesFactory;
import org.orekit.utils.Constants;
import org.orekit.utils.IERSConventions;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTAtmosphericDrag;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTSolarRadiationPressure;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTTesseral;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTThirdBody;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTZonal;


public class DSSTPropagation {
	
	/** Private constructor for utility class. */
    private DSSTPropagation() {
        // empty
    }
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
         final AbsoluteDate initialDate = new AbsoluteDate(2024,07,02,12,0,0,TimeScalesFactory.getUTC());

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
        final int datastep = 100; // Interval between recorded data points on output file
 		final int duration = 500*86400;// in seconds
        final double  mass= 2.66;
        final AbsoluteDate start = initialOrbit.getDate();
        int output_step = 8600; 
        
         // All dates in UTC
         final TimeScale utc = TimeScalesFactory.getUTC();

         final double rotationRate = Constants.WGS84_EARTH_ANGULAR_VELOCITY;
         
         
         // Defining the Propagator
         final AbstractIntegrator integrator = new ClassicalRungeKuttaIntegrator(fixedStepSize);
         
         final PropagationType outputType = PropagationType.MEAN; 
         
         final  DSSTPropagator propagator = new DSSTPropagator(integrator, outputType);
         propagator.setInitialState(new SpacecraftState(initialOrbit, mass), PropagationType.MEAN);
         
       //Models
         final IERSConventions conventions = IERSConventions.IERS_2010;
         final Frame earthFrame = FramesFactory.getITRF(conventions, false);
         final OneAxisEllipsoid earth = new OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
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
         final HarrisPriester atmos = new HarrisPriester(sun,earth);
         
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
         
         
         //Propagation
         final EphemerisGenerator dsstGenerator = propagator.getEphemerisGenerator();
         final double dsstOn = System.currentTimeMillis();
         propagator.propagate(start, start.shiftedBy(duration));
         final double dsstOff = System.currentTimeMillis();
         System.out.println("DSST execution time (without large file write) : " + (dsstOff - dsstOn) / 1000.);
         final BoundedPropagator ephemeris = dsstGenerator.getGeneratedEphemeris();
         
         System.out.format("%nEphemeris defined from %s to %s%n", ephemeris.getMinDate(), ephemeris.getMaxDate());
         
         //Initialization of list of orbit ephemeris 
         ArrayList<KeplerianOrbit> orbitList = new ArrayList<>();
        
         double interArgPer  = 0;
         List<Double> ArgPerList = new ArrayList<>();
         //Writing the results to a text file
         try {
         	
             FileWriter myWriter = new FileWriter("output/DSSTPropagation.txt");
             //Writing Header
             myWriter.write(" Semi-Major Axis ; Eccentricity ; Inclination ; Argument of the perigee ; Right Ascension of the Ascending node\n");
             
             //Get values from ephemeris
         for (int k = 0; k < duration/output_step; k= k + 1)	{
         	AbsoluteDate intermediateDate = initialDate.shiftedBy(output_step*i);
             SpacecraftState intermediateState = ephemeris.propagate(intermediateDate);
             orbitList.add(new KeplerianOrbit(intermediateState.getOrbit()));
             
             //Normalize Argument of the Perigee
             if (orbitList.get(k).getRightAscensionOfAscendingNode() < - 2*Math.PI) {
             	interArgPer = orbitList.get(k).getRightAscensionOfAscendingNode() + 2*Math.PI;
             }
             else if (orbitList.get(k).getRightAscensionOfAscendingNode() > 2*Math.PI) {
             	interArgPer = orbitList.get(k).getRightAscensionOfAscendingNode() - 2*Math.PI;
             }
             else {
             	interArgPer = orbitList.get(k).getRightAscensionOfAscendingNode();
             }
             ArgPerList.add(interArgPer);
             //Print to File
             System.out.println(orbitList.get(k).getA()); 
             myWriter.write(String.valueOf(orbitList.get(k).getA()) + ";" + String.valueOf(orbitList.get(k).getE()) + ";" + String.valueOf(orbitList.get(k).getI()) + ";" + String.valueOf(interArgPer) + ";" + String.valueOf(orbitList.get(k).getRightAscensionOfAscendingNode()) + "\n");
         }
         myWriter.close();
         }
         catch (IOException e) {
             System.out.println("An error occurred.");
             e.printStackTrace();
           }
         BasicPlot plotter = new BasicPlot(); //creating plotter class
         
         List<Double> AList = orbitList.stream().map(KeplerianOrbit::getA).collect(Collectors.toList()); //Semi-major Axis
       //  plotter.plot(AList, "Semi Major Axis" ,"DSSTA");	
         
         List<Double> EList = orbitList.stream().map(KeplerianOrbit::getE).collect(Collectors.toList()); //Eccentricity
        // plotter.plot(EList, "Eccentricity" ,"DSSTE");	
         
         List<Double> IList = orbitList.stream().map(KeplerianOrbit::getI).collect(Collectors.toList()); //Inclination
        // plotter.plot(IList, "Inclination" ,"DSSTI");	
         
        // plotter.plot(ArgPerList, "Argument of the Perigee" ,"DSSTAP"); //Argument of the Perigee

         List<Double> RaanList = orbitList.stream().map(KeplerianOrbit::getRightAscensionOfAscendingNode).collect(Collectors.toList()); //Rigth Ascension of the Ascending Node
         //plotter.plot(RaanList, "Right Ascension of Ascending Node" ,"DSSTRaan");						
         
         System.out.println("Successfully wrote to the file.");
      
         
         
}catch (OrekitException oe) {
    System.err.println(oe.getLocalizedMessage());
}
}
}



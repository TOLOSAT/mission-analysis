package quickTest;




import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

import org.orekit.data.DataContext;
import org.orekit.data.DataProvidersManager;
import org.orekit.data.DirectoryCrawler;
import org.orekit.errors.OrekitException;
import org.orekit.frames.FramesFactory;
import org.orekit.orbits.KeplerianOrbit;
import org.orekit.orbits.Orbit;
import org.orekit.orbits.PositionAngle;
import org.orekit.propagation.BoundedPropagator;
import org.orekit.propagation.EphemerisGenerator;
import org.orekit.propagation.SpacecraftState;
import org.orekit.propagation.analytical.EcksteinHechlerPropagator;
import org.orekit.time.AbsoluteDate;
import org.orekit.time.TimeScalesFactory;
import org.orekit.utils.Constants;


public class QuickTestClass{
    
	static AbsoluteDate initialDate = new AbsoluteDate();

	public static void main(String[] args) {
		
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
        
        
        initialDate = new AbsoluteDate(2024,07,02,12,0,0, TimeScalesFactory.getUTC());
        final double RE = Constants.EIGEN5C_EARTH_EQUATORIAL_RADIUS;
        double 	sma = 6878.e3;   //sma = 6903.1363e3
	 	double	ecc = 2.e-2; //0.02535084
	 	
		double	inc = 94*Math.PI/180;//CL_op_ssoJ2("i", sma, ecc);
		double	pom = Math.PI/2;
	    double	gom = 1;//CL_op_locTime(cjd0, "mlh", mlh, "ra")
		double	anm = 0;
		
		//Orbit Initialization
		Orbit initialOrbit = new KeplerianOrbit(sma,ecc,inc,pom,gom,anm,PositionAngle.MEAN, FramesFactory.getEME2000(), initialDate,
                Constants.EIGEN5C_EARTH_MU);
		
		int time_step = 8600; // in seconds
		int duration =  500*86400;// in seconds
		
		//State Initialization
		
		//Propagator definition as an Eckstein-Heckler Propagator 
		final EcksteinHechlerPropagator propagator = new EcksteinHechlerPropagator(initialOrbit,
                Constants.EIGEN5C_EARTH_EQUATORIAL_RADIUS,
                Constants.EIGEN5C_EARTH_MU, Constants.EIGEN5C_EARTH_C20,
                Constants.EIGEN5C_EARTH_C30, Constants.EIGEN5C_EARTH_C40,
                Constants.EIGEN5C_EARTH_C50, Constants.EIGEN5C_EARTH_C60);
		
		//Definition of an Ephemeris Generator, to get the intermediate results of the propagation
		final EphemerisGenerator generator = propagator.getEphemerisGenerator();
	

        // Propagation with storage of the results in an integrated ephemeris
	
		
        //Create Ephemeris
        final BoundedPropagator ephemeris = generator.getGeneratedEphemeris();
        
        System.out.format("%nEphemeris defined from %s to %s%n", ephemeris.getMinDate(), ephemeris.getMaxDate());
        
        //Initialization of list of orbit ephemeris 
        ArrayList<KeplerianOrbit> orbitList = new ArrayList<>();
       
        double interArgPer  = 0;
        List<Double> ArgPerList = new ArrayList<>();
        //Writing the results to a text file
        try {
        	
            FileWriter myWriter = new FileWriter("output/testfile.txt");
            //Writing Header
            myWriter.write("Time ; Semi-Major Axis ; Eccentricity ; Inclination ; Argument of the perigee ; Right Ascension of the Ascending node\n");
            
            //Get values from ephemeris
        for (int i = 0; i < duration/time_step; i= i + 1)	{
        	AbsoluteDate intermediateDate = initialDate.shiftedBy(time_step*i);
            SpacecraftState intermediateState = ephemeris.propagate(intermediateDate);
            orbitList.add(new KeplerianOrbit(intermediateState.getOrbit()));
            
            //Normalize Argument of the Perigee
            if (orbitList.get(i).getRightAscensionOfAscendingNode() < - 2*Math.PI) {
            	interArgPer = orbitList.get(i).getRightAscensionOfAscendingNode() + 2*Math.PI;
            }
            else if (orbitList.get(i).getRightAscensionOfAscendingNode() > 2*Math.PI) {
            	interArgPer = orbitList.get(i).getRightAscensionOfAscendingNode() - 2*Math.PI;
            }
            else {
            	interArgPer = orbitList.get(i).getRightAscensionOfAscendingNode();
            }
            ArgPerList.add(interArgPer);
            //Print to File
            System.out.println(orbitList.get(i).getA()); 
            myWriter.write(String.valueOf(orbitList.get(i).getDate().durationFrom(initialDate)) + ";" + String.valueOf(orbitList.get(i).getA()) + ";" + String.valueOf(orbitList.get(i).getE()) + ";" + String.valueOf(orbitList.get(i).getI()) + ";" + String.valueOf(interArgPer) + ";" + String.valueOf(orbitList.get(i).getRightAscensionOfAscendingNode()) + "\n");
        }
        myWriter.close();
        }
        catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
          }
        BasicPlot plotter = new BasicPlot(); //creating plotter class
        List<AbsoluteDate> DateList = orbitList.stream().map(KeplerianOrbit::getDate).collect(Collectors.toList());
        
        List<Double> TimeList =  new ArrayList<>();
        
        for (AbsoluteDate D : DateList) {
         	TimeList.add(D.durationFrom(initialDate)/(24*3600));
         }
        
        List<Double> AList = orbitList.stream().map(KeplerianOrbit::getA).collect(Collectors.toList()); //Semi-major Axis
        plotter.plot(TimeList, AList, "Semi Major Axis" ,"AnalyticalA", "Analytical");	
        
        ArrayList<Double> AltList = new ArrayList<>();
        for (double r : AList) {
        	AltList.add(r-RE);
        }
        plotter.plot(TimeList, AltList, "Altitude" ,"AnalyticalAlt", "Analytical");
        
        List<Double> EList = orbitList.stream().map(KeplerianOrbit::getE).collect(Collectors.toList()); //Eccentricity
        plotter.plot(TimeList, EList, "Eccentricity" ,"AnalyticalE", "Analytical");	
        
        List<Double> IList = orbitList.stream().map(KeplerianOrbit::getI).collect(Collectors.toList()); //Inclination
        plotter.plot(TimeList, IList, "Inclination" ,"AnalyticalI", "Analytical");	
        
        plotter.plot(TimeList, ArgPerList, "Argument of the Perigee" ,"AnalyticalAP", "Analytical"); //Argument of the Perigee

        List<Double> RaanList = orbitList.stream().map(KeplerianOrbit::getRightAscensionOfAscendingNode).collect(Collectors.toList()); //Rigth Ascension of the Ascending Node
        plotter.plot(TimeList, RaanList, "Right Ascension of Ascending Node" ,"AnalyticalRaan", "Analytical");						
        
        System.out.println("Successfully wrote to the file.");
     
		}
		
		catch (OrekitException oe) {
            System.err.println(oe.getLocalizedMessage());
        }

		    
	}
}
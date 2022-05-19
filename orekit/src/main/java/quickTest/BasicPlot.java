package quickTest;

import java.awt.Color;
import java.io.IOException;
import java.util.List;

/**
 * Simple plot generator from a list of Doubles, using Yuriy Guskov's simple-java-plot
 */

public class BasicPlot {
	 BasicPlot(){
	 }
	 
	 public void plot(List<Double> yList, String plotName, String fileName, String seriesName) {
		 
		Plot.Data data = Plot.data();
        int i=0;
        for (double y:yList) {
        	data.xy(i, y);
        	i++;
        }
        
        Plot plot = Plot.plot(Plot.plotOpts().
        		title(plotName).
        		legend(Plot.LegendFormat.BOTTOM)).
        	xAxis("x", Plot.axisOpts()).
        	yAxis("y", Plot.axisOpts()).
        	series(seriesName, data,
        	Plot.seriesOpts().
        			color(Color.BLACK));
        try {
        	plot.save("plots/" + fileName, "png");
        }
        catch (IOException e){
                System.out.println("An error occurred.");
                e.printStackTrace();
              }
        System.out.println("Successfully created plot " + fileName);
	}
	 
	 public void plot(List<Double> xList, List<Double> yList, String plotName, String fileName, String seriesName) {
		 
			Plot.Data data = Plot.data();
	        int i=0;
	        for (double y:yList) {
	        	data.xy(xList.get(i), y);
	        	i++;
	        }
	        
	        Plot plot = Plot.plot(Plot.plotOpts().
	        		title(plotName).
	        		legend(Plot.LegendFormat.BOTTOM)).
	        	xAxis("x", Plot.axisOpts()).
	        	yAxis("y", Plot.axisOpts()).
	        	series(seriesName, data,
	        		Plot.seriesOpts().
	        			color(Color.BLACK));
	        try {
	        	plot.save("plots/" + fileName, "png");
	        }
	        catch (IOException e){
	                System.out.println("An error occurred.");
	                e.printStackTrace();
	              }
	        System.out.println("Successfully created plot " + fileName);
		}
	 
}

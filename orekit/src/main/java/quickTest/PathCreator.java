package quickTest;


import gov.nasa.worldwind.WorldWind;

import gov.nasa.worldwind.avlist.AVKey;
//import gov.nasa.worldwind.geom.LatLon;
import gov.nasa.worldwind.geom.Position;
import gov.nasa.worldwind.layers.*;
import gov.nasa.worldwind.render.*;
import gov.nasa.worldwind.render.markers.*;
import gov.nasa.worldwind.util.*;
import gov.nasa.worldwindx.examples.ApplicationTemplate;
import gov.nasa.worldwind.WorldWindow;
import gov.nasa.worldwind.View;
import gov.nasa.worldwind.view.BasicView;
import gov.nasa.worldwind.view.orbit.BasicOrbitView;
import org.orekit.bodies.GeodeticPoint;
import org.orekit.utils.PVCoordinates;
import org.orekit.frames.Transform;
import org.hipparchus.geometry.euclidean.threed.Vector3D;

import java.awt.Color;

import java.util.*;


//import fr.cnes.sirius.patrius.math.util.FastMath;

public class PathCreator extends ApplicationTemplate{
	
	static ArrayList<GeodeticPoint> listOfStates;
	static double HandleFreq;
	
	public PathCreator(ArrayList<GeodeticPoint> stateList) {
		PathCreator.listOfStates = stateList;
	}
	
	public static class AppFrame extends ApplicationTemplate.AppFrame {

        /**
		 * 
		 */
		private static final long serialVersionUID = 1L;

		public AppFrame() {
            super(true, true, false);
            
           
         	
            RenderableLayer layer = new RenderableLayer();

            // Create and set an attribute bundle.
            ShapeAttributes attrs = new BasicShapeAttributes();
            attrs.setOutlineMaterial(new Material(Color.YELLOW));
            attrs.setOutlineWidth(2d);
            
            // Create a path, set some of its properties and set its attributes.
            ArrayList<Position> pathPositions = new ArrayList<>();
            for (GeodeticPoint point : listOfStates) {
            	 pathPositions.add(Position.fromRadians(point.getLatitude(),point.getLongitude(),point.getAltitude()));
            }
          
            Path path = new Path(pathPositions);
            path.setAltitudeMode(WorldWind.ABSOLUTE);
            path.setExtrude(false);
            path.setVisible(true);
            path.setPathType(AVKey.LINEAR);
            path.setAttributes(attrs);

            layer.addRenderable(path);
            
            // Add the layer to the model.
            insertBeforeCompass(getWwd(), layer);
           
            WorldWindow wwd = getWwd();
           // BasicOrbitView view = (BasicOrbitView)wwd.getView();
            
            CustomView cView = new CustomView();
           // cView.setValues(view);
            cView.setFarClipDistance(1000000000);
            cView.setNearClipDistance(1000);
            wwd.setView((View)cView);
           // List<Marker> markers = new ArrayList<>(1);
           // markers.add(new BasicMarker(Position.fromDegrees(90, 0), new BasicMarkerAttributes()));
           // MarkerLayer markerLayer = new MarkerLayer();
           // markerLayer.setMarkers(markers);
           // insertBeforeCompass(getWwd(), markerLayer);
        }
    }

}



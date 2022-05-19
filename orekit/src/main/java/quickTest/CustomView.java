package quickTest;

import gov.nasa.worldwind.view.orbit.BasicOrbitView;


public class CustomView  extends BasicOrbitView {

	private double nearClipDistanceVal;
	private double farClipDistanceVal;
	
	
	/**
	 * Constructor
	 */
	public CustomView() {
		super();
	}
	
	public void setFarClipDistance(double farClip) {
		this.farClipDistanceVal = farClip;
		//this.farClipDistance = farClip;
	}
	
	public void setNearClipDistance(double nearClip) {
		this.nearClipDistanceVal = nearClip;
		//this.nearClipDistance = nearClip;
	}

	@Override
	protected double computeNearClipDistance() {
		return nearClipDistanceVal;
	}
	
	@Override
	protected double computeFarClipDistance() {
		return farClipDistanceVal;
	}
}

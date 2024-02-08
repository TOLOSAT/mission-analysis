# Useful functions

## Eclipses
- [`compute_shadow_vector`](eclipses.py) Compute the shadow vector of the spacecraft at each epoch.  
  **Parameters**:  
  - **satellite_position** : _ndarray_  
        Array of satellite positions in ECI frame
  - **sun_position** : _ndarray_  
        Array of sun positions in ECI frame
  - **sun_radius** : _float_  
        Sun radius in meters
  - **earth_radius** : _float_  
        Earth radius in meters 
  
  **Returns**:
  - **visibility_vector**: _np.ndarray_  
    Returns a vector with the value of the shadow function at each epoch:  
    - 0 if the satellite is in umbra
    - 1 if the satellite is fully sunlit  
    - a value between 0 and 1 if the satellite is in penumbra  
- [`compute_ecplipses`](eclipses.py) Compute the eclipses of the spacecraft from a given ground station and organise it 
  into a data frame, following the steps found at [link](https://joshdevlin.com/blog/calculate-streaks-in-pandas/).  
  **Parameters**:  
  - **satellite_position** : _ndarray_  
        Array of satellite positions in ECI frame
  - **sun_position** : _ndarray_  
        Array of sun positions in ECI frame
  - **sun_radius** : _float_  
        Sun radius in meters
  - **earth_radius** : _float_  
        Earth radius in meters 
  - **epochs** : _np.ndarray_  
        Array of epochs in seconds since J2000  
  - **eclipse_type** : _string_  
        Type of eclipse to compute. Can be 'Umbra' or 'Penumbra'. optional, default is 'Umbra'.
 
  **Returns**:
  - **shadow_df**: _pd.DataFrame_  
    Returns a data frame containing the following information about the eclipses
    - 'start' : start date of the eclipse
    - 'end' : end date of the eclipse
    - 'start_epoch' : start epoch of the eclipse in seconds since J2000
    - 'end_epoch' : end epoch of the eclipse in seconds since J2000
    - 'duration' : duration of the eclipse in datetime format
    - 'duration_epoch' : duration of the eclipse in seconds
    - 'partial' : True if it is a partial eclipse, False if not

## Communication windows
- [`compute_communication_vector`](communication_windows.py) Compute the visibility vector of the spacecraft from a 
  given ground station.  
  **Parameters**:  
  - **pos_ecf** : _np.ndarray_  
    Array of satellite positions in ECEF frame 
  - **groundstation_name** : _string_  
    Name of a csv file containing the longitude, latitude, altitude, and minimum elevation of the groundstation.
  
  **Returns**:
  - **visibility_vector**: _np.ndarray_  
    Returns an array of booleans indicating whether the spacecraft is visible or not at each epoch.
- [`compute_communication_windows`](communication_windows.py) Compute the communication windows of the spacecraft 
  from a given ground station and organise it into a data frame, following the steps found at this 
  [link](https://joshdevlin.com/blog/calculate-streaks-in-pandas/).  
  **Parameters**:  
  - **pos_ecf** : _np.ndarray_  
    Array of satellite positions in ECEF frame 
  - **groundstation_name** : _string_  
    Name of a csv file containing the longitude, latitude, altitude, and minimum elevation of the groundstation. 
  - **epochs** : _np.ndarray_  
    Array of epochs in seconds since J2000  
 
  **Returns**:
  - **visibility_df**: _pd.DataFrame_  
    Returns a data frame containing the following information about the communication windows:
    - 'start' : start date of the communication window
    - 'end' : end date of the communication window
    - 'start_epoch' : start epoch of the communication window in seconds since J2000
    - 'end_epoch' : end epoch of the communication window in seconds since J2000
    - 'duration' : duration of the communication window in seconds
    - 'partial' : True if it is a partial communication window, False if not

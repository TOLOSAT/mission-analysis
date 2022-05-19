// output is a list of form [longitude_rad, latitude_rad, altitude_m; ...]
function pos = import_station_positions(filename)
    M = csvRead(filename, ',', '.')
    
    lons = M(:,2)
    lats = M(:,3)
    alts = M(:,4)
    
    pos = []
    for k = 2:size(M)(1)
        newpos = [lons(k)*%CL_deg2rad,lats(k)*%CL_deg2rad,alts(k)];
        pos = [pos; newpos];
    end
    
endfunction

stations_list = import_station_positions('ground-stations-GPS-extended.csv')

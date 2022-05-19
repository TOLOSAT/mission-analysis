// output is a list of form [longitude_rad, latitude_rad, altitude_m, min_elevation_deg; ...]
function [pos, names] = import_stations(filename)
    // TODO : if possible, create a function similar to this that calls the api directly
    M = csvRead(filename, ',', '.')
    M1 = csvRead(filename,',', [], 'string')
    
    nms = M1(:,1)
    lons = M(:,2)
    lats = M(:,3)
    alts = M(:,4)
    min_els = M(:,5)
    names = list();
    
    pos = []
    for k = 2:size(M)(1)
        if M(k,6) == 1 then
            newpos = [lons(k)*%CL_deg2rad,lats(k)*%CL_deg2rad,alts(k),min_els(k)];
            pos = [pos; newpos];
            names(length(names)+1) = nms(k);
        end
    end
    
endfunction

[stations_list, station_names] = import_stations('ground-stations-GPS-extended.csv')

// on veut une liste, pour chaque GS, de debut et fins de visibilite (ou debut et duree)
function [vizi_start_dates_days, vizi_end_dates_days, vizi_durations_secs, vizi_station_names] = pass_list(kep_mean_orbit, cjd_start_date, duration_days, time_step_days, stations_list, station_names, min_duration_secs)
    cjd = cjd_start_date + (0:time_step_days:duration_days); // list of computation dates
    t0 = cjd_start_date;
    
    // propagate and project onto earth
    kep_ana = CL_ex_propagate("j2sec","kep", t0,kep_mean_orbit,cjd,"m");
    pos_sat= CL_oe_kep2car(kep_ana);
    pos_sat_terre=CL_fr_convert("ECI","ECF",t0, pos_sat );
    
    // stats for each GS 
    vizi_start_dates_days = [];
    vizi_end_dates_days = [];
    vizi_durations_secs = [];
    vizi_station_names = list();
    for n = 1:size(stations_list)(1)
        gs_position = stations_list(n, 1:3);
        min_elevation = stations_list(n, 4);
        interv = CL_ev_stationVisibility(cjd,pos_sat_terre,gs_position',min_elevation*%CL_deg2rad); // expects lon lat alt in geodetic
        startdates_days = interv(1,:);
        enddates_days = interv(2, :);
        durations_secs = (enddates_days-startdates_days)*24*3600;
        // TODO : if possible sort all the vectors by start date instead of by station number
        vizi_start_dates_days = [vizi_start_dates_days, startdates_days];
        vizi_end_dates_days = [vizi_end_dates_days, enddates_days];
        vizi_durations_secs = [vizi_durations_secs, durations_secs];
        for i = 1:length(durations_secs)
            vizi_station_names(length(vizi_station_names)) = station_names(n)
        end
    end
endfunction

// define a polar orbit

sma = 6878.e3   //sma
ecc = 2.e-3 //0.0253508
inc = 97.4*%CL_deg2rad
pom = 1.570796327;
mlh = 6; // MLTAN (hours)
gom = 3.3392258;
anm = 0;
kep_mean_ini = [  sma;     // demi grand axe (m)
                  ecc;     // excentricité
                  inc;     // inclinaison (rad)
                  pom;     // argument du périastre, petit omega (rad)
                  gom;     // longitude du noeud ascendant raan (rad)  
                  anm]
                 

// initialize dates, times
cjd0 = CL_dat_cal2cjd(2024,01,02,12,0,0); // convertion in CNES Julian date (1950.0)
time_step =10/86400; // in second
duration =24/24; // in days
min_pass_duration = 300; // in secs

[vizi_start_dates_days, vizi_end_dates_days, vizi_durations_secs, vizi_station_names] = pass_list(kep_mean_ini, cjd0, duration, time_step, stations_list, station_names, min_pass_duration)

// returns the station with the most passes (given the input constraints) and vectors for thr starts, ends and durations of passes at that station. 
function [best_station, start_dates_days, end_dates_days, durations_secs] = best_stations(kep_mean_orbit, cjd_start_date, duration_days, time_step_days, stations_list, station_names, min_duration_secs)
    cjd = cjd_start_date + (0:time_step_days:duration_days); // list of computation dates
    t0 = cjd_start_date;
    
    // propagate and project onto earth
    kep_ana = CL_ex_propagate("j2sec","kep", t0,kep_mean_orbit,cjd,"m");
    pos_sat= CL_oe_kep2car(kep_ana);
    pos_sat_terre=CL_fr_convert("ECI","ECF",t0, pos_sat );
    
    // stats for each GS 
    best_station = station_names(1);
    start_dates_days = [];
    end_dates_days = [];
    durations_secs = [];
    best_num_passes = 0;
    for n = 1:size(stations_list)(1)
        gs_position = stations_list(n, 1:3);
        min_elevation = stations_list(n, 4);
        interv = CL_ev_stationVisibility(cjd,pos_sat_terre,gs_position',min_elevation*%CL_deg2rad); // expects lon lat alt in geodetic
        startdates_days = interv(1,:);
        enddates_days = interv(2, :);
        if length(startdates_days) > best_num_passes then
            best_station = station_names(n);
            start_dates_days = startdates_days;
            end_dates_days = enddates_days;
            durations_secs = (enddates_days-startdates_days)*24*3600;
            best_num_passes = length(startdates_days);
        end
    end
endfunction

[best_station, start_dates_days, end_dates_days, durations_secs] = best_stations(kep_mean_ini, cjd0, 3/24, time_step, stations_list, station_names, min_pass_duration)

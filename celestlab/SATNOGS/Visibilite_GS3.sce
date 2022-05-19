// --------- Section 1 ---------
// import ground stations list from csv file 
// using import_stations
// -----------------------------

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

printf('stations imported ! number found : %i\n', length(station_names))

// --------- Section 2 ---------
// define function to get list of passes for an 
// orbit and timeframe, define satellite orbit, 
// call function
// -----------------------------

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

printf('Passes calculated ! Total number of passes : %i\n', length(vizi_start_dates_days))


// --------- Section 3 ---------
// define function to get top N best stations 
// (based on single pass duration)
// and calls it to get top 5 during the time $
// interval defined before
// -----------------------------

// returns the station with the most passes (given the input constraints) and vectors for thr starts, ends and durations of passes at that station. 
function [best_stations, start_dates_days, end_dates_days, durations_secs] = n_best_stations(N, kep_mean_orbit, cjd_start_date, duration_days, time_step_days, stations_list, station_names, min_duration_secs)
    cjd = cjd_start_date + (0:time_step_days:duration_days); // list of computation dates
    t0 = cjd_start_date;
    
    // propagate and project onto earth
    kep_ana = CL_ex_propagate("j2sec","kep", t0,kep_mean_orbit,cjd,"m");
    pos_sat= CL_oe_kep2car(kep_ana);
    pos_sat_terre=CL_fr_convert("ECI","ECF",t0, pos_sat );
    
    // prepare data for top N ground stations
    best_stations = ['N/A'];
    start_dates_days = [0];
    end_dates_days = [0];
    durations_secs = [0];
    // best_pass_durations = [0];
    for k = 2:N
        best_stations = [best_stations; 'N/A'];
        start_dates_days = [start_dates_days; 0];
        end_dates_days = [end_dates_days; 0];
        durations_secs = [durations_secs; 0];
        // best_pass_durations = [best_pass_durations; 0];
    end
    
    printf('\n studying station : ')
    for n = 1:size(stations_list)(1) // for every ground station
        
        
        gs_position = stations_list(n, 1:3);
        min_elevation = stations_list(n, 4);
        interv = CL_ev_stationVisibility(cjd,pos_sat_terre,gs_position',min_elevation*%CL_deg2rad); // expects lon lat alt in geodetic
        startdates_days = interv(1,:);
        enddates_days = interv(2, :);
        durations_days = enddates_days - startdates_days;
        
        // find longest pass and its info
        if length(interv) == 0 then 
            continue
        end
        best_duration_days = durations_days(1);
        best_startdate = startdates_days(1);
        best_enddate = enddates_days(1);
        for k = 1:length(durations_days)
            if durations_days(k) < best_duration_days then
                best_duration_days = durations_days(k);
                best_startdate = startdates_days(k);
                best_enddate = enddates_days(k);
            end
        end
        
        // if we got this far, this station has more than zero passes
        printf('\n %i', n)
        // compare with number N
        best_duration_secs = best_duration_days*86400;
        if best_duration_secs > durations_secs(N) then
            best_stations(N) = station_names(n);
            start_dates_days(N) = best_startdate;
            end_dates_days(N) = best_enddate;
            durations_secs(N) = best_duration_secs;
            if N == 1 then
                continue
            end
            // find correct position
            // printf(' t > tN, comparting with t')
            correct_N = N;
            searching = 1;
            while searching then
                // printf('%i ', correct_N)
                if best_duration_secs > durations_secs(correct_N-1) then
                    correct_N = correct_N - 1;
                    if correct_N > 1 then 
                        searching = 1;
                    else
                        searching = 0;
                    end
                else
                    searching = 0;
                end
            end
            // shift others down
            // printf('\n current top N : ')
            // printf('%i ', durations_secs)
            // printf('\n my score : %i', best_duration_secs)
            // printf('\n my new rank : %i', correct_N)
            // printf('\n shifting scores down . . . ')
            for replace_N = N-1:-1:correct_N
                best_stations(replace_N+1) = best_stations(replace_N)
                start_dates_days(replace_N+1) = start_dates_days(replace_N);
                end_dates_days(replace_N+1) = end_dates_days(replace_N);
                durations_secs(replace_N+1) = durations_secs(replace_N);
            end
            // printf('\n current top N : ')
            // printf('%i ', durations_secs)
            // insert myself into correct position
            // printf('\n self-inserting at %i . . . ', correct_N)
            best_stations(correct_N) = station_names(n)
            start_dates_days(correct_N) = best_startdate;
            end_dates_days(correct_N) = best_enddate;
            durations_secs(correct_N) = best_duration_secs;
            // printf('\n current top N : ')
            // printf('%i ', durations_secs)
        end
    end
endfunction

topN = 5;
test_interval_hours = 3;

[best_stations, start_dates_days, end_dates_days, durations_secs] = n_best_stations(topN, kep_mean_ini, cjd0, test_interval_hours/24, time_step, stations_list, station_names, min_pass_duration)

printf('\n\n top %i stations in the next %f hours : \n', topN, test_interval_hours)
printf('%s ', best_stations)
printf('\n vizi durations of longest passes [s] : \n')
printf('%i ', durations_secs)
printf('\n start dates of longest passes [days] : \n')
printf('%f ', start_dates_days)
printf('\n (reference CNES date : %f days since 1950-01-01) \n', cjd0)

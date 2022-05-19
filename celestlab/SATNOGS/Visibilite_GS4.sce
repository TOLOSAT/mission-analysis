// --------- Section 1 ---------
// import ground stations list from csv file 
// using import_station_structs
// -----------------------------

// output is a list of structs representing ground stations. 
// each ground station has the attributes name, lon_rad, lat_rad, alt_m, and min_el_deg
function station_structs_list = import_station_structs(filename)
    // TODO : if possible, create a function similar to this that calls the api directly
    M = csvRead(filename, ',', '.')
    M1 = csvRead(filename,',', [], 'string')
    
    nms = M1(:,1)
    lons = M(:,2)
    lats = M(:,3)
    alts = M(:,4)
    min_els = M(:,5)
    
    station_structs_list = list()
    
    for k = 2:size(M)(1)
        if M(k,6) == 1 then
            lon_rad = lons(k)*%CL_deg2rad;
            lat_rad = lats(k)*%CL_deg2rad;
            station_structs_list($+1) = struct('name', nms(k), 'lon_rad', lon_rad, 'lat_rad', lat_rad, 'alt_m', alts(k), 'min_el_deg', min_els(k));
            
        end
    end
    
endfunction

station_structs_list = import_station_structs('C:\Users\nilsa\Documents\cubesat\ground-stations-GPS-extended.csv')

printf('stations imported ! number found : %i\n', length(station_structs_list))

// --------- Section 2 ---------
// define function to get list of passes for an 
// orbit and timeframe, define satellite orbit, 
// call function
// -----------------------------

// Output is a list of structs representing passes
// Each pass has attributes station_name, start_date_days (cjd format), end_date_days and duration_s
function passes_structs_list = generate_pass_list(kep_mean_orbit, cjd_start_date, duration_days, time_step_days, station_structs_list, min_duration_secs)

    cjd = cjd_start_date + (0:time_step_days:duration_days); // list of computation dates
    t0 = cjd_start_date;
    
    // propagate and project onto earth
    kep_ana = CL_ex_propagate("j2sec","kep", t0,kep_mean_orbit,cjd,"m");
    pos_sat= CL_oe_kep2car(kep_ana);
    pos_sat_terre=CL_fr_convert("ECI","ECF",cjd, pos_sat ); // MODIFIE 2021-04-29 : t0 -> cjd
    
    // stats for each Ground Station 
    passes_structs_list = list();
    for n = 1:length(station_structs_list)
        station_n = station_structs_list(n)
        gs_position = [station_n.lon_rad, station_n.lat_rad, station_n.alt_m];
        min_elevation = station_n.min_el_deg;
        interv = CL_ev_stationVisibility(cjd,pos_sat_terre,gs_position',min_elevation*%CL_deg2rad); // expects lon lat alt in geodetic
        startdates_days = interv(1,:);
        enddates_days = interv(2, :);
        durations_secs = (enddates_days-startdates_days)*24*3600;
        for tk = 1:length(durations_secs)
            passes_structs_list($+1) = struct('station_name', station_n.name, 'start_date_days', startdates_days(tk), 'end_date_days', enddates_days(tk), 'duration_s', durations_secs(tk))
        // TODO : if possible sort all the vectors by start date instead of by station number
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
kep_mean_ini = [sma; ecc; inc; pom; gom; anm];
// initialize dates, times
cjd0 = CL_dat_cal2cjd(2024,01,02,12,0,0); // convertion in CNES Julian date (1950.0)
time_step =10/86400; // in days
duration_days =30*24/24; // in days
min_pass_duration = 60; // in secs

// each pass is a struct with attributes 'station_name', 'start_date_days', 'end_date_days', and 'duration_s'
// passes_structs_list = generate_pass_list(kep_mean_ini, cjd0, duration_days, time_step, station_structs_list, min_pass_duration)

// printf('Passes calculated ! Total number of passes : %i\n', length(passes_structs_list))


// --------- Section 3 ---------
// define function to get top N best stations 
// (based on single pass duration)
// and calls it to get top 5 during the time $
// interval defined before
// -----------------------------

//utility functions
function sorted_struct_list = sort_passes_by_descending_length(passes_struct_list)
    n = length(passes_struct_list);
    sorted_struct_list = passes_struct_list;
    swapped = %t;
    while (swapped)
        swapped = %f
        for i=1:(n-1)
            if sorted_struct_list(i).duration_s < sorted_struct_list(i+1).duration_s
                mem = sorted_struct_list(i)
                sorted_struct_list(i) = sorted_struct_list(i+1)
                sorted_struct_list(i+1) = mem
                swapped = %t;
            end
        end
    end
endfunction
function sorted_struct_list = sort_passes_by_start_date(passes_struct_list)
    n = length(passes_struct_list);
    sorted_struct_list = passes_struct_list;
    swapped = %t;
    while (swapped)
        swapped = %f
        for i=1:(n-1)
            if sorted_struct_list(i).start_date_days > sorted_struct_list(i+1).start_date_days
                mem = sorted_struct_list(i)
                sorted_struct_list(i) = sorted_struct_list(i+1)
                sorted_struct_list(i+1) = mem
                swapped = %t;
            end
        end
    end
endfunction
function print_pass(pass_struct)
    [year, month, day, hour, mins, sec] = CL_dat_cjd2cal(pass_struct.start_date_days);
    printf("Pass at %i-%i-%i %i:%i:%i over %s, lasting %i s", year, month, day, hour, mins, sec, pass_struct.station_name,  pass_struct.duration_s);
endfunction
function boolean = passes_intersect(pass_1, pass_2)
    if (pass_1.end_date_days < pass_2.start_date_days) then
        boolean = return(%f);
    end
    if (pass_1.start_date_days > pass_2.end_date_days) then
        boolean = return(%f);
    end
    boolean = return(%t);
endfunction
function boolean = pass_overlaps_existing(test_pass, list_of_passes)
    n = length(list_of_passes);
    answer = %f;
    for i=1:n
        if passes_intersect(test_pass, list_of_passes(i)) then
            answer = %t;
            break;
        end
    end
    boolean = return(answer);
endfunction

// what are the top N passes in the next T seconds ? 
// returns list of structs representing passes
function best_passes_list = n_best_passes(N, kep_mean_orbit, cjd_start_date, duration_days, time_step_days, stations_struct_list, min_duration_secs)
    
    best_passes_list = list();
    
    passes_structs_list = generate_pass_list(kep_mean_orbit, cjd_start_date, duration_days, time_step_days, stations_struct_list, min_duration_secs)
    
    sorted_struct_list = sort_passes_by_descending_length(passes_structs_list)
    
    // pick first N (non-intersecting)
    pass_intervals = list();
    realN = min(N,length(sorted_struct_list));
    k = 1;
    while k <= realN
        if pass_overlaps_existing(sorted_struct_list(k), pass_intervals) then
            realN = min(realN+1,length(sorted_struct_list)); // skip this pass
        else
            best_passes_list($+1) = sorted_struct_list(k);
            pass_intervals($+1) = sorted_struct_list(k);
        end
        k = k+1;
    end
endfunction
function total_duration_s = total_comms_duration(passes_struct_list)
    total_duration_s = 0;
    for k = 1:length(passes_struct_list) 
        total_duration_s = total_duration_s + passes_struct_list(k).duration_s;
    end
endfunction
function mean_duration_s = mean_pass_duration(passes_struct_list)
    mean_duration_s = total_comms_duration(passes_struct_list) / length(passes_struct_list);
endfunction

topN = 5;
just_supaero = list();
sup_name = 'JN03ro';
lon = 1.444*%CL_deg2rad;
lat = 43.606*%CL_deg2rad
alt = 115
minel = 10
just_supaero($+1) = struct('name', sup_name, 'lon_rad', lon, 'lat_rad', lat, 'alt_m', alt, 'min_el_deg', minel);

selected_stations = list();
for k = 1:20
    selected_stations($+1) = station_structs_list(k);
end
my_passes = n_best_passes(36000, kep_mean_ini, cjd0, duration_days, time_step, selected_stations, min_pass_duration)
printf('\n\n Statistics : \n    Mean Pass Duration (min) : %f \n', mean_pass_duration(my_passes)/60);
decreasing_length_passes = sort_passes_by_descending_length(my_passes);
printf('    Max Pass Duration (min) : %f \n', decreasing_length_passes(1).duration_s/60);
printf('    Min Pass Duration (min) : %f \n', decreasing_length_passes($).duration_s/60);
printf('    Mean Passes Per Day : %f \n', length(my_passes)/duration_days);
printf('    Mean Communication Time Per Day (min) : %f \n', total_comms_duration(my_passes)/duration_days/60);


// find the best passes in a given time interval
// best_passes_list = n_best_passes(100, kep_mean_ini, cjd0, duration_days, time_step, selected_stations, min_pass_duration)
//printf('\n\n longest %i passes in the next %i hours : \n', topN, 24*duration_days)
//for n = 1:min(length(best_passes_list), topN)
//    printf('%i : ', n);
//    print_pass(best_passes_list(n));
//    printf("\n")
//end
//best_passes_sorted = sort_passes_by_start_date(best_passes_list);
//printf('\n\n All passes longer than %i s in the next %i hours : \n', min_pass_duration, 24*duration_days)
//for n = 1:length(best_passes_sorted)
//    printf('%i : ', n);
//    print_pass(best_passes_sorted(n));
//    printf("\n")
//end
//T = total_comms_duration(best_passes_sorted)
//printf('Total comms duration : %i seconds (%i minutes) over %i passes', T, T/60, length(best_passes_sorted));

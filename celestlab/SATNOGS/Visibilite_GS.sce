// output is a list of form [longitude_rad, latitude_rad, altitude_m; ...]
stations_list = import_station_positions('ground-stations-GPS-extended.csv')

// on veut une liste, pour chaque GS, de debut et fins de visibilite (ou debut et duree)

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
cjd = cjd0 + (0:time_step:duration) // list of computation dates

// propagate and project onto earth
kep_ana = CL_ex_propagate("j2sec","kep", cjd0,kep_mean_ini,cjd,"m");
pos_sat= CL_oe_kep2car(kep_ana);
t0=cjd0
pos_sat_terre=CL_fr_convert("ECI","ECF",t0, pos_sat );

// stats for each GS 
min_elevation = 7; // deg
vizi_start_dates_days = list();
vizi_durations_secs = list();
all_durations_secs = []
for n = 1:size(stations_list)(1)
    gs_position = stations_list(n, :);
    interv = CL_ev_stationVisibility(cjd,pos_sat_terre,gs_position',min_elevation*%CL_deg2rad); // expects lon lat alt in geodetic
    startdates_days = interv(1,:);
    enddates_days = interv(2, :);
    durations_secs = (enddates_days-startdates_days)*24*3600;
    vizi_start_dates_days(n) = startdates_days;
    vizi_durations_secs(n) = durations_secs;
    all_durations_secs = [all_durations_secs, durations_secs];
end

// example of what to do with the pass data
// number of passes per day, histogram of pass durations 
// (with numbers not frequencies), repartition of gap durations, 
// avg gap and coverage durations, maybe 2-sigma numbers
total_passes = length(all_durations_secs)

histplot(40, all_durations_secs, %f)
xlabel('pass duration [s]')
ylabel('number of passes')

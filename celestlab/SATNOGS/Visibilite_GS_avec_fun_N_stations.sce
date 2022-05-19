// output is a list of form [longitude_rad, latitude_rad, altitude_m; ...]
function pos = import_station_positions(filename)
    M = csvRead(filename, ',', '.')
    
    name = M(:,5)
    lons = M(:,2)
    lats = M(:,3)
    alts = M(:,4)
    
    pos = []
    for k = 2:size(M)(1)
        newpos = [lons(k)*%CL_deg2rad,lats(k)*%CL_deg2rad,alts(k)];
        pos = [pos; newpos];
    end
    
endfunction

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

//histplot(40, all_durations_secs, %f)
histplot(40, all_durations_secs)
xlabel('pass duration [s]')
ylabel('number of passes')

// on veut les stations qui ont le plus de visibilité entre t1 et t2
// Préconditions : 1<=N<=nbStations; delta>0; cjd0<=t1<t2<=cjd0+duration;
// Postconditions : stations contient :
//                  - à la ligne 1 les numéros de stations par ordre décroissant
//                  du nombre de secondes de visibilité durant l'intervalle delta
//                  - à la ligne 2 le nombre de secondes de visibilité associé
function[stations] = N_stations_the_more_visibile(N,t0,delta)
    t1 = t0
    t2 = t1 + delta
    if t1>= cjd0 then
        if t1<t2 then
            if t2<=cjd0+duration then
                if N >= 1 then
                        if N <= size(stations_list)(1) then
                        // on parcourt la liste des stations sol
                        // pour chaque station sol on calcul
                        // le temps de visibilité entre t1 et t2
                        duration_stations_t1t2 = []
                        t1abs = t1+cjd0
                        t2abs = t2+cjd0
                        for n = 1:size(stations_list)(1)
                            duration_t1t2 = 0
                            if size(vizi_durations_secs(n))(2) > 0 then
                                for i = 1:size(vizi_durations_secs(n))(2)
                                    ta = vizi_start_dates_days(n)(i)
                                    tb = ta + vizi_durations_secs(n)(i)/86400
                                    if t1 <= ta then
                                        if t2 >= ta then
                                            if t2 <= tb then
                                                duration_t1t2 = duration_t1t2 + t2-ta
                                            else
                                                duration_t1t2 = duration_t1t2 + tb-ta
                                            end
                                        end
                                    else
                                        if t2 <=tb then
                                            duration_t1t2 = duration_t1t2 + t2-t1
                                        else
                                            duration_t1t2 = duration_t1t2 + tb-t1
                                        end
                                    end
                                end
                            end
                            duration_t1t2 = duration_t1t2*86400
                            duration_stations_t1t2 = [duration_stations_t1t2, [n;duration_t1t2]]
                        end
                        // on trie la liste des stations sol
                        // suivant leur temps de visibilité entre t1 et t2
                        duration_stations_t1t2_trie = []
                        for n = 1:size(stations_list)(1)
                            [v,i] = max(duration_stations_t1t2(2,:))
                            duration_stations_t1t2_trie = [duration_stations_t1t2_trie, [i;v]]
                            duration_stations_t1t2(:,i) = [-1;-1]
                        end
                        // on ne revoie que les N premières stations
                        // de la liste triée avec leur durée de visibilité
                        // entre t1 et t2
                        stations = duration_stations_t1t2_trie(:,1:N)
                    else
                        printf('error : N > size(stations_list)(1)')
                        stations = []
                    end
                else
                    printf('error : N < 1')
                    stations = []
                end
            else
                printf('error : t0+delta > duration') 
                stations = []
            end
        else
            printf('error : delta < 0')
            stations = []
        end
    else
        printf('error : t0 < cjd0')
        stations = []
    end
endfunction

// exemple d'application avec un souhait d'obtenir 10 stations sol, à partir du lancement jusqu'à 3h après le lancement
stations_the_more_visible_for_3_hours = N_stations_the_more_visibile(10,cjd0,3/24)

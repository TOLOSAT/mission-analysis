// don't forget to run Fonction_iridium_utile.sce before running this ! 
// you will need Celestlab and CelestlabX

clear all;
CL_init();

//= = = = = = = = = = = = = = = = = = = = = = =  Variables  = = = = = = = = = = = = = = = = = = = = = = =  

// with these settings it takes my computer 16 minutes to run the code
// but running over longer durations yields much more statistically interesting results
time_step = 5/86400;   // in days
duration = 24/24; // in days
min_pass_duration_s = 15;
min_pass_size = ceil(15/(time_step*86400));
OrbitType = "SSO"; // or "ISS" or "ISSlow"

t0 = CL_dat_cal2cjd(2024,04,02,12,0,0); //year, month day;    // initial time
t = t0 + (0:time_step:duration) ;
freq_emission = 1617.e6;
Delta_doppler_max = 345; // +/- 345Hz/s max Doppler rate (time-derivative of Doppler Shift)
doppler_max = 35000; // Hz

//= = = = = = = = = = = = = = = = = = = = = = =  generate the constellation  = = = = = = = = = = = = = = = = = = = = = = =  

[kepConst, sat_angle_lim, cen_angle_lim, freq_emission_const, freq_reception_const] = generate_constellation("IridiumNext");


//= = = = = = = = = = = = = = = = = = = = = = =  generate the satellite  = = = = = = = = = = = = = = = = = = = = = = =  

// default : SSO 500km sunrise-sunset
sma = 6878.e3; // semi-major axis(m)
ecc = 2.e-3; // eccentricity ()
inc = 97.4*%CL_deg2rad; // inclination (rad)
aop = 1.570796327; // argument of perigee (rad)
ltan = 6; // mean local time at ascending node (hours)
raan = 3.3392258; // raan at 2024-07-02 12:00:00 to get 6h LTAN
ma = 0; // mean anomaly (rad)
if OrbitType == "ISS" then
    sma = 6378.e3+415.e3; 
    inc = 51.6*%CL_deg2rad;
elseif OrbitType == "ISSlow" then
    sma = 6378.e3+370.e3; 
    inc = 51.6*%CL_deg2rad;
elseif OrbitType == "SSO" then
    sma = 6878.e3   //sma 
    ecc = 2.e-3; //0.0253508
    inc = 97.4*%CL_deg2rad
    aop = 1.570796327;
    ltan = 6; // MLTAN (hours)
    raan = CL_op_locTime(t0, 'mlh', ltan, 'ra') // using mean local time in hours
    // raan = 3.3392258; // raan at 2024-07-02 12:00:00 to get 6h LTAN
    ma = 0;
end

kep_mean_ini = [sma; ecc; inc; aop; raan; ma];
T = 2*%pi*sqrt(sma^3/%CL_mu);

// the value 62.9deg below comes from the Iridium satellite half cone opening angle IIRC
min_el_for_vizi_deg = %CL_rad2deg * acos(sin(62.9*%CL_deg2rad)*kepConst(1,1)/sma); // about 23deg

//= = = = = = = = = = = = = = = = = = = = = = =  generation  = = = = = = = = = = = = = = = = = = = = = = =  
printf("\nGenerating TOLOSAT orbit . . .\n");

kep_sat = CL_ex_secularJ2(t0,kep_mean_ini,t); 
t_since_periapsis = pmodulo((t-t0)*86400,T);
MA_deg = t_since_periapsis*360/T;
aol = pmodulo(kep_sat(6,:) + kep_sat(4,:), 2*%pi); // mean argument of latitude is the interesting parameter

//convertion to cartesian position and velocity:
[pos_sat, vel_sat] = CL_oe_kep2car(kep_sat);
[pos_sat,vel_sat]= CL_fr_convert("ECI", "ECF", t, pos_sat,[vel_sat]);
[i,j]=size(pos_sat);

//= = = = = = = = = = = = = = = = = = = = = = =  simulation   = = = = = = = = = = = = = = = = = = = = = = =  

// initializations
t1=t0;
t1_old = t1;
[n, m] = size(kepConst); // n=6 orbital elements, m=75 satellites
elevations_over_t = zeros(m,length(t)); //deg
doppler_shifts = zeros(m,length(t)); // HZ
doppler_rates = zeros(m,length(t)); // Hz/s

// constellation propagation
printf("Generating IRIDIUM orbits . . .\n");
kepConstIridium = zeros(n, m, length(t));
for k=1:m
    kepConstIridium(:,k,:) = CL_ex_secularJ2(t0, kepConst(:,k), t);
end
    
// LOOP ON TIME
// positions have been precalculated
// calcs elevation and doppler shift
printf("Starting time loop . . . \n");
for l=1:j // (lowercase L), t = t0+dt*l
    // get params of all iridium sats at tl
    kep = kepConstIridium(:,:,l);
    [pos, vel] = CL_oe_kep2car(kep);
    [pos,vel]= CL_fr_convert("ECI", "ECF", t1,pos,[vel]);

    // compute angles between our sat and the Iridium sats
    sat_angle = CL_vectAngle(CL_dMult(ones(1,m),pos_sat(:,l))-pos, -pos);
    cen_angle = CL_vectAngle(pos_sat(:,l), pos);

    // For each Iridium sat
    // calc doppler shift and elevation of iridium sat seen by our sat
    for k=1:m // k is iridium index
        shift = doppler_shift(pos(:,k), vel(:,k), pos_sat(:,l), vel_sat(:,l), freq_emission);
        el = 90-sat_angle(k)*%CL_rad2deg-cen_angle(k)*%CL_rad2deg;
        elevations_over_t(k,l) = el;
        doppler_shifts(k,l) = shift;
    end 
    t1_old = t1;
    t1=t1+time_step;
    if (pmodulo(t1-t0, 0.50) == 0) then
        printf("%f days\n", t1-t0);
    end
end
// second loop : just to compute doppler rates a fortiori using centered numerical derivative scheme (where possible)
printf("Calculating doppler rates . . . \n");
for k=1:m
    doppler_rates(k,1) = (doppler_shifts(k,2)-doppler_shifts(k,1))/(time_step*86400);
    for l=2:(j-1)
        doppler_rates(k,l) = (doppler_shifts(k,l+1)-doppler_shifts(k,l-1))/(2*time_step*86400);
    end
    doppler_rates(k,j) = (doppler_shifts(k,j)-doppler_shifts(k,j-1))/(time_step*86400);
end

//= = = = = = = = = = = = = = = = = = = = = = =  exploitation  = = = = = = = = = = = = = = = = = = = = = = =

is_visible = (elevations_over_t >= min_el_for_vizi_deg & ... 
              abs(doppler_shifts) <= doppler_max & ...
              abs(doppler_rates) <= Delta_doppler_max)*1; // 0s and 1s

// example_pass = struct('start_date_cjd', t(100), 'end_date_cjd', t(106), 'sat_number', 46);
ordered_pass_list = GetIridiumPasses(is_visible, time_step, min_pass_duration_s, t);

[mean_passes_per_day, avg_duration_s, all_passes] = IridiumPassStatistics(ordered_pass_list, duration);

printf(' Statistics : \n    Mean Pass Duration (s) : %f \n', avg_duration_s);
printf('    Mean Passes Per Day : %f \n', mean_passes_per_day);
printf('    Mean Communication Time Per Day (min) : %f \n', mean_passes_per_day*avg_duration_s/60);

// compute expected number (in statistical sense) of  iridium satellites
// that satisfy visibility + doppler shift + doppler rate constraints
// as a function of AoL (argument of latitude, = omega + TA)
// objective : show that some geographic areas are more favorable to communication
visi_sat_expected_over_aol = zeros(1, length(t((t-t0)*86400<T)));
daol = time_step*86400*2*%pi/T;
for l=1:length(t((t-t0)*86400<T))
    myaol = aol(1,l);
    visi_sat_expected_over_aol(1,l) = sum(is_visible(:,(myaol <= aol & (aol < (myaol+daol))) ));
end
visi_sat_expected_over_aol = visi_sat_expected_over_aol./(duration.*86400./T);

raans = kep_sat(5,:);
save("big_savefile.dat", "ordered_pass_list", "is_visible", "t", ...
     "raans", "aol", "visi_sat_expected_over_aol", "kepConstIridium");
     
// RAANs histogram data
passRAANs = zeros(size(all_passes));
for p=1:length(all_passes)
    passRAANs(p) = raans(t==all_passes(p).start_date_cjd);
end

// = = = = = = = = = = = = = = = = = = = = = = =  visualisation  = = = = = = = = = = = = = = = = = = = = = = =

scf(1)
plot((t-t0)*24*60, is_visible)
xlabel('elapsed time (min)')
ylabel('Visible satellites')
title('Visible satellites ')
CL_g_stdaxes()
set(gca(),'data_bounds',[-10, -0.2; 10+duration*24*60, 1.2])

scf(1).figure_size=[2000,1000];
deletefile('visible_satellites_1.png')
xs2png(1,'visible_satellites_1.png');

// pass analytics 
// plots elevation, doppler shift and doppler rate over time for each interesting pass
// TODO: modify this code so it works if 1 sat has several passes
//for k=1:m
//    if (max(is_visible(k,:)) == 1 & duration < 1) then
//        indices_of_pass = elevations_over_t(k,:) >= min_el_for_vizi_deg;
//        scf()
//        subplot(3,1,1)
//        plot((t(indices_of_pass)'-t0)*1440,elevations_over_t(k,indices_of_pass))
//        xlabel('temps ecoulé (min)')
//        ylabel('elevation [deg]')
//        title('iridium ' + string(k))
//        CL_g_stdaxes()
//    
//        subplot(3,1,2)
//        plot((t(indices_of_pass)'-t0)*1440,doppler_shifts(k,indices_of_pass))
//        xlabel('temps ecoulé (min)')
//        ylabel('doppler shift [Hz]')
//        CL_g_stdaxes()
//        
//        subplot(3,1,3)
//        plot((t(indices_of_pass)'-t0)*1440,doppler_rates(k,indices_of_pass))
//        xlabel('temps ecoulé (min)')
//        ylabel('doppler rate [Hz/s]')
//        CL_g_stdaxes()
//    end
//end

duration_min = duration*24*60;
total_comm_time_min = sum(is_visible)*time_step*24*60;
comm_availability_ratio = total_comm_time_min/duration_min;
// TODO : get individual passes length
//scf()
//plot(MA_deg, is_visible)
//xlabel('mean anomaly (deg)')
//ylabel('Visible satellites')
//title('Visible satellites ')
//CL_g_stdaxes()
//set(gca(),'data_bounds',[-5, -0.2; 365, 1.2])
//scf()
//plot(t_since_periapsis/60, is_visible)
//xlabel('time since periapsis [min]')
//ylabel('Visible satellites')
//title('Visible satellites ')
//CL_g_stdaxes()
//set(gca(),'data_bounds',[-5, -0.2; 115, 1.2])
//scf(2)
//plot(aol*180/%pi, sum(is_visible,1))
//xlabel('argument of latitude [deg]')
//ylabel('Visible satellites')
//title('Visible satellites ')
//CL_g_stdaxes()
//set(gca(),'data_bounds',[-5, -0.2; 365, 2.2])
//
//scf(2).figure_size=[2000,1000];
//deletefile('visible_satellites_2.png')
//xs2png(2,'visible_satellites_2.png');


scf(3)
plot(aol((t-t0)*86400<T)*180/%pi, visi_sat_expected_over_aol, 'x')
xlabel('argument of latitude [deg]')
ylabel('Expected Number of Visible Satellites')
title('Expected Visible Satellites, averaged over XX days, dt=XXs ')
CL_g_stdaxes()
set(gca(),'data_bounds',[-5, -0.2; 365, 1.2])

scf(3).figure_size=[2000,1000];
deletefile('visible_satellites_3.png')
xs2png(3,'visible_satellites_3.png');


//scf(4)
//plot(t-t0, sum(is_visible, 1))
//xlabel('mission elapsed time (days)')
//ylabel('Visible satellites')
//title('Visible satellites ')
//CL_g_stdaxes()
//
//scf(4).figure_size=[2000,1000];
//deletefile('visible_satellites_4.png')
//xs2png(4,'visible_satellites_4.png');

//scf(5)
//histplot(20, passRAANs*%CL_rad2deg, normalization=%f)
//xlabel('RAAN (deg)')
//ylabel('Number of passes')
//title('Pass rate dependency on RAAN')
//CL_g_stdaxes()
//
//scf(5).figure_size=[2000,1000];
//deletefile('visible_satellites_5.png')
//xs2png(5,'visible_satellites_5.png');

//raans = kep_sat(5,:);
//scf()
//plot(t-t0, raans)
//xlabel('mission elapsed time (days)')
//ylabel('RAAN [rad]')
//title('Right Ascension of Ascending node, XX days at 370km 51.6deg')
//CL_g_stdaxes()

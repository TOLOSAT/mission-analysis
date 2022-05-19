// don't forget to run Fonction_iridium_utile.sce before running this ! 
// you will need Celestlab and CelestlabX
// this code took about 30 hours to run on my laptop. 
// you can instead download the results file and run raan_scan_reader.sce :
// https://drive.google.com/file/d/1g8aMo6MjvdOkx0f7Ck0Oa229smp0ic3G/view?usp=sharing

clear all;
CL_init();

//= = = = = = = = = = = = = = = = = = = = = = =  Variables  = = = = = = = = = = = = = = = = = = = = = = =  

// PASS STUDY SETTINGS
time_step = 5/86400;   // in days
duration = 24/24; // in days
min_pass_duration_s = 15;
min_pass_size = ceil(15/(time_step*86400));
OrbitType = "SSO"; // "SSO" or "ISS" or "ISSlow"
freq_emission = 1617.e6;
Delta_doppler_max = 345; // +/- 345Hz/s max Doppler rate (time-derivative of Doppler Shift)
doppler_max = 35000; // Hz
// RAAN SCAN SETTINGS
raan_points = 73; 
total_duration = 365; // days
dt_coarse = total_duration / raan_points; // days
t0 = CL_dat_cal2cjd(2017,01,16,12,0,0); //CL_dat_cal2cjd(2024,07,02,12,0,0); //year, month day;    // initial time
t_coarse = t0 + (0:dt_coarse:total_duration);


//= = = = = = = = = = = = = = = = = = = = = = =  generate the constellation  = = = = = = = = = = = = = = = = = = = = = = 
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
    raan = 3.3392258; // raan at 2024-07-02 12:00:00 to get 6h LTAN
    ma = 0;
end

kep_mean_ini = [sma; ecc; inc; aop; raan; ma];
T = 2*%pi*sqrt(sma^3/%CL_mu);

// the value 62.9deg below comes from the Iridium satellite half cone opening angle IIRC
min_el_for_vizi_deg = %CL_rad2deg * acos(sin(62.9*%CL_deg2rad)*kepConst(1,1)/sma); // about 23deg


//= = = = = = = = = = = = = = = = = = = = = = =  coarse simulation  = = = = = = = = = = = = = = = = = = = = = = =  

disp("Setting up STELA parameters");
params_stela =  CL_stela_params(); 
params_stela.mass = 2.66; // TOLOSAT's mass
params_stela.drag_coef = 2.2;
params_stela.drag_area = 0.025;// Area assuming random tumbling of the spacecraft
params_stela.srp_area = 0.025; // also tumbling area
params_stela.srp_coef = 1.8; // common value among spacecraft
//SETUP of the FORCE MODEL
params_stela.zonal_maxDeg = 15; // maximum zonal terms for gravity harmonics
params_stela.tesseral_maxDeg = 15; // maximum tesseral terms for gravity harmonics
params_stela.drag_solarActivityType = 'variable'; // here we have to look for the predicted solar activity in 2024, I took one of the highest values 
data_dir=strsubst(pwd(),"Iridium","Data");
params_stela.solarActivityFile =strcat([data_dir,"\stela_solar_activity.txt"]); // predicted Geomagnetic index in 2024 same method as for the solar flux
// Setup epochs vector
day_fraction = 16;
params_stela.integrator_step = 86400/day_fraction; // 1/16th of a day. 
step_stela= (params_stela.integrator_step)/86400; // propagation step in days
cjd_stela = t0 + (0:step_stela:total_duration);

//Propagation with default solar activity
disp("Beginning STELA propagation\n");
coarse_kep_stela = CL_stela_extrap("kep", t0, kep_mean_ini, cjd_stela, params_stela, 'm');
disp("Completed STELA propagation\n");
// keep only the points at the start of each precise study
coarse_t = cjd_stela(1:(dt_coarse*day_fraction):$); // verification, this should equal t_coarse
coarse_kep_sat = coarse_kep_stela(:,1:(dt_coarse*day_fraction):$);

// every fine time-point
ti = t_coarse(1);
t_fine = ti + (0:time_step:duration);
t_all = zeros(1, raan_points*length(t_fine)); 
fine_points = length(t_fine);

disp("Propagating sat in fine mode. . . ");
[n, m] = size(kepConst); // n=6 orbital elements, m=75 satellites
all_kep_sat = zeros(n, length(t_all));
for r=1:raan_points
    ti = t_coarse(r);
    t_fine = ti + (0:time_step:duration);
    t_all(((r-1)*fine_points+1):(r*fine_points)) = t_fine;
    fine_kep_sat = CL_ex_secularJ2(ti, coarse_kep_sat(:,r), t_fine);
    all_kep_sat(:,((r-1)*fine_points+1):(r*fine_points)) = fine_kep_sat;
end

// J2 prop the constellation and sat over 1 year to get kep at each study point
disp("Propagating constellation in fine+coarse mode . . . ");
all_kep_iridium = zeros(n, m, length(t_all));
for k=1:m
    all_kep_iridium(:,k,:) = CL_ex_secularJ2(t0, kepConst(:,k), t_all);
end

disp("starting raan loop . . .");
// ====  RAAN LOOP  =====
pass_rate = zeros(1,raan_points);
pass_lens = zeros(1,raan_points);
all_ordered_passes = list();
for r=1:raan_points
    // TODO : initialize whatever 
    ti = t_coarse(r);
    t_fine = ti + (0:time_step:duration);
    
    // get fine time data of the sat and iridium
    fine_kep_sat = all_kep_sat(:,((r-1)*fine_points+1):(r*fine_points));
    [pos_sat, vel_sat] = CL_oe_kep2car(fine_kep_sat);
    [pos_sat,vel_sat]= CL_fr_convert("ECI", "ECF", t_fine, pos_sat,[vel_sat]);
    [i,j]=size(pos_sat);
    kepConstIridium = zeros(n, m, length(t_fine));
    for k=1:m
        kepConstIridium(:,k,:) = all_kep_iridium(:,k,((r-1)*fine_points+1):(r*fine_points));
    end
    
    // initializations
    elevations_over_t = zeros(m,length(t_fine)); //deg
    doppler_shifts = zeros(m,length(t_fine)); // HZ
    doppler_rates = zeros(m,length(t_fine)); // Hz/s

    // LOOP ON TIME
    // positions have been precalculated
    // calcs elevation and doppler shift
    t1 = ti;
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
    end
    // second loop : just to compute doppler rates a fortiori using centered numerical derivative scheme (where possible)
    for k=1:m
        doppler_rates(k,1) = (doppler_shifts(k,2)-doppler_shifts(k,1))/(time_step*86400);
        for l=2:(j-1)
            doppler_rates(k,l) = (doppler_shifts(k,l+1)-doppler_shifts(k,l-1))/(2*time_step*86400);
        end
        doppler_rates(k,j) = (doppler_shifts(k,j)-doppler_shifts(k,j-1))/(time_step*86400);
    end
    // statistics for this RAAN shift
    is_visible = (elevations_over_t >= min_el_for_vizi_deg & ... 
                  abs(doppler_shifts) <= doppler_max & ...
                  abs(doppler_rates) <= Delta_doppler_max)*1; // 0s and 1s
    ordered_pass_list = GetIridiumPasses(is_visible, time_step, min_pass_duration_s, t_fine);
    [mean_passes_per_day, avg_duration_s, all_passes] = IridiumPassStatistics(ordered_pass_list, duration);
    printf('point number %f : \n', r);
    printf(' Statistics : \n    Mean Pass Duration (s) : %f \n', avg_duration_s);
    printf('    Mean Passes Per Day : %f \n', mean_passes_per_day);
    // save them
    pass_rate(r) = mean_passes_per_day;
    pass_lens(r) = avg_duration_s;
    all_ordered_passes($+1) = ordered_pass_list; // list of lists of lists (raan then sat then time)
end

// SAVE DATA
save("raan_scan_results.dat", "t_all", "all_kep_iridium", ...
     "all_kep_sat", "pass_rate", "pass_lens", "all_ordered_passes", ...
     "fine_points", "raan_points", "kep_mean_ini", ...
     "time_step", "duration", "total_duration");

raan_starts = coarse_kep_sat(5,1:$-1);
diffraan = raan_starts - matrix(all_kep_iridium(5,1,1:fine_points:$), [1 raan_points]);
comms_time = pass_rate.*pass_lens;
scf()
plot(raan_starts, pass_rate)
xlabel('RAAN [rad]')
ylabel('Mean passes per day')
title('Effect of RAAN on pass rate (dt=5s, 24 hour integration per point)')
CL_g_stdaxes()
scf()
plot(diffraan, pass_rate)
xlabel('RAAN_sat - RAAN_Iridium1 [rad]')
ylabel('Mean passes per day')
title('Effect of RAAN difference on pass rate (dt=5s, 24 hour integration per point)')
CL_g_stdaxes()
scf()
plot(raan_starts, pass_lens)
xlabel('RAAN [rad]')
ylabel('Mean pass duration (s)')
title('Effect of RAAN on pass duration (dt=5s, 12 hour integration per point)')
CL_g_stdaxes()

scf()
plot(diffraan, comms_time/60)
xlabel('RAAN_sat - RAAN_Iridium1 [rad]')
ylabel('Comms time per day [min/day]')
title('Effect of RAAN difference on total communication time (dt=5s, 24 hour integration per point)')
CL_g_stdaxes()


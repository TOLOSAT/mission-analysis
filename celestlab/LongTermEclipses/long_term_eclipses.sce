//=============================================================================
//
//                 MISSION ANALYSIS : Project TOLOSAT 
//
//=============================================================================


xdel(winsid())
clear
CL_init()



// =====================================================
// INITIAL ORBIT DEFINITION 
// =====================================================


// Initial mean keplerian parameters corresponding to the Polar orbit
disp("Initiating mean keplerian parameters");
sma = CL_dataGet("body.Earth.eqRad")+500e3      // Semi-major axis [m]
ecc = 2.e-3                                     // Eccentricity [-]
inc = CL_op_ssoJ2("i", sma, ecc)                // Inclination [rad]
pom = %pi/2;                                    // Argument of perigee [rad]
mlh = 6;                                        // MLTAN [hours]
cjd0 = CL_dat_cal2cjd(2024,01,02,12,0,0);       // Julian date initial time [Julian days]
gom = CL_op_locTime(cjd0, "mlh", mlh, "ra");    // Right ascension (longitude) of the ascending node (RAAN) [rad]
anm = 0;                                        // Mean anomaly [rad]
kep_mean_ini = [sma;ecc;inc;pom;gom;anm]


// =====================================================
// NUMERICAL PROPAGATION WITH STELA
// =====================================================

// STELA IS A NUMERICAL PROPAGATOR INTRODUCED BY CELESTLAB-X 
// it is used to compute the evolution of keplerian parameters during the whole life of the satellite

//force model setup:
// - use the max degree and order of gravity harmonics
// - use influence of Sun + Moon
// - model MSIS2000 for drag
// - use a constant solar activity corresponding to the prediction in 2024 
// - use solar radiation pressure
// - for the spacecraft: use the same charcteristics as in the Gmat script

disp("Setting up STELA parameters");
params_stela =  CL_stela_params(); // let's edit the parameters

// DEFINING SPACECRAFT's characteristics
params_stela.mass = 2.66; // TOLOSAT's mass
params_stela.drag_coef = 2.2;
params_stela.drag_area = 0.025;// Area assuming random tumbling of the spacecraft
params_stela.srp_area = 0.025; // also tumbling area
params_stela.srp_coef = 1.8; // common value among spacecraft

//SETUP of the FORCE MODEL
params_stela.zonal_maxDeg = 15; // maximum zonal terms for gravity harmonics
params_stela.tesseral_maxDeg = 15; // maximum tesseral terms for gravity harmonics
params_stela.drag_solarActivityType = 'variable'; // here we have to look for the predicted solar activity in 2024, I took one of the highest values 
data_dir=strsubst(pwd(),"LongTermEclipses","Data");
params_stela.solarActivityFile =strcat([data_dir,"\stela_solar_activity.txt"]); // predicted Geomagnetic index in 2024 same method as for the solar flux

// Setup epochs vector
params_stela.integrator_step = 2*%pi*sqrt(sma^3/%CL_mu); // exactly an orbit // 92*60; //92 minutes which is roughly an orbit
step_stela= (params_stela.integrator_step)/86400; // propagation step in days
cjd_stela = cjd0 + (0:step_stela:1600);


//Propagation with default solar activity
disp("Beginning STELA propagation");
mean_kep_stela = CL_stela_extrap("kep", cjd0, kep_mean_ini, cjd_stela, params_stela, 'm');
disp("Completed STELA propagation");

//Propagation using GMAT's solar activity
//params_stela_nm = params_stela;
//mean_kep_stela_nm = CL_stela_extrap("kep", cjd0, kep_mean_ini, cjd_stela, params_stela_nm, 'm');

//Getting ready for the plots
sma_stela = mean_kep_stela(1,:);
inc_stela = mean_kep_stela(3,:);
RAAN_stela =mean_kep_stela(5,:);
ecc_stela = mean_kep_stela(2,:);
pom_stela = mean_kep_stela(4,:);
mltan = CL_op_locTime(cjd_stela,"ra", mean_kep_stela(5,:), "mlh");


// =====================================================
// ECLIPSES
// =====================================================


timestep_central=1; // 30;
nb_stela_epochs=length(mean_kep_stela(1,:));
eclipse_duration_umb=zeros(1,nb_stela_epochs);
//eclipse_duration_umbc=zeros(1,nb_stela_epochs);
//eclipse_duration_pen=zeros(1,nb_stela_epochs);

disp("Beginning eclipses computations");
tic
for ii=1:nb_stela_epochs
    if ~isnan(mean_kep_stela(1,ii)) 
        Torbit_tmp=2*%pi*sqrt(mean_kep_stela(1,ii)^3/%CL_mu);
        epochs=cjd_stela(ii)+(0:timestep_central:Torbit_tmp)/86400;
        kep_tmp=CL_ex_propagate("central", "kep", cjd_stela(ii),mean_kep_stela(:,ii),epochs,'m')
        [pos_ECI,vel_ECI] = CL_oe_kep2car(kep_tmp);     // Conversion to cartesian coordinates
        Sun_eci = CL_eph_sun(epochs);                              // Position of the Sun in ECI coordinates
        eclipse_umb = CL_ev_eclipse(epochs,pos_ECI,Sun_eci,typ='umb');     // Compute eclipse start and end times
//        eclipse_umbc = CL_ev_eclipse(epochs,pos_ECI,Sun_eci,typ='umbc');     // Compute eclipse start and end times
//        eclipse_pen = CL_ev_eclipse(epochs,pos_ECI,Sun_eci,typ='pen');     // Compute eclipse start and end times
        eclipse_duration_umb(ii) = sum((eclipse_umb(2,:) - eclipse_umb(1,:)))*86400;
//        eclipse_duration_umbc(ii) = sum((eclipse_umbc(2,:) - eclipse_umbc(1,:)))*86400;
//        eclipse_duration_pen(ii) = sum((eclipse_pen(2,:) - eclipse_pen(1,:)))*86400;
    end,
    DeltaT_average=toc()/ii;
    remaining_time=(nb_stela_epochs-ii)*DeltaT_average;
    seconds=modulo(remaining_time,60);
    minutes=(remaining_time-seconds)/60;
    hours=(minutes-modulo(minutes,60))/60;
    minutes=modulo(minutes,60);
    disp(strcat(['Computation ',string(ii),'/',string(nb_stela_epochs),' (',string(ii/nb_stela_epochs*100),' %)',' Remaining : ',string(hours),' hours ',string(minutes),' minutes ',string(seconds),' seconds']));
end



// =====================================================
// PLOTS OF THE ORBIT EVOLUTION
// =====================================================

scf(1);
subplot(231)
plot(cjd_stela-cjd0,sma_stela - %CL_eqRad, 'b')
//plot(cjd_stela-cjd0,mean_kep_stela_nm(1,:) - %CL_eqRad, 'r')
title('Altitude decay with STELA propagation')
xlabel('Elapsed days since launch') 
ylabel('Altitude (m)')
//legend(['stela solar activity','GMAT solar activity'])
CL_g_stdaxes();

subplot(232)
plot(cjd_stela-cjd0,inc_stela*%CL_rad2deg)
title('Inclination with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('Inclination (deg)')
CL_g_stdaxes();

subplot(233)
plot(cjd_stela-cjd0,ecc_stela)
title('Eccentricity with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('Eccentricity')
CL_g_stdaxes();

subplot(234);
plot(cjd_stela-cjd0,pom_stela*%CL_rad2deg)
title('Argument of perigee with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('Argument of perigee (deg)')
CL_g_stdaxes();

subplot(235);
plot(cjd_stela-cjd0,RAAN_stela*%CL_rad2deg)
title('RAAN TOLOSAT with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('RAAN (deg)')
CL_g_stdaxes();

subplot(236);
plot(cjd_stela-cjd0,mltan,'.','MarkerSize',2,'Color','Blue')
title('Evolution of the MLTAN during the TOLOSAT mission')
ylabel('MLTAN [hours]')
xlabel('Elapsed days since launch')
CL_g_stdaxes();
scf(1).figure_size=[2000,1000];
deletefile('long_term_orbit.png')
xs2png(1,'long_term_orbit.png');

scf(2);
plot(cjd_stela-cjd0,eclipse_duration_umb/60,'.','MarkerSize',2,'Color','Blue')
//plot(cjd_stela-cjd0,eclipse_duration_umbc/60,'.','MarkerSize',2,'Color','Purple')
//plot(cjd_stela-cjd0,eclipse_duration_pen/60,'.','MarkerSize',2,'Color','Red')
title('Evolution of the eclipse duration during the TOLOSAT mission')
//legend(['Conical umbra','Cylindrical umbra','Penumbra'])
ylabel('Eclipse duration [mins]')
xlabel('Elapsed days since launch')
CL_g_stdaxes();
scf(2).figure_size=[2000,1000];
deletefile('long_term_eclipses.png')
xs2png(2,'long_term_eclipses.png');















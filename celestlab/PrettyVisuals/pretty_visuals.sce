//=============================================================================
//
//                 MISSION ANALYSIS : Project TOLOSAT 
//
//=============================================================================

xdel(winsid())
clear
CL_init()


// =====================================================
// SELECT LYDANE PROPAGATION EPOCHS
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
lydane_kep_ini = [sma;ecc;inc;pom;gom;anm]

lydane_duration=1;
lydane_timestep=30/86400;
lydane_cjd=cjd0+(0:lydane_timestep:lydane_duration);


// =====================================================
// ANALYTICAL PROPAGATION WITH LYDANE
// =====================================================

lydane_kep_results = CL_ex_propagate("lydlp","kep",cjd0,lydane_kep_ini,lydane_cjd,'m');


// Propagate the orbit

// The lydane model is the most complete analytical model of celestlab
// Here, mean parameters are chosen over osculating parameters as they have a better physical significance 
// https://space.stackexchange.com/questions/14731/nuances-of-the-terms-mean-osculating-keplerian-orbital-elements


//// Compute the true and eccentric anomalies from M and ecc
//E_ana = CL_kp_M2E(ecc_ana,M_ana);
//v_ana = CL_kp_M2v(ecc_ana,M_ana);
//
//// Compute the MLTAN fron the RAAN and date
//mltan_ana = CL_op_locTime(cjd, "ra", RAAN_ana, "mlh");
//
//// Compute the evolution of the orbital period
//mm = CL_kp_params('mm',sma_ana);                // Mean motion [rad]
//per = CL_kp_params('per',sma_ana);              // Orbital period [s]
//// /!\ Mean parameter are needed to accurately compute the orbital period.

lydane_sma = lydane_kep_results(1,:);                         // Semi-major axis [m]
lydane_ecc = lydane_kep_results(2,:);                         // Eccentricity [-]
lydane_inc = lydane_kep_results(3,:);                         // Inclination [rad]
lydane_pom = lydane_kep_results(4,:);                         // Argument of perigee [rad]
lydane_RAAN = lydane_kep_results(5,:);                        // Right ascension of the ascending node (RAAN) [rad]
lydane_M = lydane_kep_results(6,:);                           // Mean anomaly [rad]

// Position and velocity in ECI
[pos_eci, vel_eci] = CL_oe_kep2car(lydane_kep_results); 

// Position in ECF
pos_ecf = CL_fr_convert("ECI", "ECF", lydane_cjd, pos_eci); 
pos_lla = CL_co_car2sph(pos_ecf);


// =====================================================
// PLOTS OF THE ORBIT EVOLUTION
// =====================================================

scf(1);
CL_plot_earthMap(color_id=color("black"));
// Plot ground tracks
CL_plot_ephem(pos_ecf,color_id=color("blue"));
title('TOLOSAT Ground Track')
xlabel('Longitude (deg)')
ylabel('Latitude (deg)')
CL_g_stdaxes();
scf(1).figure_size=[2000,1000];
sleep(1000)
xs2png(1,'ground_track_lydane.png');

scf(2);
subplot(231)
plot(lydane_cjd-cjd0,lydane_sma- %CL_eqRad)
title('Altitude')
xlabel('Elapsed days since launch')
ylabel('Altitude (m)')
CL_g_stdaxes();

subplot(232)
plot(lydane_cjd-cjd0,lydane_inc*%CL_rad2deg)
title('Inclination')
xlabel('Elapsed days since launch')
ylabel('Inclination (deg)')
CL_g_stdaxes();

subplot(233)
plot(lydane_cjd-cjd0,lydane_ecc)
title('Eccentricity')
xlabel('Elapsed days since launch')
ylabel('Eccentricity')
CL_g_stdaxes();

subplot(234);
plot(lydane_cjd-cjd0,lydane_pom*%CL_rad2deg)
title('Argument of perigee')
xlabel('Elapsed days since launch')
ylabel('Argument of perigee (deg)')
CL_g_stdaxes();

subplot(235);
plot(lydane_cjd-cjd0,lydane_RAAN*%CL_rad2deg)
title('RAAN')
xlabel('Elapsed days since launch')
ylabel('RAAN (deg)')
CL_g_stdaxes();

subplot(236);
plot(lydane_cjd-cjd0,lydane_M*%CL_rad2deg)
title('Mean Anomaly')
ylabel('Mean Anomaly (deg)')
xlabel('Elapsed days since launch')
CL_g_stdaxes();

scf(2).figure_size=[2000,1000];
deletefile('orbit_evolution_lydane.png');
sleep(1000)
xs2png(2,'orbit_evolution_lydane.png');

csvWrite(pos_eci,'pos_eci.csv')
csvWrite(vel_eci,'vel_eci.csv')
csvWrite(pos_ecf,'pos_ecf.csv')
csvWrite(pos_lla,'pos_lla.csv')
csvWrite(lydane_cjd,'lydane_cjd.csv')
csvWrite(cjd0,'cjd0.csv')

csvWrite(lydane_sma,'lydane_sma.csv')
csvWrite(lydane_inc,'lydane_inc.csv')
csvWrite(lydane_ecc,'lydane_ecc.csv')
csvWrite(lydane_pom,'lydane_pom.csv')
csvWrite(lydane_RAAN,'lydane_RAAN.csv')
csvWrite(lydane_M,'lydane_M.csv')



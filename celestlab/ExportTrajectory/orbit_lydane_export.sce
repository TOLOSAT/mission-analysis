//=============================================================================
//
//                 MISSION ANALYSIS : Project TOLOSAT 
//
//=============================================================================

xdel(winsid())
clear
CL_init()

// =====================================================
// IMPORT RESULTS FROM STELA PROPAGATION
// =====================================================

stela_cjd=csvRead("stela_datevector.csv")';
stela_eclipses=csvRead("stela_eclipses.csv")';
stela_mean_kep=csvRead("stela_mean_kep.csv")';


// =====================================================
// SELECT LYDANE PROPAGATION EPOCHS
// =====================================================
stela_selected_days=[150,350,720,1070,1450];
stela_timestep=stela_cjd(2)-stela_cjd(1);
lydane_epochs_0=stela_cjd(1)+stela_selected_days;
lydane_duration=5;
lydane_timestep=30/86400



// =====================================================
// ANALYTICAL PROPAGATION WITH LYDANE
// =====================================================

lydane_cjd=%nan*zeros(length(lydane_epochs_0),length((0:lydane_timestep:lydane_duration)));
sat_x_eci=lydane_cjd;
sat_y_eci=lydane_cjd;
sat_z_eci=lydane_cjd;
sun_x_eci=lydane_cjd;
sun_y_eci=lydane_cjd;
sun_z_eci=lydane_cjd;
lydane_sma=lydane_cjd;
lydane_ecc=lydane_cjd;
lydane_inc=lydane_cjd;
lydane_pom=lydane_cjd;
lydane_RAAN=lydane_cjd;
lydane_M=lydane_cjd;

for ii=1:length(lydane_epochs_0)
    lydane_epoch_0=stela_cjd(stela_cjd>=lydane_epochs_0(ii) & stela_cjd<(lydane_epochs_0(ii)+stela_timestep))
    lydane_kep_ini=stela_mean_kep(:,stela_cjd==lydane_epoch_0)
    lydane_cjd(ii,:)=lydane_epoch_0+(0:lydane_timestep:lydane_duration)
    lydane_kep_results = CL_ex_propagate("lydlp","kep",lydane_epoch_0,lydane_kep_ini,lydane_cjd(ii,:),'m');
    [sat_pos_tmp,sat_vel_tmp] = CL_oe_kep2car(lydane_kep_results);
    sat_x_eci(ii,:)=sat_pos_tmp(1,:);
    sat_y_eci(ii,:)=sat_pos_tmp(2,:);
    sat_z_eci(ii,:)=sat_pos_tmp(3,:);
    sun_pos_tmp = CL_eph_sun(lydane_cjd(ii,:))
    sun_x_eci(ii,:)=sun_pos_tmp(1,:);
    sun_y_eci(ii,:)=sun_pos_tmp(2,:);
    sun_z_eci(ii,:)=sun_pos_tmp(3,:);
    lydane_sma(ii,:) = lydane_kep_results(1,:);                         // Semi-major axis [m]
    lydane_ecc(ii,:) = lydane_kep_results(2,:);                         // Eccentricity [-]
    lydane_inc(ii,:) = lydane_kep_results(3,:);                         // Inclination [rad]
    lydane_pom(ii,:) = lydane_kep_results(4,:);                         // Argument of perigee [rad]
    lydane_RAAN(ii,:) = lydane_kep_results(5,:);                        // Right ascension of the ascending node (RAAN) [rad]
    lydane_M(ii,:) = lydane_kep_results(6,:);                           // Mean anomaly [rad]
end

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



// =====================================================
// PLOTS OF THE ORBIT EVOLUTION
// =====================================================
Color=["blue","red","green","orange","purple"];
legend_name=string(stela_selected_days);


scf(1);
subplot(231)
for ii=1:length(lydane_epochs_0)
    plot(lydane_cjd(ii,:)-lydane_cjd(ii,1),lydane_sma(ii,:)- %CL_eqRad,"Color",Color(ii))
end
title('Altitude')
xlabel('Elapsed days since launch')
ylabel('Altitude (m)')
legend(legend_name)
CL_g_stdaxes();

subplot(232)
for ii=1:length(lydane_epochs_0)
    plot(lydane_cjd(ii,:)-lydane_cjd(ii,1),lydane_inc(ii,:)*%CL_rad2deg,"Color",Color(ii))
end
legend(legend_name)
title('Inclination')
xlabel('Elapsed days since launch')
ylabel('Inclination (deg)')
CL_g_stdaxes();

subplot(233)
for ii=1:length(lydane_epochs_0)
    plot(lydane_cjd(ii,:)-lydane_cjd(ii,1),lydane_ecc(ii,:),"Color",Color(ii))
end
legend(legend_name)
title('Eccentricity')
xlabel('Elapsed days since launch')
ylabel('Eccentricity')
CL_g_stdaxes();

subplot(234);
for ii=1:length(lydane_epochs_0)
    plot(lydane_cjd(ii,:)-lydane_cjd(ii,1),lydane_pom(ii,:)*%CL_rad2deg,"Color",Color(ii))
end
legend(legend_name)
title('Argument of perigee')
xlabel('Elapsed days since launch')
ylabel('Argument of perigee (deg)')
CL_g_stdaxes();

subplot(235);
for ii=1:length(lydane_epochs_0)
    plot(lydane_cjd(ii,:)-lydane_cjd(ii,1),lydane_RAAN(ii,:)*%CL_rad2deg,"Color",Color(ii))
end
legend(legend_name)
title('RAAN')
xlabel('Elapsed days since launch')
ylabel('RAAN (deg)')
CL_g_stdaxes();

subplot(236);
for ii=1:length(lydane_epochs_0)
    plot(lydane_cjd(ii,:)-lydane_cjd(ii,1),lydane_M(ii,:)*%CL_rad2deg,"Color",Color(ii))
end
legend(legend_name)
title('Mean Anomaly')
ylabel('Mean Anomaly (deg)')
xlabel('Elapsed days since launch')
CL_g_stdaxes();

scf(1).figure_size=[2000,1000];
deletefile('orbit_evolution_lydane.png');
xs2png(1,'orbit_evolution_lydane.png');

for ii=1:length(lydane_epochs_0)
    csvWrite([(lydane_cjd(ii,:)'-lydane_cjd(ii,1))*86400,sun_x_eci(ii,:)',sun_y_eci(ii,:)',sun_z_eci(ii,:)'],strcat(['sun_eci_',string(stela_selected_days(ii)),'.csv']))
    csvWrite([(lydane_cjd(ii,:)'-lydane_cjd(ii,1))*86400,sat_x_eci(ii,:)',sat_y_eci(ii,:)',sat_z_eci(ii,:)'],strcat(['sat_eci_',string(stela_selected_days(ii)),'.csv']))
end



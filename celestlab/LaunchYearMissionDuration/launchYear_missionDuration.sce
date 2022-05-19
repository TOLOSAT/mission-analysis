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

// Starting epochs
years=2024:2036


// Initial mean keplerian parameters corresponding to the Polar orbit
disp("Initiating mean keplerian parameters");
sma = CL_dataGet("body.Earth.eqRad")+500e3      // Semi-major axis [m]
ecc = 2.e-3                                     // Eccentricity [-]
inc = CL_op_ssoJ2("i", sma, ecc)                // Inclination [rad]
pom = %pi/2;                                    // Argument of perigee [rad]
mlh = 6;                                        // MLTAN [hours]

anm = 0;                                        // Mean anomaly [rad]
cjd=zeros(length(years),1)
kep_mean_ini=zeros(6,length(years))
for ii=1:length(years)
    cjd0(ii) = CL_dat_cal2cjd(years(ii),01,02,12,0,0);       // Julian date initial time [Julian days]
    gom = CL_op_locTime(cjd0(ii), "mlh", mlh, "ra");    // Right ascension (longitude) of the ascending node (RAAN) [rad]
    kep_mean_ini(:,ii) = [sma;ecc;inc;pom;gom;anm]
end



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
data_dir=strsubst(pwd(),"LaunchYearMissionDuration","Data");
params_stela.solarActivityFile =strcat([data_dir,"\stela_solar_activity.txt"]); // predicted Geomagnetic index in 2024 same method as for the solar flux

// Setup epochs vector
params_stela.integrator_step = 2*%pi*sqrt(sma^3/%CL_mu); // exactly an orbit // 92*60; //92 minutes which is roughly an orbit
step_stela= (params_stela.integrator_step)/86400; // propagation step in days
for ii=1:length(years)
    cjd_stela(ii,:)=cjd0(ii)+(0:step_stela:3000);
end


//Propagation with default solar activity
//sma_stela = %nan*zeros(length(years),50000);
//inc_stela = sma_stela;
//RAAN_stela =sma_stela;
//ecc_stela = sma_stela;
//pom_stela = sma_stela;
//mltan = sma_stela;

for ii=1:length(years)
    disp(strcat(["Beginning STELA propagation ",string(ii),"/",string(length(years))]));
    mean_kep_stela = CL_stela_extrap("kep", cjd0(ii), kep_mean_ini(:,ii), cjd_stela(ii,:), params_stela, 'm');
    size_stela=size(mean_kep_stela);
    nb_epochs(ii)=size_stela(2);
    sma_stela(ii,:) = mean_kep_stela(1,:);
    inc_stela(ii,:) = mean_kep_stela(3,:);
    RAAN_stela(ii,:) =mean_kep_stela(5,:);
    ecc_stela(ii,:) = mean_kep_stela(2,:);
    pom_stela(ii,:) = mean_kep_stela(4,:);
    mltan(ii,:) = CL_op_locTime(cjd_stela(ii,:),"ra", RAAN_stela(ii,:), "mlh");
end
disp("Completed STELA propagation");

//Propagation using GMAT's solar activity
//params_stela_nm = params_stela;
//mean_kep_stela_nm = CL_stela_extrap("kep", cjd0, kep_mean_ini, cjd_stela, params_stela_nm, 'm');

//Getting ready for the plots



// =====================================================
// PLOTS OF THE ORBIT EVOLUTION
// =====================================================

colors=[[0, 135, 108];
[61, 154, 112];
[100, 173, 115];
[137, 191, 119];
[175, 209, 124];
[214, 225, 132];
[255, 241, 143];
[253, 213, 118];
[251, 184, 98];
[245, 155, 86];
[238, 125, 79];
[227, 94, 78];
[212, 61, 81]]/255;

legend_strings=string(years)


scf(1);
subplot(231)
for ii=1:length(years)
    plot(cjd_stela(ii,:)-cjd0(ii,:),sma_stela(ii,:) - %CL_eqRad,'color',colors(ii,:))
end
title('Altitude decay with STELA propagation')
xlabel('Elapsed days since launch') 
ylabel('Altitude (m)')
legend(legend_strings)
CL_g_stdaxes();

subplot(232)
for ii=1:length(years)
    plot(cjd_stela(ii,:)-cjd0(ii,:),inc_stela(ii,:)*%CL_rad2deg,'color',colors(ii,:))
end
title('Inclination with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('Inclination (deg)')
CL_g_stdaxes();

subplot(233)
for ii=1:length(years)
    plot(cjd_stela(ii,:)-cjd0(ii,:),ecc_stela(ii,:),'color',colors(ii,:))
end
title('Eccentricity with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('Eccentricity')
CL_g_stdaxes();

subplot(234);
for ii=1:length(years)
    plot(cjd_stela(ii,:)-cjd0(ii,:),pom_stela(ii,:)*%CL_rad2deg,'color',colors(ii,:))
end
title('Argument of perigee with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('Argument of perigee (deg)')
CL_g_stdaxes();

subplot(235);
for ii=1:length(years)
    plot(cjd_stela(ii,:)-cjd0(ii,:),RAAN_stela(ii,:)*%CL_rad2deg,'color',colors(ii,:))
end
title('RAAN TOLOSAT with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('RAAN (deg)')
CL_g_stdaxes();

subplot(236);
for ii=1:length(years)
    plot(cjd_stela(ii,:)-cjd0(ii,:),mltan(ii,:),'color',colors(ii,:))
end
title('Evolution of the MLTAN during the TOLOSAT mission')
ylabel('MLTAN [hours]')
xlabel('Elapsed days since launch')
CL_g_stdaxes();

scf(1).figure_size=[2000,1000];
deletefile('launchYear_missionDuration.png')
sleep(1000)
xs2png(1,'launchYear_missionDuration.png');


csvWrite(years,'years.csv')
csvWrite(cjd_stela,'cjd_stela.csv')
csvWrite(cjd0,'cjd0.csv')
csvWrite(sma_stela,'sma.csv')
csvWrite(inc_stela,'inc.csv')
csvWrite(ecc_stela,'ecc.csv')
csvWrite(pom_stela,'pom.csv')
csvWrite(RAAN_stela,'RAAN.csv')
csvWrite(mltan,'mltan.csv')













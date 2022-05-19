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


// Initial mean keplerian parameters corresponding to the targeted Polar orbit
disp("Initiating mean keplerian parameters");
sma_0 = (CL_dataGet("body.Earth.eqRad")+500e3);      // Semi-major axis [m]
ecc_0 = 2.e-3;                                     // Eccentricity [-]
inc_0 = CL_op_ssoJ2("i", sma_0, ecc_0);                // Inclination [rad]
pom_0 = %pi/2;                                    // Argument of perigee [rad]
mlh = 6;                                        // MLTAN [hours]
cjd0 = CL_dat_cal2cjd(2024,01,02,12,0,0);       // Julian date initial time [Julian days]
gom_0 = CL_op_locTime(cjd0, "mlh", mlh, "ra");    // Right ascension (longitude) of the ascending node (RAAN) [rad]
anm_0 = 0;     

sma = sma_0*[1,1,1];
ecc = ecc_0*[1,1,1];
inc = inc_0*[1,1,1];
pom = pom_0*[1,1,1];
gom = gom_0*[1,1,1];
anm = anm_0*[1,1,1];



// Initial mean keplerian parameters for the different propagations
sma = sma_0+[35e3,0,-35e3];         // Semi-major axis [m]
ecc = ecc_0+[-1.2e-3,0,1.2e-3];         // Eccentricity [-]
inc = inc_0+[0.2,0,-0.2]*%CL_deg2rad;   // Inclination [rad]
gom = gom_0+[0.2,0,-0.2]*%CL_deg2rad;   // Right ascension (longitude) of the ascending node (RAAN) [rad]

kep_mean_ini = [sma;ecc;inc;pom;gom;anm]
// kep_mean_ini = [sma_0;ecc_0;inc_0;pom_0;gom_0;anm_0];

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
params_stela.integrator_step = 5*2*%pi*sqrt(mean(kep_mean_ini(1))^3/%CL_mu); // exactly five orbit // 92*60; //92 minutes which is roughly an orbit
step_stela= (params_stela.integrator_step)/86400; // propagation step in days
cjd_stela = cjd0 + (0:step_stela:3300); // 3300 for worst case, 1650 for nominal


//Propagation with default solar activity
disp("Beginning STELA propagation");
tic
nb_stela_propagations=length(kep_mean_ini)/6;
nb_stela_epochs=length(cjd_stela);
sma_stela = %nan*zeros(nb_stela_propagations,nb_stela_epochs);
ecc_stela = %nan*zeros(nb_stela_propagations,nb_stela_epochs);
inc_stela = %nan*zeros(nb_stela_propagations,nb_stela_epochs);
pom_stela = %nan*zeros(nb_stela_propagations,nb_stela_epochs);
RAAN_stela = %nan*zeros(nb_stela_propagations,nb_stela_epochs);
anm_stela = %nan*zeros(nb_stela_propagations,nb_stela_epochs);
mltan = %nan*zeros(nb_stela_propagations,nb_stela_epochs);

for ii=1:nb_stela_propagations
    disp(strcat(['Beginning Propagation ',string(ii),'/',string(nb_stela_propagations)]));
    mean_kep_stela = CL_stela_extrap("kep", cjd0, kep_mean_ini(:,ii), cjd_stela, params_stela, 'm');
    sma_stela(ii,:) = mean_kep_stela(1,:);
    ecc_stela(ii,:) = mean_kep_stela(2,:);
    inc_stela(ii,:) = mean_kep_stela(3,:);
    pom_stela(ii,:) = mean_kep_stela(4,:);
    RAAN_stela(ii,:) = mean_kep_stela(5,:);
    anm_stela(ii,:) = mean_kep_stela(6,:);
    mltan(ii,:) = CL_op_locTime(cjd_stela,"ra", mean_kep_stela(5,:), "mlh");
    DeltaT_average=toc()/ii;
    remaining_time=(nb_stela_propagations-ii)*DeltaT_average;
    seconds=modulo(remaining_time,60);
    minutes=(remaining_time-seconds)/60;
    hours=(minutes-modulo(minutes,60))/60;
    minutes=modulo(minutes,60);
    disp(strcat(['Propagation ',string(ii),'/',string(nb_stela_propagations),' (',string(ii/nb_stela_propagations*100),' %)',' Remaining : ',string(hours),' hours ',string(minutes),' minutes ',string(seconds),' seconds']));
    
end
disp("Completed STELA propagation");

//Propagation using GMAT's solar activity
//params_stela_nm = params_stela;
//params_stela_nm.solarActivityFile = 'G:\Mon Drive\Supaero Cours\TOLOSAT\acsol2022_2030.txt';
//mean_kep_stela_nm = CL_stela_extrap("kep", cjd0, kep_mean_ini, cjd_stela, params_stela_nm, 'm');


// =====================================================
// ECLIPSES
// =====================================================


timestep_central=1; // 30;
eclipse_duration_umb=%nan*zeros(nb_stela_propagations,nb_stela_epochs);
//eclipse_duration_umbc=%nan*zeros(nb_stela_propagations,nb_stela_epochs);
//eclipse_duration_pen=%nan*zeros(nb_stela_propagations,nb_stela_epochs);

pos_ECI_sat=%nan*zeros(nb_stela_propagations*nb_stela_epochs*5700,3);
pos_ECI_sun=%nan*zeros(nb_stela_propagations*nb_stela_epochs*5700,3);

disp("Beginning eclipses computations");
tic
counter=0;
epoch=1;
for jj=1:nb_stela_propagations
    for ii=1:nb_stela_epochs
        counter=counter+1;
        if ~isnan(sma_stela(jj,ii)) 
            kep_central_ini=[sma_stela(jj,ii);ecc_stela(jj,ii);inc_stela(jj,ii);pom_stela(jj,ii);RAAN_stela(jj,ii);anm_stela(jj,ii)]
            Torbit_tmp=2*%pi*sqrt(sma_stela(jj,ii)^3/%CL_mu);
            epochs=cjd_stela(ii)+(0:timestep_central:Torbit_tmp)/86400;
            kep_tmp=CL_ex_propagate("central", "kep", cjd_stela(ii),kep_central_ini,epochs,'m')
            [pos_ECI,vel_ECI] = CL_oe_kep2car(kep_tmp);     // Conversion to cartesian coordinates
            Sun_eci = CL_eph_sun(epochs);                              // Position of the Sun in ECI coordinates
            pos_ECI_sat(epoch:(epoch + length(epochs)-1),:)=pos_ECI';
            pos_ECI_sun(epoch:(epoch + length(epochs)-1),:)=Sun_eci';
            epoch=epoch+length(epochs);
            eclipse_umb = CL_ev_eclipse(epochs,pos_ECI,Sun_eci,typ='umb');     // Compute eclipse start and end times
//            eclipse_umbc = CL_ev_eclipse(epochs,pos_ECI,Sun_eci,typ='umbc');     // Compute eclipse start and end times
//            eclipse_pen = CL_ev_eclipse(epochs,pos_ECI,Sun_eci,typ='pen');     // Compute eclipse start and end times
            eclipse_duration_umb(jj,ii) = sum((eclipse_umb(2,:) - eclipse_umb(1,:)))*86400;
//            eclipse_duration_umbc(jj,ii) = sum((eclipse_umbc(2,:) - eclipse_umbc(1,:)))*86400;
//            eclipse_duration_pen(jj,ii) = sum((eclipse_pen(2,:) - eclipse_pen(1,:)))*86400;
        end,
    DeltaT_average=toc()/counter;
    remaining_time=(nb_stela_epochs*nb_stela_propagations-counter)*DeltaT_average;
    seconds=modulo(remaining_time,60);
    minutes=(remaining_time-seconds)/60;
    hours=(minutes-modulo(minutes,60))/60;
    minutes=modulo(minutes,60);
    if modulo(counter,10)==0
        disp(strcat(['Computation ',string(counter),'/',string(nb_stela_epochs*nb_stela_propagations),' (',string(counter/(nb_stela_epochs*nb_stela_propagations)*100),' %)',' Remaining : ',string(hours),' hours ',string(minutes),' minutes ',string(seconds),' seconds']));
    end
    end
end

nb_epochs_nonan=sum(~isnan(pos_ECI_sat(:,1)));
pos_ECI_sat=pos_ECI_sat(1:nb_epochs_nonan,3);
pos_ECI_sun=pos_ECI_sun(1:nb_epochs_nonan,3);


csvWrite(pos_ECI_sat,"pos_ECI_sat.csv");
csvWrite(pos_ECI_sun,"pos_ECI_sun.csv");

// =====================================================
// PLOTS OF THE ORBIT EVOLUTION
// =====================================================
Color=["blue","red","green"];
//legend_name=["Target Orbit"]
//legend_name=["sma+35km","target sma","sma-35km"];
//legend_name=["ecc+1.2e-3","target ecc","ecc-1.2e-3"];
//legend_name=["inc+0.2°","target inc","inc-0.2°"];
//legend_name=["RAAN+0.2°","target RAAN","RAAN-0.2°"];
legend_name=["sma+35km, ecc-1.2e-3, inc+0.2°, RAAN+0.2°","target orbit","sma-35km, ecc+1.2e-3, inc-0.2°, RAAN-0.2°"]

scf();
subplot(231)
for ii=1:nb_stela_propagations
    plot(cjd_stela-cjd0,sma_stela(ii,:) - %CL_eqRad, 'Color',Color(ii))
end
title('Altitude decay with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('Altitude (m)')
CL_g_stdaxes();
legend(legend_name)

subplot(232)
for ii=1:nb_stela_propagations
    plot(cjd_stela-cjd0,inc_stela(ii,:)*%CL_rad2deg, 'Color',Color(ii))
end
title('Inclination with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('Inclination (deg)')
CL_g_stdaxes();
legend(legend_name)

subplot(233)
for ii=1:nb_stela_propagations
    plot(cjd_stela-cjd0,ecc_stela(ii,:), 'Color',Color(ii))
end
title('Eccentricity with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('Eccentricity')
CL_g_stdaxes();
legend(legend_name)

subplot(234);
for ii=1:nb_stela_propagations
    plot(cjd_stela-cjd0,pom_stela(ii,:)*%CL_rad2deg, 'Color',Color(ii))
end
title('Argument of perigee with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('Argument of perigee (deg)')
CL_g_stdaxes();
legend(legend_name)

subplot(235);
for ii=1:nb_stela_propagations
    plot(cjd_stela-cjd0,RAAN_stela(ii,:)*%CL_rad2deg, 'Color',Color(ii))
end
title('RAAN TOLOSAT with STELA propagation')
xlabel('Elapsed days since launch')
ylabel('RAAN (deg)')
CL_g_stdaxes();
legend(legend_name)

subplot(236);
for ii=1:nb_stela_propagations
    plot(cjd_stela-cjd0,mltan(ii,:),'.','MarkerSize',2,'Color','Blue', 'Color',Color(ii))
end
title('Evolution of the MLTAN during the TOLOSAT mission')
ylabel('MLTAN [hours]')
xlabel('Elapsed days since launch')
CL_g_stdaxes();
legend(legend_name)


scf();
for ii=1:nb_stela_propagations
    plot(cjd_stela-cjd0,eclipse_duration_umb(ii,:)/60,'.','MarkerSize',2,'Color',Color(ii))
//    plot(cjd_stela-cjd0,eclipse_duration_umbc(ii,:)/60,'o','MarkerSize',2,'Color',Color(ii))
//    plot(cjd_stela-cjd0,eclipse_duration_pen(ii,:)/60,'x','MarkerSize',2,'Color',Color(ii))
end

title('Evolution of the eclipse duration during the TOLOSAT mission')
legend(legend_name)

ylabel('Eclipse duration [mins]')
xlabel('Elapsed days since launch')
CL_g_stdaxes();


csvWrite(cjd_stela,'cjd_stela.csv')
csvWrite(cjd0,'cjd0.csv')
csvWrite(legend_name','legend_name.csv')
csvWrite(sma_stela,'sma_stela.csv')
csvWrite(inc_stela,'inc_stela.csv')
csvWrite(ecc_stela,'ecc_stela.csv')
csvWrite(pom_stela,'pom_stela.csv')
csvWrite(RAAN_stela,'RAAN_stela.csv')
csvWrite(mltan,'mltan.csv')
csvWrite(eclipse_duration_umb,'eclipse_duration_umb.csv')












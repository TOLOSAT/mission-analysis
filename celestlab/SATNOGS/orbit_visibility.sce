clear all;
CL_init();

//= = = = = = = = = = = = = = = = = = = = = = =  Variable  = = = = = = = = = = = = = = = = = = = = = = =  
time_step =60/86400;   // in days
duration =1/24; // in days

rTerre = 6378e3 ;
t0 = CL_dat_cal2cjd(2024,07,02,12,0,0); //year, month day;    // initial time
t = t0 + (0:time_step:duration) ;
freq_emission = 1617.e6;
Delta_doppler_max = 345; // +/- 345Hz par seconde de DopplerShift max.


//= = = = = = = = = = = = = = = = = = = = = = =  generer la constellation  = = = = = = = = = = = = = = = = = = = = = = =  

[kepConst, sat_angle_lim, cen_angle_lim, freq_emission_const, freq_reception_const] = generate_constellation("IridiumNext");

//= = = = = = = = = = = = = = = = = = = = = = =  generation satellite  = = = = = = = = = = = = = = = = = = = = = = =  

//  ==>  ==>  ==>  ==>  ==>  ==>  ==>  ==>  eart  keplerian parameters 

/*
[pos_sat, jacob] = CL_co_sph2car([0*%pi/180; 0*%pi/180; (rTerre)])
[pos_sat,vel_sat]= CL_fr_convert("ECI", "ECF", t, pos_sat,[7909.4;0;0]);
kep_mean_ini = CL_oe_car2kep(pos_sat, vel_sat)
*/
//  ==>  ==>  ==>  ==>  ==>  ==>  ==>  ==>  ISS keplerian parameters 
/*
sma = 6793.23722*10^3 ;   //sma 
ecc = 3.8e-4 ;
inc = 51.6*%CL_deg2rad;
pom = 89.4772*%CL_deg2rad;
mlh = 6; // MLTAN (hours)
gom = 344,5650*%CL_deg2rad;
anm = 4.9;
kep_mean_ini = [  sma;     // demi grand axe (m)
                  ecc;     // excentricité
                  inc;     // inclinaison (rad)
                  pom;     // argument du périastre, petit omega (rad)
                  gom;     // longitude du noeud ascendant raan (rad)  
                  anm] 
*/
//  ==>  ==>  ==>  ==>  ==>  ==>  ==>  ==>  Polar orbit 

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


//= = = = = = = = = = = = = = = = = = = = = = =  generation  = = = = = = = = = = = = = = = = = = = = = = =  
kep_sat = CL_ex_secularJ2(t0,kep_mean_ini,t); 

//convertion to cartesian position and velocity:
[pos_sat, vel_sat] = CL_oe_kep2car(kep_sat);
[pos_sat,vel_sat]= CL_fr_convert("ECI", "ECF", t, pos_sat,[vel_sat]);
[i,j]=size(pos_sat);

//= = = = = = = = = = = = = = = = = = = = = = =  visibilité  = = = = = = = = = = = = = = = = = = = = = = =  

data = [];
t1=t0;
[n, m] = size(kepConst)
Doppler_list=zeros(1,m)
delta=[];
Dopp=[]
for l=1:(j-1)
//calcul à t1 des paramètres de chaque satellite Iridium
    kep = CL_ex_secularJ2(t0, kepConst, t1);
    [pos, vel] = CL_oe_kep2car(kep);
    [pos,vel]= CL_fr_convert("ECI", "ECF", t1,pos,[vel]);

// calcul des angles entre notre satellites et tout les sattelites d'iridium

    sat_angle = CL_vectAngle(CL_dMult(ones(1,m),pos_sat(l))-pos, -pos);
    cen_angle = CL_vectAngle(pos_sat(l), pos);
    printf(l)
   
//Initialisation des paramètres pour regarder si c'est visible
      
    visibles = 0;
    
// Pour chaque sattelite de Iridium 
// on regarde si il voit notre sattellite 
// puis on regarde l'effet doppler
// puis on regarde la variation de celui-ci par rapport au temps precedent d'avant
delta_l=[]
    for k=1:m
        vis=((sat_angle(k) < sat_angle_lim) & (cen_angle(k) < cen_angle_lim))*1
         
        shift = doppler_shift(pos(:,k), vel(:,k), pos_sat(l), vel_sat(l), freq_emission)
        Delta_dopp = abs((Doppler_list(1,k)-shift))/time_step;
        if vis==1 then
            if (abs(shift)<35000) then
                
                
                
                if (Delta_dopp < Delta_doppler_max) then
                    
                    visibles = vis + visibles;
                end 
            end 
            end
        Doppler_list(1,k)=shift
        delta_l=[delta_l, Delta_dopp]
    end    
    data = [data; visibles] ;
    delta=[delta;delta_l]
    t1=t1+time_step;
    Dopp=[Dopp;Doppler_list]
end

//= = = = = = = = = = = = = = = = = = = = = = =  exploitation  = = = = = = = = = = = = = = = = = = = = = = =

[duree_visibilite, duree_moy_session, sessions] = exploitation(data);

scf(1)
subplot(2,1,1)
plot(t(2:j)',delta(2:j,:))
xlabel('temps')
ylabel('delta doppler')
title('variation de leffet doppler par pas de temps')

subplot(2,1,2)
plot(t(2:j)',Dopp(2:j,:))
xlabel('temps')
ylabel(' effet doppler')
title(' effet doppler par pas de temps')

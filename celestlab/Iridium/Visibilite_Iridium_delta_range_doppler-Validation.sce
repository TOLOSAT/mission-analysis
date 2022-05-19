clear all;
CL_init();

//= = = = = = = = = = = = = = = = = = = = = = =  Variables  = = = = = = = = = = = = = = = = = = = = = = =  

time_step = 4/86400;   // in days
duration = 1/24; // in days

t0 = CL_dat_cal2cjd(2024,07,02,12,0,0); //year, month day;    // initial time
t = t0 + (0:time_step:duration) ;
freq_emission = 1617.e6;
Delta_doppler_max = 345; // +/- 345Hz par seconde de DopplerShift max.

Validation_du_code = %f ; // validation du code avec observateur au sol (%t= 1 ; %f =0)

//= = = = = = = = = = = = = = = = = = = = = = =  generer la constellation  = = = = = = = = = = = = = = = = = = = = = = =  

[kepConst, sat_angle_lim, cen_angle_lim, freq_emission_const, freq_reception_const] = generate_constellation("IridiumNext");


if  Validation_du_code  then
//= = = = = = = = = = = = = = = = = = = = = = =  position antenne terrestre= = = = = = = = = = = = = = = = = = = = = = =  
    j = length(t);    
    //= = = = = = = = = = = = = = = = = = = = = = =  generation  = = = = = = = = = = = = = = = = = = = = = = =  
    pos_obs = [1.43*%CL_deg2rad; 43.6*%CL_deg2rad ;143]; // antenna position in elliptical coordinate (lon,lat,alt) 
    pos_obs_car = CL_co_ell2car(pos_obs); // position in ECF frame
    pos_antenna =  pos_obs_car;
    //pos_antenna = repmat(pos_obs_car, 1, j); // constant position on the surface of earth

    //= = = = = = = = = = = = = = = = = = = = = = =  visibilité  = = = = = = = = = = = = = = = = = = = = = = =  
    
    sessions = list();
    data = [];
    t1=t0;
    [n, m] = size(kepConst)
    Doppler_list=zeros(1,m)
    delta=[];
    Dopp=[]
    for l=1:j
    //calcul à t1 des paramètres de chaque satellite Iridium
        kep = CL_ex_propagate("eckhech","kep",t0, kepConst, t1,'o');
        [pos, vel] = CL_oe_kep2car(kep);
        [pos,vel]= CL_fr_convert("ECI", "ECF", t1,pos,[vel]);
    
    // calcul des angles entre notre satellites et tout les sattelites d'iridium
    
        sat_angle = CL_vectAngle(CL_dMult(ones(1,m),pos_antenna)-pos, -pos);
        cen_angle = CL_vectAngle(pos_antenna, pos);
       
    //Initialisation des paramètres pour regarder si c'est visible
          
        visibles = 0;
        
    // Pour chaque sattelite de Iridium 
    // on regarde si il voit notre sattellite 
    // puis on regarde l'effet doppler
    // puis on regarde la variation de celui-ci par rapport au temps precedent d'avant
        delta_l=[]
        for k=1:m
            vis=((sat_angle(k) < sat_angle_lim) & (cen_angle(k) < cen_angle_lim))*1
             
            shift = doppler_shift(pos(:,k), vel(:,k), pos_antenna, [0;0;0], freq_emission)
            Delta_dopp = abs((Doppler_list(1,k)-shift))/(time_step*86400);
            visibles = vis + visibles;
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
    
    [duree_visibilite, duree_moy_session, sessions] = exploitation(data,time_step, duration);
    
    scf(1)
    subplot(2,1,1)
    plot((t(2:j)'-t0)*1440,delta(2:j,1:15))
    xlabel('temps ecoulé (min)')
    ylabel('delta doppler')
    title(' valeur absolue variation de l''effet doppler par pas de temps')
    
    subplot(2,1,2)
    plot((t(2:j)'-t0)*1440,Dopp(2:j,1:15))
    xlabel('temps ecoulé (min)')
    ylabel(' effet doppler')
    title(' effet doppler par pas de temps')

    scf(3)
    plot((t-t0)*1440,data)
    xlabel('temps ecoulé (min)')
    ylabel(' Visible satellites')
    title('Visible satellites')
    
    

end  

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

if  ~Validation_du_code then

//= = = = = = = = = = = = = = = = = = = = = = =  generation satellite  = = = = = = = = = = = = = = = = = = = = = = =  
    
    //  ==>  ==>  ==>  ==>  ==>  ==>  ==>  ==>  ISS keplerian parameters 
    /*
    sma = 6798.e3 ;   //sma 
    ecc = 1.5e-4 ;
    inc = 51.6*%CL_deg2rad;
    pom = 238*%CL_deg2rad;
    mlh = 6; // MLTAN (hours)
    gom = 204*%CL_deg2rad;
    anm = 0;
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
    elevations_over_t = [];
    t1=t0;
    [n, m] = size(kepConst)
    Doppler_list=zeros(1,m);
    delta=[];
    Dopp=[]
    t1_old = t1;
    for l=1:j // boucle sur le temps  t = t0+dt*l
    //calcul à t1 des paramètres de chaque satellite Iridium
        kepConst = CL_ex_secularJ2(t1_old, kepConst, t1);
        kep = kepConst;
        [pos, vel] = CL_oe_kep2car(kep);
        [pos,vel]= CL_fr_convert("ECI", "ECF", t1,pos,[vel]);
    
    // calcul des angles entre notre satellites et tout les sattelites d'iridium
    
        sat_angle = CL_vectAngle(CL_dMult(ones(1,m),pos_sat(:,l))-pos, -pos);
        cen_angle = CL_vectAngle(pos_sat(:,l), pos);
       
    //Initialisation des paramètres pour regarder si c'est visible
          
        visibles = 0;
        
    // Pour chaque sattelite de Iridium 
    // on regarde si il voit notre sattellite 
    // puis on regarde l'effet doppler
    // puis on regarde la variation de celui-ci par rapport au temps precedent d'avant
        delta_l=[0]
        els = zeros(1,m);
        for k=1:m // k is iridium index
            vis=((sat_angle(k) < sat_angle_lim) & (cen_angle(k) < cen_angle_lim))*1;
             
            shift = doppler_shift(pos(:,k), vel(:,k), pos_sat(:,l), vel_sat(:,l), freq_emission);
            if l <= 2 then
                Delta_dopp = 0;
            else
                Delta_dopp = (shift-Dopp(l-2,k))/(2*time_step*86400);
            end
            el = 90-sat_angle(k)*%CL_rad2deg-cen_angle(k)*%CL_rad2deg;
            els(k) = el;
            if vis==1 then
                if (abs(shift)<35000) then
                    
                    if (abs(Delta_dopp) < Delta_doppler_max) then
                        
                        visibles = vis + visibles;
                        
                    end 
                end 
                end
            Doppler_list(1,k)=shift;
            delta_l=[delta_l, Delta_dopp];
            
        end 
        data = [data; visibles] ;
        delta=[delta;delta_l];
        t1_old = t1;
        t1=t1+time_step;
        Dopp=[Dopp;Doppler_list];
        elevations_over_t = [elevations_over_t; els];
    end
    
    //= = = = = = = = = = = = = = = = = = = = = = =  exploitation  = = = = = = = = = = = = = = = = = = = = = = =
    
    [duree_visibilite, duree_moy_session, sessions] = exploitation(data,time_step, duration)
    
    // selet only sats that had elevation >= 25deg at one moment during the simulation period
    visible_sats = [];
    for k=1:m
        if max(elevations_over_t(:,k)) > 25 then // if elevation is less than 27deg, Iridium can't see TOLOSAT
            visible_sats = [visible_sats, k];
        end
    end
    
    scf()
    subplot(2,1,1)
    plot((t'-t0)*1440, elevations_over_t(:,visible_sats))
    xlabel('Elapsed Time [min]')
    ylabel('Elevation relative to TOLOSAT [deg]')
    title('Iridium Constellation Sessions')
    CL_g_stdaxes()
    set(gca(),'data_bounds',[0,0; 60*24*duration,90])
    subplot(2,1,2)
    plot((t(2:j)'-t0)*1440,delta(2:j,visible_sats))
    xlabel('Elapsed Time [min]')
    ylabel('Doppler Rate [Hz/s]')
    CL_g_stdaxes()
    set(gca(),'data_bounds',[0,-500; 60*24*duration,4500])
    
    
    scf(1)
    subplot(2,1,1)
    plot((t(2:j)'-t0)*1440,delta(2:j,visible_sats))
    xlabel('temps ecoulé (min)')
    ylabel('delta doppler')
    title('variation de l''effet doppler par pas de temps')
    CL_g_stdaxes()
    
    subplot(2,1,2)
    plot((t(2:j)'-t0)*1440,Dopp(2:j,visible_sats))
    xlabel('temps ecoulé (min)')
    ylabel(' effet doppler')
    title(' effet doppler par pas de temps')
    CL_g_stdaxes()
    
    scf(3)
    plot((t-t0)*1440,data)
    xlabel('temps ecoulé (min)')
    ylabel('Visible satellites')
    title('Visible satellites ')
    CL_g_stdaxes()

end

clear all
CL_init();
//Constantes globales
rTerre = 6378e3; //rayon terreste (m)
dt = 2/86400;
t_total = 2/24; //jour

tref = CL_dat_cal2cjd(2024,07,02,12,0,0); 
t = tref + (0 : dt : t_total); //matrice temps



//=========================================   generation constellation   ==================================================
// genere les coordonnées de Kepler d'une constellation à orbite circulaire

function [kepConst, sat_angle_lim, cen_angle_lim, freq_emission_const, freq_reception_const] = generate_constellation(name)
    kepConst = [];
    angle_visibilite = 0;
    freq_emission_const = 0;
    freq_reception_const = 0;
    
    if (name == "Iridium") then
        freq_reception_const = 1617.e6;
        freq_emission_const = 1617.e6;
        
        [myFile, content] = getURL("https://www.celestrak.com/NORAD/elements/iridium.txt");
        tle = CL_tle_load(myFile);
        [kep_recup, tle_time] = CL_tle_getElem(tle, "kep")
        
        names = tle.desc
        pattern = '/([ \w]+) (\d+) \[(.)\]\s/';
        [start end match foundstr] = regexp(content, pattern);
        filtre = (foundstr(:,3) <> '-')'
        
        kepConst = CL_ex_secularJ2(tle_time(filtre), kep_recup(:,filtre), tref)
        
        [sat_angle_lim, cen_angle_lim] = CL_gm_visiParams(max(kepConst(1,:)), rTerre,'elev', 0, ['sat','cen'])
    end
    if (name =="GlobalStar") then
        freq_reception_const = 1617.e6;
        freq_emission_const = 2490.e6;
        
        [myFile, content] = getURL("https://www.celestrak.com/NORAD/elements/globalstar.txt");
        tle = CL_tle_load(myFile);
        [kep_recup, tle_time] = CL_tle_getElem(tle, "kep")
        
        names = tle.desc
        pattern = '/([ \w]+) M(\d+) \[(.)\]\s/';
        [start end match foundstr] = regexp(content, pattern);
        filtre = (foundstr(:,3) <> '-')'
        
        kepConst = CL_ex_secularJ2(tle_time(filtre), kep_recup(:,filtre), tref)
        
        [sat_angle_lim, cen_angle_lim] = CL_gm_visiParams(max(kepConst(1,:)), rTerre,'elev', 0, ['sat','cen'])
    end
    if (name == "IridiumNext") then
        freq_reception_const = 1617.e6;
        freq_emission_const = 1617.e6;
        
        [myFile, content] = getURL("https://www.celestrak.com/NORAD/elements/iridium-NEXT.txt");
        tle = CL_tle_load(myFile);
        [kep_recup, tle_time] = CL_tle_getElem(tle, "kep")
        
        kepConst = CL_ex_secularJ2(tle_time, kep_recup, tref)
        
        [sat_angle_lim, cen_angle_lim] = CL_gm_visiParams(max(kepConst(1,:)), rTerre,'sat',62.9*%pi/180,['sat','cen'])
    end
    
endfunction
//================================================================================================================

//========================================   doppler ======================
// calcul de la difference entre la frequence emise et la frequence recue
function [shift] = doppler_shift(xs, vs, xr, vr, fem)
    u_sr = (xr-xs) ./ CL_norm(xr-xs) //vecteur directeur entre les deux satellites
    c = 3.e8;
    shift = fem * (1-(c - sum(vr.*u_sr)) ./ (c - sum(vs.*u_sr))); // delta_f = f * (1 - (c-vr)/(c-vs))
endfunction


//=========================================== Exploitation des constellations ( contact) =================================================
// duree_visibilite : selon le pas de tpms il va voir temps de temps par jour la constellation (min))
// La duree moyenne : d'une session ouverte (le sat est en contact sur dt d'affile)
// session : temps sur laquelle il y a une session d'ouverte

function [duree_visibilite, duree_moy_session, sessions] = exploitation(satellites_visibles)
    
    reseau = (satellites_visibles >= 1)*1;
    duree_visibilite = sum(reseau) / (t_total/dt+1)*1440 //min())
    sessions = [];
    session_active = 0;
    
    for i=1:t_total/dt+1
        if (reseau(i) == 1) then
            session_active = session_active + 1;
        else
            if (session_active > 0) then
                sessions = [sessions, session_active*dt*86400];    
            end
            session_active = 0;
        end
    end
    
    if (session_active > 0) then
        sessions = [sessions, session_active*dt*86400];    
    end
    
    duree_min_session = min(sessions);
    duree_max_session = max(sessions);
    duree_moy_session = mean(sessions);// duree moyenne d'une session en seconde
    
endfunction
 

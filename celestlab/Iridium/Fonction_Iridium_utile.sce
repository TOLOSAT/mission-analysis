clear all
CL_init();
//Constantes globales
rTerre = 6378e3; //rayon terreste (m)
dt = 2/86400;
t_total = 1/24; //jour

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
        
        // ANCHOR : modified elev=0 to sat=62.9deg (Nils, 2021-10-07)
        // iridium sats have 62.9deg half opening angle 
        // source : Pratt et. al., 1999, An Operational and Performance
        // Review of the Iridium Low Earth Orbit Satellite System
        [sat_angle_lim, cen_angle_lim] = CL_gm_visiParams(max(kepConst(1,:)), rTerre,'sat', 62.9*pi/180, ['sat','cen'])
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

function [duree_visibilite, duree_moy_session, sessions] = exploitation(satellites_visibles,dt, t_total)
    
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

// ============== Helper functions from most recent version =========
function pass_duration = IridiumPassDuration_s(IridiumPass)
    // pass structure example : 
    // example_pass = struct('start_date_cjd', t(100), 'end_date_cjd', t(106), 'sat_number', 46);
    // returns : pass duration in seconds
    pass_duration = (IridiumPass.end_date_cjd - IridiumPass.start_date_cjd)*86400;
endfunction

function is_visible = visibility_matrix(elevations_over_t, doppler_shifts, doppler_rates, min_el_for_vizi_deg, doppler_max, Delta_doppler_max)
    // inputs : (m=number of iridium sats, j=number of time points)
    //          elevations_over_t : m*j matrix of the elevations of each iridium sat seen by tolosat, in degrees
    //          doppler_shifts : m*j matrix of the doppler shifts seen from each iridium sat by tolosat, in Hz
    //          doppler_rates : m*j matrix of the doppler rates seen from each iridium sat by tolosat, in Hz/s
    //          min_el_for_vizi_deg : minimum elevation seen by tolosat to be in the cone, degrees
    //          doppler_max : max doppler shift, Hz. Usually about 35000
    //          Delta_doppler_max : max doppler rate, Hz. Usually about 345
    
    is_visible = (elevations_over_t >= min_el_for_vizi_deg & ... 
                  abs(doppler_shifts) <= doppler_max & ...
                  abs(doppler_rates) <= Delta_doppler_max)*1; // 0s and 1s
endfunction

function ordered_pass_list = GetIridiumPasses(is_visible, time_step, min_pass_duration_s, t)
    //inputs : visibility matrix (1s and 0s) for each sat and each time step
    //         time step in days
    //         minimum pass duration in seconds
    //output : list of lists of passes. 1st dimension is satellite number, 2nd is time.
    // passes are in the form example_pass = struct('start_date_cjd', t(100), 'end_date_cjd', t(106), 'sat_number', 46);
    [m,j] = size(is_visible);
    ordered_pass_list = list(); // dimension 1 is sat number, dim 2 is time
    for k=1:m
        ordered_pass_list($+1) = list();
    end
    for l_start = 2:j // loop on pass start time
        for k=1:m // loop on sat number
            if (is_visible(k,l_start) & ~is_visible(k,l_start-1)) // rising edge detected
                // now search for falling edge (or end of data)
                maybe_end_l = l_start;
                while ((maybe_end_l <= j) & is_visible(k,maybe_end_l))
                    maybe_end_l = maybe_end_l + 1;
                end
                // now maybe_end_l is either j+1 or the true end index of the pass
                l_end = maybe_end_l - 1;
                // l_start is the first index where the sat is visible. 
                // l_end is the last index where the sat is visible.
                // we ignore passes that are shorter than min_pass_duration
                if (l_end-l_start)*time_step*86400 < min_pass_duration_s
                    continue
                end
                // keep this pass if another pass is not already happening
                if sum(is_visible(:,l_start)) < 1.5
                    pass = struct('start_date_cjd', t(l_start), 'end_date_cjd', t(l_end), 'sat_number', k);
                    ordered_pass_list(k)($+1) = pass;
                end
            end
        end
    end
endfunction


function [mean_passes_per_day, avg_duration_s, all_passes] = IridiumPassStatistics(ordered_pass_list, duration)
    // inputs : list of lists of passes, as outputted by GetIridiumPasses
    //          duration of the simulation in days
    // outputs : 2 scalars + a 1D list of passes in the same format
    if duration <=0 then
        duration = abs(duration)+1/86400;
    end
    m=size(ordered_pass_list);
    N_passes = 0;
    avg_duration_s = 0;
    max_duration_s = 0;
    min_duration_s = 99999999;
    total_duration_s = 0;
    all_passes = list(); // unordered 1D list
    for k=1:m
        for p=1:length(ordered_pass_list(k))
            N_passes = N_passes+1;
            pass = ordered_pass_list(k)(p);
            all_passes($+1) = pass;
            dur = IridiumPassDuration_s(pass);
            avg_duration_s = avg_duration_s + dur;
            max_duration_s = max(max_duration_s, dur);
            min_duration_s = min(min_duration_s, dur);
            total_duration_s = total_duration_s + dur;
        end
    end
    if N_passes == 0 then
        avg_duration_s = 0;
    else
        avg_duration_s = avg_duration_s/N_passes;
    end
    mean_passes_per_day = N_passes/duration;
endfunction

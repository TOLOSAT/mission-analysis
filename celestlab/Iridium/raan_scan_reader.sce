load("raan_scan_results.dat");
m = size(all_ordered_passes(1)); // 75 iridium sats

t_starts = t_all(1:fine_points:$-1);
raan_starts = all_kep_sat(5,1:fine_points:$-1);
diffraan = raan_starts - matrix(all_kep_iridium(5,1,1:fine_points:$), [1 raan_points]);
comms_time = pass_rate.*pass_lens;

scf()
plot(pmodulo(diffraan, 2*%pi), pass_rate, 'bx')
xlabel('RAAN_sat - RAAN_Iridium1 [rad] mod 2pi')
ylabel('Mean passes per day')
title('Effect of RAAN difference on pass rate (dt=5s, 24 hour integration per point)')
CL_g_stdaxes()
scf()
plot(t_starts-t_starts(1), pass_rate)
xlabel('Mission Elapsed time [days]')
ylabel('Mean passes per day')
title('Pass durations over 1 year (dt=5s, 24 hour integration per point)')
CL_g_stdaxes()
scf()
plot(diffraan, comms_time/60)
xlabel('RAAN_sat - RAAN_Iridium1 [rad]')
ylabel('Comms time per day [min/day]')
title('Effect of RAAN difference on total communication time (dt=5s, 24 hour integration per point)')
CL_g_stdaxes()


aol_edges_deg = (0:20:360);
inds=(1:10:73); // day indices that are interesting
for i=1:length(inds)
    // obtain orbit data and passes over the fine sim period
    indices_we_want = ((inds(i)-1)*fine_points+1):(inds(i)*fine_points);
    t_fine = t_all(indices_we_want);
    kep_fine = all_kep_sat(:,indices_we_want);
    ordered_pass_list = all_ordered_passes(inds(i));
    // find aols of each pass
    all_pass_aols = [];
    for k=1:m // for each iridium sat
        for l=1:length(ordered_pass_list(k)) // for each pass of that sat
            // get the start time
            t_kl = ordered_pass_list(k)(l).start_date_cjd;
            // match it with a t_fine
            inds_fine = (1:fine_points);
            pass_start_ind = max(inds_fine(t_fine == t_kl));
            // convert to an aol
            pass_aol = pmodulo(kep_fine(6,pass_start_ind) + kep_fine(4,pass_start_ind), 2*%pi);
            all_pass_aols($+1) = pass_aol*%CL_rad2deg;
        end
    end
    scf()
    histplot(15, all_pass_aols, normalization=%f)
    xlabel('argument of latitude (deg)')
    ylabel('Number of passes')
    title('Pass rate dependency on AoL')
    CL_g_stdaxes()
end


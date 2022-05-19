load("big_savefile.dat");

duration = t($)-t(1);
t0 = t(1);
[mean_passes_per_day, avg_duration_s, all_passes] = IridiumPassStatistics(ordered_pass_list, duration);

printf(' Statistics : \n    Mean Pass Duration (s) : %f \n', avg_duration_s);
printf('    Mean Passes Per Day : %f \n', mean_passes_per_day);
printf('    Mean Communication Time Per Day (min) : %f \n', mean_passes_per_day*avg_duration_s/60);

// RAANs histogram data
passRAANs = zeros(size(all_passes));
raan = 0;
raan_rate = (raans($)-raans(1))/(duration)
bins = 20
raanbinwidth = (2*%pi/bins);
days_per_bin = abs(raanbinwidth/raan_rate)
raanbinstarts = (-%pi):raanbinwidth:(%pi);
raanbincenters = raanbinstarts(1:bins)+raanbinwidth/2;
passrate_in_bin = zeros(1, bins);
for p=1:length(all_passes)
    raan = raans(t==all_passes(p).start_date_cjd);
    if raan > %pi then
        raan = raan - 2*%pi;
    elseif raan < -%pi then
        raan = raan + 2*%pi;
    end
    passRAANs(p) = raan;
    // increment correct bin by 1
    for ind = 1:bins
        if ((raan >= raanbinstarts(ind)) & (raan < raanbinstarts(ind+1))) then
            passrate_in_bin(ind) = passrate_in_bin(ind)+1;
        end
    end
end
// go from pass number in bin to avg pass rate in bin
passrate_in_bin = passrate_in_bin / days_per_bin; 

scf(0)
histplot(bins, passRAANs*%CL_rad2deg, normalization=%f)
xlabel('RAAN (deg)')
ylabel('Number of passes')
title('Pass rate dependency on RAAN')
CL_g_stdaxes()
set(gca(),'data_bounds',[-180, 0; 180, 500])

scf(1)
plot(t-t0, raans)
xlabel('mission elapsed time (days)')
ylabel('RAAN [rad]')
title('Right Ascension of Ascending node, 70 days at 370km 51.6deg')
CL_g_stdaxes()

scf(2)
plot(raanbincenters, passrate_in_bin)
xlabel('RAAN [rad]')
ylabel('passes per day')
title('Pass rate varying with RAAN, 70 days at 370km 51.6deg')
CL_g_stdaxes()

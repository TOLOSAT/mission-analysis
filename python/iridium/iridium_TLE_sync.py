import datetime
import numpy as np
import pandas as pd
from requests import get

from sgp4.api import Satrec, jday, SatrecArray
from sgp4.conveniences import sat_epoch_datetime

from useful_functions import datetime_to_epoch, teme_to_j2000

# Download current iridium Iridium from Celestrak and save to file
iridium_url = ("https://celestrak.org/NORAD/elements/gp.php?GROUP=iridium-NEXT&FORMAT=tle")
TLEs_text = get(iridium_url).text
with open("TLEs.txt", "w", newline="") as f:
    f.write(TLEs_text)
TLEs_lines = TLEs_text.splitlines()

# Parse TLEs into list of dictionaries
satellites = []
for i in range(0, len(TLEs_lines), 3):
    name = TLEs_lines[i].strip()
    line1 = TLEs_lines[i + 1].strip()
    line2 = TLEs_lines[i + 2].strip()
    satellites.append({"name": name, "line1": line1, "line2": line2})

# Filter TLEs no older than 3 days
filtered_satellites = []
now = datetime.datetime.now(datetime.timezone.utc)
max_age = datetime.timedelta(days=5)
for sat in satellites:
    try:
        s = Satrec.twoline2rv(sat["line1"], sat["line2"])
        tle_datetime = sat_epoch_datetime(s)
        if abs(now - tle_datetime) <= max_age:
            filtered_satellites.append({"name": sat["name"], "line1": sat["line1"], "line2": sat["line2"], "satrec": s})
        else:
            print(f"Skipping {sat['name']} (TLE too old: {tle_datetime.date()})")
    except Exception as e:
        print(f"Skipping {sat['name']} (invalid TLE): {e}")

print(f"\n{len(filtered_satellites)} TLEs passed age filtering.")

# Use current UTC datetime as propagation epoch
target_datetime = now.replace(microsecond=0)
target_epoch = datetime_to_epoch(target_datetime)
target_jd, target_fr = jday(
    target_datetime.year,
    target_datetime.month,
    target_datetime.day,
    target_datetime.hour,
    target_datetime.minute,
    target_datetime.second,
)

# Prepare SatrecArray and propagate
sat_objects = [s["satrec"] for s in filtered_satellites]
sat_names = [s["name"] for s in filtered_satellites]
sat_array = SatrecArray(sat_objects)
jd_array = np.full(len(sat_objects), target_jd)
fr_array = np.full(len(sat_objects), target_fr)
errors, positions_km, velocities_kms = sat_array.sgp4(jd_array, fr_array)

# Convert to J2000 states and collect valid results
iridium_states_synced = []
for i, name in enumerate(sat_names):
    if errors[i][0] != 0:
        print(f"SGP4 error for {name} (code {errors[i][0]})")
        continue
    teme_state_km = np.concatenate([positions_km[i][0], velocities_kms[i][0]]) * 1e3  # to meters
    final_state = teme_to_j2000(teme_state_km, target_epoch)
    iridium_states_synced.append(
        dict(
            name=name,
            x=final_state[0],
            y=final_state[1],
            z=final_state[2],
            vx=final_state[3],
            vy=final_state[4],
            vz=final_state[5],
            epoch=target_epoch,
        )
    )

# Convert to DataFrame and extract list of names
iridium_states_synced = pd.DataFrame(iridium_states_synced)
iridium_names = iridium_states_synced["name"].to_list()
start_datetime = target_datetime


# Print summary
print(f" {len(iridium_states_synced)} iridium propagated successfully")
print(f" {len(filtered_satellites) - len(iridium_states_synced)} iridium failed to propagate")

import tletools
from requests import get
from sgp4.api import Satrec, jday

from useful_functions import *

# Get Galileo TLEs and save to file
galileo_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=galileo&FORMAT=tle"
TLEs_text = get(galileo_url).text
with open("TLEs.txt", "w", newline="") as f:
    f.write(TLEs_text)
TLEs_lines = TLEs_text.splitlines()

# Load TLEs into pandas dataframe
TLEs = tletools.pandas.load_dataframe("TLEs.txt")

# Process datetimes
TLEs.rename(columns={"epoch": "datetime"}, inplace=True)
TLEs["epoch"] = datetime_to_epoch(TLEs["datetime"])

# max epoch rounded to next 10
target_year = TLEs["epoch_year"].max()
target_day = np.ceil(TLEs["epoch_day"].max())
target_datetime = datetime.datetime(target_year, 1, 1, 0, 0, 0) + datetime.timedelta(
    days=target_day - 1
)
target_jd, target_fr = jday(
    target_datetime.year,
    target_datetime.month,
    target_datetime.day,
    target_datetime.hour,
    target_datetime.minute,
    target_datetime.second,
)
target_epoch = datetime_to_epoch(target_datetime)

# Sync galileo satellites
galileo_states_synced = []
for i in tqdm(range(len(TLEs)), desc="Syncing TLEs", ncols=80, total=len(TLEs)):
    tle_l1 = TLEs_lines[i * 3 + 1]
    tle_l2 = TLEs_lines[i * 3 + 2]
    sat = Satrec.twoline2rv(tle_l1, tle_l2)
    _, teme_r, teme_v = sat.sgp4(target_jd, target_fr)
    teme_state = np.concatenate((teme_r, teme_v)) * 1e3
    final_state = teme_to_j2000(teme_state, target_epoch)
    galileo_states_synced.append(
        dict(
            name=TLEs.iloc[i].loc["name"],
            x=final_state[0],
            y=final_state[1],
            z=final_state[2],
            vx=final_state[3],
            vy=final_state[4],
            vz=final_state[5],
            epoch=target_epoch,
        )
    )
galileo_states_synced = pd.DataFrame(galileo_states_synced)
galileo_names = galileo_states_synced["name"].to_list()

import geopandas as gpd
import folium
import json
from tqdm import tqdm
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(module)s - : Line (%(lineno)d) - %(message)s",
    level=logging.INFO,
)
import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("mode.chained_assignment", None)


logging.info("get transportation modes per line and merging them to observations")
geom = gpd.GeoDataFrame(pd.read_pickle("data/computed/stops_geom.pkl"))

t = []
for name, group in geom.groupby("ligne_cleaned"):
    t.append((group.iloc[0].ligne_cleaned, group.iloc[0]["mode"]))


modes = pd.DataFrame(t, columns=["ligne_cleaned", "mode"])

obs = pd.read_pickle("data/computed/observed_time.pkl").merge(
    modes, "left", left_on="route_short_name", right_on="ligne_cleaned"
)

logging.info("Emptying memory")
del modes, geom

logging.info("Extracting schedules")


def turn_sec_to_hours(time_in_sec: float) -> str:
    hours = int(time_in_sec / 3600)
    minutes = int(((time_in_sec / 3600) - hours) * 60)
    seconds = int(time_in_sec - hours * 3600 - minutes * 60)
    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)
    if len(str(hours)) == 1:
        hours = "0" + str(hours)
    if len(str(seconds)) == 1:
        seconds = "0" + str(seconds)
    return str(hours) + ":" + str(minutes) + ":" + str(seconds)


def extract_schedule(
    schedule: pd.DataFrame,
    transportation_type: int,
    thresh_gaps: int = 120,
    distance_col: str = "distance_from_point",
    speeds_ms: dict[int, float] = {
        "B": 4.333333333333333,  # Bus
        "T": 4.527777777777778,  # Tram
        "M": 7.749999999999999,  # Metro
    },
) -> pd.DataFrame:
    if schedule.shape[0] > 1:
        schedule.sort_values("time_seconds")
        schedule["lag_-1"] = schedule[distance_col].shift(1)
        schedule["lag_+1"] = schedule[distance_col].shift(-1)
        schedule["t_lag_before"] = schedule.sort_values("time_seconds")[
            "time_seconds"
        ].shift(1)
        schedule["t_diff(sec)"] = schedule["time_seconds"] - schedule["t_lag_before"]

        arr = schedule[(schedule["lag_-1"] > schedule[distance_col])]

        if (schedule.iloc[0][distance_col] > 0) | (
            schedule.iloc[0][distance_col] == 0 & schedule.iloc[1][distance_col] > 0
        ):
            arr = pd.concat([arr, schedule.head(1)])

        dep = schedule[(schedule["lag_+1"] > schedule[distance_col])]
        gaps = schedule[schedule["t_diff(sec)"] > thresh_gaps]

        FS = pd.concat([arr, dep, gaps])

    else:
        FS = schedule

    FS["adjusted_arrival_time(ts)"] = round(
        FS.time_seconds - (FS.distance_from_point / speeds_ms.get(transportation_type)),
        3,
    )
    FS["adjusted_arrival_time"] = FS["adjusted_arrival_time(ts)"].apply(
        turn_sec_to_hours
    )

    return FS.sort_values(by="adjusted_arrival_time(ts)")


obs_g = obs.groupby(
    ["date", "stop_name", "stop_id_cleaned", "stop_name__terminus", "route_short_name"]
)

obs_sched = []
for name, group in tqdm(obs_g):
    tt = group.iloc[0]["mode"]
    es = extract_schedule(group, tt)
    obs_sched.extend(es.to_dict("records"))

logging.info("Empty Memory")
del obs, obs_g


logging.info("Creating DataFrame")
obs_schedules = pd.DataFrame(obs_sched)

logging.info("Exporting the data")
obs_schedules.to_pickle("data/computed/observed_time_ES.pkl")

logging.info("Done")

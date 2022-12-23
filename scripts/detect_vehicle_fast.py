import geopandas as gpd
import folium
import json
from tqdm import tqdm
import re
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(module)s - : Line (%(lineno)d) - %(message)s",
    level=logging.INFO,
)
import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("mode.chained_assignment", None)

logging.info("Loading the data")
ht = pd.read_pickle("data/computed/schedule_normalized_dist.pkl")
obs = pd.read_pickle("data/computed/observed_time_ES.pkl")
ht_g = ht.groupby(by=["route_short_name", "trip_id", "service_id", "date_normalized"])
obs_g = obs.groupby(
    by=[
        "date",
        "stop_name",
        "stop_id_cleaned",
        "stop_name__terminus",
        "route_short_name",
    ]
)


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


def match_schedule_for_service_line_optim(
    schedule: pd.DataFrame,
    observations: pd.DataFrame,
    vehicle_id: int,
    date: str,
    midnight_tresh: int = 7200,
) -> pd.DataFrame:
    speeds_ms = {
        3: 4.333333333333333,  # Bus
        0: 4.527777777777778,  # Tram
        1: 7.749999999999999,  # Metro
    }
    d = []
    times_ser = 0
    for row in schedule.sort_values("time_seconds").to_dict("records"):
        stop_id_cleaned = re.sub("\D", "", row["stop_id"].lstrip("0"))
        try:
            if row["time_seconds"] > 86400:
                time_to_match_mid = row["time_seconds"] - 86400
                dts = date.split("-")
                dts[0] = str(int(dts[0]) + 1)
                dts = "-".join(dts)
                es_mid = observations.get_group(
                    (
                        dts,
                        row["stop_name"],
                        stop_id_cleaned,
                        row["trip_headsign"],
                        row["route_short_name"],
                    )
                )
                del dts

                if es_mid.empty == False:
                    es_mid["diff_time"] = abs(
                        es_mid["adjusted_arrival_time(ts)"] - time_to_match_mid
                    )

            es = observations.get_group(
                (
                    date,
                    row["stop_name"],
                    stop_id_cleaned,
                    row["trip_headsign"],
                    row["route_short_name"],
                )
            )

            if es.empty:
                rec_matched = {}
                rec_matched["vehicule_id"] = vehicle_id
                d.append(temp)

            else:
                es["diff_time"] = abs(
                    es["adjusted_arrival_time(ts)"] - row["time_seconds"]
                )

                if row["time_seconds"] > 86400:
                    es = pd.concat([es, es_mid])
                    del es_mid

                rec_matched = es[es.diff_time == min(es.diff_time)].to_dict("records")[
                    0
                ]

                if (
                    (
                        (rec_matched["adjusted_arrival_time(ts)"] < midnight_tresh)
                        & (rec_matched["adjusted_arrival_time(ts)"] + 86400 < times_ser)
                    )
                    | (
                        (rec_matched["adjusted_arrival_time(ts)"] > midnight_tresh)
                        & (rec_matched["adjusted_arrival_time(ts)"] < times_ser)
                    )
                ) & (rec_matched["diff_time"] < row["cluster_agg_value"] * 60):

                    delta_time = row["dist_m"] / speeds_ms[row["route_type"]]

                    rec_matched["adjusted_arrival_time(ts)"] = times_ser + delta_time
                    rec_matched["adjusted_arrival_time"] = turn_sec_to_hours(
                        rec_matched["adjusted_arrival_time(ts)"]
                    )
                    rec_matched["approx_rec"] = 1

                if rec_matched["diff_time"] > row["cluster_agg_value"] * 60:
                    rec_matched = {}
                else:
                    times_ser = rec_matched["adjusted_arrival_time(ts)"]

                rec_matched["vehicule_id"] = vehicle_id

                del es
                temp = {**row, **rec_matched}
                d.append(temp)
        except Exception as e:
            rec_matched = {}
            rec_matched["vehicule_id"] = vehicle_id
            temp = {**row, **rec_matched}
            d.append(temp)
            # logging.warn(e)

    vehicle_id += 1
    del times_ser
    return d


logging.info("Matching theoretical schedules to observed")
matched = []
i = 0

for name, group in tqdm(ht_g):
    t = match_schedule_for_service_line_optim(
        schedule=group, observations=obs_g, vehicle_id=i, date=name[3]
    )
    matched.extend(t)
    i += 1

del ht, obs, ht_g, obs_g

logging.info("Creating the dataframes")

full_matchs = pd.DataFrame(matched)

logging.info("Exporting the data")
full_matchs.to_pickle("data/computed/finally_matches.pkl")

logging.info("done")

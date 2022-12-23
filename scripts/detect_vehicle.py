import geopandas as gpd
import folium
import json
from tqdm import tqdm
import re
import sys

from custom_functions.gtfs_methods import (
    detect_direction,
    match_schedule_for_service_line,
)
import pandas as pd
import numpy as np
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(module)s - : Line (%(lineno)d) - %(message)s",
    level=logging.INFO,
)


pd.set_option("display.max_columns", None)
pd.set_option("mode.chained_assignment", None)

logging.info("Reading the data")

stop_cleaned = pd.read_pickle("data/computed/gtfs3_/stops.pkl")
exceptions = pd.read_pickle("data/computed/gtfs3_/calendar_dates.pkl")
geom = gpd.GeoDataFrame(pd.read_pickle("data/computed/stops_geom.pkl"))
obs = pd.read_pickle("data/computed/observed_time.pkl")
ht = pd.read_pickle("data/computed/schedule.pkl")

chunk = sys.argv[1]
group = pd.read_pickle("data/chunks/chunk_" + str(chunk) + ".pkl")

bugs = []
obs_to_collect = []
ID_v = 0

for name in tqdm(group.to_dict("records"), "matching the trips"):
    r_name = name["route"]
    vehicle_ = name["trip_id"]
    service_ = name["service_id"]

    # Theoretical schedule to search
    sched = ht[
        (ht.route_short_name == r_name)
        & (ht.service_id == service_)
        & (ht.trip_id == vehicle_)
    ]

    # obs schedule to search
    obs_sample = obs[obs.route_short_name == r_name]

    try:
        # Get direction
        direction = detect_direction(ligne=r_name, geom=geom, schedule=sched)

        # running the match
        match = match_schedule_for_service_line(
            schedule=sched,
            exceptions=exceptions,
            observations=obs_sample,
            geometry_table=direction,
            vehicle_id=ID_v,
        )
        obs_to_collect.extend(match[0])
        ID_v = match[1]
        del match, direction, obs_sample

    except Exception as inst:
        bugs.append((r_name, vehicle_, service_, inst))


logging.info("Exporting the matched data")
pd.DataFrame(obs_to_collect).to_pickle("data/matched/chunk_" + str(chunk) + ".pkl")
pd.DataFrame(bugs, columns=["route", "trip_id", "service_id", "exception"]).to_pickle(
    "data/bugs/chunk_" + str(chunk) + ".pkl"
)

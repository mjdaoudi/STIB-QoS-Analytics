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

logging.info("Reading the data")
schedules_normalized = pd.read_pickle("data/computed/schedule_normalized.pkl")
stops_geom = gpd.read_file("data/map/2109_STIB_MIVB_Network/ACTU_STOPS.shp")

logging.info("Cleaning the stops")
schedules_normalized["stop_id_clean_c"] = schedules_normalized.stop_id.apply(
    lambda x: re.sub("\D", "", x.lstrip("0"))
)

sg = stops_geom[["stop_id", "descr_fr", "descr_nl", "geometry"]].drop_duplicates(
    "stop_id"
)

m_stop_id = schedules_normalized.merge(
    sg, "left", left_on="stop_id", right_on="stop_id"
)

logging.info("Emptying memory")
del schedules_normalized, stops_geom

dist = gpd.GeoDataFrame(m_stop_id)

dist_g = dist.groupby(
    by=["route_short_name", "trip_id", "service_id", "date_normalized"]
)

logging.info("Computing distances")
lgs = []
for name, group in tqdm(dist_g):
    group = group.sort_values(by="time_seconds")
    group["geom_position_before"] = group.geometry.shift(1)
    group["dist_m"] = group["geometry"].distance(group["geom_position_before"])
    lgs.extend(group.to_dict("records"))

logging.info("Emptying memory")
del dist, dist_g, m_stop_id

logging.info("Creating the dataframe")
lgs = pd.DataFrame(lgs)

logging.info("Exporting the results")
lgs.to_pickle("data/computed/schedule_normalized_dist.pkl")

logging.info("Emptying memory")
del lgs

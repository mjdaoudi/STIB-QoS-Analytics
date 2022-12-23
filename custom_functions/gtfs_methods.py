import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
import numpy as np
import ruptures as rpt
from tqdm import tqdm
import re

import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(module)s - : Line (%(lineno)d) - %(message)s",
    level=logging.INFO,
)


def compute_headway(
    df: pd.DataFrame,
    headway_col_name: str = "headway_min",
    time_sec_col_name: str = "time_seconds",
) -> pd.DataFrame:
    df[headway_col_name] = (
        df[time_sec_col_name].sort_values()
        - df[time_sec_col_name].sort_values().shift()
    ) / 60
    return df


def headways(
    table_times_trips: pd.DataFrame,
    stop_col: str,
    route_col: str,
    direction_col: object,
    service_col: str,
    headway_col_name: str = "headway_min",
    time_col: str = None,
    time_sec_name: str = None,
) -> pd.DataFrame:
    """This function compute the headway of a given table in a specific format using
    a grouping approach.

    Args:
        table_times_trips (pd.DataFrame): the table containing all the trips, lines, stops and direction
        time_col (str): Column containing the time
        stop_col (str): Column containing the stops
        route_col (str): Column containing the route
        direction_col (str): Column containing the description
        service_col (str): Column containing the service

    Returns:
        pd.DataFrame: An ungrouped dataframe with all the headways computed in the stop
        added in an additionnal column
    """

    if (time_col == None) and (time_sec_name == None):
        raise Exception("No time columns were provided, could you investigate ?")

    if time_sec_name == None:
        time_sec_name = "time_seconds"
        time = table_times_trips[time_col].str.split(":", expand=True)
        table_times_trips[time_sec_name] = (
            time[0].astype(int) * 3600 + time[1].astype(int) * 60 + time[2].astype(int)
        )

    logging.info("Grouping the data")
    groups_stop_route_direction_service = table_times_trips.groupby(
        by=[stop_col, route_col, direction_col, service_col]
    )

    logging.info("Computing headways")
    headway = []
    for name, group in groups_stop_route_direction_service:
        headway.append(compute_headway(group, headway_col_name, time_sec_name))

    del groups_stop_route_direction_service

    headway = pd.concat(headway).reset_index(drop=True)

    return headway


def convert_jsons_to_df(folder: str) -> pd.DataFrame:
    l = []
    for file in [folder + "/" + i for i in os.listdir(folder)]:
        with open(file) as f:
            data = json.load(f)
            for parent in data["data"]:
                if parent is not None:
                    time = parent["time"]
                    for rec in parent["Responses"]:
                        if rec is not None:
                            for line in rec["lines"]:
                                line_id = line["lineId"]
                                for position in line["vehiclePositions"]:
                                    dt = datetime.fromtimestamp(int(time) / 1000)
                                    f_rec = {
                                        "date": dt.date().strftime("%d-%m-%Y"),
                                        "time": dt.time().strftime("%H:%M:%S"),
                                        "route_short_name": line_id,
                                        "distance_from_point": position[
                                            "distanceFromPoint"
                                        ],
                                        "stop_id": position["pointId"],
                                        "stop_id_terminus": position["directionId"],
                                    }
                                    l.append(f_rec)
    df = pd.DataFrame(l)
    del l

    return df


def get_schedule(
    timetable: pd.DataFrame,
    stopsTable: pd.DataFrame,
    route_id: int,
    direction_id: int,
    stop_name: str = None,
    stop_id: str = None,
    service_id: int = None,
    longest_service: bool = True,
) -> tuple[pd.DataFrame, tuple[str, int, int, int]]:
    """Function able to quickly get the daily schedule for a given line, direction and stop.
    The stop name is enough, the ID is not necessary. Even the sequence ID is not necessarly needed
    because it look at the most busy sequence ID and return that schedule (which is usually during
    weekdays).

    Args:
        timetable (pd.DataFrame): The flattened timetable
        stopsTable (pd.DataFrame): The table with the stops information
        route_id (int): The id of the route. Carefull, not necessarly equal the route short name!
        direction_id (int): The direction within the line
        stop_name (str, optional): The name of the stop. Defaults to None.
        stop_id (str, optional): The id of the stop. Defaults to None.
        service_id (int, optional): The service if one is provided. Defaults to None.
        longest_service (bool, optional): If you don't have a particular service ID. Defaults to True.

    Raises:
        Exception: In case of missing data or not having any matching.

    ! Bug Report ! :
        - Returns a longer dataframe than expected sometimes

    Returns:
        _type_: _description_
    """

    schedule = pd.DataFrame()
    schedule_set_up = None
    stop_data = pd.DataFrame()

    if stop_name != None:
        stops_ids = stopsTable[stopsTable.stop_name == stop_name].stop_id

        if stops_ids.shape[0] == 0:
            raise Exception(
                "No stops are existing using that name... Did you write correctly (all caps please) ?"
            )

        st_id = None
        for stop_id_temp in stops_ids:
            temp = timetable[
                (timetable.stop_id == stop_id_temp)
                & (timetable.route_id == route_id)
                & (timetable.direction_id == direction_id)
            ]
            if temp.shape[0] != 0 and stop_data.empty:
                stop_data = temp
                st_id = stop_id_temp
                del temp
            elif temp.shape[0] != 0 and not stop_data.empty:
                raise Exception(
                    f"The transport {route_id} at stop {stop_name} is going through several stop_ids[{st_id}, {stop_id_temp},...]. Can you investigate ?"
                )
    else:
        if stop_id == None:
            raise Exception(
                "Can you please provide a stop_id in the case you don't have the stop_name ?"
            )

        stop_data = timetable[
            (timetable.stop_id == stop_id)
            & (timetable.route_id == route_id)
            & (timetable.direction_id == direction_id)
        ]

    if stop_data.empty:
        raise Exception(
            f"The transport {route_id} at stop {stop_name} could not find any match for the line. Did you provided correctly a stop id or stop name? Can you investigate ?"
        )

    if longest_service:
        stop_data = stop_data.groupby(by="service_id")
        for name, group in stop_data:
            if group.shape[0] > schedule.shape[0]:
                schedule = group
                schedule_set_up = (stop_name, route_id, direction_id, name)

    else:
        schedule = stop_data[(stop_data.service_id == service_id)]
        schedule_set_up = (stop_name, route_id, direction_id, service_id)

    return (schedule, schedule_set_up)


def segmentation_model(serie: pd.Series, penalty, model) -> list:
    serie = np.array(serie.dropna().to_list())
    if len(serie) > 1:
        PELT = rpt.Pelt(model=model).fit(serie)
        PELT_res = PELT.predict(pen=penalty)
    else:
        PELT_res = [1]
    return PELT_res


def cluster_assgnement(clusters: list[int]) -> list[int]:
    clstrs = []
    cluster_index = 0
    for i in range(len(clusters)):
        if i == 0:
            clstrs.append([cluster_index for x in range(clusters[i])])
        else:
            clstrs.append([cluster_index for x in range(clusters[i - 1], clusters[i])])
        cluster_index += 1
    clusters_flatten = ["cluster_" + str(0)] + [
        "cluster_" + str(cl) for sublist in clstrs for cl in sublist
    ]
    return clusters_flatten


def compute_clusters(
    timetable: pd.DataFrame,
    cluster_computation_col_name: str = "headway_min",
    cluster_col_name: str = "clusters",
    penalty: int = 3,
    model: str = "rbf",
):
    breakpoints = segmentation_model(
        timetable.sort_values(by="time_seconds")[cluster_computation_col_name],
        penalty,
        model,
    )
    temp = timetable.sort_values(by="time_seconds")
    temp[cluster_col_name] = cluster_assgnement(breakpoints)
    return temp


def assess_regularity(
    timetable: pd.DataFrame,
    threshold: int = 12,
    aggregation_method: str = "median",
    cluster_computation_col_name: str = "headway_min",
    cluster_col_name: str = "clusters",
    col_reg_name: str = "regularity",
) -> pd.DataFrame:
    agg = timetable.groupby(cluster_col_name)[cluster_computation_col_name].agg(
        aggregation_method
    )
    temp = timetable.merge(agg, "left", cluster_col_name,).rename(
        columns={
            cluster_computation_col_name + "_x": cluster_computation_col_name,
            cluster_computation_col_name + "_y": "cluster_agg_value",
        }
    )
    temp[col_reg_name] = np.where(temp["cluster_agg_value"] <= threshold, 1, 0)
    return temp


def assess_qos_metrics(
    timetable: pd.DataFrame,
    stop_col: str,
    route_col: str,
    direction_col: object,
    service_col: str,
) -> pd.DataFrame:
    logging.info("Grouping the data")
    grouped_timetable = timetable.groupby(
        by=[stop_col, route_col, direction_col, service_col]
    )

    logging.info("Computing clusters and assessing regularity")
    qos_met = []
    for name, group in grouped_timetable:
        try:
            if group.shape[0] > 1:
                qos_met.append(assess_regularity(compute_clusters(group)))
            else:
                group["clusters"] = 0
                group["cluster_agg_value"] = np.NaN
                group["regularity"] = 0
        except Exception as e:
            print(name)
            print(group.shape)
            raise e

    del grouped_timetable

    qos_met = pd.concat(qos_met).reset_index(drop=True)

    return qos_met


def get_largest_group(
    grouped_df: pd.core.groupby.generic.DataFrameGroupBy, position: int = 0
) -> pd.DataFrame:
    groups_ = [(name, group) for name, group in grouped_df]
    groups_ = sorted(groups_, key=lambda x: x[1].shape[0], reverse=True)
    goi = groups_[position]
    del groups_
    return goi


def extract_schedules_from_observed(
    obs: pd.DataFrame, transportation_type: str
) -> pd.DataFrame:

    logging.info("Grouping the data")
    groups = obs.groupby(by=["date", "route_short_name", "stop_id", "stop_id_terminus"])

    logging.info("Extracting through groups schedules")
    temp = []
    for name, group in groups:
        try:
            t = extract_schedule(
                schedule=group.drop_duplicates(),
                transportation_type=group.iloc[0][transportation_type],
            )
            temp.append(t)

        except Exception as e:
            print(name)
            print(group.shape)
            raise e

    del groups
    observed_schedule = pd.concat(temp).reset_index(drop=True)

    return observed_schedule


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
        3: 4.333333333333333,  # Bus
        0: 4.527777777777778,  # Tram
        1: 7.749999999999999,  # Metro
    },
) -> pd.DataFrame:
    if schedule.shape[0] > 1:

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


def define_date_window(
    schedule_start_date: pd._libs.tslibs.timestamps.Timestamp,
    schedule_end_date: pd._libs.tslibs.timestamps.Timestamp,
    label: str,
    service_id: int,
    exceptions: pd.DataFrame,
    obs_start_date: str = "2021-09-06 00:00:00",
    obs_end_date: str = "2021-09-21 00:00:00",
) -> list[str]:
    labels_dict = {
        "workdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "saturday": ["Saturday"],
        "sunday": ["Sunday"],
    }

    min_date = pd.to_datetime(obs_start_date)
    max_date = pd.to_datetime(obs_end_date)

    added_dates = pd.to_datetime(
        exceptions[
            (exceptions.service_id == service_id) & (exceptions.exception_type == 1)
        ].date_ft
    )
    removed_dates = pd.to_datetime(
        exceptions[
            (exceptions.service_id == service_id) & (exceptions.exception_type == 2)
        ].date_ft
    )

    service_window = pd.date_range(start=schedule_start_date, end=schedule_end_date)
    data_window = pd.date_range(start=min_date, end=max_date)

    woi_raw = [
        date
        for date in data_window
        if (date in service_window) & (date.strftime("%A") in labels_dict[label])
    ]

    woi_raw.extend(
        [dt for dt in added_dates if (dt not in woi_raw) & (dt not in data_window)]
    )

    woi = [dt.strftime("%d-%m-%Y") for dt in woi_raw if dt not in removed_dates]

    return woi


def search_time(
    schedule: pd.DataFrame,
    expected_time: float,
    headway: float,
    stop_dist: float,
    speed_vehicle: float,
    time_last_val: float,
) -> dict:
    schedule["diff_time"] = abs(schedule["adjusted_arrival_time(ts)"] - expected_time)
    rec_matched = schedule[schedule.diff_time == min(schedule.diff_time)].to_dict(
        "records"
    )[0]

    t_diff = rec_matched["diff_time"]
    t_time = rec_matched["adjusted_arrival_time(ts)"]

    if (t_time < time_last_val) & (t_diff < headway * 60):
        delta_time = stop_dist / speed_vehicle
        rec_matched["adjusted_arrival_time(ts)"] = time_last_val + delta_time
        rec_matched["adjusted_arrival_time"] = turn_sec_to_hours(
            rec_matched["adjusted_arrival_time(ts)"]
        )
        rec_matched["approx_rec"] = 1

    return rec_matched


def detect_direction(
    ligne: str, geom: pd.DataFrame, schedule: pd.DataFrame
) -> pd.DataFrame:
    g = geom[(geom.ligne_cleaned == ligne)]
    g_dir = pd.DataFrame()

    for name, group in g.groupby("VARIANTE"):
        sched_stops = schedule.sort_values("time_seconds").stop_name.to_list()

        hset_fr = group.sort_values("succession").descr_fr.to_list()
        hset_nl = group.sort_values("succession").descr_nl.to_list()

        for i in range(len(hset_fr) - len(sched_stops) + 1):
            if (sched_stops == hset_fr[i : i + len(sched_stops)]) | (
                sched_stops == hset_nl[i : i + len(sched_stops)]
            ):
                g_dir = group

    return g_dir


def match_schedule_for_service_line(
    schedule: pd.DataFrame,
    exceptions: pd.DataFrame,
    observations: pd.DataFrame,
    geometry_table: pd.DataFrame,
    vehicle_id: int,
) -> pd.DataFrame:
    speeds_ms = {
        3: 4.333333333333333,  # Bus
        0: 4.527777777777778,  # Tram
        1: 7.749999999999999,  # Metro
    }

    d = []
    sch = schedule.iloc[0]
    start_date = sch.start_date_ft
    end_date = sch.end_date_ft
    lab = sch.label
    service_id = sch.service_id
    doi = define_date_window(start_date, end_date, lab, service_id, exceptions)

    for date in doi:
        times_ser = [0]
        for row in schedule.sort_values("time_seconds").to_dict("records"):
            stop_name = row["stop_name"]
            stop_id = re.sub("\D", "", row["stop_id"].lstrip("0"))
            direction = row["trip_headsign"]
            transport_type = row["route_type"]
            expected_time = row["time_seconds"]
            headway = row["cluster_agg_value"]
            stop_dist_table = geometry_table[geometry_table.descr_fr == stop_name]
            if stop_dist_table.empty:
                stop_dist_table = geometry_table[geometry_table.descr_nl == stop_name]
            stop_dist = stop_dist_table.iloc[0].dist_m

            es = extract_schedule(
                observations[
                    (observations.stop_name == stop_name)
                    & (observations.stop_id_cleaned == stop_id)
                    & (observations.date == date)
                    & (observations.stop_name__terminus == direction)
                ],
                transport_type,
            )

            if not es.empty:
                rec_matched = search_time(
                    es,
                    expected_time=expected_time,
                    headway=headway,
                    stop_dist=stop_dist,
                    speed_vehicle=speeds_ms[transport_type],
                    time_last_val=times_ser[-1],
                )

                if rec_matched["diff_time"] > headway * 60:
                    rec_matched = {}
                else:
                    times_ser.append(rec_matched["adjusted_arrival_time(ts)"])

                rec_matched["dist_previous_stop"] = stop_dist
                rec_matched["date_searched"] = date
                rec_matched["vehicule_id"] = vehicle_id

                temp = {**row, **rec_matched} if rec_matched != {} else row
                d.append(temp)
        vehicle_id += 1

    return (d, vehicle_id)


def turn_hour_to_seconds(
    time_in_hour: str,
    timetable: pd.DataFrame,
    col_name: str = "time_seconds",
    format24: bool = True,
) -> pd.DataFrame:
    timetable = timetable.dropna(subset=time_in_hour)
    time = timetable[time_in_hour].str.split(":", expand=True)
    timetable[col_name] = (
        time[0].astype(int) * 3600 + time[1].astype(int) * 60 + time[2].astype(int)
    )
    if format24:
        timetable[col_name] = np.where(
            timetable[col_name] < 7200, timetable[col_name] + 86400, timetable[col_name]
        )

    return timetable


def compute_EWT(
    timetable: pd.DataFrame,
    stop_col: str = "stop_id",
    route_col: str = "route_id",
    direction_col: str = "direction_id",
    service_col: str = "service_id",
    date_col: str = "date_normalized",
    cluster_col: str = "clusters",
    s_headway_col: str = "headway_th",
    a_headway_col: str = "headway_real",
) -> pd.DataFrame:

    logging.info("Computing the square of headways")
    timetable["s_headway_square"] = timetable[s_headway_col] ** 2
    timetable["a_headway_square"] = timetable[a_headway_col] ** 2

    logging.info("Computing SWT & AWT per stop, route, direction, date and cluster")
    SWT = timetable.groupby(
        by=[stop_col, route_col, direction_col, service_col, date_col, cluster_col]
    ).apply(lambda x: x["s_headway_square"].sum() / (2 * (x[s_headway_col].sum())))
    AWT = timetable.groupby(
        by=[stop_col, route_col, direction_col, service_col, date_col, cluster_col]
    ).apply(lambda x: x["a_headway_square"].sum() / (2 * (x[a_headway_col].sum())))

    SWT.name = "SWT"
    AWT.name = "AWT"

    timetable = timetable.merge(
        SWT,
        on=[stop_col, route_col, direction_col, service_col, date_col, cluster_col],
        how="left",
    ).merge(
        AWT,
        on=[stop_col, route_col, direction_col, service_col, date_col, cluster_col],
        how="left",
    )

    logging.info("Computing EWT")
    timetable["EWT"] = timetable["AWT"] - timetable["SWT"]

    timetable = timetable.drop(columns=["s_headway_square", "a_headway_square"])

    return timetable

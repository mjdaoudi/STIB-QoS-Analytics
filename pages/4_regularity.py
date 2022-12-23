import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px

px.set_mapbox_access_token(
    "pk.eyJ1IjoibWpkYW91ZGkiLCJhIjoiY2xibm54OThyMGdyOTNvcnhqeTYyZmRuYiJ9.rfxe3z8triwA5yvV1XZA-A"
)

dash.register_page(
    __name__,
    title="Regularity",
    name="Regularity",
)

data = pd.read_pickle("data/computed/matches_clean_EWT_delay.pkl")

data_g = data.groupby(
    ["route_short_name", "date_label", "trip_headsign", "delay_label_strict"]
)
data_g_spec = data.groupby(["route_short_name", "date_label", "trip_headsign"])
coord = pd.read_pickle("data/computed/stops.geo.pkl")

unique_routes = np.sort(data.route_short_name.unique().astype(int)).tolist()

tab_1_content = [
    html.H2(
        "Regularity per line, stop, and day",
    ),
    html.P(
        """
            Each line can be analysed depending on the filters selected on the left pane. 
            Here is a comparison between theoretical and observed headways within each cluster for which the regularity is more important than the punctuality (headway<12min).
            In the observed headways, the EWT for each cluster can be found in the summary section.
        """,
        style={"margin-bottom": "40px", "max-width": "150ch"},
    ),
    dbc.Row(
        style={"margin-bottom": "40px"},
        children=[
            dbc.Col(
                children=[
                    html.H4(
                        "Theoretical headways",
                    ),
                    html.P(
                        """
                            The theoretical headways are referring to the scheduled time between two consecutive vehicles. This allows to assess how regular vehicles are for a line at a specific stop. 
                        """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dcc.Graph(
                        id="cluster_theoretical",
                        style={"margin-bottom": "40px"},
                    ),
                ]
            ),
            dbc.Col(
                children=[
                    html.H4(
                        "Observed headways",
                    ),
                    html.P(
                        """
                            The observed headways are referring to the real time between two consecutive vehicles. This allows to assess how regular vehicles are for a line at a specific stop in reality.
                        """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dcc.Graph(
                        id="cluster_real",
                        style={"margin-bottom": "40px"},
                    ),
                ]
            ),
        ],
    ),
]

tab_2_content = [
    html.H2("EWT mapping per line"),
    html.P(
        """ 
            EWT is a metric that assess the additional waiting time for a passage due to irregularity in the network. Mapping the EWT for a specific line at each stop shows how irregularities can propagate throughout the line.  
        """
    ),
    dbc.Row(
        children=[
            dcc.Graph(
                id="dd-median-EWT-points",
                style={"margin-bottom": "40px", "height": "80vh"},
            ),
        ],
    ),
]

layout = [
    html.H1(children="Regularity Analysis"),
    dbc.Row(
        children=[
            dbc.Col(
                width=2,
                style={
                    "height": "100%",
                    "padding": "10px 20px",
                    "position": "sticky",
                },
                children=[
                    html.H5("Filters"),
                    html.P("Line", style={"margin-bottom": "3px"}),
                    dcc.Dropdown(
                        unique_routes,
                        unique_routes[0],
                        id="lines_drop_down_value-r",
                        clearable=False,
                        style={"margin-bottom": "20px"},
                    ),
                    html.P(
                        "Stop (not applicable on the Map)",
                        style={"margin-bottom": "3px"},
                    ),
                    dcc.Dropdown(
                        clearable=False,
                        id="stops_drop_down_value-r",
                        style={"margin-bottom": "20px"},
                    ),
                    html.P("Direction", style={"margin-bottom": "3px"}),
                    dcc.Dropdown(
                        clearable=False,
                        id="dir_drop_down_value-r",
                        style={"margin-bottom": "20px"},
                    ),
                    html.P(
                        "Date (not applicable on the Map)",
                        style={"margin-bottom": "3px"},
                    ),
                    dcc.Dropdown(
                        clearable=False,
                        id="date_drop_down_value-r",
                        style={"margin-bottom": "20px"},
                    ),
                    html.P("Service_id", style={"margin-bottom": "3px"}),
                    dcc.Dropdown(
                        clearable=False,
                        id="service_id_drop_down_value-r",
                        style={"margin-bottom": "20px"},
                    ),
                    html.Hr(className="my-2"),
                    html.H5(children="Summary", style={"margin-top": "50px"}),
                    html.P(id="text-summary-r"),
                ],
            ),
            dbc.Col(
                style={
                    "padding": "10px 20px",
                    "height": "86vh",
                    "overflow": "scroll",
                },
                children=[
                    dbc.Tabs(
                        children=[
                            dbc.Tab(
                                children=tab_1_content,
                                label="Static",
                                style={"padding-top": "20px", "padding-bottom": "20px"},
                            ),
                            dbc.Tab(
                                children=tab_2_content,
                                label="Map",
                                style={"padding-top": "20px", "padding-bottom": "20px"},
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
]

# Callbacks for dropdown filters


@callback(
    [
        Output("stops_drop_down_value-r", "options"),
        Output("stops_drop_down_value-r", "value"),
    ],
    Input("lines_drop_down_value-r", "value"),
)
def update_stops(value):
    temp = data[data.route_short_name == str(value)]["stop_name"].unique()
    return temp, temp[0]


@callback(
    [
        Output("dir_drop_down_value-r", "options"),
        Output("dir_drop_down_value-r", "value"),
    ],
    [
        Input("lines_drop_down_value-r", "value"),
        Input("stops_drop_down_value-r", "value"),
    ],
)
def update_direction(route, stop):
    temp = data[(data.route_short_name == str(route)) & (data.stop_name == stop)][
        "trip_headsign"
    ].unique()
    return temp, temp[0]


@callback(
    [
        Output("date_drop_down_value-r", "options"),
        Output("date_drop_down_value-r", "value"),
    ],
    [
        Input("lines_drop_down_value-r", "value"),
        Input("stops_drop_down_value-r", "value"),
        Input("dir_drop_down_value-r", "value"),
    ],
)
def update_date(route, stop, direction):
    temp = data[
        (data.route_short_name == str(route))
        & (data.stop_name == stop)
        & (data.trip_headsign == direction)
    ]["date_normalized"].unique()
    return temp, temp[0]


@callback(
    [
        Output("service_id_drop_down_value-r", "options"),
        Output("service_id_drop_down_value-r", "value"),
    ],
    [
        Input("lines_drop_down_value-r", "value"),
        Input("stops_drop_down_value-r", "value"),
        Input("dir_drop_down_value-r", "value"),
        Input("date_drop_down_value-r", "value"),
    ],
)
def update_service(route, stop, direction, date):
    temp = data[
        (data.route_short_name == str(route))
        & (data.stop_name == stop)
        & (data.trip_headsign == direction)
        & (data.date_normalized == date)
    ]["service_id"].unique()
    return temp, temp[0]


@callback(
    Output("text-summary-r", "children"),
    [
        Input("lines_drop_down_value-r", "value"),
        Input("stops_drop_down_value-r", "value"),
        Input("dir_drop_down_value-r", "value"),
        Input("date_drop_down_value-r", "value"),
    ],
)
def update_summary(route, stop, direction, date):
    if (route != None) & ((stop != None)) & ((direction != None) & (date != None)):
        transport_type = {"M": "metro", "T": "tram", "B": "bus"}
        temp = data[
            (data.route_short_name == str(route))
            & (data.stop_name == stop)
            & (data.trip_headsign == direction)
            & (data.date_normalized == date)
            & (data.regularity == 1)
        ]
        mode = transport_type.get(temp.iloc[0]["mode"])
        name = temp.iloc[0].route_long_name.split(" - ")
        # origin = temp.sort_values(by = "th_time_sec").iloc[0].stop_name

        s = f"You have selected the {mode} {str(route)}, operating between {name[0]} and {name[1]}, in direction of {direction} at the stop {stop} on the {date}."
        card = ""
        for i in temp.clusters.unique():
            j = round(temp[temp.clusters == i].EWT.iloc[0], 2)
            card += "EWT for " + str(i) + " : " + str(j) + " min;" + "\n"
        s += "\n" + card
    else:
        s = "No summary yet available."

    return s


@callback(
    Output("cluster_theoretical", "figure"),
    [
        Input("lines_drop_down_value-r", "value"),
        Input("stops_drop_down_value-r", "value"),
        Input("dir_drop_down_value-r", "value"),
        Input("date_drop_down_value-r", "value"),
        Input("service_id_drop_down_value-r", "value"),
    ],
)
def plot_clusters(route, stop, direction, date, service_id):
    temp = data[
        (data.route_short_name == str(route))
        & (data.stop_name == stop)
        & (data.trip_headsign == direction)
        & (data.date_normalized == date)
        & (data.service_id == service_id)
        & (data.regularity == 1)
    ]
    fig = px.scatter(
        temp,
        x="theoretical_time",
        y="headway_th",
        color="clusters",
        labels=dict(
            headway_th="Theoretical Headway (min)", theoretical_time="Scheduled Time"
        ),
    ).update_yaxes(range=(0, max(temp.headway_real) + 5), constrain="domain")
    return fig


@callback(
    Output("cluster_real", "figure"),
    [
        Input("lines_drop_down_value-r", "value"),
        Input("stops_drop_down_value-r", "value"),
        Input("dir_drop_down_value-r", "value"),
        Input("date_drop_down_value-r", "value"),
        Input("service_id_drop_down_value-r", "value"),
    ],
)
def plot_clusters(route, stop, direction, date, service_id):
    temp = data[
        (data.route_short_name == str(route))
        & (data.stop_name == stop)
        & (data.trip_headsign == direction)
        & (data.date_normalized == date)
        & (data.service_id == service_id)
        & (data.regularity == 1)
    ]
    fig = px.scatter(
        temp,
        x="adj_real_time",
        y="headway_real",
        color="clusters",
        labels=dict(
            headway_real="Observed Headway (min)", adj_real_time="Observed Time"
        ),
        hover_data={"EWT": ":.2f"},
    ).update_yaxes(range=(0, max(temp.headway_real) + 5), constrain="domain")
    return fig


@callback(
    Output("dd-median-EWT-points", "figure"),
    [
        Input("lines_drop_down_value-r", "value"),
        Input("date_drop_down_value-r", "value"),
        Input("dir_drop_down_value-r", "value"),
    ],
)
def map_line_EWT_points(line, date, direction):
    date_label = data[data.date_normalized == date].date_label.iloc[0]

    temp = data_g.get_group((str(line), date_label, direction, "lat"))

    temp = (
        temp[["stop_id", "EWT"]]
        .groupby("stop_id", as_index=False)
        .median("EWT")
        .merge(coord, "left", "stop_id")
        .merge(temp[["stop_id", "stop_name"]].drop_duplicates(), "left", "stop_id")
    )

    fig = px.scatter_mapbox(
        temp,
        lat="stop_lat",
        lon="stop_lon",
        color="EWT",
        size="EWT",
        zoom=11,
        color_continuous_scale="portland",
        hover_data={"EWT": ":.2f"},
        hover_name="stop_name",
    ).update_layout(mapbox_style="light", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import dash_daq as daq


px.set_mapbox_access_token(
    "pk.eyJ1IjoibWpkYW91ZGkiLCJhIjoiY2xibm54OThyMGdyOTNvcnhqeTYyZmRuYiJ9.rfxe3z8triwA5yvV1XZA-A"
)

dash.register_page(
    __name__,
    title="Segment Analysis",
    name="Segment Analysis",
)

data = pd.read_pickle("data/computed/matches_clean_EWT_delay_seq.pkl")
fs_delay = pd.read_pickle("data/computed/freq_mining.pkl")
fs_delay_EWT = pd.read_pickle("data/computed/freq_mining_EWT.pkl")
data_g_spec = data.groupby(["route_short_name", "trip_headsign"])
data_g_nd = data.groupby(["route_short_name", "date_label", "trip_headsign"])
data_g = data.groupby(
    ["route_short_name", "date_label", "trip_headsign", "delay_label_strict"]
)
coord = pd.read_pickle("data/computed/stops.geo.pkl")

lg = pd.read_pickle("data/computed/lines_growth_th.pkl")
lg_g = (
    lg[
        [
            "route_short_name",
            "stop_name",
            "date_normalized",
            "trip_headsign",
            "succession",
            "stop_lat",
            "stop_lon",
            "growth_cut",
            "lab_growth",
            "delay",
        ]
    ]
    .groupby(
        [
            "route_short_name",
            "stop_name",
            "date_normalized",
            "trip_headsign",
            "succession",
        ],
        as_index=False,
    )
    .median()
).groupby(["route_short_name", "date_normalized", "trip_headsign"])

lge = pd.read_pickle("data/computed/lines_growth_EWT_th.pkl")
lg_ge = (
    lge[
        [
            "route_short_name",
            "stop_name",
            "date_normalized",
            "trip_headsign",
            "succession",
            "stop_lat",
            "stop_lon",
            "growth_cut",
            "lab_growth",
            "EWT",
        ]
    ]
    .groupby(
        [
            "route_short_name",
            "stop_name",
            "date_normalized",
            "trip_headsign",
            "succession",
        ],
        as_index=False,
    )
    .median()
).groupby(["route_short_name", "date_normalized", "trip_headsign"])


unique_routes = np.sort(data.route_short_name.unique().astype(int)).tolist()


def get_map_delay(type):
    _ = fs_delay[fs_delay["mode"] == type]

    _ = _[~_.stop_name.isin(_[_.duplicated(subset="stop_name")].stop_name)]

    fig = px.scatter_mapbox(
        _,
        lat="stop_lat",
        lon="stop_lon",
        hover_name="stop_name",
        color="cat",
        zoom=10,
        color_continuous_scale="Portland",
    )
    fig.update_layout(mapbox_style="light")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def get_map_EWT(type):
    _ = fs_delay_EWT[fs_delay_EWT["mode"] == type]

    _ = _[~_.stop_name.isin(_[_.duplicated(subset="stop_name")].stop_name)]

    fig = px.scatter_mapbox(
        _,
        lat="stop_lat",
        lon="stop_lon",
        hover_name="stop_name",
        color="cat",
        zoom=10,
        color_continuous_scale="Portland",
    )
    fig.update_layout(mapbox_style="light")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


tab_1_content = [
    html.H2("Frequent delaying stop"),
    html.P(
        "These maps were built by aggregating the daily median delay for each line and direction. After which, a polynomial modelling has been performed to detect the slopes of the delays throughout the sequence per day. A positive slope means that the delay is increasing through the sequence and a negative slope means that, on the opposite, the vehicle is catching its delay. After that, a frequent pattern model has been set up to detect throughout the STIB network whether some stops are repeating themselves. This modelling has been applied with a punctuality and regularity point of view.",
        style={"margin-bottom": "50px", "max-width": "150ch"},
    ),
    html.H4("Bus Segment Mining"),
    dbc.Row(
        style={
            "margin-bottom": "50px",
        },
        children=[
            dbc.Col(
                children=[
                    html.H5("Delay"),
                    html.P(
                        "Top segment offenders for buses. A stop can be a delayer (which mean creating delay when arriving) or a catcher (catching delay while arriving at the stop) in terms of delay.",
                        style={"margin-bottom": "20px", "max-width": "125ch"},
                    ),
                    dcc.Graph(figure=get_map_delay("B")),
                ]
            ),
            dbc.Col(
                children=[
                    html.H5("EWT"),
                    html.P(
                        "Top segment offenders for buses. A stop can be a delayer (which mean creating delay when arriving) or a catcher (catching delay while arriving at the stop) in terms of EWT.",
                        style={"margin-bottom": "20px", "max-width": "125ch"},
                    ),
                    dcc.Graph(figure=get_map_EWT("B")),
                ]
            ),
        ],
    ),
    html.H4("Tram Segment Mining"),
    dbc.Row(
        style={"margin-bottom": "50px"},
        children=[
            dbc.Col(
                children=[
                    html.H5("Delay"),
                    html.P(
                        "Top segment offenders for trams. A stop can be a delayer (which mean creating delay when arriving) or a catcher (catching delay while arriving at the stop) in terms of delay.",
                        style={"margin-bottom": "20px", "max-width": "125ch"},
                    ),
                    dcc.Graph(figure=get_map_delay("T")),
                ]
            ),
            dbc.Col(
                children=[
                    html.H5("EWT"),
                    html.P(
                        "Top segment offenders for trams. A stop can be a delayer (which mean creating delay when arriving) or a catcher (catching delay while arriving at the stop) in terms of EWT.",
                        style={"margin-bottom": "20px", "max-width": "125ch"},
                    ),
                    dcc.Graph(figure=get_map_EWT("T")),
                ]
            ),
        ],
    ),
    html.H4("Metro Segment Mining"),
    dbc.Row(
        style={"margin-bottom": "50px"},
        children=[
            dbc.Col(
                children=[
                    html.H5("Delay"),
                    html.P(
                        "Top segment offenders for metro. A stop can be a delayer (which mean creating delay when arriving) or a catcher (catching delay while arriving at the stop) in terms of delay.",
                        style={"margin-bottom": "20px", "max-width": "125ch"},
                    ),
                    dcc.Graph(figure=get_map_delay("M")),
                ]
            ),
            dbc.Col(
                children=[
                    html.H5("EWT"),
                    html.P(
                        "Top segment offenders for metro. A stop can be a delayer (which mean creating delay when arriving) or a catcher (catching delay while arriving at the stop) in terms of EWT.",
                        style={"margin-bottom": "20px", "max-width": "125ch"},
                    ),
                    dcc.Graph(figure=get_map_EWT("M")),
                ]
            ),
        ],
    ),
]

tab_1_content_lp = [
    html.H2(
        "Lines performances",
    ),
    html.P(
        """
            Each line can be analysed depending on the filters selected on the left pane. 
            Two types of visualisations are available, in term of density and in terms of point.
            This enables analysts to have a view on how the delay is evolving through the line precisly.
        """,
        style={"margin-bottom": "40px", "max-width": "150ch"},
    ),
    dbc.Row(
        style={"margin-bottom": "40px"},
        children=[
            dbc.Col(
                children=[
                    html.H4(
                        "Top delays offenders (Density based)",
                    ),
                    html.P(
                        """
                            Summing the delays at each stop shows the most problematic stops on the chosen line in terms of most observed delays during the chosen day. The density map highlights close stops that have similar values.
                        """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dcc.Graph(
                        id="dd-sum-delays",
                        style={"margin-bottom": "40px"},
                    ),
                ]
            ),
            dbc.Col(
                children=[
                    html.H4(
                        "Median offender (Density based)",
                    ),
                    html.P(
                        """
                            Mapping the median delay for a specific line at each stop shows how delays can propagate throughout the line. The density map highlights segments that are problematic. 
                        """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dcc.Graph(
                        id="dd-median-delays",
                        style={"margin-bottom": "40px"},
                    ),
                ]
            ),
        ],
    ),
    dbc.Row(
        children=[
            dbc.Col(
                children=[
                    html.H4(
                        "Top delays offenders (Point based)",
                    ),
                    html.P(
                        """
                            Summing the delays at each stop shows the most problematic stops on the chosen line in terms of most observed delays during the chosen day. The point map highlights the problematic stops.
                        """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dcc.Graph(
                        id="dd-sum-delays-points",
                        style={"margin-bottom": "40px"},
                    ),
                ]
            ),
            dbc.Col(
                children=[
                    html.H4(
                        "Median offender (Point based)",
                    ),
                    html.P(
                        """
                            Mapping the median delay for a specific line at each stop shows how delays can propagate throughout the line. The point map highlights stops that are problematic. 
                        """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dcc.Graph(
                        id="dd-median-delays-points",
                        style={"margin-bottom": "40px"},
                    ),
                ]
            ),
        ],
    ),
]

tab_2_content_lp = [
    html.H2("Sequence Mining"),
    html.P(
        "Detecting positive and negative slopes in delays/EWT for transportation vehicle highlights whether it is creating delays or not. This analysis is useful to assess how delay is propagating through a sequence of stops.",
        style={"margin-bottom": "50px", "max-width": "150ch"},
    ),
    dbc.Row(
        style={"margin-bottom": "40px"},
        children=[
            dbc.Col(
                children=[
                    html.H4(
                        "Problematic segment in delay (sec)",
                    ),
                    html.P(
                        """
                            Mapping the slope of delays at each stop highlights the stops that are increasing the delays and affecting the network and the stops that are catching the delays and helping smoothening the network. 
                        """,
                        style={
                            "max-width": "150ch",
                        },
                    ),
                    dcc.Graph(
                        id="chart-delay-prop",
                        style={"margin-bottom": "40px"},
                    ),
                ]
            ),
            dbc.Col(
                children=[
                    html.H4(
                        "Problematic segment in EWT (min)",
                    ),
                    html.P(
                        """
                            Mapping the slope of EWT at each stop highlights the positive and negative stops. The negative stops are increasing the irregularity of the network and worsening the additional waiting time for passenger.  The positive stops are catching the irregularity and help reducing the additional waiting time for passengers. 
                        """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dcc.Graph(
                        id="chart-EWT-prop",
                        style={"margin-bottom": "40px"},
                    ),
                ]
            ),
        ],
    ),
    html.H4("Median delay evolution"),
    html.P(
        """
        Analysing the median delay / EWT through a sequence of stops for all the observed days shows if there are any repeating trends in slopes and frequent patterns (Daily filter not applicable, use the legend to focus).
    """,
        style={
            "max-width": "150ch",
            "margin-bottom": "10px",
        },
    ),
    dbc.Row(
        children=[
            dbc.Col(
                width="auto",
                children=html.P(
                    "EWT : ",
                    style={"margin-right": "5px"},
                ),
            ),
            dbc.Col(
                width="auto",
                children=daq.ToggleSwitch(
                    style={"width": "150px"},
                    id="toggle-punct-EWT",
                    value=False,
                    size=45,
                ),
            ),
        ],
    ),
    dcc.Graph(
        id="sequence-evolution",
        style={"margin-bottom": "40px"},
    ),
]

tab_2_content = [
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
                        id="lines_drop_down_value",
                        clearable=False,
                        style={"margin-bottom": "20px"},
                    ),
                    html.P("Workday/Weekday", style={"margin-bottom": "3px"}),
                    dcc.Dropdown(
                        clearable=False,
                        id="date_label_drop_down_value",
                        style={"margin-bottom": "20px"},
                    ),
                    html.P(
                        "Day (only for Sequence Mining)", style={"margin-bottom": "3px"}
                    ),
                    dcc.Dropdown(
                        clearable=False,
                        id="exact_date",
                        style={"margin-bottom": "20px"},
                    ),
                    html.P("Direction", style={"margin-bottom": "3px"}),
                    dcc.Dropdown(
                        clearable=False,
                        id="dir_drop_down_value",
                        style={"margin-bottom": "50px"},
                    ),
                    html.Hr(className="my-2"),
                    html.H5(children="Summary", style={"margin-top": "50px"}),
                    html.P(id="text-summary"),
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
                                children=tab_1_content_lp,
                                label="Line Performances",
                                style={"padding-top": "20px", "padding-bottom": "20px"},
                            ),
                            dbc.Tab(
                                children=tab_2_content_lp,
                                label="Sequence Analysis",
                                style={"padding-top": "20px", "padding-bottom": "20px"},
                            ),
                        ]
                    ),
                ],
            ),
        ],
    ),
]

layout = html.Div(
    children=[
        html.H1(children="Segment Performances"),
        dbc.Tabs(
            children=[
                dbc.Tab(
                    children=tab_1_content,
                    label="Overview",
                    style={"padding-top": "20px", "padding-bottom": "20px"},
                ),
                dbc.Tab(
                    children=tab_2_content,
                    label="Specific",
                    style={"padding-top": "20px", "padding-bottom": "20px"},
                ),
            ]
        ),
    ]
)

# Callbacks for dropdown filters


@callback(
    [
        Output("date_label_drop_down_value", "options"),
        Output("date_label_drop_down_value", "value"),
    ],
    Input("lines_drop_down_value", "value"),
)
def update_stops(value):
    temp = data[data.route_short_name == str(value)]["date_label"].unique()
    return temp, temp[0]


@callback(
    [
        Output("dir_drop_down_value", "options"),
        Output("dir_drop_down_value", "value"),
    ],
    [
        Input("lines_drop_down_value", "value"),
        Input("date_label_drop_down_value", "value"),
    ],
)
def update_direction(route, date):
    temp = data[(data.route_short_name == str(route)) & (data.date_label == date)][
        "trip_headsign"
    ].unique()
    return temp, temp[0]


@callback(
    Output("text-summary", "children"),
    [
        Input("lines_drop_down_value", "value"),
        Input("date_label_drop_down_value", "value"),
        Input("dir_drop_down_value", "value"),
    ],
)
def update_summary(line, date_label, direction):

    transport_type = {"M": "metro", "T": "tram", "B": "bus"}
    temp = data_g.get_group((str(line), date_label, direction, "lat"))
    mode = transport_type.get(temp.iloc[0]["mode"])
    name = temp.iloc[0].route_long_name.split(" - ")
    # origin = temp.sort_values(by = "th_time_sec").iloc[0].stop_name

    return f"You have selected the {mode} {str(line)}, operating between {name[0]} and {name[1]}, in direction of {direction} during {date_label}."


@callback(
    Output("dd-sum-delays", "figure"),
    [
        Input("lines_drop_down_value", "value"),
        Input("date_label_drop_down_value", "value"),
        Input("dir_drop_down_value", "value"),
    ],
)
def map_line_delays(line, date_label, direction):

    temp = data_g.get_group((str(line), date_label, direction, "lat"))

    temp = (
        temp[["stop_id", "delay"]]
        .groupby("stop_id", as_index=False)
        .sum("delay")
        .merge(coord, "left", "stop_id")
        .merge(temp[["stop_id", "stop_name"]].drop_duplicates(), "left", "stop_id")
    )

    fig = px.density_mapbox(
        temp,
        lat="stop_lat",
        lon="stop_lon",
        z="delay",
        radius=20,
        center=dict(lat=50.85, lon=4.45),
        zoom=10,
        color_continuous_scale="portland",
        mapbox_style="light",
        hover_data=["delay"],
        hover_name="stop_name",
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


@callback(
    Output("dd-median-delays", "figure"),
    [
        Input("lines_drop_down_value", "value"),
        Input("date_label_drop_down_value", "value"),
        Input("dir_drop_down_value", "value"),
    ],
)
def map_line_delays(line, date_label, direction):

    temp = data_g.get_group((str(line), date_label, direction, "lat"))

    temp = (
        temp[["stop_id", "delay"]]
        .groupby("stop_id", as_index=False)
        .median("delay")
        .merge(coord, "left", "stop_id")
        .merge(temp[["stop_id", "stop_name"]].drop_duplicates(), "left", "stop_id")
    )

    fig = px.density_mapbox(
        temp,
        lat="stop_lat",
        lon="stop_lon",
        z="delay",
        radius=20,
        center=dict(lat=50.85, lon=4.45),
        zoom=10,
        color_continuous_scale="portland",
        mapbox_style="light",
        hover_data=["delay"],
        hover_name="stop_name",
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


@callback(
    Output("dd-sum-delays-points", "figure"),
    [
        Input("lines_drop_down_value", "value"),
        Input("date_label_drop_down_value", "value"),
        Input("dir_drop_down_value", "value"),
    ],
)
def map_line_delays_points(line, date_label, direction):

    temp = data_g.get_group((str(line), date_label, direction, "lat"))

    temp = (
        temp[["stop_id", "delay"]]
        .groupby("stop_id", as_index=False)
        .sum("delay")
        .merge(coord, "left", "stop_id")
        .merge(temp[["stop_id", "stop_name"]].drop_duplicates(), "left", "stop_id")
    )

    fig = px.scatter_mapbox(
        temp,
        lat="stop_lat",
        lon="stop_lon",
        color="delay",
        zoom=10,
        size="delay",
        color_continuous_scale="portland",
        hover_data=["delay"],
        hover_name="stop_name",
    ).update_layout(mapbox_style="light", margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


@callback(
    Output("dd-median-delays-points", "figure"),
    [
        Input("lines_drop_down_value", "value"),
        Input("date_label_drop_down_value", "value"),
        Input("dir_drop_down_value", "value"),
    ],
)
def map_line_delays_points(line, date_label, direction):

    temp = data_g.get_group((str(line), date_label, direction, "lat"))

    temp = (
        temp[["stop_id", "delay"]]
        .groupby("stop_id", as_index=False)
        .median("delay")
        .merge(coord, "left", "stop_id")
        .merge(temp[["stop_id", "stop_name"]].drop_duplicates(), "left", "stop_id")
    )

    fig = px.scatter_mapbox(
        temp,
        lat="stop_lat",
        lon="stop_lon",
        color="delay",
        size="delay",
        zoom=10,
        color_continuous_scale="portland",
        hover_data=["delay"],
        hover_name="stop_name",
    ).update_layout(mapbox_style="light", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


@callback(
    Output("sequence-evolution", "figure"),
    [
        Input("lines_drop_down_value", "value"),
        Input("dir_drop_down_value", "value"),
        Input("date_label_drop_down_value", "value"),
        Input("toggle-punct-EWT", "value"),
    ],
)
def map_line_delays_points(line, direction, date_label, EWT):

    _ = data_g_spec.get_group((str(line), direction))
    _ = _[(_["date_label"] == date_label)]

    m = "EWT" if EWT else "delay"
    unit = "min" if EWT else "sec"

    _ = (
        _[
            [
                "route_short_name",
                "stop_name",
                "date_normalized",
                "direction_id",
                "succession",
                "EWT" if EWT else "delay",
            ]
        ]
        .groupby(
            [
                "route_short_name",
                "stop_name",
                "date_normalized",
                "direction_id",
                "succession",
            ],
            as_index=False,
        )
        .median()
    )

    fig = px.scatter(
        _,
        x="succession",
        y="EWT" if EWT else "delay",
        labels=dict(
            succession="Stop sequence order",
            date_normalized="date",
        ),
        hover_data=["stop_name"],
        color="date_normalized",
    )

    fig.update_layout(
        {"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)"},
        yaxis_title=f"Median {m} ({unit})",
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="gray")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="gray")

    return fig


@callback(
    [
        Output("exact_date", "options"),
        Output("exact_date", "value"),
    ],
    [
        Input("lines_drop_down_value", "value"),
        Input("date_label_drop_down_value", "value"),
        Input("dir_drop_down_value", "value"),
    ],
)
def date_update(line, date_label, direction):
    _ = data_g_nd.get_group((str(line), date_label, direction)).date_normalized.unique()
    return _, _[0]


@callback(
    Output("chart-delay-prop", "figure"),
    [
        Input("lines_drop_down_value", "value"),
        Input("exact_date", "value"),
        Input("dir_drop_down_value", "value"),
    ],
)
def map_line_delays_points(line, date_label, direction):

    _ = lg_g.get_group((str(line), date_label, direction))

    _["lab_growth"] = _["lab_growth"].astype(str)
    fig = px.scatter_mapbox(
        _,
        lat="stop_lat",
        lon="stop_lon",
        hover_name="stop_name",
        color="lab_growth",
        zoom=10,
        labels=dict(lab_growth="Slope sign"),
    )

    fig.update_layout(mapbox_style="light", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


@callback(
    Output("chart-EWT-prop", "figure"),
    [
        Input("lines_drop_down_value", "value"),
        Input("exact_date", "value"),
        Input("dir_drop_down_value", "value"),
    ],
)
def map_line_delays_points(line, date_label, direction):

    _ = lg_ge.get_group((str(line), date_label, direction))

    _["lab_growth"] = _["lab_growth"].astype(str)
    fig = px.scatter_mapbox(
        _,
        lat="stop_lat",
        lon="stop_lon",
        hover_name="stop_name",
        color="lab_growth",
        zoom=10,
        labels=dict(lab_growth="Slope sign"),
    )

    fig.update_layout(mapbox_style="light", margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig

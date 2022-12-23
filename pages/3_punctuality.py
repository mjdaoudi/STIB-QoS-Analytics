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
    title="Punctuality",
    name="Punctuality",
)

data = pd.read_pickle("data/computed/matches_clean_EWT_delay.pkl")

data_g = data.groupby(["route_short_name", "date_label", "trip_headsign"])
coord = pd.read_pickle("data/computed/stops.geo.pkl")

unique_routes = np.sort(data.route_short_name.unique().astype(int)).tolist()


tab_1_content = [
    html.H2(
        "Overall performance",
    ),
    dbc.Row(
        children=[
            dbc.Col(
                width=6,
                style={
                    "padding": "10px 20px",
                },
                children=[
                    html.H4(
                        "Median delay per hour",
                    ),
                    html.P(
                        """
                            The median delay per hour is highlighting the overall delay for the STIB network during the day for each transportation mode. It can be further analysed by drilling down on the day label.
                        """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dbc.Row(
                        justify="start",
                        children=[
                            dbc.Col(
                                width="auto",
                                children=html.P(
                                    "Day label :", style={"margin-right": "5px"}
                                ),
                            ),
                            dbc.Col(
                                width="auto",
                                children=dcc.RadioItems(
                                    ["all", "workdays", "saturday", "sunday"],
                                    "all",
                                    inline=True,
                                    id="gen-radio-hour",
                                    labelStyle={"margin-right": "20px"},
                                    inputStyle={"margin-right": "5px"},
                                ),
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="gen-median-hour",
                        style={"margin-bottom": "40px"},
                    ),
                ],
            ),
            dbc.Col(
                width=6,
                style={
                    "padding": "10px 20px",
                },
                children=[
                    html.H4(
                        "Median delay per day",
                    ),
                    html.P(
                        """
                    The median delay per day is highlighting the overall delay for the STIB network during the observation period for each transportation mode. It can be further analysed by drilling down on the day label.
                """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dbc.Row(
                        justify="start",
                        children=[
                            dbc.Col(
                                width="auto",
                                children=html.P(
                                    "Day label :", style={"margin-right": "5px"}
                                ),
                            ),
                            dbc.Col(
                                width="auto",
                                children=dcc.RadioItems(
                                    ["all", "workdays", "saturday", "sunday"],
                                    "all",
                                    inline=True,
                                    id="gen-radio-day",
                                    labelStyle={"margin-right": "20px"},
                                    inputStyle={"margin-right": "5px"},
                                ),
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="gen-median-day",
                        style={"margin-bottom": "40px"},
                    ),
                ],
            ),
        ]
    ),
    html.H2(
        "On time positionning (OTP)",
    ),
    dbc.Row(
        children=[
            dbc.Col(
                width=6,
                style={
                    "padding": "10px 20px",
                },
                children=[
                    html.H4(
                        "OTP per hour",
                    ),
                    html.P(
                        """
                    The OTP is used to assess the share of vehicle arriving on time. By on time, several definitions can affect its performance. These can be loose or stricter. Analysing it per hour can show signs of pressure on the network on certain hours.
                """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dbc.Row(
                        justify="start",
                        children=[
                            dbc.Col(
                                width="auto",
                                children=html.P(
                                    "Delay definition :", style={"margin-right": "5px"}
                                ),
                            ),
                            dbc.Col(
                                width="auto",
                                children=dcc.RadioItems(
                                    ["120s", "60s", "strict"],
                                    "120s",
                                    inline=True,
                                    id="gen-radio-hour-otp",
                                    labelStyle={"margin-right": "20px"},
                                    inputStyle={"margin-right": "5px"},
                                ),
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="gen-OTP-hour",
                        style={"margin-bottom": "40px"},
                    ),
                ],
            ),
            dbc.Col(
                width=6,
                style={
                    "padding": "10px 20px",
                },
                children=[
                    html.H4(
                        "OTP per day",
                    ),
                    html.P(
                        """
                    The OTP is used to assess the share of vehicle arriving on time. By on time, several definitions can affect its performance. These can be loose or stricter. Analysing it per day can show sign of pressure on the network on certain days. The punctuality focus label is cutting the data on only the punctuality clusters defined on the theoretical headway page.
                """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dbc.Row(
                        justify="start",
                        children=[
                            dbc.Col(
                                width="auto",
                                children=html.P(
                                    "Delay definition :", style={"margin-right": "5px"}
                                ),
                            ),
                            dbc.Col(
                                width="auto",
                                children=dcc.RadioItems(
                                    ["120s", "60s", "strict"],
                                    "120s",
                                    inline=True,
                                    id="gen-radio-day-otp",
                                    labelStyle={"margin-right": "20px"},
                                    inputStyle={"margin-right": "5px"},
                                ),
                            ),
                            dbc.Col(
                                width="auto",
                                children=dbc.Row(
                                    children=[
                                        dbc.Col(
                                            width="auto",
                                            children=html.P(
                                                "Punctuality Focus : ",
                                                style={"margin-right": "5px"},
                                            ),
                                        ),
                                        dbc.Col(
                                            width="auto",
                                            children=daq.ToggleSwitch(
                                                style={"width": "150px"},
                                                id="toggle-punct",
                                                value=False,
                                                size=45,
                                            ),
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="gen-OTP-day",
                        style={"margin-bottom": "40px"},
                    ),
                ],
            ),
        ]
    ),
    dbc.Row(
        children=[
            dbc.Col(
                width=6,
                style={
                    "padding": "10px 20px",
                },
                children=[
                    html.H4(
                        "Median Delay vs OTP(%) in lines",
                    ),
                    html.P(
                        """
                        Assessing the median delay on a line level compared to its OTP can highlight top tier lines (high OTP – low delay) compared to weak performer ones.
                        """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dbc.Row(
                        justify="start",
                        children=[
                            dbc.Col(
                                width="auto",
                                children=html.P(
                                    "Delay definition :", style={"margin-right": "5px"}
                                ),
                            ),
                            dbc.Col(
                                width="auto",
                                children=dcc.RadioItems(
                                    ["120s", "60s", "strict"],
                                    "120s",
                                    inline=True,
                                    id="gen-radio-line-otp",
                                    labelStyle={"margin-right": "20px"},
                                    inputStyle={"margin-right": "5px"},
                                ),
                            ),
                            dbc.Col(
                                width="auto",
                                children=dbc.Row(
                                    children=[
                                        dbc.Col(
                                            width="auto",
                                            children=html.P(
                                                "Punctuality Focus : ",
                                                style={"margin-right": "5px"},
                                            ),
                                        ),
                                        dbc.Col(
                                            width="auto",
                                            children=daq.ToggleSwitch(
                                                style={"width": "150px"},
                                                id="toggle-punct-line",
                                                value=False,
                                                size=45,
                                            ),
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="gen-line-opt",
                        style={"margin-bottom": "40px"},
                    ),
                ],
            ),
            dbc.Col(
                width=6,
                style={
                    "padding": "10px 20px",
                },
                children=[
                    html.H4(
                        "Median Delay vs OTP(%) in stops",
                    ),
                    html.P(
                        """
                    Assessing the median delay on a stop level compared to its OTP can highlight top tier stops (high OTP – low delay) compared to weak performer ones. Analyst can further deep dive on the specific tab.
                """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dbc.Row(
                        justify="start",
                        children=[
                            dbc.Col(
                                width="auto",
                                children=html.P(
                                    "Delay definition :", style={"margin-right": "5px"}
                                ),
                            ),
                            dbc.Col(
                                width="auto",
                                children=dcc.RadioItems(
                                    ["120s", "60s", "strict"],
                                    "120s",
                                    inline=True,
                                    id="gen-radio-stops-otp",
                                    labelStyle={"margin-right": "20px"},
                                    inputStyle={"margin-right": "5px"},
                                ),
                            ),
                            dbc.Col(
                                width="auto",
                                children=dbc.Row(
                                    children=[
                                        dbc.Col(
                                            width="auto",
                                            children=html.P(
                                                "Punctuality Focus : ",
                                                style={"margin-right": "5px"},
                                            ),
                                        ),
                                        dbc.Col(
                                            width="auto",
                                            children=daq.ToggleSwitch(
                                                style={"width": "150px"},
                                                id="toggle-punct-stops",
                                                value=False,
                                                size=45,
                                            ),
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="gen-stops-otp-delay",
                        style={"margin-bottom": "40px"},
                    ),
                ],
            ),
        ]
    ),
]

tab_2_content = (
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
                        id="lines_drop_down_value-p",
                        clearable=False,
                        style={"margin-bottom": "20px"},
                    ),
                    html.P("Workday/Weekday", style={"margin-bottom": "3px"}),
                    dcc.Dropdown(
                        clearable=False,
                        id="date_label_drop_down_value-p",
                        style={"margin-bottom": "20px"},
                    ),
                    html.P("Direction", style={"margin-bottom": "3px"}),
                    dcc.Dropdown(
                        clearable=False,
                        id="dir_drop_down_value-p",
                        style={"margin-bottom": "20px"},
                    ),
                    html.P(
                        "Delay definition (OTP only)", style={"margin-bottom": "3px"}
                    ),
                    dcc.RadioItems(
                        ["120s", "60s", "strict"],
                        "120s",
                        style={"margin-bottom": "20px"},
                        inline=True,
                        id="gen-radio-p",
                        labelStyle={"margin-right": "20px"},
                        inputStyle={"margin-right": "5px"},
                    ),
                    dbc.Row(
                        style={"margin-bottom": "50px"},
                        children=[
                            dbc.Col(
                                width="auto",
                                children=html.P(
                                    "Punctuality Focus : ",
                                    style={"margin-right": "5px"},
                                ),
                            ),
                            dbc.Col(
                                width="auto",
                                children=daq.ToggleSwitch(
                                    style={"width": "150px"},
                                    id="toggle-punct-p",
                                    value=False,
                                    size=45,
                                ),
                            ),
                        ],
                    ),
                    html.Hr(className="my-2"),
                    html.H5(children="Summary", style={"margin-top": "50px"}),
                    html.P(id="text-summary-p"),
                ],
            ),
            dbc.Col(
                style={
                    "padding": "10px 20px",
                    "height": "86vh",
                    "overflow": "scroll",
                },
                children=[
                    html.H2(
                        "Performance per line",
                    ),
                    html.P(
                        """
                                Each line can be analysed depending on the filters selected on the left pane. Two types of visualization are available, the evolution during a day and the evolution between days. This enables analysts to have a view on how the delays are evolving for a specific line. 
                            """,
                        style={"margin-bottom": "40px", "max-width": "150ch"},
                    ),
                    dbc.Row(
                        style={"margin-bottom": "40px"},
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4(
                                        "Median delay per hour",
                                    ),
                                    html.P(
                                        """
                                                The median delay per hour is highlighting the overall delay for the chosen line during the chosen type of day. 
                                            """,
                                        style={
                                            "max-width": "150ch",
                                            "margin-bottom": "10px",
                                        },
                                    ),
                                    dcc.Graph(
                                        id="median-hour-spec",
                                        style={"margin-bottom": "40px"},
                                    ),
                                ]
                            ),
                            dbc.Col(
                                children=[
                                    html.H4(
                                        "Median delay per day",
                                    ),
                                    html.P(
                                        """
                                                The median delay per day is highlighting the overall delay for the chosen line and chose type of day during the observation period. 
                                            """,
                                        style={
                                            "max-width": "150ch",
                                            "margin-bottom": "10px",
                                        },
                                    ),
                                    dcc.Graph(
                                        id="median-day-spec",
                                        style={"margin-bottom": "40px"},
                                    ),
                                ]
                            ),
                        ],
                    ),
                    html.H2(
                        "On time performance (OTP)",
                    ),
                    html.P(
                        """
                                Each line can be analysed depending on the filters selected on the left pane. Two types of visualization are available, the evolution during a day and the evolution between days. This enables analysts to have a view on how the OTP are evolving for a specific line. 
                            """,
                        style={"margin-bottom": "40px", "max-width": "150ch"},
                    ),
                    dbc.Row(
                        style={"margin-bottom": "40px"},
                        children=[
                            dbc.Col(
                                children=[
                                    html.H4(
                                        "OTP per hour",
                                    ),
                                    html.P(
                                        """
                                    The OTP per hour is highlighting the overall OTP for the chosen line during the chosen type of day. 
                                """,
                                        style={
                                            "max-width": "150ch",
                                            "margin-bottom": "10px",
                                        },
                                    ),
                                    dcc.Graph(
                                        id="OTP-hour-spec",
                                        style={"margin-bottom": "40px"},
                                    ),
                                ]
                            ),
                            dbc.Col(
                                children=[
                                    html.H4(
                                        "OTP per day",
                                    ),
                                    html.P(
                                        """
                                    The OTP per day is highlighting the overall OTP for the chosen line and chosen type of day during the observation period. 
                                """,
                                        style={
                                            "max-width": "150ch",
                                            "margin-bottom": "10px",
                                        },
                                    ),
                                    dcc.Graph(
                                        id="OTP-day-spec",
                                        style={"margin-bottom": "40px"},
                                    ),
                                ]
                            ),
                        ],
                    ),
                    html.H4(
                        "Median Delay vs OTP(%) in stops",
                    ),
                    html.P(
                        """
                           Assessing the median delay on a stop level compared to its OTP can highlight for a specific line top tier stops (high OTP – low delay) compared to weak performer ones.  
                        """,
                        style={
                            "max-width": "150ch",
                            "margin-bottom": "10px",
                        },
                    ),
                    dcc.Graph(
                        id="gen-stops-otp-delay-spec", style={"margin-bottom": "40px"}
                    ),
                ],
            ),
        ],
    ),
)

layout = [
    html.H1(children="Punctuality Analysis"),
    dbc.Tabs(
        children=[
            dbc.Tab(
                tab_1_content,
                label="Overview",
                style={"padding-top": "20px", "padding-bottom": "20px"},
            ),
            dbc.Tab(
                tab_2_content,
                label="Specific",
                style={"padding-top": "20px", "padding-bottom": "20px"},
            ),
        ],
    ),
]

# Callbacks for dropdown filters


@callback(
    [
        Output("date_label_drop_down_value-p", "options"),
        Output("date_label_drop_down_value-p", "value"),
    ],
    Input("lines_drop_down_value-p", "value"),
)
def update_stops(value):
    temp = data[data.route_short_name == str(value)]["date_label"].unique()
    return temp, temp[0]


@callback(
    [
        Output("dir_drop_down_value-p", "options"),
        Output("dir_drop_down_value-p", "value"),
    ],
    [
        Input("lines_drop_down_value-p", "value"),
        Input("date_label_drop_down_value-p", "value"),
    ],
)
def update_direction(route, date):
    temp = data[(data.route_short_name == str(route)) & (data.date_label == date)][
        "trip_headsign"
    ].unique()
    return temp, temp[0]


@callback(
    Output("text-summary-p", "children"),
    [
        Input("lines_drop_down_value-p", "value"),
        Input("date_label_drop_down_value-p", "value"),
        Input("dir_drop_down_value-p", "value"),
    ],
)
def update_summary(line, date_label, direction):
    if (line != None) & ((date_label != None)) & ((direction != None)):
        transport_type = {"M": "metro", "T": "tram", "B": "bus"}
        temp = data_g.get_group((str(line), date_label, direction))
        mode = transport_type.get(temp.iloc[0]["mode"])
        name = temp.iloc[0].route_long_name.split(" - ")
        # origin = temp.sort_values(by = "th_time_sec").iloc[0].stop_name

        s = f"You have selected the {mode} {str(line)}, operating between {name[0]} and {name[1]}, in direction of {direction} during {date_label}."
    else:
        s = "No summary yet available."

    return s


# Callbacks general charts
@callback(
    Output("gen-median-hour", "figure"),
    [
        Input("gen-radio-hour", "value"),
    ],
)
def gen_hour_delay(value):

    _ = (
        data[data.regularity == 0]
        if value == "all"
        else data[(data.regularity == 0) & (data.date_label == value)]
    )

    _ = _[["hour", "mode", "delay"]].groupby(["hour", "mode"], as_index=False).median()
    _ = _[_.hour <= 24]

    fig = px.line(
        _,
        x="hour",
        y="delay",
        color="mode",
        labels=dict(hour="Hour of the day", delay="Median delay (in sec)"),
    ).update_layout({"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)"})
    fig.update_xaxes(showline=True, linewidth=1, linecolor="gray")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="gray")

    return fig


@callback(
    Output("gen-median-day", "figure"),
    [
        Input("gen-radio-day", "value"),
    ],
)
def gen_day_delay(value):

    _ = (
        data[(data.regularity == 0)]
        if value == "all"
        else data[(data.regularity == 0) & (data.date_label == value)]
    )

    _ = _[["day", "mode", "delay"]].groupby(["day", "mode"], as_index=False).median()

    fig = px.line(
        _,
        x="day",
        y="delay",
        color="mode",
        labels=dict(day="Daily evolution", delay="Median delay (in sec)"),
    ).update_layout({"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)"})
    fig.update_xaxes(showline=True, linewidth=1, linecolor="gray")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="gray")

    return fig


@callback(
    Output("gen-OTP-hour", "figure"),
    [
        Input("gen-radio-hour-otp", "value"),
    ],
)
def gen_OTP_hour(value):

    d = {
        "strict": "delay_label_strict",
        "60s": "delay_label_60",
        "120s": "delay_label_120",
    }

    _ = (
        data[["hour", "mode", d[value]]]
        .groupby(["hour", "mode"], as_index=False)
        .apply(
            lambda x: pd.Series(
                {"OTP": (x[x[d[value]] == "nan"].shape[0] / x.shape[0]) * 100}
            )
        )
    )

    _ = _[_.hour <= 24]

    fig = px.line(
        _,
        x="hour",
        y="OTP",
        color="mode",
        labels=dict(hour="Hour of the day (h)", OTP="OTP (%)"),
    )

    fig.update_layout(
        {"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)"}
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="gray")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="gray", rangemode="tozero")

    return fig


@callback(
    Output("gen-OTP-day", "figure"),
    [
        Input("gen-radio-day-otp", "value"),
        Input("toggle-punct", "value"),
    ],
)
def gen_OTP_day(value, punct):

    d = {
        "strict": "delay_label_strict",
        "60s": "delay_label_60",
        "120s": "delay_label_120",
    }

    if punct:
        _ = (
            data[data.regularity == 0][["day", "mode", d[value]]]
            .groupby(["day", "mode"], as_index=False)
            .apply(
                lambda x: pd.Series(
                    {"OTP": (x[x[d[value]] == "nan"].shape[0] / x.shape[0]) * 100}
                )
            )
        )
    else:
        _ = (
            data[["day", "mode", d[value]]]
            .groupby(["day", "mode"], as_index=False)
            .apply(
                lambda x: pd.Series(
                    {"OTP": (x[x[d[value]] == "nan"].shape[0] / x.shape[0]) * 100}
                )
            )
        )

    fig = px.line(
        _,
        x="day",
        y="OTP",
        color="mode",
        labels=dict(day="Daily evolution", OTP="OTP (%)"),
    )

    fig.update_layout(
        {"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)"}
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="gray")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="gray", rangemode="tozero")

    return fig


@callback(
    Output("gen-line-opt", "figure"),
    [
        Input("gen-radio-line-otp", "value"),
        Input("toggle-punct-line", "value"),
    ],
)
def gen_OTP_median_line(value, punct):

    d = {
        "strict": "delay_label_strict",
        "60s": "delay_label_60",
        "120s": "delay_label_120",
    }

    if punct:
        _ = (
            data[data.regularity == 0][["route_short_name", d[value], "delay"]]
            .groupby(["route_short_name"], as_index=False)
            .apply(
                lambda x: pd.Series(
                    {
                        "OTP": (x[x[d[value]] == "nan"].shape[0] / x.shape[0]) * 100,
                        "median": x.delay.median(),
                    }
                )
            )
        )
    else:
        _ = (
            data[["route_short_name", d[value], "delay"]]
            .groupby(["route_short_name"], as_index=False)
            .apply(
                lambda x: pd.Series(
                    {
                        "OTP": (x[x[d[value]] == "nan"].shape[0] / x.shape[0]) * 100,
                        "median": x.delay.median(),
                    }
                )
            )
        )

    fig = px.scatter(
        _,
        x="OTP",
        y="median",
        color="route_short_name",
        text="route_short_name",
        trendline="lowess",
        trendline_scope="overall",
        labels=dict(
            OTP="OTP (%)", median="Median delays (sec)", route_short_name="Line"
        ),
    )

    fig.update_traces(textposition="top center")
    fig.update_layout(
        {"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)"}
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="gray")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="gray")

    return fig


@callback(
    Output("gen-stops-otp-delay", "figure"),
    [
        Input("gen-radio-stops-otp", "value"),
        Input("toggle-punct-stops", "value"),
    ],
)
def gen_OTP_median_stops(value, punct):

    d = {
        "strict": "delay_label_strict",
        "60s": "delay_label_60",
        "120s": "delay_label_120",
    }

    if punct:
        _ = (
            data[data.regularity == 0][["stop_name", d[value], "delay"]]
            .groupby(["stop_name"], as_index=False)
            .apply(
                lambda x: pd.Series(
                    {
                        "OTP": (x[x[d[value]] == "nan"].shape[0] / x.shape[0]) * 100,
                        "median": x.delay.median(),
                    }
                )
            )
        )
    else:
        _ = (
            data[["stop_name", d[value], "delay"]]
            .groupby(["stop_name"], as_index=False)
            .apply(
                lambda x: pd.Series(
                    {
                        "OTP": (x[x[d[value]] == "nan"].shape[0] / x.shape[0]) * 100,
                        "median": x.delay.median(),
                    }
                )
            )
        )

    fig = px.scatter(
        _,
        x="OTP",
        y="median",
        color="stop_name",
        trendline="lowess",
        trendline_scope="overall",
        labels=dict(OTP="OTP (%)", median="Median delays (sec)", stop_name="Stop Name"),
    )

    fig.update_layout(
        {"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)"}
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="gray")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="gray")

    return fig


@callback(
    Output("median-hour-spec", "figure"),
    [
        Input("lines_drop_down_value-p", "value"),
        Input("date_label_drop_down_value-p", "value"),
        Input("dir_drop_down_value-p", "value"),
        Input("gen-radio-p", "value"),
        Input("toggle-punct-p", "value"),
    ],
)
def median_delay_hour_spec(line, date_label, direction, strict, punct):
    d = {
        "strict": "delay_label_strict",
        "60s": "delay_label_60",
        "120s": "delay_label_120",
    }
    _ = data_g.get_group((str(line), date_label, direction))

    _ = _[(_.regularity == 0)] if punct else _
    _ = _[_.hour <= 24]

    _ = _[["hour", "delay"]].groupby(["hour"], as_index=False).median()

    fig = px.line(
        _,
        x="hour",
        y="delay",
        labels=dict(hour="Hour of the day", delay="Median delay (in sec)"),
    ).update_layout({"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)"})
    fig.update_xaxes(showline=True, linewidth=1, linecolor="gray")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="gray")

    return fig


@callback(
    Output("median-day-spec", "figure"),
    [
        Input("lines_drop_down_value-p", "value"),
        Input("date_label_drop_down_value-p", "value"),
        Input("dir_drop_down_value-p", "value"),
        Input("gen-radio-p", "value"),
        Input("toggle-punct-p", "value"),
    ],
)
def median_delay_day_spec(line, date_label, direction, strict, punct):
    d = {
        "strict": "delay_label_strict",
        "60s": "delay_label_60",
        "120s": "delay_label_120",
    }
    _ = data_g.get_group((str(line), date_label, direction))

    _ = _[(_.regularity == 0)] if punct else _

    _ = _[["day", "delay"]].groupby(["day"], as_index=False).median()

    fig = px.line(
        _,
        x="day",
        y="delay",
        labels=dict(day="Daily evolution", delay="Median delay (in sec)"),
    ).update_layout({"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)"})
    fig.update_xaxes(showline=True, linewidth=1, linecolor="gray")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="gray")

    return fig


@callback(
    Output("OTP-hour-spec", "figure"),
    [
        Input("lines_drop_down_value-p", "value"),
        Input("date_label_drop_down_value-p", "value"),
        Input("dir_drop_down_value-p", "value"),
        Input("gen-radio-p", "value"),
        Input("toggle-punct-p", "value"),
    ],
)
def otp_hour_spec(line, date_label, direction, strict, punct):
    d = {
        "strict": "delay_label_strict",
        "60s": "delay_label_60",
        "120s": "delay_label_120",
    }
    _ = data_g.get_group((str(line), date_label, direction))

    _ = _[(_.regularity == 0)] if punct else _

    _ = _[_.hour <= 24]

    _ = (
        _[["hour", d[strict]]]
        .groupby(
            [
                "hour",
            ],
            as_index=False,
        )
        .apply(
            lambda x: pd.Series(
                {"OTP": (x[x[d[strict]] == "nan"].shape[0] / x.shape[0]) * 100}
            )
        )
    )

    fig = px.line(
        _,
        x="hour",
        y="OTP",
        labels=dict(hour="Hour of the day(h)", OTP="OTP (in %)"),
    ).update_layout({"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)"})
    fig.update_xaxes(showline=True, linewidth=1, linecolor="gray")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="gray", rangemode="tozero")

    return fig


@callback(
    Output("OTP-day-spec", "figure"),
    [
        Input("lines_drop_down_value-p", "value"),
        Input("date_label_drop_down_value-p", "value"),
        Input("dir_drop_down_value-p", "value"),
        Input("gen-radio-p", "value"),
        Input("toggle-punct-p", "value"),
    ],
)
def otp_day_spec(line, date_label, direction, strict, punct):
    d = {
        "strict": "delay_label_strict",
        "60s": "delay_label_60",
        "120s": "delay_label_120",
    }
    _ = data_g.get_group((str(line), date_label, direction))

    _ = _[(_.regularity == 0)] if punct else _

    _ = (
        _[["day", d[strict]]]
        .groupby(
            [
                "day",
            ],
            as_index=False,
        )
        .apply(
            lambda x: pd.Series(
                {"OTP": (x[x[d[strict]] == "nan"].shape[0] / x.shape[0]) * 100}
            )
        )
    )

    fig = px.line(
        _,
        x="day",
        y="OTP",
        labels=dict(day="Daily evolution", OTP="OTP (in %)"),
    ).update_layout({"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)"})
    fig.update_xaxes(showline=True, linewidth=1, linecolor="gray")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="gray", rangemode="tozero")

    return fig


@callback(
    Output("gen-stops-otp-delay-spec", "figure"),
    [
        Input("lines_drop_down_value-p", "value"),
        Input("date_label_drop_down_value-p", "value"),
        Input("dir_drop_down_value-p", "value"),
        Input("gen-radio-p", "value"),
        Input("toggle-punct-p", "value"),
    ],
)
def gen_OTP_median_stops(line, date_label, direction, strict, punct):

    d = {
        "strict": "delay_label_strict",
        "60s": "delay_label_60",
        "120s": "delay_label_120",
    }

    _ = data_g.get_group((str(line), date_label, direction))
    _ = _[(_.regularity == 0)] if punct else _

    _ = (
        _[["stop_name", d[strict], "delay"]]
        .groupby(["stop_name"], as_index=False)
        .apply(
            lambda x: pd.Series(
                {
                    "OTP": (x[x[d[strict]] == "nan"].shape[0] / x.shape[0]) * 100,
                    "median": x.delay.median(),
                }
            )
        )
    )

    fig = px.scatter(
        _,
        x="OTP",
        y="median",
        color="stop_name",
        trendline="ols",
        trendline_scope="overall",
        labels=dict(OTP="OTP (%)", median="median delays (sec)", stop_name="Stop Name"),
    )

    fig.update_layout(
        {"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)"}
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="gray")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="gray")

    return fig

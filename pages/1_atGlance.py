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
    path="/",
    name="Stib at Glance",
)

data = pd.read_pickle("data/computed/matches_clean_EWT_delay.pkl")
coord = pd.read_pickle("data/computed/stops.geo.pkl")

dela_i = round((data.delay_label_120.value_counts() / data.shape[0]) * 100, 2).to_dict()
dela_i_p = round(
    (
        data[data.regularity == 0].delay_label_120.value_counts()
        / data[data.regularity == 0].shape[0]
    )
    * 100,
    2,
).to_dict()

reg = round(
    (
        data[data.regularity == 1].EWT_label.value_counts()
        / data[data.regularity == 1].shape[0]
    )
    * 100,
    2,
).to_dict()

top_stop_offender_punct = (
    data[(data.regularity == 0) & (data.delay_label_120 == "lat")][
        ["stop_name", "route_short_name", "delay"]
    ]
    .groupby(
        ["stop_name", "route_short_name"],
        as_index=False,
    )
    .sum()
    .sort_values("delay", ascending=False)
    .iloc[0]
)
top_stop_median_punctuality = (
    data[(data.regularity == 0) & (data.delay_label_120 == "lat")][
        ["stop_name", "route_short_name", "delay"]
    ]
    .groupby(["stop_name", "route_short_name"], as_index=False)
    .median()
    .sort_values("delay", ascending=False)
).iloc[0]

EWT_line = (
    data[data.regularity == 1][["route_short_name", "EWT"]]
    .groupby(by=["route_short_name"], as_index=False)
    .median()
    .sort_values("EWT", ascending=False)
    .iloc[0]
)


def main_illustration():
    temp = data.groupby(["stop_id"]).agg({"delay": ["median"]}).reset_index()
    temp.columns = temp.columns.get_level_values(0)
    temp = temp.merge(coord, "left", "stop_id")
    fig = px.density_mapbox(
        temp,
        lat="stop_lat",
        lon="stop_lon",
        z="delay",
        radius=10,
        center=dict(lat=50.85, lon=4.45),
        zoom=10,
        mapbox_style="white-bg",
        color_continuous_scale="portland",
    )

    fig.update_coloraxes(showscale=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def get_probs():
    _ = (
        data[(data.regularity == 0) & (data.delay_label_strict == "lat")][
            ["stop_name", "route_short_name", "delay"]
        ]
        .groupby(["stop_name", "route_short_name"], as_index=False)
        .count()
        .sort_values("delay", ascending=False)
        .merge(
            data[(data.regularity == 0)][["stop_name", "delay", "route_short_name"]]
            .groupby(["stop_name", "route_short_name"], as_index=False)
            .count()
            .sort_values("delay", ascending=True),
            "left",
            ["stop_name", "route_short_name"],
        )
    )
    _["Probs"] = round((_.delay_x / _.delay_y) * 100)
    return _[_.delay_y > 100].sort_values(by="Probs", ascending=False)


ponct_probs = get_probs()


def tailor_card(header, metric, explanation):
    crd = dbc.Card(
        style={"width": "30%", "padding": "0"},
        color="secondary",
        outline=True,
        children=[
            dbc.CardHeader(header),
            dbc.CardBody(
                children=[
                    html.H4(
                        metric,
                        className="card-title",
                    ),
                    html.P(
                        explanation,
                        className="card-text",
                    ),
                ],
            ),
        ],
    )
    return crd


layout = html.Div(
    children=[
        dbc.Row(
            # style={"margin-bottom": "10%", "margin-top": "10%"},
            children=[
                dbc.Col(
                    width=3,
                    children=[
                        html.H1(
                            style={"padding-top": "40%"},
                            children="STIB at Glance",
                        ),
                        html.P(
                            style={"margin-bottom": "40px", "max-width": "150ch"},
                            children="By Amri Hakim, Oumahi Abdelmoumen, Baguia Rania, Jdaoudi Mehdi",
                        ),
                    ],
                ),
                dbc.Col(
                    dcc.Graph(figure=main_illustration()),
                ),
            ],
        ),
        html.Hr(className="my-2"),
        dbc.Row(
            style={"margin-bottom": "5%", "margin-top": "2%"},
            children=[
                dbc.Col(
                    width=3,
                    children=[html.H4(children="Aim of the Dasboard")],
                ),
                dbc.Col(
                    children=[
                        html.P(
                            children=[
                                html.H5(
                                    "The aim of this dashboard is to provide clear and useful insights to STIB's analysts and associates.",
                                    style={
                                        "max-width": "150ch",
                                        "margin-bottom": "20px",
                                    },
                                ),
                                html.P(
                                    "The dashboard is divided in 3 main sections: Punctuality, Regularity, and Segment Analysis:",
                                    style={
                                        "max-width": "150ch",
                                        "margin-bottom": "20px",
                                    },
                                ),
                                dbc.Row(
                                    children=[
                                        dbc.Col(
                                            width=2, children=html.P("Punctuality")
                                        ),
                                        dbc.Col(
                                            html.P(
                                                "Highlighting how the network is performing overall in terms of OTP. Three thresholds have been set up defining the notion of delay. Furthermore, specific lines can be investigated for details.",
                                                style={
                                                    "max-width": "150ch",
                                                    "margin-bottom": "20px",
                                                },
                                            )
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    children=[
                                        dbc.Col(width=2, children=html.P("Regularity")),
                                        dbc.Col(
                                            html.P(
                                                "Comparing how the real headway is performing against the schedule within regularity clusters, previously detected using change point detection mining methods.",
                                                style={
                                                    "max-width": "150ch",
                                                    "margin-bottom": "20px",
                                                },
                                            )
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    children=[
                                        dbc.Col(
                                            width=2, children=html.P("Segment Analysis")
                                        ),
                                        dbc.Col(
                                            html.P(
                                                "Enlightening which sequence of stops may be problematic within the network across line, day, and time. Specific tabs are there to further assists analysts to provide a better understanding of offending stops. It also helps in assessing where the delay is being propagated and whether it can  be caught or not.",
                                                style={
                                                    "max-width": "150ch",
                                                    "margin-bottom": "20px",
                                                },
                                            )
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Hr(className="my-2"),
        dbc.Row(
            style={"margin-bottom": "10%", "margin-top": "2%"},
            children=[
                dbc.Col(
                    width=3,
                    children=[
                        html.H4(children="Key Figures"),
                        html.P(children="From the 6th to the 21st of Septembre 2021."),
                    ],
                ),
                dbc.Col(
                    children=[
                        html.P(children="Within the STIB network ..."),
                        dbc.Row(
                            style={"margin-bottom": "30px"},
                            justify="between",
                            children=[
                                tailor_card(
                                    "Global",
                                    "+"
                                    + str(round(data.stop_id.unique().shape[0] - 12)),
                                    "Number of stops",
                                ),
                                tailor_card(
                                    "Global",
                                    "+"
                                    + str(
                                        round(
                                            data.route_short_name.unique().shape[0] - 4
                                        )
                                    ),
                                    "Number of routes",
                                ),
                                tailor_card(
                                    "Global",
                                    "+ 40,000",
                                    "Number of trips performed by more than 1k vehicles",
                                ),
                            ],
                        ),
                        dbc.Row(
                            style={"margin-bottom": "50px"},
                            justify="between",
                            children=[
                                tailor_card(
                                    "Global",
                                    str(dela_i["nan"]) + "%",
                                    "On time Performance (OTP)",
                                ),
                                tailor_card(
                                    "Global",
                                    str(dela_i["adv"]) + "%",
                                    "Share of advanced trips",
                                ),
                                tailor_card(
                                    "Global",
                                    str(dela_i["lat"]) + "%",
                                    "Share of delayed trips",
                                ),
                            ],
                        ),
                        html.Hr(
                            className="my-2",
                        ),
                        html.P(
                            children="Within punctuality clusters",
                            style={"margin-top": "20px"},
                        ),
                        dbc.Row(
                            style={"margin-bottom": "30px"},
                            justify="between",
                            children=[
                                tailor_card(
                                    "Punctuality",
                                    str(dela_i_p["nan"]) + "%",
                                    "On time Performance (OTP)",
                                ),
                                tailor_card(
                                    "Punctuality",
                                    str(dela_i_p["adv"]) + "%",
                                    "Share of advanced trips",
                                ),
                                tailor_card(
                                    "Punctuality",
                                    str(dela_i_p["lat"]) + "%",
                                    "Share of delayed trips",
                                ),
                            ],
                        ),
                        dbc.Row(
                            style={"margin-bottom": "30px"},
                            justify="between",
                            children=[
                                tailor_card(
                                    "Punctuality",
                                    ponct_probs.iloc[0].stop_name
                                    + " from line "
                                    + str(ponct_probs.iloc[0].route_short_name),
                                    "Stop most likely to have delays",
                                ),
                                tailor_card(
                                    "Punctuality",
                                    top_stop_median_punctuality.stop_name
                                    + " from line "
                                    + str(top_stop_median_punctuality.route_short_name),
                                    "Top stop median delay",
                                ),
                                tailor_card(
                                    "Punctuality",
                                    top_stop_offender_punct.stop_name
                                    + " from line "
                                    + str(top_stop_offender_punct.route_short_name),
                                    f"Top stop delay offender",
                                ),
                            ],
                        ),
                        html.Hr(
                            className="my-2",
                        ),
                        html.P(
                            children="Within Regularity clusters",
                            style={"margin-top": "50px"},
                        ),
                        dbc.Row(
                            style={"margin-bottom": "30px"},
                            justify="between",
                            children=[
                                tailor_card(
                                    "Regularity",
                                    str(reg["regular"]) + "%",
                                    "Share of regular clusters",
                                ),
                                tailor_card(
                                    "Regularity",
                                    str(reg["irregular"]) + "%",
                                    "Share of irregular clusters",
                                ),
                                html.Div(),
                            ],
                        ),
                    ]
                ),
            ],
        ),
    ],
)

"""
dbc.Row(
    style={"margin-bottom": "30px"},
    justify="between",
    children=[
        tailor_card(
            "Regularity",
            EWT_line.route_short_name,
            "Highest median EWT on line",
        ),
        tailor_card(
            "Regularity",
            "To Do",
            "Top stop median delay",
        ),
        tailor_card(
            "Regularity",
            "To Do",
            "Top stop delay offender",
        ),
    ],
),
"""

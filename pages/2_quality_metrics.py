import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px


dash.register_page(
    __name__,
    title="Theoretical Headways",
    name="Theoretical Headways",
)

data = pd.read_pickle("data/computed/theoretical_schedule_qos.pkl")

unique_routes = np.sort(data.route_short_name.unique()).tolist()

layout = html.Div(
    children=[
        html.H1(children="Theoretical Headways"),
        dbc.Row(
            style={
                "position": "sticky",
            },
            children=[
                dbc.Col(
                    width=2,
                    style={
                        "height": "50vh",
                        "padding": "10px 20px",
                        "position": "sticky",
                        "top": "0",
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
                        html.P("Stop", style={"margin-bottom": "3px"}),
                        dcc.Dropdown(
                            clearable=False,
                            id="stops_drop_down_value",
                            style={"margin-bottom": "20px"},
                        ),
                        html.P("Direction", style={"margin-bottom": "3px"}),
                        dcc.Dropdown(
                            clearable=False,
                            id="direction_drop_down_value",
                            style={"margin-bottom": "20px"},
                        ),
                        html.P("Service_id", style={"margin-bottom": "3px"}),
                        dcc.Dropdown(
                            clearable=False,
                            id="service_drop_down_value",
                            style={"margin-bottom": "20px"},
                        ),
                        html.Hr(className="my-2"),
                        html.H5(children="Summary", style={"margin-top": "50px"}),
                        html.P(id="text-summary-q"),
                    ],
                ),
                dbc.Col(
                    width=9,
                    style={"padding": "10px 20px"},
                    children=[
                        html.H2("Time groups segmentation"),
                        html.P(
                            """ For each vehicle at a specified stop, in a specified direction, and for a specified service, you can find the different time groups. 
                            Each time group is labelled with "regularity" which explains if the regularity (1), or the punctuality (0), is preferred for the time group. 
                            """
                        ),
                        dcc.Graph(
                            id="dd-headways_group",
                            style={"margin-bottom": "40px"},
                        ),
                        html.H4("Data Table"),
                        html.Div(
                            id="dd-table",
                            style={
                                "height": "30vh",
                                "overflow": "scroll",
                            },
                        ),
                    ],
                ),
            ],
        ),
    ]
)

# Callbacks for dropdown filters
@callback(
    [
        Output("stops_drop_down_value", "options"),
        Output("stops_drop_down_value", "value"),
    ],
    Input("lines_drop_down_value", "value"),
)
def update_stops(value):
    temp = data[data.route_short_name == value]["stop_name"].unique()
    return temp, temp[0]


@callback(
    [
        Output("direction_drop_down_value", "options"),
        Output("direction_drop_down_value", "value"),
    ],
    [Input("lines_drop_down_value", "value"), Input("stops_drop_down_value", "value")],
)
def update_direction(route, stop):
    temp = data[(data.route_short_name == str(route)) & (data.stop_name == stop)][
        "trip_headsign"
    ].unique()
    return temp, temp[0]


@callback(
    [
        Output("service_drop_down_value", "options"),
        Output("service_drop_down_value", "value"),
    ],
    [
        Input("lines_drop_down_value", "value"),
        Input("stops_drop_down_value", "value"),
        Input("direction_drop_down_value", "value"),
    ],
)
def service_id(route, stop, direction):
    temp = data[
        (data.route_short_name == str(route))
        & (data.stop_name == stop)
        & (data.trip_headsign == direction)
    ]["service_id"].unique()
    return temp, temp[0]


# Callback for dataset selected with filters


@callback(
    Output("dd-table", "children"),
    [
        Input("lines_drop_down_value", "value"),
        Input("stops_drop_down_value", "value"),
        Input("direction_drop_down_value", "value"),
        Input("service_drop_down_value", "value"),
    ],
)
def update_table(route, stop, direction, service):
    temp = data[
        (data.route_short_name == str(route))
        & (data.stop_name == stop)
        & (data.trip_headsign == direction)
        & (data.service_id == service)
    ].sort_values(by="arrival_time")
    return dbc.Table.from_dataframe(temp)


# Callback for graphics


@callback(
    Output("dd-headways_group", "figure"),
    [
        Input("lines_drop_down_value", "value"),
        Input("stops_drop_down_value", "value"),
        Input("direction_drop_down_value", "value"),
        Input("service_drop_down_value", "value"),
    ],
)
def plot_clusters(route, stop, direction, service):
    temp = data[
        (data.route_short_name == str(route))
        & (data.stop_name == stop)
        & (data.trip_headsign == direction)
        & (data.service_id == service)
    ].sort_values(by="arrival_time")
    fig = px.scatter(
        temp,
        x="arrival_time",
        y="headway_min",
        color="clusters",
        symbol="regularity",
        marginal_y="box",
        labels=dict(
            headway_min="Theoretical Headway (min)", arrival_time="Scheduled Time"
        ),
    )
    return fig


@callback(
    Output("text-summary-q", "children"),
    [
        Input("lines_drop_down_value", "value"),
        Input("stops_drop_down_value", "value"),
        Input("direction_drop_down_value", "value"),
        Input("service_drop_down_value", "value"),
    ],
)
def update_summary(route, stop, direction, service):
    if (route != None) & ((stop != None)) & ((direction != None) & (service != None)):
        temp = data[
            (data.route_short_name == str(route))
            & (data.stop_name == stop)
            & (data.trip_headsign == direction)
            & (data.service_id == service)
        ]
        name = temp.iloc[0].route_long_name.split(" - ")
        # origin = temp.sort_values(by = "th_time_sec").iloc[0].stop_name

        s = f"You have selected the line {str(route)}, operating between {name[0]} and {name[1]}, in direction of {direction} at the stop {stop}."

    else:
        s = "No summary yet available."

    return s

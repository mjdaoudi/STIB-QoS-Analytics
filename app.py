from dash import Dash, html, dcc, dash_table
import dash
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.COSMO],
    use_pages=True
    # , suppress_callback_exceptions=True
)


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(page.get("name"), href=page.get("relative_path")))
        for page in dash.page_registry.values()
    ],
    style={"padding": "0% 3%"},
    brand="QoS Dashboard",
    brand_href="/",
    color="#002366",
    dark=True,
    fluid=True,
    sticky="top",
)


# app rendering
app.layout = html.Div(
    children=[
        navbar,
        html.Div(
            style={"padding": "1% 3%", "overflow": "hidden"},
            children=[dash.page_container],
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)

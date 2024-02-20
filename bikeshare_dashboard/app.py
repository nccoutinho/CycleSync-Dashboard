from dash import dash, dash_table, callback, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import altair as alt
from datetime import date

alt.data_transformers.disable_max_rows()

# Read in data globally
#data = pd.read_csv('../dataset/Mobi_System_Data_2023-01.csv', parse_dates=True, index_col=0)

# Setup app and layout/frontend
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Assistant:wght@300&display=swap",
        dbc.icons.FONT_AWESOME,
        dbc.themes.JOURNAL,
    ]
)

# Server
server = app.server

# Title
app.title = 'Bikeshare Dashboard'

# HEADER
header = html.Div(
    id="app-header",
    children=[
        html.H1(
            "Bikeshare Dashboard",
            style={
                "display": "inline",
                "font-size": "1.5em",
                "margin-left": "1.8px",
                "color": "white",  # Set font color to white
                "background-color": "#D80808",  # Set background color to red
                "padding": "10px"  # Add padding for better appearance
            }
        )
    ],
    style={"align": "center", "margin-left": 15}
)

# SIDEBAR
sidebar = dbc.Col(
    [
        header,
        html.Div(style={"height": "20px"}),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
                dbc.NavItem(dbc.NavLink("Trends", href="/trends")),
                dbc.NavItem(dbc.NavLink("Map", href="/map")),
            ],
            vertical=True,
            pills=True,
            className="mb-3",
        ),
    ],
    width=2.1,
    style={"background-color": "#f8f9fa", "height": "100vh", "position": "fixed", "padding-top": "20px"},
)

# TABLE FILTER
sort_table_1 = dcc.Dropdown(
    id='table_filter_1',
    options=[
        {'label': 'Density plot', 'value': 'density_plot'},
        {'label': 'Marker plot', 'value': 'marker_plot'}
   ],
   value='density_plot'
)

sort_table_2 = dcc.Dropdown(
    id='table_filter_2',
    options=[
        {'label': 'Electric bike', 'value': 'electric_bike'},
        {'label': 'Classic bike', 'value': 'classic_bike'}
   ],
   value='electric_bike'
)
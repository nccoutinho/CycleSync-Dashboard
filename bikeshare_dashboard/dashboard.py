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

# CHARTS / TABLE
# FIRST ROW:
# Define a function to generate card with icon
def generate_card(title, content, icon):
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H6(title, className="card-title", style={"color": "gray", "margin-bottom": "0"}),
                style={"background-color": "transparent", "border": "none"}
            ),
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.H3(content),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.I(className=icon, style={"color": "white", "fontSize": "1.4em"}),
                                        ],
                                        style={"background-color": "#D80808", "padding": "9px", "border-radius": "8px"}
                                    ),
                                ],
                                style={"display": "flex", "align-items": "center"}
                            ),
                        ],
                        style={"display": "flex", "justify-content": "space-between"}
                    ),
                ],
                style={"padding": "20px"}
            ),
        ],
        className="mb-3",
        style={
            "width": "16%",
            "margin-left": "auto",
            "border": "1px solid lightgray",
            "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
        }
    )



no_of_rides = generate_card("No. of rides", "6.5 M", "fas fa-bicycle")
max_duration = generate_card("Maximum duration", "30 Mins", "fas fa-hourglass")
max_distance = generate_card("Maximum distance", "8 KM", "fas fa-road")
busiest_station = generate_card("Busiest station", "8th & Ash", "fas fa-building")
busiest_day = generate_card("Busiest day", "Saturday", "fas fa-calendar-alt")

# SECOND ROW:
active_stations = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H1("142", style={"color": "#D80808", "margin-bottom": "25px", "font-size": "5.5em"}),
                dbc.Col(html.H6("active stations around the city, accessible 24/7, 365 days a year."))
            ],
            style={"display": "flex", "flex-direction": "column", "justify-content": "center"}
        )
    ],
    className="mb-3",
    style={
        "width": "29%",
        "height": "300px",
        "margin-left": "auto",
        "border": "1px solid lightgray",
        "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
    }
)

pie_chart = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.Col("insert pie chart here.")
            ],
            style={"display": "flex", "flex-direction": "column", "justify-content": "center"}
        )
    ],
    className="mb-3",
    style={
        "width": "29%",
        "height": "300px",
        "margin-left": "auto",
        "border": "1px solid lightgray",
        "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
    }
)

day_of_week = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.Col("insert bar plot here.")
            ],
            style={"display": "flex", "flex-direction": "column", "justify-content": "center"}
        )
    ],
    className="mb-3",
    style={
        "width": "29%",
        "height": "300px",
        "margin-left": "auto",
        "border": "1px solid lightgray",
        "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
    }
)

# THIRD ROW:
temperature_duration = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.Col("insert heat map here.")
            ],
            style={"display": "flex", "flex-direction": "column", "justify-content": "center"}
        )
    ],
    className="mb-3",
    style={
        "width": "50%",
        "height": "350px",
        "margin-left": "auto",
        "border": "1px solid lightgray",
        "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
    }
)

common_end_station = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.Col("insert bar plot here.")
            ],
            style={"display": "flex", "flex-direction": "column", "justify-content": "center"}
        )
    ],
    className="mb-3",
    style={
        "width": "41%",
        "height": "350px",
        "margin-left": "auto",
        "border": "1px solid lightgray",
        "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
    }
)

# LAYOUT
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),  # Location component to track the URL
        sidebar,
        html.Div(
            [
                html.Hr(),
                html.Div(
                    [
                        html.H6("Page / ", style={'display': 'inline'}),
                        html.Span(id='current-page', style={'font-weight': 'bold'})
                    ],
                    className='top-bar',
                    style={'margin-bottom': '20px'}  # Add vertical space between the sidebar and top bar
                ),
                dbc.Row(
                    [
                        no_of_rides,
                        max_duration,
                        max_distance,
                        busiest_station,
                        busiest_day
                    ],
                    justify="center",
                    style={'margin-top': '20px', 'padding-right': '60px'}  
                ),
                dbc.Row(
                    [
                        active_stations,
                        pie_chart,
                        day_of_week
                    ],
                    justify="center",
                    style={'margin-top': '20px', 'padding-right': '60px'}  
                ),
                html.Hr()
            ],
            style={"margin": "0", "margin-left": "230px", "padding-left": "20px"}  # Adjusted styles for better alignment
        ),
    ]
)

# Callback to update the current page based on the URL
@app.callback(
    Output('current-page', 'children'),
    [Input('url', 'pathname')]
)
def update_current_page(pathname):
    if pathname == '/dashboard':
        return 'Dashboard'
    elif pathname == '/trends':
        return 'Trends'
    elif pathname == '/map':
        return 'Map'
    else:
        return 'Unknown Page'


if __name__ == '__main__':
    app.run_server(debug=True, port=8057) 
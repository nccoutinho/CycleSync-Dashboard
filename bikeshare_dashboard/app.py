from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output  # Add this line

# Import layouts from separate pages
# from dashboard import dashboard_layout
# from trends import trends_layout
from map import map_layout

app = Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])

# Define the sidebar separately
sidebar = dbc.Col([
    # ... sidebar content ...
    dbc.Nav([
        dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
        dbc.NavItem(dbc.NavLink("Trends", href="/trends")),
        dbc.NavItem(dbc.NavLink("Map", href="/map"))
    ],
        vertical=True,
        pills=True,
        className="mb-3",
    ),
],
    width=2.1,
    style={"background-color": "#f8f9fa", "height": "100vh", "position": "fixed", "padding-top": "20px"},
)

# Define layout for the main app
app.layout = html.Div([
    # Sidebar goes here
    sidebar,

    # Content area goes here (initially empty)
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback to update the content based on the URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]  # Use Input directly
)

def display_page(pathname):
    if not pathname or pathname == '/':
        return map_layout
    # elif pathname == '/dashboard':
    #     return dashboard_layout
    # elif pathname == '/trends':
    #     return trends_layout
    elif pathname == '/map':
        return map_layout
    else:
        return '404 Page Not Found'

if __name__ == '__main__':
    app.run_server(debug=True, port=8061)

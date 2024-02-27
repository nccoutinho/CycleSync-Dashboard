from dash import dash, dash_table, callback, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import altair as alt
import os
import plotly.graph_objects as go
import plotly.express as px
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

# --------------------------------------
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

# --------------------------------------
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

# --------------------------------------
# STATISTICS CODE
# Number of active station:
# Path to the folder containing your files
folder_path = '../dataset'

# Initialize an empty list to store DataFrames
dfs = []

# Iterate over each file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):  # Assuming all files are CSV, you can change the condition accordingly
        file_path = os.path.join(folder_path, filename)
        # Try different encodings to read the file
        for encoding in ['utf-8', 'latin-1']:  # You can add more encodings to try if needed
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                dfs.append(df)  # Append the DataFrame to the list
                break  # Break the loop if reading is successful
            except UnicodeDecodeError:
                print(f"Error decoding file {filename} with encoding {encoding}. Trying another encoding...")

# Concatenate all DataFrames in the list into one
combined_df = pd.concat(dfs, ignore_index=True)

# ---------------PLOT 1-----------------------

# Remove null records
combined_df = combined_df.dropna(subset=['Departure station'])

# Count occurrences of each station
station_counts = combined_df['Departure station'].value_counts()

# Get the number of unique stations
num_stations = len(station_counts)

# ---------------PLOT 2-----------------------

# Convert 'Departure Date' column to datetime
combined_df['Departure'] = pd.to_datetime(combined_df['Departure'])

# Extract day of the week
combined_df['Day of Week'] = combined_df['Departure'].dt.day_name()

# Count trips by day of the week
trips_by_day = combined_df['Day of Week'].value_counts()

# Sort days of the week
sorted_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
trips_by_day = trips_by_day.reindex(sorted_days)

# ---------------PLOT 3-----------------------

counts_series = combined_df['Membership type'].value_counts()
index_list = counts_series.index.tolist()
counts_list = counts_series.tolist()

labels = index_list[:18]
labels.append('Others')
values = counts_list[:18]
values.append(sum(counts_list[18:]))

total_count = sum(values)

fig2 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, textinfo='none', marker=dict(colors=px.colors.sequential.Reds[::-1]))])

fig2.add_annotation(text='Number of Rides<br>' + str(total_count), showarrow=False, font=dict(size=15), x=0.5, y=0.5)

fig2.update_layout(showlegend=False)

# ---------------PLOT 4-----------------------

# Remove null records
combined_df = combined_df.dropna(subset=['Return station'])

# Get the top 10 most common end trip stations
top_end_stations = combined_df['Return station'].value_counts().nlargest(10)

# Calculate percentages
percentage_values = (top_end_stations / top_end_stations.sum()) * 100

# Create a horizontal bar graph using Plotly Express
fig = px.bar(
    top_end_stations,
    orientation='h',
    labels={'Return Station', 'Count'},
    color=percentage_values.index,  # Use the stations as the color variable
    text=percentage_values.round(2).astype(str) + '%'  # Display percentages as text on the bars
)
# Sort bars in descending order
fig.update_yaxes(categoryorder='total ascending')

# Remove color legend
fig.update_layout(showlegend=False)

# Remove y-axis and x-axis names
fig.update_layout(
    xaxis_title='',
    yaxis_title='',
)


# --------------------------------------
# EMPTY CARDS / BOXES
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
                html.H1(f"{num_stations}", style={"color": "#D80808", "margin-bottom": "25px", "font-size": "5.8em"}),
                dbc.Col(html.H5("active stations around the city, accessible 24/7, 365 days a year."))
            ],
            style={"display": "flex", "flex-direction": "column", "justify-content": "center"}
        )
    ],
    className="mb-3",
    style={
        "width": "610px",
        "height": "240px",
        "margin-left": "auto",
        "border": "1px solid lightgray",
        "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
    }
)


pie_chart = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.Col(
                    [
                        html.H1("Rides by Membership Type", style={"font-size": "1.5em"}),
                        dcc.Graph(
                            figure=fig2
                            )
                    ],
                    width=12  # Adjust the width as needed
                )
            ],
            style={"display": "flex", "flex-direction": "column", "justify-content": "center"}
        )
    ],
    className="mb-3",
    style={
        "width": "800px",
        "height": "510px",
        "margin-left": "auto",
        "border": "1px solid lightgray",
        "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
    }
)



# day_of_week = dbc.Card(
#     [
#         dbc.CardBody(
#             [
#                 dbc.Col()
#             ],
#             style={"display": "flex", "flex-direction": "column", "justify-content": "center"}
#         )
#     ],
#     className="mb-3",
#     style={
#         "width": "29%",
#         "height": "300px",
#         "margin-left": "auto",
#         "border": "1px solid lightgray",
#         "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
#     }
# )


# THIRD ROW:
trip_day = dbc.Card(
    [
                dbc.Col(
                    [
                        html.H1("Trips by Day of the Week", style={"font-size": "1.5em", "padding-top": "18px", "padding-left": "18px"}),
                        dcc.Graph(
                            id='trips-by-day-bar',
                            figure={
                                'data': [
                                    {'x': trips_by_day.index, 
                                     'y': trips_by_day.values, 
                                     'type': 'bar', 
                                     'name': 'Trips', 
                                     'marker': {'color': 'indianred'},
                                     'hovertemplate': 'Day: %{x}<br>Trips: %{y:,.0f}'},
                                ],
                                'layout': {
                                    'xaxis': {'title': 'Day of the Week'},
                                    'yaxis': {'title': 'Trips'},
                                    #'width': '1000px',
                                    'height': 300
                                }
                            }
                        )
                    ],
                    width=12  # Adjust the width as needed
                )
            ],
    className="mb-3",
    style={
        "width": "800px",
        "height": "360px",
        "margin-left": "auto",
        "border": "1px solid lightgray",
        "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
    }
)

common_end_station = dbc.Card(
    [
                dbc.Col(
                    [
                        html.H1("Top 10 Most Common End Trip Stations", style={"font-size": "1.5em", "padding-top": "18px", "padding-left": "18px"}),
                        dcc.Graph(
                            figure=fig.update_traces(marker_color='indianred').update_layout(
                                width=605,  
                                height=572,  
                                )
                            )
                    ],
                    width=12  # Adjust the width as needed
                )
    ],
    className="mb-3",
    style={
        "width": "610px",
        "height": "630px",
        "margin-left": "auto",
        "border": "1px solid lightgray",
        "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
    }
)

# --------------------------------------
# LAYOUT
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
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
                    style={'margin-bottom': '20px', 'padding': '10px', 'background-color': '#f8f9fa'}  
                ),
                dbc.Row(
                    [no_of_rides, max_duration, max_distance, busiest_station, busiest_day],
                    justify="center",
                    style={'margin-top': '20px', 'padding-right': '60px'}  
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [active_stations, html.Div(style={'height': '20px'}), common_end_station],
                            width=5,
                            style={'margin-top': '10px', 'padding-left': '60px', 'padding-right': '20px'}  
                        ),
                        dbc.Col(
                            [pie_chart, html.Div(style={'height': '20px'}), trip_day],
                            width=5,
                            style={'margin-top': '10px', 'padding-left': '55px', 'padding-right': '60px'}  
                        )
                    ],
                    style={'margin-top': '20px'}  
                ),
                html.Hr()
            ],
            style={"margin": "0", "margin-left": "230px", "padding-left": "20px"}  
        ),
    ]
)

# --------------------------------------
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
    app.run_server(debug=True, port=8058) 
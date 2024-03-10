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
import calendar
import folium
from folium.plugins import HeatMap

alt.data_transformers.disable_max_rows()

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
app.title = 'CycleSync'

# --------------------------------------
# HEADER
header = html.Div(
    id="app-header",
    children=[
        html.Div([
            html.I(className="fas fa-bicycle", style={"color": "#D80808", "fontSize": "4em", "margin-right": "1px", "margin-bottom": "15px"}),
            html.Div([
                html.H1(
                    "CycleSync",
                    style={
                        "display": "inline",
                        "font-size": "3.1em",
                        "margin-left": "1.8px",
                        "color": "#D80808",  # Set font color to white
                        "padding": "10px",  # Add padding for better appearance
                        "width": "100%"
                    }
                ),
                html.P(
                    "Powered by Mobi",
                    style={
                        "font-size": "0.85em",
                        "color": "#666666",  # Set font color to a subdued color
                        "margin-top": "-2px",  # Adjust margin to align with the H1 element
                        "padding": "10px"
                    }
                ),
            ], style={"flex": 1})
        ], style={"display": "flex", "align-items": "center"}),
    ],
    style={"align": "center", "margin-left": 15}
)

combined_df = pd.read_csv('../data/processed/mobi_data.csv')

dfc = pd.read_csv('../data/coordinates/station_coordinates.csv')
dfc.drop(columns=['comments'], inplace=True)

vancouver_geojson = {
    "type": "Feature",
    "properties": {
        "name": "Vancouver",
        "description": "Boundary of the city of Vancouver, British Columbia, Canada"
    }
}

months = sorted(combined_df['Month'].unique().tolist())
marks = {
    0: {'label': 'Jan'},
    1: {'label': 'Feb'},
    2: {'label': 'Mar'},
    3: {'label': 'Apr'},
    4: {'label': 'May'},
    5: {'label': 'Jun'},
    6: {'label': 'Jul'},
    7: {'label': 'Aug'},
    8: {'label': 'Sep'},
    9: {'label': 'Oct'},
    10: {'label': 'Nov'},
    11: {'label': 'Dec'}
}

# ---------------DATE FILTER--------------------
date_picker = dcc.DatePickerRange(
    id="calendar",
    min_date_allowed=date(2023, 1, 1),
    max_date_allowed=date(2023, 12, 31),
    start_date=date(2023, 1, 1),
    end_date=date(2023, 12, 31),
    start_date_placeholder_text="Start Date",
    end_date_placeholder_text="End Date",
    clearable=True
)

# ---------------ROW 1-----------------------

# Get the count of rides
rides_count = len(combined_df)

# Assuming combined_df has been defined and 'Departure Temperature' column is present
average_departure_temperature = f"{round(combined_df['Departure temperature (C)'].mean(),0)}°C"

# Find the maximum covered distance
max_covered_distance = combined_df['Covered distance (m)'].max()

max_covered_distance_kilometers = f"{round((max_covered_distance / 1000 ),0)} km"

# Remove null records
combined_df = combined_df.dropna(subset=['Departure station'])

# Count occurrences of each station
station_counts = combined_df['Departure station'].value_counts()

# Get the busiest station
busiest_station_departure = station_counts.idxmax()

# Convert 'Departure' to datetime
combined_df['Departure'] = pd.to_datetime(combined_df['Departure'])

# Extract day of the week
combined_df['Day of Week'] = combined_df['Departure'].dt.day_name()

# Count the number of trips for each day of the week
busiest_day_weekly = combined_df['Day of Week'].value_counts().idxmax()

# ---------------PLOT 1-----------------------

# Get the number of unique stations
num_stations = len(combined_df['Departure station'].unique())

# ---------------PLOT 2-----------------------

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
def generate_card(title, content, icon, id):
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
                            html.H5(content),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.I(className=icon, style={"color": "white", "fontSize": "1.4em"}),
                                        ],
                                        style={"background-color": "#D80808", "padding": "9px", "border-radius": "8px"}
                                    ),
                                ],
                                style={"display": "flex", "align-items": "center", "padding-left": "5px"}
                            ),
                        ],
                        style={"display": "flex", "justify-content": "space-between"}
                    ),
                ],
                style={"padding": "20px"}
            ),
        ],
        className="mb-3",
        id=id,  # Include the id argument here
        style={
            "width": "16%",
            "margin-left": "auto",
            "border": "1px solid lightgray",
            "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
        }
    )



# no_of_rides = generate_card("No. of rides", rides_count, "fas fa-bicycle")
# avg_temperature = generate_card("Average temperature", average_departure_temperature, "fas fa-hourglass")
# max_distance = generate_card("Maximum distance", max_covered_distance_kilometers, "fas fa-road")
# busiest_station = generate_card("Busiest station", busiest_station_departure[5:], "fas fa-building")
# busiest_day = generate_card("Busiest day", busiest_day_weekly, "fas fa-calendar-alt")

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
        "width": "660px",
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
        "width": "900px",
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
                                    'width': 870,
                                    'height': 305
                                }
                            }
                        )
                    ],
                    width=12  # Adjust the width as needed
                )
            ],
    className="mb-3",
    style={
        "width": "900px",
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
                        html.H1("Top 10 Most Used End Trip Stations", style={"font-size": "1.5em", "padding-top": "18px", "padding-left": "18px"}),
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
        "width": "660px",
        "height": "630px",
        "margin-left": "auto",
        "border": "1px solid lightgray",
        "box-shadow": "0px 1px 4px 0px rgba(0, 0, 0, 0.1)"
    }
)


# TABLE FILTER
sort_table_2 = dcc.Dropdown(
    id='table_filter_1',
    options=[
        {'label': 'All', 'value': 'all'},
        {'label': '24 Hour', 'value': '24 Hour'},
        {'label': '30 Day Pass', 'value': '30 Day Pass'},
        {'label': '365 Corporate Plus', 'value': '365 Corporate Plus'},
        {'label': '365 Corporate Plus Renewal', 'value': '365 Corporate Plus Renewal'},
        {'label': '365 Corporate Standard', 'value': '365 Corporate Standard'},
        {'label': '365 Corporate Standard Renewal', 'value': '365 Corporate Standard Renewal'},
        {'label': '365 Day Founding Plus', 'value': '365 Day Founding Plus'},
        {'label': '365 Day Founding Standard', 'value': '365 Day Founding Standard'},
        {'label': '365 Day Pass Plus', 'value': '365 Day Pass Plus'},
        {'label': '365 Day Pass Plus SALE', 'value': '365 Day Pass Plus SALE'},
        {'label': '365 Day Pass Standard', 'value': '365 Day Pass Standard'},
        {'label': '365 Day Pass Standard SALE', 'value': '365 Day Pass Standard SALE'},
        {'label': 'Archived Monthly Plus', 'value': 'Archived Monthly Plus'},
        {'label': 'Archived Monthly Standard', 'value': 'Archived Monthly Standard'},
        {'label': 'Community Pass', 'value': 'Community Pass'},
        {'label': 'Community Pass E-bike', 'value': 'Community Pass E-bike'},
        {'label': 'Community Pass E-bike (PWD)', 'value': 'Community Pass E-bike (PWD)'},
        {'label': 'Herbaland Pass', 'value': 'Herbaland Pass'},
        {'label': 'Limited Classic Bikes Only (60 min)', 'value': 'Limited Classic Bikes Only (60 min)'},
        {'label': 'Pay Per Ride', 'value': 'Pay Per Ride'},
        {'label': 'UBC Inclusive Corporate Pass', 'value': 'UBC Inclusive Corporate Pass'},
        {'label': 'VIP', 'value': 'VIP'}
],
   value=['all'],
   multi=True,
   clearable=False
)

sort_table_1 = dcc.Dropdown(
    id='table_filter_2',
    options=[
        {'label': 'Electric', 'value': 'electric'},
        {'label': 'Classic', 'value': 'classic'},
        {'label': 'Both', 'value': 'both'}
   ],
   value='both',
   clearable=False
)

slider = dcc.RangeSlider(
    id='season_range_slider',
    marks={0: 'Winter', 1: 'Spring', 2: 'Summer', 3: 'Fall'},
    min=0,
    max=3,
    step=1,
    value=[0, 3]  # Initial range from Winter to Fall
)


dashboard_layout = html.Div(
    [
        dcc.Location(id='dashboard-url', refresh=False),
        #header,
        html.Div(
            [
                html.Hr(),
                html.Div(
                    [
                        # html.H6("Page / ", style={'display': 'inline'}),
                        html.Span(id='current-page', style={'font-weight': 'bold'})
                    ],
                    className='top-bar',
                    style={'margin-bottom': '5px', 'padding': '10px'}
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [html.H6("Date Range:"), date_picker]
                        )
                    ],
                    style={'margin-bottom': '40px', 'padding-left': '60px'}           
                ),
                dbc.Row(
                    [
                        generate_card("No. of rides", rides_count, "fas fa-bicycle", id="rides-count"),
                        generate_card("Average temperature", average_departure_temperature, "fas fa-hourglass", id="average-temperature"),
                        generate_card("Maximum distance", max_covered_distance_kilometers, "fas fa-road", id="max-covered-distance"),
                        generate_card("Busiest station", busiest_station_departure, "fas fa-building", id="busiest-station"),
                        generate_card("Busiest day", busiest_day_weekly, "fas fa-calendar-alt", id="busiest-day")
                    ],
                    id='first-row-cards',
                    justify="center",
                    style={'margin-top': '20px', 'padding-right': '90px'}
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [active_stations, html.Div(style={'height': '20px'}), common_end_station],
                            width=5,
                            style={'margin-top': '10px', 'padding-left': '30px', 'padding-right': '20px'},
                            id='first-col-cards'
                        ),
                        dbc.Col(
                            [pie_chart, html.Div(style={'height': '20px'}), trip_day],
                            width=5,
                            style={'margin-top': '10px', 'padding-left': '55px', 'padding-right': '30px'},
                            id='second-col-cards'
                        )
                    ],
                    style={'margin-top': '20px'}
                ),
                html.Hr()
            ],
            style={"margin": "0", "padding-left": "20px"}
        )
    ]
)

# Set up callbacks/backend
@app.callback(
     Output('first-row-cards', 'children'),
    #  Output('average-temperature', 'children'),
    #  Output('max-covered-distance', 'children'),
    #  Output('busiest-station', 'children'),
    #  Output('busiest-day', 'children'),
     [Input('calendar', 'start_date'),
     Input('calendar', 'end_date')]
)

def update_first_row_cards(start_date, end_date):
    # Filter data based on selected date range
    # filtered_df = combined_df[(combined_df['Departure'] >= start_date) & (combined_df['Departure'] <= end_date)]
    filtered_df = combined_df[(combined_df['Departure'].notnull()) & (combined_df['Departure'] >= start_date) & (combined_df['Departure'] <= end_date)]

    # Update metrics
    rides_count = len(filtered_df)
    average_departure_temperature = f"{round(filtered_df['Departure temperature (C)'].mean(),0)}°C"
    
    # Check if there are records in the filtered DataFrame before calculating the maximum covered distance
    if not filtered_df.empty:
        max_covered_distance = filtered_df['Covered distance (m)'].max()
        max_covered_distance_kilometers = f"{round((max_covered_distance / 1000), 0)} km"
    else:
        max_covered_distance_kilometers = "No data available"

    # Check if there are records in the filtered DataFrame before calculating the busiest station
    if not filtered_df.empty:
        station_counts = filtered_df['Departure station'].value_counts()
        busiest_station_departure = station_counts.idxmax()
    else:
        busiest_station_departure = "No data available"  

    # Check if there are records in the filtered DataFrame before calculating the busiest day
    if not filtered_df.empty and not filtered_df['Day of Week'].empty:
        busiest_day_weekly = filtered_df['Day of Week'].value_counts().idxmax()
    else:
        busiest_day_weekly = "No data available"  
    
    return (
        generate_card("No. of rides", f"{rides_count}", "fas fa-bicycle", id="rides-count"),
        generate_card("Average temperature", f"{average_departure_temperature}", "fas fa-hourglass", id="average-temperature"),
        generate_card("Maximum distance", f"{max_covered_distance_kilometers}", "fas fa-road", id="max-covered-distance"),
        generate_card("Busiest station", f"{busiest_station_departure}", "fas fa-building", id="busiest-station"),
        generate_card("Busiest day", f"{busiest_day_weekly}", "fas fa-calendar-alt", id="busiest-day")
    )

# Set up callbacks/backend
@app.callback(
     Output('first-col-cards', 'children'),
     [Input('calendar', 'start_date'),
     Input('calendar', 'end_date')]
)

trends_layout = html.Div(
    [
        dcc.Location(id='trends-url', refresh=False),  # Location component to track the URL
        html.Div(
            [
                html.Hr(),
                dbc.Row(
                    [
                         dbc.Col(
                            [
                                html.Label('Bike Type:', style={'font-weight':'bold'}),
                                sort_table_1,
                            ],
                            width=2,
                            style={'margin-right': '20px'}  # Add horizontal space between top bar and sort tables
                        ),
                        dbc.Col(
                            [
                                html.Label('Membership Type:', style={'font-weight':'bold'}),
                                sort_table_2
                            ],
                            width=2,
                            style={'margin-right': '20px'}  # Add horizontal space between top bar and sort tables
                        ),
                        dbc.Col(
                            width=9
                        ),
                    ],
                    justify="start",
                    style={'margin-top': '20px'}  # Add vertical space between top bar and sort tables/map_plot
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H4("Average Bike Departures by Season and Month", style={"margin-bottom": "20px", "text-align": "center"}),
                                dcc.Graph(id='trend-plot1', figure={}),
                            ],
                            width=6  # Adjust the width based on your design
                        ),
                        dbc.Col(
                            [
                                html.H4("Average Covered Distance by Season and Month", style={"margin-bottom": "20px", "text-align": "center"}),
                                dcc.Graph(id='trend-plot2', figure={}),
                            ],
                            width=6  # Adjust the width based on your design
                        ),
                    ],
                    justify="center",  # Center the charts
                    style={'margin-top': '20px'}  # Add vertical space between the top bar and charts
                ),
                slider,
                html.Hr()
            ],
            style={"margin": "0", "padding-left": "20px"}  # Adjusted styles for better alignment
        ),
    ]
)

@app.callback(
    Output('trend-plot1', 'figure'),
    [Input('table_filter_2', 'value'),
     Input('table_filter_1', 'value'),
     Input('season_range_slider', 'value')]
)
def update_chart1(selected_bike, selected_membership, selected_season):

    start_season, end_season = selected_season
    
    # Check for Bike Type selected
    if selected_bike == 'electric':
        # Filter data for 'Electric bike'
        df = combined_df[combined_df['Electric bike'] == True]
    elif selected_bike == 'classic':
        df = combined_df[combined_df['Electric bike'] == False]
    else:
        df = combined_df

    if 'all' not in selected_membership:
        df = df[df['Membership type'].isin([m for m in selected_membership])]
    
    # Define custom sort order for months
    month_order = ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']    
    
    # Filter data based on selected months
    selected_months = []
    for season_index in range(start_season, end_season + 1):
        start_month_index = season_index * 3
        end_month_index = start_month_index + 2
        selected_months.extend(month_order[start_month_index:end_month_index + 1])

    df = df[df['Month'].isin(selected_months)]

    # Group by season, then by month, and calculate average count of bike departures
    seasonal_bike_count = df.groupby(['Season', 'Month']).size().reset_index(name='Bike Count')
    average_counts = seasonal_bike_count.groupby(['Month', 'Season'])['Bike Count'].mean().reset_index()

    # Group by season, then by month, and calculate average covered distance of bike trips
    seasonal_bike_distance = df.groupby(['Season', 'Month'])['Covered distance (m)'].mean().reset_index(name='Average Covered Distance (m)')

    # Sort the DataFrame by the 'Month' column using the custom order
    average_counts = average_counts.loc[average_counts['Month'].isin(month_order)]
    average_counts['Month'] = pd.Categorical(average_counts['Month'], categories=month_order, ordered=True)
    average_counts = average_counts.sort_values(by='Month')

    # Sort the DataFrame by the 'Month' column using the custom order
    seasonal_bike_distance = seasonal_bike_distance.loc[seasonal_bike_distance['Month'].isin(month_order)]
    seasonal_bike_distance['Month'] = pd.Categorical(seasonal_bike_distance['Month'], categories=month_order, ordered=True)
    seasonal_bike_distance = seasonal_bike_distance.sort_values(by='Month')


    # Create separate line plots for each season
    fig_winter = px.line(
        average_counts[average_counts['Month'].isin(['Dec', 'Jan', 'Feb', 'Mar'])],
        x='Month',
        y='Bike Count',
        line_shape='linear',
        color_discrete_sequence=['blue'],
        hover_data={'Month': True, 'Bike Count': True, 'Season': True}  
    )


    fig_spring = px.line(
        average_counts[average_counts['Month'].isin(['Mar', 'Apr', 'May', 'Jun'])],
        x='Month',
        y='Bike Count',
        line_shape='linear',
        color_discrete_sequence=['green'],
        hover_data={'Month': True, 'Bike Count': True, 'Season': True}  
    )


    fig_summer = px.line(
        average_counts[average_counts['Month'].isin(['Jun', 'Jul', 'Aug', 'Sep'])],
        x='Month',
        y='Bike Count',
        line_shape='linear',
        color_discrete_sequence=['red'],
        hover_data={'Month': True, 'Bike Count': True, 'Season': True}  
    )


    fig_fall = px.line(
        average_counts[average_counts['Month'].isin(['Sep', 'Oct', 'Nov'])],
        x='Month',
        y='Bike Count',
        line_shape='linear',
        color_discrete_sequence=['#ffd300'],
        hover_data={'Month': True, 'Bike Count': True, 'Season': True} 
    )


    # Combine the line plots
    fig = fig_winter.add_traces(fig_spring.data)
    fig.add_traces(fig_summer.data)
    fig.add_traces(fig_fall.data)


    # Update layout
    fig.update_layout(
        yaxis_title='Average Bike Departure Count',
        xaxis = dict(
            title=None
        )
    )
    return {'data': fig['data'], 'layout': fig['layout']}

@app.callback(
    Output('trend-plot2', 'figure'),
    [Input('table_filter_2', 'value'),
     Input('table_filter_1', 'value'),
     Input('season_range_slider', 'value')]
)

def update_chart2(selected_bike, selected_membership, selected_season):

    start_season, end_season = selected_season
    
    # Check for Bike Type selected
    if selected_bike == 'electric':
        # Filter data for 'Electric bike'
        df = combined_df[combined_df['Electric bike'] == True]
    elif selected_bike == 'classic':
        df = combined_df[combined_df['Electric bike'] == False]
    else:
        df = combined_df

    if 'all' not in selected_membership:
        df = df[df['Membership type'].isin([m for m in selected_membership])]
    
    # Define custom sort order for months
    month_order = ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
    
    # Filter data based on selected months
    selected_months = []
    for season_index in range(start_season, end_season + 1):
        start_month_index = season_index * 3
        end_month_index = start_month_index + 2
        selected_months.extend(month_order[start_month_index:end_month_index + 1])

    df = df[df['Month'].isin(selected_months)]

    # Group by season, then by month, and calculate average count of bike departures
    seasonal_bike_count = df.groupby(['Season', 'Month']).size().reset_index(name='Bike Count')
    average_counts = seasonal_bike_count.groupby(['Month', 'Season'])['Bike Count'].mean().reset_index()

    # Group by season, then by month, and calculate average covered distance of bike trips
    seasonal_bike_distance = df.groupby(['Season', 'Month'])['Covered distance (m)'].mean().reset_index(name='Average Covered Distance (m)')

    

    # Sort the DataFrame by the 'Month' column using the custom order
    average_counts = average_counts.loc[average_counts['Month'].isin(month_order)]
    average_counts['Month'] = pd.Categorical(average_counts['Month'], categories=month_order, ordered=True)
    average_counts = average_counts.sort_values(by='Month')

    # Sort the DataFrame by the 'Month' column using the custom order
    seasonal_bike_distance = seasonal_bike_distance.loc[seasonal_bike_distance['Month'].isin(month_order)]
    seasonal_bike_distance['Month'] = pd.Categorical(seasonal_bike_distance['Month'], categories=month_order, ordered=True)
    seasonal_bike_distance = seasonal_bike_distance.sort_values(by='Month')


    # Create separate line plots for each season
    fig_winter = px.line(
        seasonal_bike_distance[seasonal_bike_distance['Month'].isin(['Dec', 'Jan', 'Feb', 'Mar'])],
        x='Month',
        y='Average Covered Distance (m)',
        line_shape='linear',
        color_discrete_sequence=['blue'],
        hover_data={'Month': True, 'Average Covered Distance (m)': True, 'Season': True}  # Add 'Season' to hover
    )

    fig_spring = px.line(
        seasonal_bike_distance[seasonal_bike_distance['Month'].isin(['Mar', 'Apr', 'May', 'Jun'])],
        x='Month',
        y='Average Covered Distance (m)',
        line_shape='linear',
        color_discrete_sequence=['green'],
        hover_data={'Month': True, 'Average Covered Distance (m)': True, 'Season': True}  # Add 'Season' to hover
    )

    fig_summer = px.line(
        seasonal_bike_distance[seasonal_bike_distance['Month'].isin(['Jun', 'Jul', 'Aug', 'Sep'])],
        x='Month',
        y='Average Covered Distance (m)',
        line_shape='linear',
        color_discrete_sequence=['red'],
        hover_data={'Month': True, 'Average Covered Distance (m)': True, 'Season': True}  # Add 'Season' to hover
    )

    fig_fall = px.line(
        seasonal_bike_distance[seasonal_bike_distance['Month'].isin(['Sep', 'Oct', 'Nov'])],
        x='Month',
        y='Average Covered Distance (m)',
        line_shape='linear',
        color_discrete_sequence=['#ffd300'],
        hover_data={'Month': True, 'Average Covered Distance (m)': True, 'Season': True}  # Add 'Season' to hover
    )

    # Combine the line plots
    fig = fig_winter.add_traces(fig_spring.data)
    fig.add_traces(fig_summer.data)
    fig.add_traces(fig_fall.data)

    # Update layout
    fig.update_layout(
        yaxis_title='Average Covered Distance (m)',
        xaxis = dict(
            title=None
        )
    )
    
    return {'data': fig['data'], 'layout': fig['layout']}



map_layout = html.Div(
    [
        dcc.Location(id='map-url', refresh=False),  # Location component to track the URL
        #header,
        html.Div(
            [
                html.Hr(),
                html.Div(
                    [
                        html.H4("Geospatial Activity Map"),
                        html.P("A dynamic map visualizing Mobi bike-sharing station activity in Vancouver, displaying either individual markers or a heatmap representing station activity."),
                        dbc.Row(
                            [
                                # Column for the first dropdown (View)
                                dbc.Col(
                                    [   
                                        html.Label('View:', style={'font-weight':'bold'}),
                                        dcc.Dropdown(
                                            id='plot-type-dropdown',
                                            options=[
                                                {'label': 'Marker Plot', 'value': 'marker plot'},
                                                {'label': 'Density Plot', 'value': 'density plot'}
                                            ],
                                            value='marker plot',
                                            multi=False,
                                            clearable=False,
                                            style={'width': '100%'}  # Set width for the dropdown
                                        ),
                                    ],
                                    width=2,
                                    style={'margin-right': '20px', 'margin-bottom': '20px'}  # Add spacing between dropdowns
                                ),
                                # Column for the second dropdown (Bike Type)
                                dbc.Col(
                                    [
                                        html.Label('Bike Type:', style={'font-weight':'bold'}),
                                        dcc.Dropdown(
                                            id='bike-type-dropdown',
                                            options=[
                                                {'label': 'Electric', 'value': 'electric'},
                                                {'label': 'Classic', 'value': 'classic'},
                                                {'label': 'Both', 'value': 'both'}
                                            ],
                                            value='both',
                                            multi=False,
                                            clearable=False,
                                            style={'width': '100%'}  # Set width for the dropdown
                                        ),
                                    ],
                                    width=2
                                )
                            ]
                        ),
                        html.Div(id='map-container', style={'font-weight': 'bold'}),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.RangeSlider(
                                            id='map-month-range-slider',
                                            marks=marks,
                                            min=0,
                                            max=len(months) - 1,
                                            step=1,
                                            value=[0, len(months) - 1]
                                        )
                                    ],
                                    style={'margin-top': '20px'}  # Add spacing
                                )
                            ],
                            justify="center",  # Center justify the row
                            style={'margin-top': '20px'}  # Add vertical space between dropdowns and slider
                        ),
                    ],
                    className='top-bar',
                    style={'margin-bottom': '20px', 'margin-top': '20px'}  # Adjusted styles
                ),
                
                html.Hr()
            ],
            style={'margin': '0', 'padding-left': '80px', 'padding-right': '80px'}  # Adjusted styles for better alignment
        ),
    ]
)

# Define callback to update the map
@app.callback(
    Output('map-container', 'children'),
    [Input('map-month-range-slider', 'value'),  # RangeSlider input
     Input('bike-type-dropdown', 'value'),
     Input('plot-type-dropdown', 'value')]  # Dropdown input
)

def update_map(value, bike_type, plot_type):
    
    # Filtering based on bike type
    if bike_type == 'electric':
        df = combined_df[combined_df['Electric bike'] == True]
    elif bike_type == 'classic':
        df = combined_df[combined_df['Electric bike'] == False]
    else:
        df = combined_df
    
    departure_counts = df.groupby(['Departure station', 'Month']).agg({'Electric bike': 'count'}).reset_index()
    return_counts = df.groupby(['Return station', 'Month']).agg({'Electric bike': 'count'}).reset_index()

    # Rename columns for clarity
    departure_counts.columns = ['Station', 'Month', 'Departure Count']
    return_counts.columns = ['Station', 'Month', 'Return Count']

    # Merge the two DataFrames on Station and Month
    combined_counts = pd.merge(departure_counts, return_counts, on=['Station', 'Month'], how='outer').fillna(0)
    combined_counts['Total Count'] = combined_counts['Departure Count'] + combined_counts['Return Count']

    combined_counts.drop(['Departure Count', 'Return Count'], axis = 1, inplace = True)

    df2 = pd.merge(combined_counts, dfc, on = ['Station'])

    total_counts_by_station = df2.groupby(['Station', 'Coordinates', 'Month'])['Total Count'].sum().reset_index(name='Total Count')
    
    # Obtain the coordinates of the markers.
    marker_locations = total_counts_by_station.to_dict(orient='records')
    
    for entry in marker_locations:
        entry['Coordinates'] = tuple(map(float, entry['Coordinates'].strip('()').split(', ')))
    
    # Convert float values to integers
    value = [int(v) for v in value]

    # Filter marker locations based on selected months
    months = sorted(set(item['Month'] for item in marker_locations))
    start_month = months[value[0]]
    end_month = months[value[1]]
    filtered_marker_locations = [item for item in marker_locations if start_month <= item['Month'] <= end_month]

    # Calculate total count
    total_count = sum(item['Total Count'] for item in filtered_marker_locations)

    # Create a Folium map centered around Vancouver
    map_vancouver = folium.Map(location=[49.2827, -123.1207], zoom_start=12)

    # Add GeoJSON boundary to the map
    folium.GeoJson(vancouver_geojson).add_to(map_vancouver)
    
    # Filtering based on the plot type
    if plot_type == 'marker plot':
        # Add markers to specific locations
        for item in filtered_marker_locations:
            location = item["Coordinates"]
            name = item["Station"]
            info = int(item["Total Count"])
            folium.Marker(
                location=location,
                icon=folium.Icon(icon='bicycle', prefix='fa', color='red'),
                tooltip=f"{name}<br>Activity: {info}"
            ).add_to(map_vancouver)

        # Save the map to HTML and return it
        map_html = map_vancouver.get_root().render()
        return html.Iframe(srcDoc=map_html, width='100%', height='600')
    else:
        # Create HeatMap layer
        heatmap_data = [(loc['Coordinates'][0], loc['Coordinates'][1], loc['Total Count']) for loc in filtered_marker_locations]
        HeatMap(heatmap_data, radius=15, max_zoom=13).add_to(map_vancouver)
        
        # Save the map to HTML and return it
        map_html = map_vancouver.get_root().render()
        return html.Iframe(srcDoc=map_html, width='100%', height='600')


dashboard_tab = dcc.Tab(label='Overview', children=[dashboard_layout])
trends_tab = dbc.Tab(label="Trends", children=[trends_layout])
map_tab = dbc.Tab(label="Map", children=[map_layout])

app.layout = html.Div([
    header,
    dcc.Tabs(
        [
            dashboard_tab,
            trends_tab,
            map_tab
        ],
        colors={
            "border": "white",
            "primary": "#D80808",
            "background": "lightgrey",
        },
        style={
            "width": "100%",
            "fontFamily": "Arial, sans-serif",
            "margin-left": "auto"
        }
    )
])


if __name__ == '__main__':
    app.run_server(debug=True, port=8065)
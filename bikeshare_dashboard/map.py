from dash import dash, dash_table, callback, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import altair as alt
from datetime import date
import os
import calendar
import requests
from io import BytesIO
from PIL import Image
import folium
from folium.plugins import HeatMap

alt.data_transformers.disable_max_rows()

# Read in data globally
#data = pd.read_csv('../dataset/Mobi_System_Data_2023-01.csv', parse_dates=True, index_col=0)

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

# Removing the bike column
combined_df = combined_df.drop(['Bike'], axis = 1)

# Remove NA values
combined_df.dropna(inplace=True)

combined_df['Departure'] = pd.to_datetime(combined_df['Departure'])

# Extract month and season
combined_df['Month'] = combined_df['Departure'].dt.month

combined_df['Month'] = combined_df['Month'].apply(lambda x: calendar.month_abbr[x])

# Remove rows with negative duration
combined_df = combined_df[combined_df['Duration (sec.)'] >= 0]

# Data cleaning
combined_df.loc[combined_df['Departure station'].str.startswith('0099'), 'Departure station'] = "0099 šxʷƛ̓ənəq Xwtl'e7énḵ Square - Vancouver Art Gallery North Plaza"
combined_df.loc[combined_df['Return station'].str.startswith('0099'), 'Return station'] = "0099 šxʷƛ̓ənəq Xwtl'e7énḵ Square - Vancouver Art Gallery North Plaza"
combined_df.loc[combined_df['Departure station'].str.startswith('0136'), 'Departure station'] = '0136 David Lam Park - West'
combined_df.loc[combined_df['Return station'].str.startswith('0136'), 'Return station'] = '0136 David Lam Park - West'
combined_df.loc[combined_df['Departure station'].str.startswith('0201'), 'Departure station'] = '0201 Shaw Tower'
combined_df.loc[combined_df['Return station'].str.startswith('0201'), 'Return station'] = '0201 Shaw Tower'
combined_df.loc[combined_df['Departure station'].str.startswith('0237'), 'Departure station'] = '0237 Glen & 6th'
combined_df.loc[combined_df['Return station'].str.startswith('0237'), 'Return station'] = '0237 Glen & 6th'
combined_df.loc[combined_df['Departure station'].str.startswith('1002'), 'Departure station'] = '1002 PNE - Hastings & Windermere'
combined_df.loc[combined_df['Return station'].str.startswith('1002'), 'Return station'] = '1002 PNE - Hastings & Windermere'
combined_df.loc[combined_df['Departure station'].str.startswith('2143'), 'Departure station'] = '2143 War Memorial Gym'
combined_df.loc[combined_df['Return station'].str.startswith('2143'), 'Return station'] = '2143 War Memorial Gym'
combined_df.loc[combined_df['Departure station'].str.startswith('0154'), 'Departure station'] = '0155 Arbutus & McNicoll'
combined_df.loc[combined_df['Return station'].str.startswith('0154'), 'Return station'] = '0155 Arbutus & McNicoll'
combined_df.loc[combined_df['Departure station'].str.startswith('0165'), 'Departure station'] = '0150 Alexander & Main'
combined_df.loc[combined_df['Return station'].str.startswith('0165'), 'Return station'] = '0150 Alexander & Main'
values_to_remove = ['0980 Workshop - Balancer Bike Check In', '0981 Workshop - Service Complete', '0982 Workshop - Bike Testing', '0987 Quebec Yard - Rogers', '0991 HQ Workshop', '0992 Workshop - Return to Smoove', '0994 Workshop - Transmitter Testing', '0995 Workshop - Transmitter On Deck', '0997 Workshop - Demo Station', '0985 Quebec Yard - To Service', '1000 Temporary Station', '1000 Vancouver PRIDE Valet Station', '3000 Temporary Station - Celebration of Light']
combined_df = combined_df[~combined_df['Departure station'].isin(values_to_remove)]
combined_df = combined_df[~combined_df['Return station'].isin(values_to_remove)]


dfc = pd.read_csv('../dataset/coordinates/station_coordinates.csv')
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



app.layout = html.Div(
    [
        dcc.Location(id='map-url', refresh=False),  # Location component to track the URL
        #header,
        html.Div(
            [
                html.Hr(),
                html.Div(
                    [
                        html.H4("Geospatial Activity Map"),
                        html.P("Utilize either counts or a heat map visualization for comprehensive insights into Mobi bike-sharing station usage patterns."),
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
            style={'margin': '0', 'padding-left': '20px', 'padding-right': '20px'}  # Adjusted styles for better alignment
        ),
    ]
)

# Callback to update the current page based on the URL
# @app.callback(
#     Output('current-page', 'children'),
#     [Input('url', 'pathname')]
# )
# def update_current_page(pathname):
#     if pathname == '/dashboard':
#         return 'Dashboard'
#     elif pathname == '/trends':
#         return 'Trends'
#     elif pathname == '/map':
#         return 'Map'
#     else:
#         return 'Unknown Page'



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



if __name__ == '__main__':
    app.run_server(debug=True, port=8059) 
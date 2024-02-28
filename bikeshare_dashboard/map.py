from dash import dash, dash_table, callback, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import altair as alt
from datetime import date

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


dfc = pd.read_csv('data.csv')
dfc.drop(columns=['comments'], inplace=True)

departure_counts = combined_df.groupby(['Departure station', 'Month']).agg({'Electric bike': 'count'}).reset_index()
return_counts = combined_df.groupby(['Return station', 'Month']).agg({'Electric bike': 'count'}).reset_index()

# Rename columns for clarity
departure_counts.columns = ['Station', 'Month', 'Departure Count']
return_counts.columns = ['Station', 'Month', 'Return Count']

# Merge the two DataFrames on Station and Month
combined_counts = pd.merge(departure_counts, return_counts, on=['Station', 'Month'], how='outer').fillna(0)
combined_counts['Total Count'] = combined_counts['Departure Count'] + combined_counts['Return Count']

combined_counts.drop(['Departure Count', 'Return Count'], axis = 1, inplace = True)

df2 = pd.merge(combined_counts, dfc, on = ['Station'])

total_counts_by_station = df2.groupby(['Station', 'Coordinates', 'Month'])['Total Count'].sum().reset_index(name='Total Count')

marker_locations = total_counts_by_station.to_dict(orient='records')

for entry in marker_locations:
    entry['Coordinates'] = tuple(map(float, entry['Coordinates'].strip('()').split(', ')))



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

# CHARTS / TABLE
map_plot = dbc.Card(
    [
        dbc.CardHeader(
            html.H4("Geospatial Bike Concentration Plot", className="card-title", style={"color": "white"}),
            style={"background-color": "#D80808"}
        ),
        dbc.CardBody(
            dbc.Col([
                dcc.Loading(
                    id="loading-1",
                    type="circle",
                    children=html.Iframe(
                        id="polar_chart",
                        style={
                            "height": "22rem",
                            "width": "100%",
                            "border": "0",
                            "display": "flex",
                            "align-items": "center",
                            "justify-content": "center"
                            }
                        ),
                    color="#D80808"
                )
            ])
        )
    ],
    className="mb-3",
    style={
        "width": "90%",
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
                        dbc.Col(
                            [
                                html.H5("View:"),
                                sort_table_1,
                                html.H5("Bike type:"),
                                sort_table_2
                            ],
                            width=2,
                            style={'margin-right': '20px'}  # Add horizontal space between top bar and sort tables
                        ),
                        dbc.Col(
                            map_plot,
                            width=9
                        ),
                    ],
                    justify="center",
                    style={'margin-top': '20px'}  # Add vertical space between top bar and sort tables/map_plot
                ),
                html.Hr()
            ],
            style={"margin": "0", "margin-left": "220px", "padding-left": "20px"}  # Adjusted styles for better alignment
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
    app.run_server(debug=True, port=8056) 
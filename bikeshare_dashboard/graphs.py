import pandas as pd
import os
import dash
import plotly.express as px
import altair as alt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

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

# Remove null records
combined_df = combined_df.dropna(subset=['Departure station'])

# Count occurrences of each station
station_counts = combined_df['Departure station'].value_counts()

# Get the number of unique stations
num_stations = len(station_counts)

# Remove null records
combined_df = combined_df.dropna(subset=['Departure'])

# Convert 'Departure Date' column to datetime
combined_df['Departure'] = pd.to_datetime(combined_df['Departure'])

# Extract day of the week
combined_df['Day of Week'] = combined_df['Departure'].dt.day_name()

# Count trips by day of the week
trips_by_day = combined_df['Day of Week'].value_counts()

# Sort days of the week
sorted_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
trips_by_day = trips_by_day.reindex(sorted_days)

# Remove null records
combined_df = combined_df.dropna(subset=['Return station'])

# Get the top 10 most common end trip stations
top_end_stations = combined_df['Return station'].value_counts().nlargest(10)

# Calculate percentages
percentage_values = (top_end_stations / top_end_stations.sum()) * 100

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout of the app1
app.layout = html.Div(
    children=[
        html.H1(f"{num_stations}", style={'color': 'red', 'font-weight': 'bold', 'font-size': '24px'}),
        html.P("Active stations around the city. Accessible 24/7, 365 days a year.")
    ]
)

# Define layout of the app2
app.layout = html.Div(
    children=[
        html.H1("Trips by Day of the Week"),
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
                }
            }
        )
    ]
)

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

# Define layout of the app
app.layout = html.Div(
    children=[
        html.H1("Top 10 Most Common End Trip Stations"),
        dcc.Graph(
            figure=fig.update_traces(marker_color='indianred')
        )
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
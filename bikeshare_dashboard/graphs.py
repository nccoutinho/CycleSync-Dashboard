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

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout of the app1
app.layout = html.Div(
    children=[
        html.H1(f"{num_stations}", style={'color': 'red', 'font-weight': 'bold', 'font-size': '24px'}),
        html.P("Active stations around the city. Accessible 24/7, 365 days a year.")
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)


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
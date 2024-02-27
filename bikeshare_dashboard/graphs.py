import pandas as pd
import os
import dash
import calendar
import plotly.express as px
import altair as alt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Path to the folder containing your files
folder_path = './dataset'

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

# Extract seasons
combined_df['Season'] = combined_df['Departure'].dt.month.map({
    12: 'Winter', 1: 'Winter', 2: 'Winter',
    3: 'Spring', 4: 'Spring', 5: 'Spring',
    6: 'Summer', 7: 'Summer', 8: 'Summer',
    9: 'Autumn', 10: 'Autumn', 11: 'Autumn'
})

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


# Assuming combined_df has 'Departure' column
# Convert 'Departure' to datetime
combined_df['Departure'] = pd.to_datetime(combined_df['Departure'])

# Extract month and season
combined_df['Month'] = combined_df['Departure'].dt.month
combined_df['Season'] = combined_df['Departure'].dt.month % 12 // 3 + 1

# Map season and month names
combined_df['Season'] = combined_df['Season'].map({1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'})
combined_df['Month'] = combined_df['Month'].apply(lambda x: calendar.month_abbr[x])

# Group by season, then by month, and calculate average count of bike departures
seasonal_bike_count = combined_df.groupby(['Season', 'Month']).size().reset_index(name='Bike Count')
average_counts = seasonal_bike_count.groupby(['Month', 'Season'])['Bike Count'].mean().reset_index()

# Group by season, then by month, and calculate average covered distance of bike trips
seasonal_bike_distance = combined_df.groupby(['Season', 'Month'])['Covered distance (m)'].mean().reset_index(name='Average Covered Distance (m)')

# Define custom sort order for months
month_order = ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']

# Sort the DataFrame by the 'Month' column using the custom order
average_counts = average_counts.loc[average_counts['Month'].isin(month_order)]
average_counts['Month'] = pd.Categorical(average_counts['Month'], categories=month_order, ordered=True)
average_counts = average_counts.sort_values(by='Month')

# Sort the DataFrame by the 'Month' column using the custom order
seasonal_bike_distance = seasonal_bike_distance.loc[seasonal_bike_distance['Month'].isin(month_order)]
seasonal_bike_distance['Month'] = pd.Categorical(seasonal_bike_distance['Month'], categories=month_order, ordered=True)
seasonal_bike_distance = seasonal_bike_distance.sort_values(by='Month')

# -------------------------------------------------

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
                    'title': 'Trips by Day of the Week',
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

# Create separate line plots for each season
fig_winter = px.line(
    average_counts[average_counts['Month'].isin(['Dec', 'Jan', 'Feb', 'Mar'])],
    x='Month',
    y='Bike Count',
    title='Average Bike Departures in Winter',
    line_shape='linear',
    color_discrete_sequence=['blue'],
    hover_data={'Month': True, 'Bike Count': True, 'Season': True}  
)


fig_spring = px.line(
    average_counts[average_counts['Month'].isin(['Mar', 'Apr', 'May', 'Jun'])],
    x='Month',
    y='Bike Count',
    title='Average Bike Departures in Spring',
    line_shape='linear',
    color_discrete_sequence=['green'],
    hover_data={'Month': True, 'Bike Count': True, 'Season': True}  
)


fig_summer = px.line(
    average_counts[average_counts['Month'].isin(['Jun', 'Jul', 'Aug', 'Sep'])],
    x='Month',
    y='Bike Count',
    title='Average Bike Departures in Summer',
    line_shape='linear',
    color_discrete_sequence=['red'],
    hover_data={'Month': True, 'Bike Count': True, 'Season': True}  
)


fig_fall = px.line(
    average_counts[average_counts['Month'].isin(['Sep', 'Oct', 'Nov'])],
    x='Month',
    y='Bike Count',
    title='Average Bike Departures in Fall',
    line_shape='linear',
    color_discrete_sequence=['yellow'],
    hover_data={'Month': True, 'Bike Count': True, 'Season': True} 
)


# Combine the line plots
fig_combined = fig_winter.add_traces(fig_spring.data)
fig_combined.add_traces(fig_summer.data)
fig_combined.add_traces(fig_fall.data)


# Update layout
fig_combined.update_layout(
    yaxis_title='Average Bike Departure Count',
    xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type='category'
    )
)

# Define layout of the app
app.layout = html.Div(
    children=[
        html.H1("Average Bike Departures by Season and Month"),
        dcc.Graph(
            figure=fig_combined.update_traces(marker_color='indianred')
        )
    ]
)

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
    color_discrete_sequence=['yellow'],
    hover_data={'Month': True, 'Average Covered Distance (m)': True, 'Season': True}  # Add 'Season' to hover
)

# Combine the line plots
fig_combined = fig_winter.add_traces(fig_spring.data)
fig_combined.add_traces(fig_summer.data)
fig_combined.add_traces(fig_fall.data)

# Update layout
fig_combined.update_layout(
    yaxis_title='Average Covered Distance (m)',
    xaxis=dict(
        rangeslider=dict(
            visible=True
        ),
        type='category'
    )
)

# Define layout of the app
app.layout = html.Div(
    children=[
        html.H1("Average Covered Distance by Season and Month"),
        dcc.Graph(
            figure=fig_combined.update_traces(marker_color='indianred')
        )
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)



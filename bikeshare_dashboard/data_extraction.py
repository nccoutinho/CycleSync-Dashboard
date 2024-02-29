import pandas as pd
from datetime import date
import calendar
import os

def bikeshare_data():
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

    # Convert 'Departure' to datetime
    combined_df['Departure'] = pd.to_datetime(combined_df['Departure'])

    # Extract month and season
    combined_df['Month'] = combined_df['Departure'].dt.month
    combined_df['Season'] = combined_df['Departure'].dt.month % 12 // 3 + 1
    
    combined_df['Day of Week'] = combined_df['Departure'].dt.day_name()
    
    # Map season and month names
    combined_df['Season'] = combined_df['Season'].map({1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'})
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
    
    return combined_df, dfc
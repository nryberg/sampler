import requests
import json
import csv
import pandas as pd
import numpy

# Read in the stations.csv file
# This file contains the station id and the state name
# The station id is used to pull the weather data
# The state name is used to name the csv file
#
# The file is read in as a pandas dataframe
# The station id is stored in the station_id column
# The state name is stored in the state_name column
# The dataframe is stored in the variable df
#
# The file is read in using the read_csv function
# The file is read in using the tab delimiter
#
# The file is located in the data folder

df = pd.read_csv('./data/stations.txt', delimiter='\t')

# Ensure the column names match those in the stations.txt file
df.columns = df.columns.str.strip()  # Remove any leading/trailing whitespace from column names

print(df.head())

# Read in the attributes.txt file
# This file contains the attributes to be pulled for each station
# The attributes are stored in a list called attributes

attributes = []
with open('./data/attributes.txt', 'r') as file:
    attributes = file.read().splitlines()

# Function to pull the latest observation for a given station
def pull_latest_observation(station_id):
    url = f"https://api.weather.com/v2/pws/observations/current?stationId={station_id}&format=json&units=m&apiKey=YOUR_API_KEY"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        observation = data['observations'][0]
        return {attr: observation.get(attr, None) for attr in attributes}
    else:
        return None

# Iterate over each station and pull the latest observation
for index, row in df.iterrows():
    station_id = row['station_id']  # Ensure this matches the column name in stations.txt
    state_name = row['state_name']  # Ensure this matches the column name in stations.txt
    observation = pull_latest_observation(station_id)
    if observation:
        # Save the observation to a csv file named after the state
        with open(f'data/{state_name}.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=attributes)
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(observation)

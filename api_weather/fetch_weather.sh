#!/bin/bash

# Ensure the script runs from its directory
cd "$(dirname "$0")"

# Ensure the data directory exists
mkdir -p data

# Read the stations.csv file line by line, skipping the header
while IFS=',' read -r station_id state_name city_name url; do
    # Trim whitespace from the URL
    url=$(echo "$url" | xargs)

    # Fetch the data from the URL and incorporate station_id into the JSON
    response=$(curl -s "$url" | jq --arg station_id "$station_id" '. + {station_id: $station_id}')
    
    # Check if the response is valid JSON
    if echo "$response" | jq empty > /dev/null 2>&1; then
        # Save the response to a JSON file named after the station_id
        echo "$response" > "data/${station_id}.json"
        echo "Saved data for station: $station_id"
    else
        echo "Failed to fetch or parse data for station: $station_id"
    fi
done < <(tail -n +2 stations.csv)
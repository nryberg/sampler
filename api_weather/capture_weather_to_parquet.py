#!/usr/bin/env python3
"""
Weather Data Capture Script
Fetches weather data for multiple cities and saves to a timestamped parquet file.
"""

import pandas as pd
import requests
from datetime import datetime
import json
from pathlib import Path

def fetch_station_weather(station_id, state_name, city_name, url):
    """Fetch weather data for a single station."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract properties from the response
        properties = data.get('properties', {})

        # Create a flat dictionary with relevant weather data
        weather_data = {
            'station_id': station_id,
            'state_name': state_name,
            'city_name': city_name,
            'station': properties.get('station'),
            'timestamp': properties.get('timestamp'),
            'temperature': properties.get('temperature', {}).get('value'),
            'textDescription': properties.get('textDescription'),
            'windSpeed': properties.get('windSpeed', {}).get('value'),
            'windDirection': properties.get('windDirection', {}).get('value'),
            'relativeHumidity': properties.get('relativeHumidity', {}).get('value'),
            'heatIndex': properties.get('heatIndex', {}).get('value'),
            'windChill': properties.get('windChill', {}).get('value'),
            'visibility': properties.get('visibility', {}).get('value'),
            'elevation': properties.get('elevation', {}).get('value'),
        }

        return weather_data
    except Exception as e:
        print(f"Error fetching data for {station_id} ({city_name}): {e}")
        return None

def main():
    """Main function to fetch weather data and save to parquet."""
    # Read stations from CSV
    stations_df = pd.read_csv('stations.csv')

    # Capture timestamp for this run
    capture_time = datetime.now()

    # Collect weather data for all stations
    weather_records = []

    print(f"Fetching weather data for {len(stations_df)} stations...")
    for idx, row in stations_df.iterrows():
        station_id = row['station_id']
        state_name = row['state_name']
        city_name = row['city_name']
        url = row['url']

        print(f"  Fetching {station_id} ({city_name})...", end=" ")
        weather_data = fetch_station_weather(station_id, state_name, city_name, url)

        if weather_data:
            # Add capture timestamp
            weather_data['capture_timestamp'] = capture_time
            weather_records.append(weather_data)
            print("✓")
        else:
            print("✗")

    # Convert to DataFrame
    df = pd.DataFrame(weather_records)

    # Create output filename with timestamp
    timestamp_str = capture_time.strftime('%Y%m%d_%H%M%S')
    output_file = f'weather_data_{timestamp_str}.parquet'

    # Save to parquet file
    df.to_parquet(output_file, index=False)

    print(f"\n✓ Successfully saved {len(df)} records to {output_file}")
    print(f"  Capture time: {capture_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  File size: {Path(output_file).stat().st_size / 1024:.2f} KB")

if __name__ == "__main__":
    main()

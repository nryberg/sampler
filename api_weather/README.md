# Weather Data Capture System

A collection of scripts for fetching, processing, and storing weather data from multiple weather stations across the United States.

## Quick Start

### Capture Weather Data to Parquet (Recommended)

The simplest way to capture current weather data for all stations:

```bash
python3 capture_weather_to_parquet.py
```

This creates a timestamped parquet file (e.g., `weather_data_20251122_140615.parquet`) containing weather observations for all configured stations.

## Data Sources

Weather data is fetched from the National Weather Service API (weather.gov) for 20 stations across the US:

- **Alaska**: Anchorage (PANC)
- **Arizona**: Phoenix (KPHX)
- **California**: Los Angeles (KLAX), San Francisco (KSFO)
- **Florida**: Miami (KMIA)
- **Georgia**: Atlanta (KATL)
- **Hawaii**: Honolulu (PHNL)
- **Illinois**: Chicago (KORD)
- **Maine**: Bangor (KBGR)
- **Minnesota**: International Falls (KINL), Minneapolis-Saint Paul (KMSP)
- **Missouri**: Kansas City (KMCI)
- **Montana**: Kalispell (KGPI)
- **New York**: New York (KJFK)
- **Oregon**: Portland (KPDX)
- **Texas**: Brownsville (KBRO), Corpus Christi (KCRP), Dallas-Fort Worth (KDFW), Houston (KIAH)
- **Washington**: Seattle (KSEA)

Station configuration is stored in `stations.csv`.

## Scripts

### Primary Scripts

#### `capture_weather_to_parquet.py`
Fetches current weather observations for all stations and saves to a timestamped parquet file.

**Output**: `weather_data_YYYYMMDD_HHMMSS.parquet`

**Fields captured**:
- Station identification: station_id, state_name, city_name
- Temperature and conditions: temperature, textDescription
- Wind: windSpeed, windDirection
- Humidity and comfort: relativeHumidity, heatIndex, windChill
- Visibility and elevation
- Timestamps: observation timestamp, capture_timestamp

**Usage**:
```bash
python3 capture_weather_to_parquet.py
```

#### `pull_weather.py`
Alternative Python script for pulling weather data using the Weather Underground API (requires API key).

### Legacy Pipeline Scripts

A multi-step shell-based pipeline for processing weather data:

1. **`fetch_weather.sh`**: Fetches JSON data from weather.gov API for each station
2. **`step_2_process_multiple_stations.sh`**: Processes multiple station files
3. **`step_3_combine_json_into_one.sh`**: Combines individual JSON files into one
4. **`step_4_jq_combined_to_csv.sh`**: Converts combined JSON to CSV using jq
5. **`step_5_mlr_join_files.sh`**: Joins files using Miller (mlr)
6. **`step_6_cut_to_station_temp.sh`**: Extracts specific fields (station ID and temperature)

### Processing Scripts

- **`process_combined.py`**: Processes combined weather data files
- **`dasel.sh`**: Data selection and transformation using dasel
- **`mlr_join.sh`**: Miller-based join operations

## Configuration Files

- **`stations.csv`**: Primary station configuration (station_id, state_name, city_name, url)
- **`weather_stations.csv`**: Additional station metadata
- **`query.jq`**: jq query template for JSON processing

## Data Directories

- **`data/`**: Raw JSON files from weather API
- **`clean_json/`**: Processed/cleaned JSON files
- **`output/`**: Processed output files

## Output Files

### Parquet Files
- `weather_data_YYYYMMDD_HHMMSS.parquet`: Timestamped weather snapshots

### CSV Files
- `combined_weather_data.csv`: Combined weather observations
- `station_temps_f.csv`: Station temperatures in Fahrenheit
- Various processed CSV files (`*_combined_weather.csv`)

## Dependencies

### Python
```bash
pip install pandas requests pyarrow
```

### Shell Tools
- `jq`: JSON processing
- `curl`: HTTP requests
- `mlr` (Miller): Data processing
- `dasel`: Data selection (optional)

## Data Schema

### Parquet Output Schema

| Field | Type | Description |
|-------|------|-------------|
| station_id | string | Station identifier (e.g., KJFK) |
| state_name | string | State name |
| city_name | string | City name |
| station | string | Station API URL |
| timestamp | datetime | Observation time (from weather service) |
| temperature | float | Temperature in Celsius |
| textDescription | string | Weather description |
| windSpeed | float | Wind speed (km/h) |
| windDirection | float | Wind direction (degrees) |
| relativeHumidity | float | Relative humidity (%) |
| heatIndex | float | Heat index in Celsius |
| windChill | float | Wind chill in Celsius |
| visibility | float | Visibility in meters |
| elevation | float | Station elevation in meters |
| capture_timestamp | datetime | When data was captured |

## Adding New Stations

1. Find the station ID from [weather.gov](https://www.weather.gov/)
2. Add a row to `stations.csv`:
   ```csv
   KXXX,State,City,https://api.weather.gov/stations/KXXX/observations/latest
   ```
3. Run the capture script

## Notes

- Weather data is from NOAA/National Weather Service (public domain)
- API calls include a timeout of 10 seconds per station
- Temperature values are in Celsius (from the API)
- Parquet format provides efficient storage and fast querying
- Each capture creates a new timestamped file for historical tracking

#!/bin/bash

# First, let's transform the stations.csv to match the URL format in our weather data
mlr put '$url = sub($url, "/observations/latest", "")' stations.csv > stations_fixed.csv

# Then join the files
mlr --csv join -j url -f stations_fixed.csv -l station then \
  rename station,station_url then \
  cut -x -f station_url then \
  reorder -f station_id,state_name,city_name ./clean_json/weather_stations.csv > combined_weather_data.csv

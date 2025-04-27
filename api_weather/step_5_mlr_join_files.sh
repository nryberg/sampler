#!/bin/bash

mlr --csv join -j station_id -f stations.csv then \
  cut -x -f url then \
  reorder -f station_id,state_name,city_name \
  weather_stations.csv > combined_weather_data.csv
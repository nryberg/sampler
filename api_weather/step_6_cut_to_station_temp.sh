#!/bin/bash

mlr --no-color --csv cut -f station_id,state_name,city_name,temperature then \
  put '$temperature = ($temperature * 9/5) + 32; $temperature = round($temperature)' then \
  rename temperature,temperature_f then \
  sort -nr temperature_f \
  combined_weather_data.csv > station_temps_f_sorted.csv

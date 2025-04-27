#!/bin/bash

jq -r '(input | keys) as $keys | 
  $keys | @csv, 
  (inputs | [.[$keys[]]] | @csv)' ./clean_json/combined.json > weather_stations.csv
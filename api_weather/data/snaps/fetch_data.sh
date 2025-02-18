#!/bin/bash

# Loop through each line in urls.txt
while read -r url; do
  # Extract station code using cut
  station=$(echo "$url" | cut -d'/' -f5)
  # Fetch the data and save it as a .json file
  curl -s "$url" -o "${station}.json"
  echo "Downloaded: ${station}.json"
done < urls.txt


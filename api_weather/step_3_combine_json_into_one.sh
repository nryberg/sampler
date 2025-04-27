#!/bin/bash

for file in ./data/*.json; do
    jq -f query.jq "$file"
done > ./clean_json/combined.json

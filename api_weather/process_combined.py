#!/usr/bin/env python3
import csv
import json
import sys

def convert_jsonl_to_csv(input_file, output_file):
    # Read all the lines from the input file
    with open(input_file, 'r') as f:
        # Parse each line as a JSON object
        json_objects = []
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                json_objects.append(json.loads(line))
    
    if not json_objects:
        print("No JSON objects found in the input file.")
        return
    
    # Get field names from the first object
    fieldnames = json_objects[0].keys()
    
    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(json_objects)
    
    print(f"Successfully converted {len(json_objects)} records to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python json_to_csv.py input.json output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_jsonl_to_csv(input_file, output_file)
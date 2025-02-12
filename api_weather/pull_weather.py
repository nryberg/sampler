# Using the stations.txt file, this script will pull the weather data for each station and save it to a csv file
# I would like to pull the attributes in the attributes.txt file
# I would like to pull the latest observation for each station

import requests
import json
import csv
import pandas as pd
import numpy

# Read in the stations.txt file
# This file contains the station id and the state name
# The station id is used to pull the weather data
# The state name is used to name the csv file
#
# The file is read in as a pandas dataframe
# The station id is stored in the station_id column
# The state name is stored in the state_name column
# The dataframe is stored in the variable df
#
# The file is read in using the read_csv function
# The file is read in using the tab delimiter
#
# The file is located in the data folder

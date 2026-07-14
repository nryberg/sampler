import pandas as pd
import requests

# Define the Wikipedia URL
url = "https://en.wikipedia.org/wiki/List_of_Best_in_Show_winners_of_the_Westminster_Kennel_Club_Dog_Show"

# Add a User-Agent header to pretend to be a standard web browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Fetch the page content securely
response = requests.get(url, headers=headers)

# Read the HTML content into pandas DataFrames
tables = pd.read_html(response.text)

# The main winners table is the second table on this specific page (index 1)
winners_table = tables[1]

# Save the DataFrame directly to a CSV file
winners_table.to_csv("westminster_winners.csv", index=False)

print("CSV file 'westminster_winners.csv' successfully created!")


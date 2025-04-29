import pandas as pd 
import pyarrow

df_flights = pd.read_parquet("./over_my_head/Flights.parquet")
df_flights.head()

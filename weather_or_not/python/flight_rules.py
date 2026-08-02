"""Classify KMSP METAR observations into FAA flight-rules categories.

Pandas port of queries/flight_rules.sql, written as a single top-to-bottom
workflow.

The category is the MORE RESTRICTIVE of the ceiling and the visibility:

    Category  Ceiling (ft AGL)      Visibility (statute miles)
    --------  --------------------  --------------------------
    LIFR      below 500             below 1
    IFR       500 to below 1,000    1 to below 3
    MVFR      1,000 to 3,000        3 to 5
    VFR       above 3,000           above 5

CEILING is the lowest BROKEN (BKN), OVERCAST (OVC) or obscured/vertical-
visibility (VV) layer. FEW and SCT layers are NOT ceilings, so a sky of only
FEW/SCT/CLR has an "unlimited" ceiling (NaN here -> treated as VFR).

METAR reports cloud layers in ascending altitude, so the FIRST BKN / OVC / VV
group in the raw text is the lowest one. Heights are in hundreds of feet
(e.g. OVC002 = 200 ft, BKN140 = 14,000 ft).

Usage:
    python python/flight_rules.py                      # prints summary + sample
    python python/flight_rules.py --db path/to.db      # custom database
    python python/flight_rules.py --csv out.csv        # write classified rows
"""

import argparse
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_DB = Path(__file__).resolve().parent.parent / "sqlite_Weather_Log.db"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite database path")
parser.add_argument("--csv", type=Path, help="write classified rows to this CSV")
args = parser.parse_args()

# --- Load: KMSP observations, dropping repeat scrapes of the same timestamp ---
with sqlite3.connect(args.db) as conn:
    df = pd.read_sql_query(
        "SELECT Station, Observed_Date, Temp_Celsius, Wind_Speed, Wind_Direction, "
        "Cover, Visibility, Observation "
        "FROM Weather_History WHERE Station = 'KMSP'",
        conn,
    )
df = df.drop_duplicates(subset=["Station", "Observed_Date"])

# --- Ceiling: lowest BKN/OVC/VV layer in feet (NaN when the sky has none) ---
# METAR lists layers low -> high, so the first match is the ceiling layer.
# Heights are in hundreds of feet, so multiply the captured 3 digits by 100.
hundreds = df["Observation"].str.extract(r"(?:BKN|OVC|VV)(\d{3})", expand=False)
df["ceiling_ft"] = pd.to_numeric(hundreds, errors="coerce") * 100

# --- Classify: the more restrictive of ceiling and visibility ---
# NaN ceiling == unlimited; use +inf so it never triggers a low category.
ceil = df["ceiling_ft"].fillna(np.inf)
vis = df["Visibility"]
df["flight_rules"] = np.select(
    [
        (ceil < 500) | (vis < 1),
        (ceil < 1000) | (vis < 3),
        (ceil <= 3000) | (vis <= 5),
    ],
    ["LIFR", "IFR", "MVFR"],
    default="VFR",
)

# --- Tidy: rename, keep the reporting columns, order by observation time ---
df = (
    df.rename(columns={"Visibility": "visibility_sm"})
    [["Observed_Date", "Temp_Celsius", "Wind_Speed", "Cover",
      "visibility_sm", "ceiling_ft", "flight_rules"]]
    .sort_values("Observed_Date")
    .reset_index(drop=True)
)

# --- Report ---
order = ["LIFR", "IFR", "MVFR", "VFR"]
counts = df["flight_rules"].value_counts().reindex(order, fill_value=0)
summary = pd.DataFrame({"obs": counts, "pct": (100 * counts / counts.sum()).round(1)})

print("=== Flight-rules distribution ===")
print(summary.to_string())
print("\n=== Lowest-ceiling / worst observations ===")
worst = df[df["flight_rules"].isin(["LIFR", "IFR"])].sort_values("ceiling_ft")
print(worst.head(6).to_string(index=False))

if args.csv:
    df.to_csv(args.csv, index=False)
    print(f"\nWrote {len(df)} rows to {args.csv}")

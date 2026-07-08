# Flights of Fancy

A sample dataset of ADS-B flight-tracking observations, joined with basic
aircraft/operator metadata. Each row is a single position report for one
aircraft at one point in time — 1,806 observations across 779 distinct
aircraft (by `icao24` hex code), spanning 2023-09-20 to 2023-11-26.

The data is provided in several equivalent forms for testing tools that
read different formats: CSV, Parquet, Excel, DuckDB, and SQLite.

## Files

| File | Description |
|---|---|
| `Flights.csv` / `Flights.parquet` | The main fact table — 1,806 flight observations |
| `Aircraft_Category.csv` / `aircraft_category.parquet` | Lookup table decoding the `af_category` codes |
| `Flight_Traffic.xlsx` | Both tables above, as workbook sheets |
| `duckdb_Flight_Traffic.db` | DuckDB database with both tables loaded |
| `sqlite_Flight_Traffic.db` | SQLite database with both tables loaded |
| `process_flights.py` | Example script reading `Flights.parquet` with pandas |

## Table: `Flights`

1,806 rows. One row per aircraft position report.

| Column | Type | Notes |
|---|---|---|
| `icao24` | varchar | Aircraft's unique 24-bit ICAO hex address (779 distinct aircraft) |
| `flight` | varchar | Flight/callsign, e.g. `QTR99V` (blank on some rows) |
| `ts_date` | date | Observation date |
| `ts_time` | time | Observation time (UTC) |
| `alt` | int | Altitude (feet) |
| `track` | int | Heading/track angle (degrees) |
| `groundspeed` | int | Ground speed (knots) |
| `af_category` | varchar | Aircraft weight/performance category code — see `Aircraft_Category` lookup |
| `registration` | varchar | Tail number, e.g. `A7-BBC` |
| `manufacturername` | varchar | Airframe manufacturer, e.g. `Boeing`, `Airbus` |
| `model` | varchar | Aircraft model, e.g. `777 2DZLR` |
| `typecode` | varchar | ICAO aircraft type code, e.g. `B77L` |
| `operator` | varchar | Operating airline/company (64 distinct values; not normalized — e.g. `United Airlines` and `United Airlines Inc. - United States Of America` both appear) |
| `operatorcallsign` | varchar | Operator's radio callsign, e.g. `QATARI` |
| `operatoricao` | varchar | Operator's 3-letter ICAO code, e.g. `QTR` |
| `owner_name` | varchar | Registered owner (often same as operator) |
| `built` | date | Aircraft manufacture date |

## Table: `Aircraft_Category`

7 rows. Decodes the `af_category` (`A1`–`A7`) codes used in `Flights`.

| Column | Notes |
|---|---|
| `Category` | Code, e.g. `A5` |
| `Description` | e.g. `Heavy (> 300 000 lbs.)` |

## Notes

- `operator` and `manufacturername` are raw source values and are not
  deduplicated/normalized — expect near-duplicate strings for the same
  real-world entity (e.g. `Boeing`, `Boeing Co`, `Boeing Company`, `The
  Boeing Co.`).
- `process_flights.py` references a `./over_my_head/Flights.parquet` path
  that doesn't exist in this folder — update the path to `./Flights.parquet`
  before running it.

# soccer_player_pay

MLS player salary/compensation data and season standings, 2014–2026.

## Salary data

Source is the [MLSPA Salary Guide](https://mlsplayers.org/resources/salary-guide) (see `pdfs/`, the original PDF releases per year) plus the fall 2026 Spring Salary Guide PDF (`Spring-2026-MLSPA-Salary-Guide.pdf`).

- `mls_<year>.csv` — one file per season (2014–2026), scraped/transcribed from that year's MLSPA salary guide PDF. Column names vary year to year since MLSPA changes the guide's format (e.g. `Base Salary` vs `PA Base Salary`, `Club` vs `Team Name`, `Playing Position` vs `Position(s)`); no column has been normalized across years.
- `mls_2019_1.csv` / `mls_2019_2.csv` — split extracts of the 2019 guide (different tables/pages from the same PDF), not yet merged into `mls_2019.csv`.
- `mls_all_clubs_2014_2024.csv` — cleaned, unioned dataset across 2014–2024 with consistent columns: `Club, Last Name, First Name, Position, Salary, Compensation, Year`.
- `msl_all_2014_2024.parquet` — same unioned 2014–2024 dataset as above, in Parquet form (8,130 rows, same 7 columns).
- `MLS_Players_2014_2024.xlsx` — Excel version of the unioned dataset.
- `Clubs.csv` — club abbreviation-to-full-name lookup (e.g. `ATL` → `Atlanta United`).
- `2022/raw_2022.csv`, `2022/raw_2022.xlsx` — raw (pre-cleaning) extract of the 2022 salary guide.
- `pdfs/` — original MLSPA salary guide PDFs, one per year, 2014–2024.

## Standings data

- `mls_standings_2014_2025.csv` — final Eastern/Western conference standings for each MLS season 2014–2025 (position, team, games played, W/L/T, goals for/against, goal differential, points), scraped from Wikipedia's per-season MLS articles. Useful for joining against the salary data to relate club spending to on-field performance.

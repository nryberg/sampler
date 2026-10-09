# NFL QB movement data, 2015–2026

Built from nflverse data on 2026-10-09 (2026 season through Week 4).
The same tables and views are in the MotherDuck database `nfl`.

## Files

- `nfl_qb.duckdb`: everything, as one DuckDB database. The raw tables are stored, and the QB tables are views over them.
  Open it with `duckdb nfl_qb.duckdb`, or `duckdb.connect('nfl_qb.duckdb')` in Python.
- `parquet/`: every table and view, one file each.
- `csv/`: the QB views plus `rosters` and `games`. The two large raw tables are Parquet only.
- `views.sql`: the SQL behind every view.

## QB views

| View | One row per | Notes |
|---|---|---|
| `qb_starts` | team × game | Starting QB (gsis `player_id`) for every completed game |
| `qb_snaps` | QB × game | Offensive snaps, snap %, and team snaps that game |
| `team_game_snaps` | team × game | Team offensive snaps |
| `qb_team_seasons` | QB × team × season | Regular season: games, starts, snaps, snap_share, passing, EPA, `meaningful` flag |
| `qb_seasons` | QB × season | Meaningful seasons only; `primary_team` = team with most snaps; `midseason_move` |
| `qb_moves` | move | `primary_team` differs from the QB's previous meaningful season |
| `team_lead_qbs` | team × season | QB with most snaps, and `how`: Returning / Arrived from another team / First meaningful season |

**Meaningful** = at least one regular-season start, or 100+ QB snaps with 25+ pass attempts.
**Returning** = meaningful for the same team within the previous two seasons.

## Raw tables

`rosters`, `player_week_stats`, `games`, `snap_counts`, and `player_ids` (a Pro Football Reference ID → nflverse gsis ID map).
Team codes are normalized to current franchises: OAK→LV, SD→LAC, STL→LA.

## Source and attribution

Data: nflverse (https://github.com/nflverse), including nflverse-data releases and nfldata games.csv.
Snap counts originate from Pro Football Reference. Check the nflverse-data license notes before republishing raw tables, and credit nflverse.

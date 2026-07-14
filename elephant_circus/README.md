# elephant_circus

Two loosely-related historical datasets: American circus tour routes (1865–1960) and a monthly U.S. bank clearings index (1875–1943). The overlapping date range suggests these were put together to explore whether circus touring activity (route density, number of shows on the road, geographic reach) tracked macroeconomic conditions — but that link isn't documented anywhere yet, see questions below.

## `routes/`

One file per sampled year — `routes_<year>.csv` — covering 1865, 1870, 1875, ... 1960 (5-year intervals, plus 1865 as the earliest year). Each file holds every recorded tour stop for that year only (not a 5-year span, despite the interval implied by the filenames).

Columns: `CircusName, Year, Country, State, City, FullDate`

- 31,747 stops total across 20 files, 156 unique circus/show names (e.g. Ringling Bros. Barnum & Bailey Circus, Barnum & Bailey's Greatest Show on Earth, Al G. Barnes Circus, Buffalo Bill's Wild West).
- Mostly United States (30,201 stops), plus Canada, Germany, France, England, Italy, Mexico, and Austria.
- All rows parse cleanly with a standard CSV reader (quoted fields, embedded commas in names like "Ringling Bros. Barnum & Bailey Circus" are handled correctly — a naive comma-split will mis-parse them).
- No missing months/gaps checked yet within a season, only that each file is well-formed.
- **Not tracked in git.** `routes/*.csv` is listed in the repo's `.gitignore` — see the sourcing note below. The raw files still exist locally; only the aggregated output in `analysis/` (below) is committed.

### Sourcing / license concern ⚠️

Source: [Circus Historical Society](https://www.circushistory.org) (circushistory.org), via its Circus Routes research pages. A copy of the site's Terms of Use is saved at `sourcing/Terms of Use - Circus Historical Society.html` (dated 7-17-20).

Those terms are restrictive in ways that likely conflict with having this data in a **public** repo:

- **"Use of this website must be for personal, non-commercial use."**
- **"Outside of personal viewing, you may not copy, reproduce, distribute (digital or print), transmit, broadcast, display, sell, license, or otherwise use Content without our prior written consent..."**
- Automated scraping beyond normal human browsing speed is explicitly disallowed ("robots," "spiders," "offline readers") — relevant if this CSV was scraped rather than transcribed by hand.
- CHS states it doesn't own much of the site's content (the routes data reads as contributed/compiled historical research) and says it **can't grant permission for third-party content even on request**: *"CHS cannot grant permission, or licenses, to use Content owned by third parties on its Site."*

This repo (`nryberg/sampler`) is public on GitHub and is explicitly intended for reuse in testing/developing analytic tools — that's redistribution beyond "personal viewing." As things stand, this dataset's presence here isn't clearly authorized by the source's own terms.

**Mitigation applied:** `routes/*.csv` is now gitignored, so the raw per-stop data is no longer published in the public repo — only the derived aggregate counts in `analysis/` (below) are committed. That's a reasonable-effort reduction of exposure, not a legal clearance; aggregated output still ultimately derives from CHS's compiled research. Requesting written permission from CHS (`webmaster@circushistory.org`) or swapping in a differently-licensed source remains the more durable fix if this dataset needs to keep growing.

## `bank_clearing/`

`bank_clearing_data_nationwide.csv` — a monthly time series, 1875-01 through 1943-09 (825 observations, no gaps), two columns: `observation_date`, and a value column named `M12013USM144NNBR_20050801`.

That column name looks like a FRED series ID (`NNBR` suggests it's sourced from FRED's NBER Macrohistory database, `_20050801` looks like a vintage/revision date FRED appends). I haven't confirmed what the series actually measures (e.g. nationwide bank clearings volume/value, index vs. raw dollars, which cities are included) — flagging rather than guessing.

## `analysis/`

- `build_city_visits.py` — reads the raw `routes/*.csv` files (gitignored, see above) and aggregates them into `city_visits_by_year.csv`, a count of circus visits per city per sampled year for 10 cities chosen to span a range of sizes and regions: Minneapolis, Chicago, New York City, Boston, New Orleans, Atlanta, San Francisco, Seattle, Denver, and Dallas. The goal is a rough proxy for how "economically busy" each city was over 1865–1960, to eventually compare against `bank_clearing/`.
- `city_visits_by_year.csv` — output of the script above; committed, since it's aggregate counts rather than the underlying routes content. Columns:
  - `City`, `Year`
  - `Engagements` — the primary metric. One engagement = one contiguous run of dates for a single circus in a single city (a multi-week indoor season, e.g. Ringling Bros. at Madison Square Garden, counts as **1** visit, not one per day).
  - `DistinctCircuses` — count of unique circuses that visited that city that year (breadth, ignores how long each stayed).
  - `StopDays` — total recorded tour-stop days in that city that year (volume, the raw row count).
- Cleanup decisions baked into the script (documented in its docstring/comments):
  - The raw data uses three interchangeable labels for the same Manhattan venue/city — `New York City`, `New York`, and `Madison Square Garden` (all `State=New York`) — merged into a single `New York City` after confirming by inspection they're the same recurring seasons.
  - `Brooklyn` is kept separate, since it was an independent city until the 1898 consolidation into NYC.
  - **1865 has no rows for any of the 10 cities** — the only circus tracked that year (Yankee Robinson Circus / Palmers Circus) toured small Illinois/Iowa towns, none of which are in the target list. Confirmed by inspecting the raw file directly; not a script bug.
- `city_economic_profile.csv` — a static, one-row-per-city lookup: `City, State, Region, PrimaryIndustries, Notes`, describing each of the 10 cities' historical industrial base (e.g. Minneapolis = flour milling, Denver = mining supply/smelting, Seattle = timber/shipbuilding/aircraft). **Manually compiled from general historical knowledge, not scraped or pulled from a citable dataset** — treat as a reasonable starting characterization, not verified fact, and check specifics before relying on it for real analysis.
- `city_population_by_decade.csv` — decennial population for the same 10 cities, 1860–1960 (11 census years), columns `City, State, Year, Population, RankAmongTop100, Notes`. This is used as the quantitative "how economically busy was this city" proxy the routes/bank-clearing data can be compared against — there's no clean standardized city-level economic-output (GDP-equivalent) series for this era, so population is the best available substitute, not a literal measure of economic activity. Sourced from the U.S. Census Bureau's [Population of the 100 Largest Cities and Other Urban Places in the United States: 1790–1990](https://www.census.gov/library/working-papers/1998/demo/POP-twps0027.html) (Gibson, Population Division Working Paper No. 27), pulled directly from the underlying [decennial tables](https://www2.census.gov/library/working-papers/1998/demographics/pop-twps0027/) — public-domain U.S. government data, no licensing concern like `routes/`.
  - Rows with a blank `Population` mean the city hadn't yet grown into the top 100 urban places that census year (e.g. Denver/Seattle/Dallas/Minneapolis before ~1880–1890) — noted in `Notes`, not a data error.
  - **New York City has a break in comparability**: 1860–1890 figures are pre-consolidation (Manhattan/Bronx only); the 1900 jump to 3.4M reflects the 1898 merger of the five boroughs, not organic growth — flagged in `Notes` on that row.

## Open questions

1. What is `M12013USM144NNBR_20050801` actually measuring, and what are its units? Worth renaming the column to something readable once known.
2. `bank_clearing/` is nationwide, not city-level, so it can't be joined directly against `city_visits_by_year.csv` / `city_population_by_decade.csv` by city — only by year, at a national level. Is a city-level bank clearing series available/desired (some cities in the NBER Macrohistory database have their own series), or is the nationwide series meant to stand in as a macro backdrop only?
3. Why 5-year sampled intervals for routes instead of a continuous year range? Is there a reason 1965–present isn't included, or was data unavailable/not collected past 1960?
4. **Routes data licensing**: has anyone requested written permission from CHS to redistribute this data, or should it be pulled from the public repo / replaced with a differently-licensed source (see sourcing note above)?
5. Bank clearings data stops in 1943 — is that a hard limit of the source series, or just where the extract was cut off?
6. Was the routes data scraped programmatically, or transcribed by hand? CHS's terms specifically prohibit automated collection exceeding normal browsing speed, which matters independent of the redistribution question.
7. `city_economic_profile.csv`'s industry descriptions are from general knowledge, not a citable source — worth backing with real references (e.g. Census "Historical Statistics of the United States," city almanacs) if this dataset needs to hold up to scrutiny.

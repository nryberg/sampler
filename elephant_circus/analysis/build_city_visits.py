"""
Aggregates elephant_circus/routes/*.csv (raw, gitignored) into circus
"visits" (engagements) by city by sampled year, for a fixed set of 10
cities chosen for geographic spread and a range of city sizes.

A visit/engagement = a contiguous run of dates for one circus in one city
in one year. A multi-week indoor season (e.g. Ringling Bros. at Madison
Square Garden) counts as one visit, not one per day. A gap of more than
one day between dates for the same circus in the same city starts a new
engagement.

Output is aggregate counts only (no per-stop rows), safe to commit even
though the underlying routes/ CSVs are not (see README.md sourcing note).
"""
import csv
import glob
from collections import defaultdict
from datetime import datetime

# (State, {city name variants}) -> canonical city label.
# NYC data uses three interchangeable labels for the same place
# ("New York City", "New York", "Madison Square Garden"); merged here.
# Brooklyn is kept separate (independent city until the 1898 consolidation).
CITIES = {
    ("Minnesota", frozenset({"Minneapolis"})): "Minneapolis",
    ("Illinois", frozenset({"Chicago"})): "Chicago",
    ("New York", frozenset({"New York City", "New York", "Madison Square Garden"})): "New York City",
    ("Massachusetts", frozenset({"Boston"})): "Boston",
    ("Louisiana", frozenset({"New Orleans"})): "New Orleans",
    ("Georgia", frozenset({"Atlanta"})): "Atlanta",
    ("California", frozenset({"San Francisco"})): "San Francisco",
    ("Washington", frozenset({"Seattle"})): "Seattle",
    ("Colorado", frozenset({"Denver"})): "Denver",
    ("Texas", frozenset({"Dallas"})): "Dallas",
}

# state -> [(city_variants, canonical_name), ...] for fast lookup
BY_STATE = defaultdict(list)
for (state, variants), canonical in CITIES.items():
    BY_STATE[state].append((variants, canonical))


def canonical_city(state, city):
    for variants, canonical in BY_STATE.get(state, []):
        if city in variants:
            return canonical
    return None


def count_engagements(dates):
    """dates: sorted list of datetime.date. Returns number of runs where
    consecutive entries are exactly 1 day apart."""
    if not dates:
        return 0
    engagements = 1
    for prev, curr in zip(dates, dates[1:]):
        if (curr - prev).days > 1:
            engagements += 1
    return engagements


def main():
    # (canonical_city, year) -> circus name -> sorted list of dates
    by_city_year_circus = defaultdict(lambda: defaultdict(list))

    for path in sorted(glob.glob("../routes/routes_*.csv")):
        with open(path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row["Country"] != "United States":
                    continue
                city = canonical_city(row["State"], row["City"])
                if city is None:
                    continue
                year = row["Year"]
                date = datetime.strptime(row["FullDate"], "%Y-%m-%d").date()
                by_city_year_circus[(city, year)][row["CircusName"]].append(date)

    results = []
    for (city, year), circuses in by_city_year_circus.items():
        engagements = 0
        stop_days = 0
        for dates in circuses.values():
            dates.sort()
            engagements += count_engagements(dates)
            stop_days += len(dates)
        results.append({
            "City": city,
            "Year": year,
            "Engagements": engagements,
            "DistinctCircuses": len(circuses),
            "StopDays": stop_days,
        })

    # fill zeros for (city, year) combos with no recorded visits
    all_years = sorted({y for (_, y) in by_city_year_circus.keys()})
    present = {(r["City"], r["Year"]) for r in results}
    for canonical in set(CITIES.values()):
        for year in all_years:
            if (canonical, year) not in present:
                results.append({
                    "City": canonical, "Year": year,
                    "Engagements": 0, "DistinctCircuses": 0, "StopDays": 0,
                })

    results.sort(key=lambda r: (r["City"], int(r["Year"])))

    out_path = "city_visits_by_year.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["City", "Year", "Engagements", "DistinctCircuses", "StopDays"])
        writer.writeheader()
        writer.writerows(results)

    print(f"wrote {len(results)} rows to {out_path}")


if __name__ == "__main__":
    main()

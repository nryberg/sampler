# dogs

Best in Show winners of the Westminster Kennel Club Dog Show, 1907–2026.

- `fetch.py` — scrapes the winners table from [Wikipedia's List of Best in Show winners](https://en.wikipedia.org/wiki/List_of_Best_in_Show_winners_of_the_Westminster_Kennel_Club_Dog_Show) (`pandas.read_html`, second table on the page) and writes it to `westminster_winners.csv`. Re-run it to refresh the data for future years.
- `westminster_winners.csv` — 120 rows, one per show year. Columns: `Year, Winner, Image, Breed, Group, Owner, Ref(s)`.
  - `Image` is empty for every row (Wikipedia's image cells don't carry over through `read_html`) and `Ref(s)` holds Wikipedia footnote markers (e.g. `[15]`) — both are scrape artifacts, not missing data worth backfilling.
  - **1923 has no winner** (`Not awarded` in every field) — the show didn't name a Best in Show that year. No other year is missing, including WWII, when the show still ran.
  - `Group` is the AKC breed group (Terrier, Sporting, Working, Non-Sporting, Toy, Hound, Herding). Terrier dominates the early decades (47 of 119 awarded winners overall) — Fox Terrier (Wire) alone accounts for 15 wins, mostly pre-1940s.

## `breed_traits.csv`

A static lookup table, one row per distinct `Breed` value in `westminster_winners.csv` (51 rows, exact string match on `Breed` so it joins cleanly — includes the Wikipedia footnote artifacts like `[B]` that appear on a few Cocker Spaniel color varieties). Columns: `Breed, CanonicalBreed, Variety, Group, SizeCategory, WeightRangeLbs, LifespanYears, OriginCountry, HistoricalPurpose`.

- `CanonicalBreed` / `Variety` collapse cosmetic splits in the source data — e.g. `Poodle (Miniature)`, `Poodle (Standard)`, and `Poodle (Toy)` are all `CanonicalBreed=Poodle` with the size as `Variety`; `German Shepherd` and `German Shepherd Dog` (a naming change over time) both map to `German Shepherd Dog`. `Pointer` and `Pointer (German Shorthaired)` are kept as genuinely different breeds (English Pointer vs. German Shorthaired Pointer), not merged.
- `Group` was **pulled directly from `westminster_winners.csv`** (verified one consistent value per breed across all its winning years), not reconstructed from memory — zero fabrication risk on that column. Note `Collie (Rough)` and `Old English Sheepdog` show `Working`, not `Herding` — AKC didn't create a separate Herding group until 1983, so their historical wins are recorded under the group that existed at the time.
- `SizeCategory`, `WeightRangeLbs`, `LifespanYears`, `OriginCountry`, and `HistoricalPurpose` are **compiled from general/well-established AKC breed-standard knowledge, not pulled from a specific citable source**. Treat these as a reasonable starting characterization — verify specifics before relying on them for rigorous analysis, same caveat as `elephant_circus/analysis/city_economic_profile.csv`.

## Sourcing

Wikipedia content is CC BY-SA licensed and the underlying data traces back to Westminster Kennel Club's own published records — no redistribution concern like `elephant_circus/routes/`.

## Ideas for a contextual dataset

- **AKC annual breed registration rankings** (how popular each breed was with the general dog-owning public that year) would let you ask whether a Westminster win moves the needle on a breed's popularity afterward, or whether winners tend to come from already-popular breeds vs. obscure ones. AKC doesn't publish a clean historical download, so this would need scraping from press releases/secondary compilations, with likely spotty coverage before the ~1990s.
- **Show entry counts by year** — investigated and shelved. The Westminster Kennel Club's own ["Show Records"](https://www.westminsterkennelclub.org/event-history/show-records/) page looks like it should have this but its entry-count column is broken/template data (`350/700` repeated identically across 12 different years; `3160/3092` repeated across two different shows at different venues) — not usable without fabricating the gaps. Wikipedia only has two scattered one-off figures. Would need a different primary source to revisit.

# dogs

Best in Show winners of the Westminster Kennel Club Dog Show, 1907–2026.

- `fetch.py` — scrapes the winners table from [Wikipedia's List of Best in Show winners](https://en.wikipedia.org/wiki/List_of_Best_in_Show_winners_of_the_Westminster_Kennel_Club_Dog_Show) (`pandas.read_html`, second table on the page) and writes it to `westminster_winners.csv`. Re-run it to refresh the data for future years.
- `westminster_winners.csv` — 120 rows, one per show year. Columns: `Year, Winner, Image, Breed, Group, Owner, Ref(s)`.
  - `Image` is empty for every row (Wikipedia's image cells don't carry over through `read_html`) and `Ref(s)` holds Wikipedia footnote markers (e.g. `[15]`) — both are scrape artifacts, not missing data worth backfilling.
  - **1923 has no winner** (`Not awarded` in every field) — the show didn't name a Best in Show that year. No other year is missing, including WWII, when the show still ran.
  - `Group` is the AKC breed group (Terrier, Sporting, Working, Non-Sporting, Toy, Hound, Herding). Terrier dominates the early decades (47 of 119 awarded winners overall) — Fox Terrier (Wire) alone accounts for 15 wins, mostly pre-1940s.

## Sourcing

Wikipedia content is CC BY-SA licensed and the underlying data traces back to Westminster Kennel Club's own published records — no redistribution concern like `elephant_circus/routes/`.

## Ideas for a contextual dataset

AKC annual breed registration rankings (how popular each breed was with the general dog-owning public that year) would pair well here — it'd let you ask whether a Westminster win moves the needle on a breed's popularity afterward, or whether winners tend to come from already-popular breeds vs. obscure ones. The catch is that AKC doesn't publish a clean historical download; rankings would likely need to be scraped year-by-year from press releases or secondary compilations, so coverage before ~1990s may be spotty.

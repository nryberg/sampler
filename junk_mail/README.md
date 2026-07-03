# Spam / Promotions Mailbox Sample Dataset

A realistic spam/promotional email dataset for testing tools that read CSV,
Parquet, or DuckDB. Sourced from two real Gmail folder exports from the same
mailbox — `Spam.mbox` (89 messages, all included) and `Category
Promotions.mbox` (16,509 messages, randomly sampled down to 1,000) — merged,
deduped, and normalized into a related, snowflake-shaped table schema.
1,089 emails total.

## Privacy / anonymization

Both source mbox files are real personal mailbox exports and contain real
identifiers throughout — not just the recipient's own name/address, but an
entire family's: a personal domain, several personal and work email
addresses, and first names that show up in marketing addressed to different
family members (e.g. college-admissions mail). None of that appears in the
output tables:

- Every real name and email address tied to this family — across headers,
  subjects, `List-Unsubscribe` URLs, and bodies — is replaced with a fixed
  placeholder identity: `Sample User` / `sample.user@example.com`. This
  includes VERP/bounce-encoded addresses (e.g.
  `bounces+123-name=domain.com@sender.example.com`), which use `=` instead
  of `@` before the real domain and need a wider character class to catch.
- The Gmail label matching the recipient's first name (a personal mail
  filter) is renamed to `Personal`.
- **Messages where the family is the *sender*, not a marketer** (self-forwards,
  replies to personal correspondence — 9 messages found in `Category
  Promotions.mbox`, mislabeled by Gmail) are **excluded from the dataset
  entirely**, not just anonymized. Their bodies contain unpredictable
  third-party PII (quoted personal emails, other people's names and
  details) that a targeted find-and-replace can't safely guarantee to catch.
  Anonymizing headers alone was tried and found insufficient — see the
  `is_self_sent()` filter in `extract.py`.
- Sender information for actual third-party mail (company names, marketing
  domains, subjects, body copy) is left as-is; that's the actual content of
  interest for this dataset and isn't personal to the mailbox owner.

`extract.py` runs a regex substitution pass (`anonymize_text`) over every
extracted field before it's written out, and filters out self-sent messages
before they're ever parsed into a row. The actual identifiers being scrubbed
live in `private_config.py`, a local-only file excluded via `.gitignore` —
the real names/domains never appear in the committed source, only in this
untracked file on the machine that has the source mbox files. `export.py`
re-derives everything from the source mbox files from scratch each run, so
nothing anonymized is cached from an earlier, less-careful pass.

Discovering the full scope of what needed scrubbing took a few passes —
initial patterns only covered the primary recipient's name/domain; later
passes found a second family member's address, two of the mailbox owner's
work-email aliases (which incidentally revealed employers), a first name
used in third-party marketing, and a `List-Unsubscribe` field that was being
decoded but never actually run through the anonymizer. Each was found by
grep-scanning the *final output tables* for residual identifiers after each
pipeline run, not just trusting the code to be correct — worth re-running
that check (see below) after any change to the source data or patterns.

### Re-verifying anonymization after any change

```sh
python3 -c "
import duckdb
pattern = r'(?i)delaney|ryberg|\bnick\w*|\balex\b|\bkerwin\b'
con = duckdb.connect('output/spam_sampler.duckdb')
for name in ['domains','senders','industries','email_types','emails',
             'email_labels','email_bodies','subject_keywords']:
    df = con.execute(f'SELECT * FROM {name}').df()
    for col in df.columns:
        if df[col].dtype == object:
            mask = df[col].astype(str).str.contains(pattern, na=False, regex=True)
            if mask.any():
                print(name, col, mask.sum())
"
```
(A `\bnick\w*` hit on words like "Nickelodeon" is an expected false
positive, not a leak — inspect matches before assuming a real one.)

## Pipeline

```
Spam.mbox                  Category Promotions.mbox
(89 msgs, all kept)        (16,509 msgs)
   │                            │
   │                       lightweight pass: Message-ID + From per message
   │                       → drop self-sent, drop dupes vs Spam.mbox,
   │                       → fixed-seed random sample of 1,000 (seed=42)
   │                            │
   └──────────┬─────────────────┘
              ▼
extract.py        parse each message with Python's `mailbox`/`email` stdlib,
                   decode MIME headers, strip HTML bodies to text, anonymize
                   PII (subject/body/from-fields/list-unsubscribe), pull
                   SPF/DKIM/DMARC results and link counts
   │  (flat one-row-per-email DataFrame, tagged with source_mbox)
   ▼
categorize.py      rule-based classification: sending domain -> industry
                   (keyword-matched against ~90 known brand domains, e.g.
                   "groupon" -> Deals & Coupons); subject/body keyword
                   regex -> email_type, with an industry-based fallback so
                   nothing falls into a catch-all bucket; subject line ->
                   normalized keyword tokens (stopwords removed)
   │
   ▼
build_tables.py    reshape the flat data into 8 related tables (below):
                   dedupe senders/domains into dimension tables, explode
                   multi-valued Gmail labels and subject keywords into
                   bridge tables
   │
   ▼
export.py          write every table to CSV, Parquet, and a DuckDB database
                   (output/csv/, output/parquet/, output/spam_sampler.duckdb)
```

Run the whole thing with:

```sh
python3 export.py
```

Requires `pandas`, `pyarrow`, `duckdb`, and `beautifulsoup4`, plus both
source mbox files and a local `private_config.py` (gitignored, not included
in this repo) defining the real identifiers to scrub — see
`extract.py`/`private_config.py` for the expected `REAL_NAME_PATTERN` /
`REAL_EMAIL_PATTERNS` / `LABEL_RENAMES` shape. The full run takes roughly a
minute, dominated by two passes over the 1.5GB `Category Promotions.mbox`
(one lightweight Message-ID/From scan for dedup+sampling, one full parse of
just the sampled 1,000).

## Table structure

8 tables, organized as a small snowflake schema: `domains` -> `senders` ->
`emails`, with `industries` and `email_types` as lookup dimensions on
`emails`, and `email_labels` / `email_bodies` / `subject_keywords` as
detail/bridge tables keyed by `email_id`.

```
domains ──┬─< senders ──┬─< emails ──┬─< email_labels
          │             │            ├─< email_bodies
industries┼─────────────┼───────────>┤
          │             │            └─< subject_keywords
email_types┴─────────────┴───────────>┘
```

### `domains` (121 rows)
One row per sending domain, with rollup stats.

| column | type | notes |
|---|---|---|
| `domain_id` | int, PK | |
| `domain` | varchar | e.g. `r.groupon.com` |
| `email_count` | int | messages from this domain |
| `sender_count` | int | distinct from-addresses at this domain |
| `first_seen` / `last_seen` | timestamptz | date range observed |

### `senders` (147 rows)
One row per distinct sending address.

| column | type | notes |
|---|---|---|
| `sender_id` | int, PK | |
| `domain_id` | int, FK -> `domains` | |
| `from_email` | varchar | e.g. `shop@poshmark.com` |
| `from_name` | varchar | most common display name used |
| `email_count` | int | |
| `first_seen` / `last_seen` | timestamptz | |

### `industries` (12 rows)
Lookup: broad industry vertical, assigned by keyword-matching the sending
domain against a curated brand list (`Retail & Shopping`, `Deals &
Coupons`, `Food & Delivery`, `Sports & Entertainment`, `Entertainment &
Events`, `Travel & Real Estate`, `Newsletter & Media`, `Software & SaaS`,
`Photo Printing & Retail`, `Community & Religious`, `Legal & Class Action
Notices`, `Other`). See `categorize.py:DOMAIN_INDUSTRY_RULES`.

| column | type |
|---|---|
| `industry_id` | int, PK |
| `industry` | varchar |

### `email_types` (10 rows)
Lookup: content-derived type of pitch (`Promotional`, `Newsletter`, `Content
/ News`, `Product Update`, `Legal Notice`, `Policy Update`, `Event Invite`,
`Community Update`, `Social Notification`, `General / Other`). Assigned by
keyword regex over the subject/body first; anything unmatched falls back to
an industry-appropriate default (e.g. unmatched `Retail & Shopping` ->
`Promotional`) rather than dumping into a generic bucket. See
`categorize.py:EMAIL_TYPE_RULES` / `INDUSTRY_DEFAULT_TYPE`.

| column | type |
|---|---|
| `email_type_id` | int, PK |
| `email_type` | varchar |

### `emails` (1,089 rows)
One row per message — the central fact table. 89 from `Spam.mbox` (all of
it), 1,000 randomly sampled from `Category Promotions.mbox` (of 16,509,
after dropping messages already covered by `Spam.mbox` and self-sent
personal correspondence).

| column | type | notes |
|---|---|---|
| `email_id` | int, PK | |
| `sender_id` | int, FK -> `senders` | |
| `industry_id` | int, FK -> `industries` | |
| `email_type_id` | int, FK -> `email_types` | |
| `source_mbox` | varchar | `Spam.mbox` or `Category Promotions.mbox` |
| `message_id` | varchar | original `Message-ID` header |
| `thread_id` | varchar | Gmail `X-GM-THRID` |
| `to_email` | varchar | anonymized placeholder, same for every row |
| `subject` | varchar | decoded, anonymized |
| `date_utc` | timestamptz | |
| `category` | varchar | Gmail's own `Category Promotions` / `Category Updates` label, kept denormalized for convenience (also present in `email_labels`) |
| `is_archived` / `is_unread` | boolean | denormalized from Gmail labels |
| `content_type` | varchar | MIME type, e.g. `multipart/alternative` |
| `size_bytes` | int | raw message size |
| `has_list_unsubscribe` | boolean | |
| `list_unsubscribe_url` | varchar | decoded and anonymized `List-Unsubscribe` header |
| `spf_result` / `dkim_result` / `dmarc_result` | varchar | parsed from `Authentication-Results` |
| `link_count` | int | `<a href>` count in the HTML body |

### `email_labels` (4,038 rows)
Bridge table: every Gmail label applied to each message (a message can have
several — `Spam`, `Unread`, `Archived`, `Category Promotions`, `Personal`,
`Inbox`, etc). Many-to-many with `emails`.

| column | type |
|---|---|
| `email_id` | int, FK -> `emails` |
| `label` | varchar |

### `email_bodies` (1,089 rows)
The (large) body text, split out from `emails` so the fact table stays
narrow.

| column | type | notes |
|---|---|---|
| `email_id` | int, PK, FK -> `emails` | |
| `body_text` | varchar | HTML stripped to plain text, anonymized, truncated to 2000 chars |
| `body_length` | int | character length of `body_text` |

### `subject_keywords` (5,363 rows)
Bridge table: subject line tokenized into normalized keywords (lowercased,
stopwords removed, 3+ characters) — one row per (email, keyword). Built for
trend analysis, e.g. how marketing keywords ("off", "free", "sale") trend
week over week.

| column | type |
|---|---|
| `email_id` | int, FK -> `emails` |
| `keyword` | varchar |

## Output files

```
output/
├── csv/                  one CSV per table
├── parquet/               one Parquet file per table
└── spam_sampler.duckdb    all 8 tables loaded into one DuckDB file
```

## Example queries

Keyword trend over time (what the `subject_keywords` table is for):

```sql
SELECT date_trunc('week', e.date_utc) AS week, k.keyword, count(*) AS n
FROM subject_keywords k
JOIN emails e USING (email_id)
GROUP BY ALL
ORDER BY week, n DESC;
```

Spam volume and unsubscribe rate by industry:

```sql
SELECT i.industry, count(*) AS n,
       round(avg(e.has_list_unsubscribe::int), 2) AS pct_unsubscribable
FROM emails e
JOIN industries i USING (industry_id)
GROUP BY ALL
ORDER BY n DESC;
```

Email type mix by sender:

```sql
SELECT s.from_email, t.email_type, count(*) AS n
FROM emails e
JOIN senders s USING (sender_id)
JOIN email_types t USING (email_type_id)
GROUP BY ALL
ORDER BY s.from_email, n DESC;
```

Source mbox mix (does the sampled Promotions data look like the Spam data?):

```sql
SELECT source_mbox, i.industry, count(*) AS n
FROM emails e
JOIN industries i USING (industry_id)
GROUP BY ALL
ORDER BY source_mbox, n DESC;
```

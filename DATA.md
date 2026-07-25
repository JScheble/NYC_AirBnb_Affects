# Data Vintage Table

Every listings snapshot used in this project, where it came from, and how it was verified. This exists because one of the core identification problems in this project is survivorship bias in Airbnb listing data (see `audit.md` §2.2) — the fix requires multiple snapshots taken *at* different points in time, not one snapshot reconstructed retroactively. Precise provenance matters more here than in a typical project.

## Airbnb listings snapshots

| Snapshot date | Source | Rows | Role in analysis |
|---|---|---|---|
| 2019-07-08 | [dgomonov/new-york-city-airbnb-open-data](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data) (Kaggle) | 48,895 | Pre-COVID, pre-adoption dose baseline |
| 2020-01-03/06 | Inside Airbnb detailed-listings format, presumed official (see note below) | 51,361 | Immediate pre-COVID trajectory point 1 of 3 |
| 2020-02-12/13 | Inside Airbnb detailed-listings format, presumed official (see note below) | 51,097 | Immediate pre-COVID trajectory point 2 of 3 |
| 2020-03-13/15 | Inside Airbnb detailed-listings format, presumed official (see note below) | 50,796 | Last pre-lockdown trajectory point (NYC's stay-at-home order was 2020-03-22) |
| 2022-06-03 | [dominoweir/inside-airbnb-nyc] https://www.kaggle.com/datasets/dominoweir/inside-airbnb-nyc (Kaggle) | 37,410 | Near-adoption anticipation-window check (5 months after LL18 adopted); paired with `reviews_2022.csv` |
| 2023-03 | [godofoutcasts/new-york-city-airbnb-2023-public-data](https://www.kaggle.com/datasets/godofoutcasts/new-york-city-airbnb-2023-public-data) (Kaggle) | 42,931 | Pre-enforcement dose baseline (anticipation window) |
| 2024-01 | [vrindakallu/new-york-dataset](https://www.kaggle.com/datasets/vrindakallu/new-york-dataset) (Kaggle) | 20,758 | Immediate post-enforcement snapshot (first-stage) |
| 2025-01 | [an1005/airbnb-new-york-listings](https://www.kaggle.com/datasets/an1005/airbnb-new-york-listings) (Kaggle) | 37,784 | Settled post-enforcement snapshot (first-stage) |
| 2025-12-04/11 | Inside Airbnb, official (`scrape_id 20251204025441`) | 36,261 | Post-enforcement baseline; paired with `reviews_2025.csv` |
| 2026-06-14/23 | Inside Airbnb, official (`scrape_id 20260614073253`) | 30,259 | Most recent post-enforcement snapshot; extends the first-stage panel 6 months past 2025-12; paired with `reviews_2026.csv` |

LL18 timeline for reference: adopted 2022-01-09; registration portal opened ~2023-03; Airbnb's lawsuit dismissed 2023-08-09; enforcement began 2023-09-05.

### The three 2020 files: split from a mislabeled multi-month bundle, one redundant file dropped

Two files were added under placeholder names `2021_test1.csv` and `2021_test2.csv`. Neither was actually 2021 data:

- **`2021_test1.csv`** (584 MB) turned out to be **three different Inside Airbnb monthly "detailed listings" scrapes concatenated into one file** — distinguishable by three distinct `scrape_id`/`last_scraped` clusters: 2020-01-03→06, 2020-02-12→13, and 2020-03-13→15 (153,254 rows total, ~51k per month). Using it as one snapshot would have triple-counted most listings. It was split by `scrape_id` into `listings_jan_2020.csv`, `listings_feb_2020.csv`, and `listings_mar_2020.csv` (trimmed to the same column set used elsewhere in this table), each independently verified with 0% id corruption and 0 date-consistency violations. The original combined file was deleted after splitting. Provenance is *inferred, not confirmed*: the file carries Inside Airbnb's full 106-column detailed-listings schema (including genuine per-row `scrape_id`/`last_scraped`, unlike the Kaggle-simplified files) and shows zero id corruption, which is consistent with an unmangled direct pull — but unlike the 2025-12/2026-06 files, no explicit source confirmation was given, so treat as presumed-official rather than verified-official.
- **`2021_test2.csv`** (65 MB) was **100% redundant** — all 30,179 of its ids matched `listings_jul_2019.csv` exactly, meaning it's the "detailed" column-format companion to the same July 2019 scrape already in the table, not a new time point. It also carried its own corruption: `host_since` had been converted to raw Excel serial-date integers (e.g. `39698`) — the same Kaggle/Excel mangling pattern documented below, just hitting a date column instead of `id`. Deleted; added no coverage the project didn't already have.

The three 2020 files meaningfully shrink what was previously the panel's largest blind spot — the 2019-07 → 2022-06 gap spanned 35 months and covered the entire COVID crash/rebound cycle and LL18's actual adoption with zero direct observations in between (see `audit.md` §2.1 on the COVID pre-trend). Real listing counts at Jan/Feb/Mar 2020 now anchor the immediate pre-COVID trajectory instead of leaving it entirely to inference.

### Correction: `listings_jun_2021.csv` / `reviews_2021.csv` were mislabeled — actually June 2022

Both files were originally named for June 2021. The date-consistency check below (the same one applied to every other file) caught the mismatch: `last_review` values cluster heavily at 2022-05-30 through 2022-06-03 — hundreds of rows per day right at the tail — which is the same "genuine scrape lands at month-start" signature used to validate every other snapshot's true date, just pointing to June 2022 instead. The paired reviews file's own max date (2022-06-03) matches exactly, and the two files are a clean 100% `id`/`listing_id` match against each other, confirming they're a genuine same-scrape pair — just one year off from their original filenames. Both files were renamed (`listings_jun_2022.csv`, `reviews_2022.csv`) to match reality; no data was altered, only filenames.

### The official / presumed-official snapshots needed no Kaggle-style verification

2025-12 and 2026-06 were pulled directly from Inside Airbnb, not re-hosted by a third party, so each carries Inside Airbnb's own `scrape_id`/`last_scraped` fields — self-attested provenance that the four Kaggle-sourced files lack. The three 2020 files are presumed-official on schema/corruption evidence (see split note above) but weren't explicitly source-confirmed. That's why only the four confirmed-Kaggle files go through the full three-check verification process below; the rest are trusted on their scrape metadata and corruption-check evidence. (2022-06's *listings* file is Kaggle-sourced and goes through the checks; its *reviews* file has no independent way to verify beyond the id-match and date-clustering evidence above.)

### Known issue: `id` column corruption in three of the four confirmed-Kaggle files

The 2023-03, 2024-01, and 2025-01 files were re-hosted on Kaggle by third parties, not downloaded directly from Inside Airbnb. At some point in that re-hosting, each file passed through a tool (almost certainly Excel) that silently converted large integer `id` values to truncated scientific notation (e.g. `9.68982E+17` instead of the true 18-digit id) on save. This is irreversible — the original id cannot be recovered from the truncated value. The 2022-06 file (also Kaggle-sourced) and the three 2020 files do **not** show this corruption — 0% affected on all four.

| Snapshot | Rows with corrupted `id` |
|---|---|
| 2020-01 | 0 / 51,361 (0%) |
| 2020-02 | 0 / 51,097 (0%) |
| 2020-03 | 0 / 50,796 (0%) |
| 2022-06 | 0 / 37,410 (0%) |
| 2023-03 | 13,333 / 42,931 (31%) |
| 2024-01 | 8,046 / 20,758 (39%) |
| 2025-01 | 16,470 / 37,784 (44%) |

**Consequence:** the three corrupted files cannot be used for listing-level joins (matching a specific listing across snapshots, or to a reviews file by `listing_id`). `latitude`, `longitude`, `host_id`, `room_type`, and all other fields are unaffected. **All zip-level aggregation from these files is done via spatial join on lat/long and row counts, not `id`-based counts**, which sidesteps the corruption entirely.

### Verification performed

Reproducible in [`verify_snapshots.py`](verify_snapshots.py) — run `python verify_snapshots.py` (needs the pandas/numpy interpreter; see the note at the top of that file if your default `python` lacks pandas). Previously these checks were run ad hoc in a Claude Code session and only the resulting numbers were written here; the script closes that reproducibility gap and now covers all ten listings snapshots and all three review files.

1. **Schema check** — all four confirmed-Kaggle listings files match Inside Airbnb's standard "summary listings" column format (matches `dgomonov`'s 2019 file); the three 2020 files match Inside Airbnb's full detailed-listings format.
2. **Date-consistency check** — across all ten files, zero rows have a `last_review` date after the file's claimed month, and each file's maximum `last_review` lands on or just before its own scrape date (2019-07-08, 2020-01-04, 2020-02-13, 2020-03-14, 2022-06-03, 2023-03-06, 2024-01-05, 2025-01-02, 2025-12-08, 2026-06-22 — the last matching the 2026-06-14→23 `last_scraped` range exactly) — consistent with a genuine scrape at the claimed time, not a fabricated or backfilled file. This is the same check that caught the 2021→2022 mislabeling above.
3. **Cross-snapshot continuity check** — using only the non-corrupted ids across all ten snapshots, 46,114 individual listings were tracked across at least 4 of the 10 (2019→2026). Review counts should only increase over a listing's life; 92.6% are perfectly monotonic, and the remaining share show a median single-step dip of just 1 review (consistent with normal Airbnb review removals, not data corruption) — only 21 of 3,575 dips exceed 20 reviews.
4. **Review↔listing crosswalk match rate** — each review file's `listing_id`s matched against its own paired listings file: `reviews_2022.csv` vs. `listings_jun_2022.csv` 100.0% (29,461/29,461), `reviews_2025.csv` vs. `listings_dec_2025.csv` 100.0% (24,912/24,912), `reviews_2026.csv` vs. `listings_jun_2026.csv` 98.9% (21,700/21,939, the gap being listings delisted between the two scrapes).

None of this proves authenticity with certainty for the Kaggle-sourced or presumed-official files (no confirmed `scrape_id` to check against Inside Airbnb's own records for the fully-unconfirmed ones), but independent checks landing exactly where a genuine scrape should is strong circumstantial evidence, and is the most verification possible without paying for Inside Airbnb's official archive. 2025-12 and 2026-06 pass the same date-consistency and continuity checks trivially, as expected from official-source data.

## Review-level data: three independent scrapes, unioned

Unlike the listings snapshots (each a self-contained census), the three review files are combined into one dataset for analysis, because each is limited to whatever listings existed at its own scrape date and therefore misses listings the others catch.

| File | Source | Coverage | Paired listings file |
|---|---|---|---|
| `reviews_2022.csv` | Kaggle (re-hosted; see mislabeling correction above) | Review-level, 2009-04-23 to 2022-06-03, for the 29,461 listings that survived to the Jun-2022 scrape | `listings_jun_2022.csv` |
| `reviews_2025.csv` | Inside Airbnb, official (same 2025-12 scrape) | Review-level, 2009-05-25 to 2025-12-08, for the 24,912 listings that survived to the Dec-2025 scrape | `listings_dec_2025.csv` |
| `reviews_2026.csv` | Inside Airbnb, official (same 2026-06 scrape) | Review-level, 2009-05-25 to 2026-06-22, for the 21,939 listings that survived to the Jun-2026 scrape | `listings_jun_2026.csv` |

**Why union instead of using one:** each review file only knows about listings that hadn't yet been delisted as of its own scrape — 15,224 listing_ids in `reviews_2022.csv` never appear in the other two, precisely because most of them were delisted before Dec 2025 (see `audit.md` §2.2 for why this survivorship pattern matters). Concatenating all three, deduplicated on `(listing_id, date)`, raises the review-bearing listing universe from 26,954 (just the two most recent files) to 42,178.

**Zip attribution:** each review row is crosswalked to a zip code using *its own paired listings file* (not a newer or older one) — a listing's `listing_id` is only guaranteed to appear in the listings file scraped at the same time as its reviews. Using the union of these three paired listings files covers 42,086 of the 42,178 union listing_ids (99.8%, "review crosswalk check" above); the remaining 92 existed only in the gaps between their review scrape and its paired listings snapshot and aren't attributable via any of the three paired files.

**Data-quality note:** even for the 19,897 listing_ids present in both `reviews_2025.csv` and `reviews_2026.csv`, roughly 10% of individual `(listing_id, date)` review rows differ between the two scrapes — most likely Airbnb review removals/edits in the 6-month gap, not corruption. Deduplicated concatenation handles this: a review survives in the combined dataset if it appears in *either* scrape.

## Other data

| File | Source | Coverage |
|---|---|---|
| `Zip_zori_uc_sfrcondomfr_sm_month.csv` | Zillow Observed Rent Index | Zip-month, 2015–2025 |
| `ACSDP5Y2023.DP04-Data.csv` | American Community Survey, 5-year estimates | Housing unit counts by zip |
| `nyc_zip_geo.geojson` | NYC zip code boundary polygons | Used for all spatial joins |

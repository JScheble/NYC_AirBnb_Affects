# Data Vintage Table

Every listings snapshot used in this project, where it came from, and how it was verified. This exists because one of the core identification problems in this project is survivorship bias in Airbnb listing data (see `audit.md` §2.2) — the fix requires multiple snapshots taken *at* different points in time, not one snapshot reconstructed retroactively. Precise provenance matters more here than in a typical project.

## Airbnb listings snapshots

| Snapshot date | Source | Rows | Role in analysis |
|---|---|---|---|
| 2019-07-08 | [dgomonov/new-york-city-airbnb-open-data](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data) (Kaggle) | 48,895 | Pre-COVID, pre-adoption dose baseline |
| 2023-03 | [godofoutcasts/new-york-city-airbnb-2023-public-data](https://www.kaggle.com/datasets/godofoutcasts/new-york-city-airbnb-2023-public-data) (Kaggle) | 42,931 | Pre-enforcement dose baseline (anticipation window) |
| 2024-01 | [vrindakallu/new-york-dataset](https://www.kaggle.com/datasets/vrindakallu/new-york-dataset) (Kaggle) | 20,758 | Immediate post-enforcement snapshot (first-stage) |
| 2025-01 | [an1005/airbnb-new-york-listings](https://www.kaggle.com/datasets/an1005/airbnb-new-york-listings) (Kaggle) | 37,784 | Settled post-enforcement snapshot (first-stage) |
| 2025-12-04/11 | Inside Airbnb, official (`scrape_id 20251204025441`) | 36,261 | Current baseline; source of `reviews.csv` review-level history |

LL18 timeline for reference: adopted 2022-01-09; registration portal opened ~2023-03; Airbnb's lawsuit dismissed 2023-08-09; enforcement began 2023-09-05.

### Known issue: `id` column corruption in the three Kaggle mid-period files

The 2023-03, 2024-01, and 2025-01 files were re-hosted on Kaggle by third parties, not downloaded directly from Inside Airbnb. At some point in that re-hosting, each file passed through a tool (almost certainly Excel) that silently converted large integer `id` values to truncated scientific notation (e.g. `9.68982E+17` instead of the true 18-digit id) on save. This is irreversible — the original id cannot be recovered from the truncated value.

| Snapshot | Rows with corrupted `id` |
|---|---|
| 2023-03 | 13,333 / 42,931 (31%) |
| 2024-01 | 8,046 / 20,758 (39%) |
| 2025-01 | 16,470 / 37,784 (44%) |

**Consequence:** these three files cannot be used for listing-level joins (matching a specific listing across snapshots, or to `reviews.csv` by `listing_id`). `latitude`, `longitude`, `host_id`, `room_type`, and all other fields are unaffected. **All zip-level aggregation from these files is done via spatial join on lat/long and row counts, not `id`-based counts**, which sidesteps the corruption entirely.

### Verification performed (since none of the three Kaggle files carry Inside Airbnb's own `scrape_id`/`last_scraped` fields)

1. **Schema check** — all three match Inside Airbnb's standard "summary listings" column format (matches `dgomonov`'s 2019 file).
2. **Date-consistency check** — in each file, zero rows have a `last_review` date after the file's claimed month (0 violations across 101,473 rows total), and each file's maximum `last_review` lands in the first week of its claimed month (2023-03-06, 2024-01-05, 2025-01-02) — consistent with a genuine early-month scrape.
3. **Cross-snapshot continuity check** — using only the non-corrupted ids, 15,821 individual listings were tracked across at least 4 of the 5 snapshots (2019→2025). Review counts should only increase over a listing's life; 84% are perfectly monotonic, and the remaining 16% show a median single-step dip of just 1 review (consistent with normal Airbnb review removals, not data corruption) — only 9 of 2,626 dips exceed 20 reviews.

None of this proves authenticity with certainty (no `scrape_id` to check against Inside Airbnb's own records), but three independent checks landing exactly where a genuine scrape should is strong circumstantial evidence, and is the most verification possible without paying for Inside Airbnb's official archive.

## Other data

| File | Source | Coverage |
|---|---|---|
| `reviews.csv` | Inside Airbnb, official (same 2025-12 scrape) | Review-level, 2009-05-25 to 2025-12-08, but only for the 24,912 listings that survived to the Dec-2025 scrape (see `audit.md` §2.2 for the survivorship implications) |
| `Zip_zori_uc_sfrcondomfr_sm_month.csv` | Zillow Observed Rent Index | Zip-month, 2015–2025 |
| `ACSDP5Y2023.DP04-Data.csv` | American Community Survey, 5-year estimates | Housing unit counts by zip |
| `nyc_zip_geo.geojson` | NYC zip code boundary polygons | Used for all spatial joins |

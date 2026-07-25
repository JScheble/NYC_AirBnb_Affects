"""
Reproduces the provenance checks reported in DATA.md for every listings and
reviews snapshot: id-corruption count, last_review date-consistency,
cross-snapshot listing continuity, and review<->listing crosswalk match rates.

Run: python verify_snapshots.py
(needs the pandas/numpy interpreter — see DATA.md environment note if `python` on
PATH lacks pandas)

Note: listings_jun_2021.csv / reviews_2021.csv were renamed to _jun_2022 /
_2022 after this script's date-consistency check showed their last_review
dates cluster at 2022-06-01..03, not June 2021 -- the files were mislabeled,
not the data itself.
"""
import re

import pandas as pd

SNAPSHOTS = {
    "2019-07": {"file": "listings_jul_2019.csv", "claimed_month": "2019-07", "official": True},
    "2020-01": {"file": "listings_jan_2020.csv", "claimed_month": "2020-01", "official": True},
    "2020-02": {"file": "listings_feb_2020.csv", "claimed_month": "2020-02", "official": True},
    "2020-03": {"file": "listings_mar_2020.csv", "claimed_month": "2020-03", "official": True},
    "2022-06": {"file": "listings_jun_2022.csv", "claimed_month": "2022-06", "official": False},
    "2023-03": {"file": "listings_mar_2023.csv", "claimed_month": "2023-03", "official": False},
    "2024-01": {"file": "listings_jan_2024.csv", "claimed_month": "2024-01", "official": False},
    "2025-01": {"file": "listings_jan_2025.csv", "claimed_month": "2025-01", "official": False},
    "2025-12": {"file": "listings_dec_2025.csv", "claimed_month": "2025-12", "official": True},
    "2026-06": {"file": "listings_jun_2026.csv", "claimed_month": "2026-06", "official": True},
}

# Each review file was scraped alongside exactly one listings snapshot, so its
# listing_id space matches that one file far better than any other (see
# review_crosswalk_check). listings_jul_2019/mar_2023/jan_2024/jan_2025 have
# no review-file companion.
REVIEW_PAIRS = {
    "2022-06": "reviews_2022.csv",
    "2025-12": "reviews_2025.csv",
    "2026-06": "reviews_2026.csv",
}

ID_RE = re.compile(r"^\d+$")


def load(meta):
    cols = ["id", "last_review", "number_of_reviews"]
    df = pd.read_csv(meta["file"], usecols=lambda c: c in cols, dtype={"id": str})
    df["id"] = df["id"].fillna("")
    return df


def corruption_check(dfs):
    print("=== id corruption check ===")
    for name, df in dfs.items():
        corrupted = ~df["id"].str.match(ID_RE)
        n = int(corrupted.sum())
        print(f"{name}: {n}/{len(df)} corrupted ({n / len(df):.1%})")


def date_consistency_check(dfs):
    print("\n=== last_review date-consistency check ===")
    for name, df in dfs.items():
        month_end = pd.Period(SNAPSHOTS[name]["claimed_month"], freq="M").end_time
        lr = pd.to_datetime(df["last_review"], errors="coerce")
        violations = int((lr > month_end).sum())
        print(f"{name}: {violations} rows with last_review after {month_end.date()}; max last_review = {lr.max().date()}")


def continuity_check(dfs):
    print("\n=== cross-snapshot continuity check (clean ids only) ===")
    order = list(dfs.keys())
    frames = []
    for name, df in dfs.items():
        clean = df[df["id"].str.match(ID_RE)].copy()
        clean["number_of_reviews"] = pd.to_numeric(clean["number_of_reviews"], errors="coerce")
        clean["snapshot"] = name
        frames.append(clean[["id", "snapshot", "number_of_reviews"]])
    long = pd.concat(frames, ignore_index=True)
    wide = long.pivot_table(index="id", columns="snapshot", values="number_of_reviews", aggfunc="first")
    wide = wide[order]

    present_count = wide.notna().sum(axis=1)
    threshold = (len(order) * 4) // 5 if len(order) >= 5 else 4
    tracked = wide[present_count >= 4]
    print(f"{len(tracked)} listings present in >=4 of {len(order)} snapshots")

    def is_monotonic(row):
        vals = row.dropna().values
        return all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))

    mono = tracked.apply(is_monotonic, axis=1)
    print(f"{mono.mean():.1%} perfectly monotonic")

    dips = []
    for _, row in tracked[~mono].iterrows():
        vals = row.dropna().values
        for i in range(len(vals) - 1):
            if vals[i + 1] < vals[i]:
                dips.append(vals[i] - vals[i + 1])
    if dips:
        dip_s = pd.Series(dips)
        print(
            f"{len(dip_s)} single-step dips, median size {dip_s.median()}, "
            f"{(dip_s > 20).sum()} exceed 20 reviews"
        )


def review_crosswalk_check():
    print("\n=== review <-> listing crosswalk check ===")
    listing_id_sets = {}
    for snap in REVIEW_PAIRS:
        lst = pd.read_csv(SNAPSHOTS[snap]["file"], usecols=["id"], dtype={"id": str})
        listing_id_sets[snap] = set(lst["id"])

    review_id_sets = {}
    for snap, path in REVIEW_PAIRS.items():
        rev = pd.read_csv(path, usecols=["listing_id"], dtype={"listing_id": str})
        ids = set(rev["listing_id"].unique())
        review_id_sets[snap] = ids
        match = ids & listing_id_sets[snap]
        print(f"{path} vs {SNAPSHOTS[snap]['file']}: {len(match):,}/{len(ids):,} matched ({len(match) / len(ids):.1%})")

    all_review_ids = set().union(*review_id_sets.values())
    all_paired_listing_ids = set().union(*listing_id_sets.values())
    covered = all_review_ids & all_paired_listing_ids
    print(f"\nunion of all 3 review files: {len(all_review_ids):,} unique listing_ids")
    print(
        f"covered by union of the 3 own-scrape-paired listings files: "
        f"{len(covered):,} ({len(covered) / len(all_review_ids):.1%})"
    )


if __name__ == "__main__":
    dfs = {name: load(meta) for name, meta in SNAPSHOTS.items()}
    for name, df in dfs.items():
        print(f"{name}: {len(df)} rows loaded from {SNAPSHOTS[name]['file']}")
    print()
    corruption_check(dfs)
    date_consistency_check(dfs)
    continuity_check(dfs)
    review_crosswalk_check()

# Do Today — Presentability Pass (2026-07-02)

**Goal for tonight:** make the repo safe to show a stranger. No new analysis, no re-estimation —
that's the next phase (audit E1–E5). Tonight is purely about making sure nothing in the repo
*asserts* the biased result as a finding. The test for every edit: "if an economist reads only
this sentence, does it make me look like I believed the trend-model coefficient?"

---

## Step 0 — Restore the notebook before editing anything (5 min)

The working copy of `Airbnb_Law_Effect.ipynb` was re-run against a kernel **without pandas**:
cell 1 now contains a `ModuleNotFoundError` and several figure outputs were stripped on save.
The only real content change vs. the last commit is the `** UNDER REVISION **` marker in the
abstract — which tonight's rewrite supersedes anyway.

- [ ] `git checkout -- Airbnb_Law_Effect.ipynb` to get the fully-rendered version back
- [ ] Tonight, edit **markdown cells only** — that never touches stored outputs, so the notebook
      stays fully rendered without needing a working kernel
- [ ] Fix the kernel selection separately (pandas is installed somewhere — `test.ipynb` was the
      probe; delete it once the kernel works)
- [ ] Any wording that lives in **code** (figure titles, axis labels) goes on the "queued for
      re-run" list at the bottom, *not* tonight — editing code without re-running creates a
      source/output mismatch, which is its own red flag

---

## 1. Rewrite the three front-door claims around the honest arc (~1.5 h)

The three places an outsider actually reads: **README "Key Findings"**, the **abstract**
(cell ~2), and the **conclusion** (cell 115). All three currently present the trend-corrected
−0.5% (p<0.001) as the settled result. Per audit §6, the README is the single most dangerous
artifact in the repo. Rewrite all three to the same arc:

> Baseline DiD: precise null → the comparison was never valid (COVID rebound + differential
> gentrification) → the common "fix" (group-specific trends) manufactures a large effect, and
> here's how it fools you → what the data can honestly support is still open (revision underway).

Specific edits:

- [ ] **Lead with the correct baseline number.** The clustered baseline is coef −0.0004,
      SE 0.0013, **p = 0.75** — a precise-ish zero. The p=0.23 in the abstract is the
      *unclustered* p-value; don't cite it (the notebook itself argues clustering is right).
- [ ] **Demote the trend model everywhere.** It stays in the paper as a cautionary
      specification, described in language like: "adding a group-specific linear trend produces
      a large, significant estimate (−0.5%/unit, p<0.001) — but multiplies the coefficient 12×
      while *shrinking* the SE, the classic signature of a control absorbing the outcome
      dynamics rather than cleaning the comparison. We treat it as an upper bound, not an
      estimate." Never present it standalone.
- [ ] **Name COVID once, plainly** (currently "pandemic" appears exactly once in 116 cells):
      enforcement (Sept 2023) landed exactly as the post-COVID rent rebound in high-Airbnb zips
      was cresting; both "the rebound plateaued" and "the law suppressed rents" predict the same
      data, and no within-city estimator fully separates them. This is the most important
      limitations sentence in the project.
- [ ] **Fix the placebo language.** Conclusion says the model was "confirmed with a placebo
      test (p=0.077)" — a fail-to-reject can't confirm anything, and 0.077 is significant at
      the 10% level in the tables' own starring. Rephrase as "fails to reject" + note the
      placebo window is two-thirds COVID. Same pass on cell 85's "97% confident" sentence —
      that is not what a p-value means, and it's the kind of line that ends a cold-email read.
- [ ] **Dollar figures:** cut the $50 / $300/month claims from the README entirely. Where they
      survive in the notebook, label them as "implied by the trend specification, which we do
      not endorse" — or attach the 95% CI (≈ −0.34% to −0.65%/unit → Williamsburg ≈ $195–$390)
      *and* the conditionality caveat.
- [ ] Suggested README "Key Findings" replacement (adjust voice as needed):
      - A baseline two-way fixed-effects model finds **no significant rent effect** of LL18
        across 82 NYC zips (clustered p = 0.75).
      - The identifying assumption (parallel trends across Airbnb-intensity levels) **fails
        visibly**, driven by the COVID rent crash and rebound in high-intensity neighborhoods.
      - A group-specific linear-trend "correction" yields a large significant effect (−0.5% per
        intensity unit) but is **shown to be an artifact** of fitting a straight line through
        the crash-rebound cycle; we present it as a bound, not a finding.
      - Revision in progress: rebuilt treatment dose from pre-enforcement snapshots (see
        `DATA.md`), corrected event study, and Rambachan–Roth honest-bounds sensitivity analysis.

---

## 2. Terminology, label, and typo sweep (~45 min, markdown cells + README only)

Small individually, but a dozen of them reads as carelessness that a reader will extrapolate
to the code. Exact strings to hunt (all verified still present):

- [ ] **ZRI → ZORI** everywhere: the outcome file is the Zillow *Observed* Rent Index
      (`Zip_zori_uc_sfrcondomfr_sm_month.csv`); "ZRI" is a different, discontinued product.
      First data fact a referee checks. (Notebook methodology cell + README.)
- [ ] **Cell 81 group mixup:** treatment/control are described as "high-rent" vs. "low-rent"
      zips — treatment intensity is *Airbnb density*, not rent level. Also fix "you can clearly
      the difference" in the same cell.
- [ ] **"Enacted" vs. "enforced":** adopted Jan 9 2022; enforced Sept 5 2023. Fix in prose
      tonight; the figure vertical-line labels ("Law Enacted") are code → queued list.
- [ ] **README corrections:** "2009 to 2025" → rent panel 2015–2025, regression sample
      2019–2025 (reviews data reaches to 2009 but no causal analysis uses pre-2015); drop
      `sqlite3` from the libraries list; add a one-line link to `DATA.md` (it's genuinely
      strong — data provenance + the survivorship problem caught and documented — surface it).
- [ ] **Typos:** "formate" (cell 16), "greeen" (cell 108 code comment — text-only, safe),
      "an maximum" (cell 20), "Summer 23'" → "Summer '23", inconsistent I/we.
- [ ] **Word policing:** "significant" → "statistically significant" or a magnitude, every
      occurrence.

---

## 3. Repo hygiene + re-render (~30 min)

- [ ] Delete `nyc_airbnb.db` (0 bytes) and `test.ipynb`
- [ ] Create `requirements.txt` with pinned versions (pandas, numpy, statsmodels, geopandas,
      matplotlib, stargazer — from the working env once the kernel is fixed)
- [ ] Re-render `Airbnb_Law_Effect.html` via **nbconvert without execution**
      (`jupyter nbconvert --to html Airbnb_Law_Effect.ipynb`) so the HTML picks up tonight's
      markdown edits while keeping the restored outputs. The current HTML still shows the old
      victory-lap conclusion — it must not outlive tonight.
- [ ] Commit with a message that frames this honestly (e.g. "Reframe findings around baseline
      null; demote trend-model estimate pending revision")

---

## Queued for the re-run / rework phase (do NOT touch tonight)

Code changes that alter outputs — they happen together with the E1–E5 rework so source and
outputs never diverge:

- Figure labels: "Law Enacted" → "Law Enforced (Sept 2023)" (cells 16, 108); event-study y-axis
  ("% Difference…Treatment and Control zips" → log points per intensity unit, no discrete groups)
- Remove unused imports (`sqlite3`, `sys`, `re`)
- Event-study endpoint binning (audit §2.3), dose rebuild from the DATA.md snapshots (§2.2),
  first-stage event study (§2.4), HonestDiD (§3.2) — the deep rework, next session

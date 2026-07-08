# Referee Audit: *Does Restricting Airbnb Lower Rents? Estimating Effects from NYC's Local Law 18*

**Auditor role:** senior applied micro-econometrician, acting as referee and mentor.
**Files reviewed:** `Airbnb_Law_Effect.ipynb` (all 116 cells, including the embedded regression tables), `README.md`, `spatial_helpers.py`, plus a read-only inspection of the raw data files to verify their vintage. Cell numbers below refer to the notebook's JSON cell order (0–115).
**Calibration:** the bar here is "a working economist reads this and concludes the author is honest, competent, and self-aware" — resume / cold-email / pre-doc level, not a dissertation. Everything below is judged against that bar.

---

## 0. TL;DR verdict

The project has real strengths: a genuinely interesting and unanswered policy question, a sensible panel design, correct instincts about clustering, an event study, a placebo test, and — most importantly — you *caught your own identification problem* instead of shipping the significant number uncritically. That instinct is the most valuable thing in the repo. Protect it.

But the current headline result (−0.5% per intensity unit, p<0.001, ~$50 median / ~$300 max monthly savings) is **not credible and should not be the headline**. Your own diagnosis of why is essentially correct, and I'll sharpen it below. The two biggest problems, in order:

1. **COVID is the elephant in the room, and the notebook never addresses it.** The word "pandemic" appears exactly once (cell 20, a passing comment on a descriptive table). Yet the panel runs 2019–2025: the entire "differential pre-trend" you found is, to a first approximation, the COVID rent crash and rebound, which hit high-Airbnb zips (Manhattan, North Brooklyn) hardest. The linear-trend "fix" fits a straight line through a crash-and-rebound cycle and labels the post-2023 deviation from that line "the law." The 12× coefficient jump is the signature of exactly that.
2. **The treatment dose is measured with survivorship bias.** Your `listings.csv` is a December 2025 Inside Airbnb snapshot (scrape_id 20251204025441). Inside Airbnb files only contain listings visible at (or near) scrape time — so your "active listings in 2022" counts only listings that *survived to Dec 2025*. The ban removed listings, and removed them most where it bit hardest, so the dose is undercounted precisely in the most-treated zips. Your validation against AirROI (cells 36–37) validates the wrong quantity: it checks the 2025 count, not the 2022 count you actually use.

Your proposed path forward (event study as centerpiece, Honest DiD bounds, synthetic control cross-check, demote the trend model) is the right family of moves and I endorse it with modifications — the most important being: **fix the event study's mechanical errors and rebuild the dose variable first**, because Honest DiD and synthetic DiD applied to the current event study would be rigor layered on top of broken inputs.

**Tooling call: stay in Python for everything except one ~30-line R script for the canonical `HonestDiD` package.** Reasoning in §4.

A credible "not robustly identified, and here is exactly why" paper from this project is *more* impressive for pre-doc purposes than the current significant result. Working economists smell a group-specific-trend rescue from a mile away; they will respect the autopsy far more than the miracle.

---

## 1. Corrections to your own account (verify-against-the-notebook items)

Before the main findings — places where your summary to me, or the notebook's narrative, doesn't match what the code actually shows:

- **"Baseline TWFE: null (p≈0.23)."** Not quite. The unclustered p-value is 0.2018; with clustering by zip — which you correctly argue is the right choice in cell 69 — the baseline p-value is **0.7532** (cell 68 table: coef −0.0004, clustered SE 0.0013). The honest statement is that the baseline estimate is a *precise-ish zero*, not a marginal one. This matters for framing: the design isn't "tantalizingly close to significance"; it's flatly null until the trend term is added.
- **"The pre-trend was nonlinear (widened then decelerated)."** Correct per the event-study figure, but the notebook's own text (cell 81) garbles the groups: it calls the treatment group "high-rent zips" and the control "low-rent zips." Treatment intensity is *Airbnb density*, not rent level. An economist reading cell 81 will wince.
- **The re-placebo "pass" (cell 98–99).** p = 0.077 is a marginal fail-to-reject, on a sample (2019–2021) that is two-thirds COVID. The conclusion (cell 115) then cites this as the model being "confirmed with a placebo test (p=0.077)" — a failure to reject cannot confirm anything, and 0.077 would be starred as significant at the 10% level in your own tables' notation (`* p<0.1`). This sentence, as written, is the kind of thing that ends a cold-email read.
- **Cell 85's p-value interpretation:** "our placebo test was 97% confident our fake law had a .33% change" — that is not what p = 0.0265 means (a p-value is the probability of data this extreme *if there were no effect*, not the probability the effect is real). Economists are allergic to this phrasing.
- **README** says the panel covers "2009 to 2025"; the regression sample is 2019–2025 (cell 56), and the rent data starts in 2015 (cell 8). The reviews *data* reaches back to ~2009, but nothing in the causal analysis uses pre-2015 data.
- **"Enacted" vs "enforced."** The intro (cell 28) correctly says adopted January 9, 2022, enforced September 5, 2023. But the figures (cells 16, 108) label the September 2023 line "Law Enacted," and the README says "the September 2023 ban." The 20-month gap between adoption and enforcement is not pedantry — it's an anticipation window that matters for your design (see §2.4).
- **The outcome index is ZORI, not ZRI.** The file is `Zip_zori_uc_sfrcondomfr_sm_month.csv` — the Zillow *Observed* Rent Index (smoothed, single-family+condo, not seasonally adjusted). The notebook and README call it the "Zillow Rent Index (ZRI)," a different, discontinued product. Small, but it's the first data fact a referee checks.

---

## 2. What's wrong, ranked by severity

### Severity 1 — identification (these decide whether the project has a result at all)

#### 2.1 COVID is the confounder, and the analysis never engages with it

*Plain-language gloss — parallel trends:* a difference-in-differences design assumes that, absent the law, high-dose and low-dose zips' rents would have moved in parallel; the control group's path stands in for the treated group's unobservable "what if."

Your event study (cells 77–81) covers September 2021 to September 2024. The pre-period of that window is precisely the COVID *rebound*: Manhattan and North Brooklyn rents collapsed ~10–25% in 2020–21 and then snapped back violently through 2022–23, far more than outer-borough zips did. High-Airbnb-intensity zips are, almost by construction, the tourist-dense, transit-rich, young-renter zips that experienced the deepest crash and sharpest rebound. So:

- The "differential pre-trend" (high-intensity zips appreciating faster pre-law) **is largely the mechanical signature of the rebound**, not a stable gentrification differential.
- The "deceleration" you observed before September 2023 is what a rebound does when it finishes. Any recovery flattens as it approaches the new equilibrium.
- The linear `intensity × time_trend` term, fitted over 2019–2025, draws a straight line through crash + rebound + plateau. The line's slope is dominated by the rebound segment, so it *overshoots* after mid-2023, and the shortfall relative to the overshooting line gets relabeled "Local Law 18." Your instinct that "the 12× jump is the signature of a control absorbing the wrong thing" is exactly right — and here is the concrete red flag from your own table (cell 92): adding the trend didn't just move the coefficient from −0.0004 to −0.0049, it also *shrank* the clustered SE from 0.0013 to 0.0008. When a "control" simultaneously multiplies your coefficient by 12 and cuts your standard error, it is not cleaning your comparison; it is manufacturing one.
- You are also right that quadratic/cubic trends don't rescue this — each is a different unprovable guess about the same invisible counterfactual. The classic cautionary tale is Wolfers (2006, AER) on unilateral-divorce laws, where group-specific trends absorbed the dynamics of the effect itself; the modern statement is in Roth, Sant'Anna, Bilinski & Poe (2023, *Journal of Econometrics*, "What's trending in difference-in-differences?").

One refinement to your reasoning: the problem isn't *only* functional form. Even a perfectly flexible trend model can't separate "the rebound naturally plateaued in late 2023" from "the law suppressed rents starting late 2023," because both hypotheses make the same prediction for high-intensity zips at the same moment. Enforcement landing *exactly when the COVID rebound was cresting* is brutal timing for identification, and no within-NYC estimator fully escapes it. Say this plainly in the paper; it is the single most important sentence of the limitations section.

What to do (details in §3): show the event study over a longer horizon so the reader can *see* 2020–21; re-estimate on windows that exclude or bracket COVID (e.g., a 2015–2019 pre-trend check of whether high-intensity zips were diverging *before* COVID; a post-rebound-only window as robustness); and let Honest DiD formalize how big the trend violation would have to be to kill the result.

#### 2.2 The dose variable is contaminated by survivorship and anticipation

Two distinct problems with `airbnb_intensity` (cell 45):

**(a) Survivorship in the Inside Airbnb snapshot.** `listings.csv` was scraped December 2025 (verified: `scrape_id 20251204025441`, `source` values "city scrape"/"previous scrape"). Inside Airbnb's `reviews.csv` only contains reviews for listings present in that snapshot. Your "active listings in 2022" = listings *that still existed on Airbnb in December 2025* and had a 2022 review. But LL18's whole point was to remove listings — a >80–90% reduction in short-stay listings by most accounts (e.g., roughly 23,000 → ~4,000 in the first year per ACE's summary of the public data). Listings that were delisted in 2023–24 are invisible to you, and they were concentrated exactly where the law bit hardest. Consequences:

- Treated zips' 2022 intensity is **undercounted in proportion to how strongly the law hit them** — non-classical measurement error correlated with the treatment response itself. This can bias the dose-response coefficient in either direction and distorts the cross-zip ranking that your whole design leans on.
- The AirROI cross-check (cells 36–37) compares your proxy's *Jan–Dec 2025* active-listing count (10,789) to AirROI's 2025 count (11,084). Both are post-purge quantities. Agreement there says nothing about whether your *2022* counts are right — and mechanically they cannot be, because the 2022 market was several times larger than what a 2025 snapshot can see.

**Fix (essential, and cheap):** rebuild intensity from an *archived* Inside Airbnb snapshot scraped before enforcement (Inside Airbnb publishes dated archives; academic mirrors also exist for NYC). A snapshot from mid-2023 sees the pre-purge market. This is a few hours of work and changes a first-order input.

**(b) 2022 is a post-adoption baseline.** LL18 was adopted January 9, 2022; registration opened March 2023; Airbnb's lawsuit was dismissed August 2023. Measuring the dose over calendar 2022 means measuring it *during* the anticipation period, when forward-looking hosts may already have been exiting or converting. *Plain-language gloss — anticipation:* if agents respond before the official enforcement date, the "pre" period is partially treated, which both contaminates the dose and flattens the estimated jump at the event date. Prefer a 2019 (or 2018–19 pooled) baseline for the dose — with the archived-snapshot fix in (a), that becomes possible; with the current December 2025 snapshot, a 2019 baseline would be even *more* survivorship-distorted than 2022. The two fixes go together.

#### 2.3 The event study is mechanically mis-specified (endpoints dropped, not binned)

Cells 77–78 build `intensity × month` interactions only for event-time k ∈ [−24, +12], on a panel that spans k ∈ [−56, +27]. The months outside the window get **no interaction term at all**, which in a regression means their intensity-specific deviation is constrained to zero — i.e., they are silently pooled into the reference period along with k = −1. Two consequences:

- Every plotted coefficient is measured relative to a "reference" that is actually the average of August 2023 *plus* January 2019–August 2021 *plus* October 2024–November 2025. The last chunk is **post-treatment** — if the law has effects past month +12, part of the treatment effect is baked into the baseline, mechanically shrinking the plotted post coefficients and distorting the pre-trend shape.
- The plot invites the reader to interpret coefficients as "relative to just before the law," which they are not.

*Plain-language gloss — binning:* the standard practice (Schmidheiny & Siegloch, 2023, *Journal of Applied Econometrics*) is to add catch-all endpoint dummies ("k ≤ −24" and "k ≥ +12") so distant periods have their own coefficients instead of contaminating the reference. Alternatively, restrict the estimation sample to the plotted window. Either is a 5-line fix. Do this before anything else, because every downstream step (Honest DiD especially) consumes these coefficients.

Also small but real: the event-study y-axis label ("% Difference in Log Rent Between Treatment and Control zips") is wrong twice — units are log points per unit of intensity, and there are no discrete treatment/control groups in a continuous-dose design.

#### 2.4 There is no zero-dose control group, and no first stage

All 82 zips have positive intensity (min 0.36, cell 59) — everyone is treated, just more or less. That's inherent to a dose design, but it raises the bar: identification rests on comparisons *across dose levels*, which (as Callaway, Goodman-Bacon & Sant'Anna formalize) require a stronger assumption than ordinary parallel trends — "strong parallel trends," which fails if high-dose zips would have trended differently *even at the same dose*. *Plain-language gloss — selection on gains:* zips didn't get their Airbnb intensity randomly; STR operators concentrated where rent growth was expected. The dose is chosen partly *because of* the outcome's future path. You already flagged this; you're right, and it's another reason the dose-response magnitude shouldn't be read literally.

Separately, the notebook never establishes the **first stage** as a regression: did STR activity actually fall *more in high-dose zips*, and when? You have a suggestive map (cells 29–33: summer '23 vs '24 review changes, which shows heterogeneity, including ~10 zips where activity *rose*) but no formal link. An event study of log review volume (or active listings) on `intensity × month` would (a) prove the treatment intensity gradient is real, (b) date exactly when treatment began — likely revealing anticipation before September 2023, and (c) give you a per-zip "listings removed" measure that makes the rent effect interpretable as an elasticity you can compare to the literature. This is the single highest-value *addition* (as opposed to fix) available, and it's easy.

### Severity 2 — results and inference

#### 2.5 The headline magnitude, functional form, and narrative

- **Instant level shift.** The model imposes that rents drop by the full 0.49%·dose in the month enforcement begins and stay there. Rents adjust through lease turnover; ZORI is additionally a 3-month-smoothed *asking-rent* index. An immediate step is not an economically sensible impulse response, and your own event study doesn't show one. The event-study dynamics *are* the honest answer; the single post coefficient is a summary that hides the implausibility.
- **"Cumulative effect" language (cells 93, 106–109) is wrong.** The model's effect in logs is a constant −0.49%·dose for every post month. The Williamsburg counterfactual plot's gap "widens" in dollars only because a constant percentage of a growing base grows in dollars. Calling this "the policy effect compounds over time" misdescribes your own model.
- **Magnitude vs. literature** (full benchmarking in §5): the median-zip implied effect (~−1.4%) is actually in the plausible range; the top-of-dose Williamsburg effect (−6.3% within ~27 months) is at or beyond the extreme end of anything in the literature, delivered implausibly fast. Linearity in dose is doing a lot of work at the top of the distribution — your own limitations paragraph (cell 113) worries linearity might *understate* effects in concentrated zips, but given the literature, the risk runs the other way.

#### 2.6 The placebo architecture doesn't test what it claims

- The 2019 placebo (cell 83) uses 2019–2021 data: the "post-fake-law" period is dominated by the COVID crash. Of course intensity × post is significant — high-intensity zips crashed. This placebo detects COVID, not a generic pre-trend.
- The re-placebo (cell 98) then shows the trend-corrected model "passes" on the same COVID window at p = 0.077. Passing a placebo *after fitting a trend to the same window* is close to mechanical — the trend was estimated to absorb precisely that variation. It is weak evidence that the trend correction produces the right counterfactual in 2023–25.
- A better placebo battery: fake laws at many dates in a clean window (e.g., 2016–2019 if you extend the rent data back, since ZORI starts 2015), reporting the distribution of placebo t-stats; and a "placebo outcome" (something the law shouldn't affect, e.g., ZORI in zero-Airbnb zips is already implicit, but home *values* in the same zips is a nice contrast since ownership markets should respond less to STR removal in the short run... actually the literature says prices respond too — better placebo outcomes are hard here; the fake-date battery is the workhorse).

#### 2.7 Uncertainty is missing from every headline number

- The $50 median / $300 Williamsburg savings, the savings map (cell 112), and the counterfactual plot (cell 108) carry **no confidence intervals at all**. The Williamsburg figure's title states "$298" as if measured. Every dollar figure should be reported as a range built from the CI of β₁ (delta method or just plug in the CI endpoints — at 95%, roughly −0.0049 ± 1.96·0.0008 → −0.34% to −0.65% per unit → Williamsburg $195–$390, and that's *conditional on believing the specification*, which you shouldn't).
- **82 clusters** is above the usual danger zone (~40), but your dose is heavily right-skewed (median 2.9, max 12.8), so a handful of high-intensity zips carry most of the identifying variation — effective cluster count is smaller than 82. *Plain-language gloss — wild cluster bootstrap:* a resampling method that gives more reliable p-values when clusters are few or unbalanced in influence. The Python `wildboottest` package (MacKinnon–Nielsen–Webb algorithms; integrates with `pyfixest`) makes this a 10-line robustness line in the table. Cheap, standard, worth doing.
- The notebook repeatedly triggers (and silently ignores) statsmodels warnings that the cluster-robust covariance is rank-deficient (cells 68, 73, 84, 92) — benign for the interaction coefficient (it's about the FE block and the F-stat; note the nonsense F = 1,021,807 in your table), but say so rather than letting warnings sit in the output of a polished report.

### Severity 3 — data and sample

#### 2.8 Sample selection is non-random and unacknowledged in the estimand

Keeping only zips with ≤5% missing ZORI drops 67 of 149 zips (cells 52–56), and Zillow coverage is worst in low-rent, outer-borough, high-rent-stabilization areas. Your limitations paragraph (cell 113) admits this — good — but the framing should go further: the estimand is "the effect in the 82 data-rich, generally more market-rate zips," full stop. Two cheap upgrades: (i) a map or table comparing included vs. excluded zips on rent level, borough, and intensity (you have all inputs already); (ii) a robustness run at the 10% threshold (86→~63 more zips? cell 52 says 63 zips at <10% — check that number; the histogram text and printout disagree slightly with the later filter yielding 82 at ≤5%, so reconcile the thresholds when you revisit). Also note the interpolation step (strategy 3) turned out to be a no-op — the summary table shows 6,806 observations before and after — so the balanced 82×83 panel came entirely from the filter; delete or simplify that code path.

#### 2.9 What ZORI is and isn't

ZORI is a **smoothed (3-month), repeat-weighted index of asking rents on listed units**, single-family+condo, not seasonally adjusted in your file variant. Implications worth one honest paragraph: (i) asking rents respond faster than sitting-tenant rents — favorable for detecting effects, but your estimates then apply to *new leases*, not the average renter's bill, so "median tenant saves $50/month" overstates coverage; (ii) the 3-month smoothing mechanically spreads any true effect across adjacent months and adds serial correlation (clustering handles the inference side; the event-study timing is still blurred); (iii) roughly 40+% of NYC's rental stock is rent-stabilized and largely invisible to an asking-rent index — the policy-relevant "who benefits" discussion should say so. Month fixed effects absorb the seasonality issue.

#### 2.10 Spillovers / SUTVA

*Plain-language gloss — SUTVA:* the assumption that one zip's treatment doesn't affect another zip's outcome. Here it fails in known directions: displaced STR demand moved to hotels and to *neighboring* zips (your own map shows ~10 zips with review *increases* post-law — likely spillover destinations, possibly also unregistered activity migrating); displaced units returning to the long-term market can soften rents in adjacent zips too. Both directions contaminate low-dose "control" zips, biasing the DiD toward zero (if controls also got rent relief) or away (if controls absorbed displaced STR demand). You don't need spatial econometrics; a paragraph plus one robustness check (drop control zips adjacent to high-dose zips, or compare border vs. interior controls) is the right calibration. Also state the corollary: a within-city DiD identifies *relative* effects only; any citywide effect of the law (in either direction) is absorbed by the month fixed effects and is invisible to this design.

### Severity 4 — presentation and hygiene (fast to fix, disproportionate reputational impact)

- Factual label fixes: ZRI→ZORI everywhere; "Law Enforced (Sept 2023)" on figures; treatment/control described by intensity, not rent (cell 81); event-study axis label (§2.3).
- The p-value language in cells 85 and 115 (§1).
- Typos and register: "formate" (cell 16), "you can clearly the difference" (cell 81), "greeen" (cell 108), "Summer 23'" → "Summer '23", inconsistent I/we, "an maximum" (cell 20). A cold-emailed economist will forgive one typo; a dozen reads as carelessness that they'll (unfairly but predictably) extrapolate to the code.
- README: presents the trend-corrected estimate as a settled "Key Finding" with p<0.001 and no uncertainty or identification caveat — this must change to match the honest framing (§6); says "2009 to 2025"; lists `sqlite3` among methods but `nyc_airbnb.db` is a 0-byte file and the import is unused — delete both.
- Table craft: the five-column stargazer table mixes estimators, samples, and even different coefficients in one covariate block; the unclustered column leads. A referee-friendly layout: Table 1 = baseline TWFE (clustered only) + luxury subsample; Table 2 = trend model, clearly labeled as a bounding specification; placebos to an appendix table. Report 95% CIs, drop the redundant "P-Value" add-on lines (stars + SEs suffice), suppress the meaningless F row.
- `spatial_helpers.py` duplicates the same join logic in two near-identical functions; harmless, but merge them when convenient.

---

## 3. Verdict on your proposed path forward

**Overall: endorse the direction, reorder the steps, and lower the machinery-to-credibility ratio in one place (SDID).** Point by point:

1. **Event study as centerpiece — yes, strongly.** But it must be the *fixed* event study: binned endpoints (§2.3), rebuilt dose (§2.2), reference period chosen away from the anticipation window (consider k = −20 or a pre-2022 average as reference, or at least show robustness to it), and plotted over the full horizon so COVID is visible rather than cropped out. Add the first-stage event study (review volume) as its twin panel — "the law removed listings here (first stage); rents did/didn't respond (reduced form)" is a professional and intuitive structure.

2. **Honest DiD (Rambachan & Roth 2023, REStud; R package `HonestDiD`, CRAN v0.2.8) — yes, as the lead inference.** *Plain-language gloss:* instead of assuming parallel trends held exactly, you assume the post-period violation is disciplined by the pre-period violations — e.g., "no larger than M̄ times the worst pre-period deviation" (relative magnitudes) or "the trend's slope can change by at most M per period" (smoothness) — and you get confidence sets that are valid under that assumption. The *breakdown point* is the M̄ at which your effect is no longer distinguishable from zero. Set expectations now: **your pre-period deviations are COVID-sized, so the breakdown point will almost certainly be tiny** (a significant effect will survive only under near-exact parallel trends). That is not a failure — it is the finding. "The data cannot distinguish a modest rent-suppressing effect from a continuation of post-COVID normalization; effects larger than X% are ruled out" is a genuinely useful, publishable-honest sentence, and Honest DiD is what lets you write it with numbers. Two practical notes: (i) run it on the *smoothness* class as well as relative magnitudes, since your worry is specifically trend curvature; (ii) it consumes the event-study coefficient vector and covariance matrix, which is why the §2.3 fix is a prerequisite.

3. **Synthetic control / synthetic DiD (Arkhangelsky et al. 2021, AER) — yes, but temper expectations and simplify.** *Plain-language gloss:* instead of assuming low-dose zips are a valid comparison, build a weighted average of them that *matches the treated zips' pre-period rent path*, so the comparison is constructed to be parallel by design; SDID additionally re-weights time periods and keeps DiD's fixed-effects structure. Dichotomizing into top-quartile vs. bottom-half exposure is the right move. Two cautions: (a) the donor pool is the same COVID-shocked city, so if *no* combination of low-dose zips can match the high-dose zips' 2020–22 rollercoaster, the method will tell you so via bad pre-fit — report that honestly rather than forcing it; (b) with ~20 treated units and ~40 donors, use placebo-in-space inference (re-run assigning treatment to donors, compare gap distributions) rather than leaning on asymptotic SEs. One upgrade worth considering because your data already supports it: **ZORI is national**, so the donor pool doesn't have to be NYC. High-Airbnb zips in other large metros without a 2023 regulatory shock (e.g., Boston, Chicago, Miami — *not* LA or Jersey City, which have their own ordinances) experienced the same national COVID rebound cycle and make more plausible counterfactuals for "tourist-dense urban zips absent a ban." That's the single strongest design improvement available to this project; it's nice-to-have, not essential, at your ambition level.

4. **Demote the linear-trend model to "optimistic end of a range" — yes.** Keep it in the paper; it's pedagogically valuable and shows you understand *why* it fails. Present it alongside the baseline null as bracketing scenarios, with the event study + Honest DiD arbitrating between them.

5. **Cite Callaway, Goodman-Bacon & Sant'Anna (continuous-treatment DiD; NBER WP 32117, latest version on Sant'Anna's site) rather than implement — yes.** Their "strong parallel trends" concept gives you the precise language for why the dose comparison is fragile (§2.4), and flagging the likely failure of no-selection-on-gains in one paragraph is exactly the right depth. Implementing their estimators would be over-engineering here.

6. **"A credible null beats a fragile significant result" — correct, and it's also the more interesting paper.** Given the aggregate arithmetic (§5) and the NYC-specific reporting to date, a defensible conclusion along the lines of *"we can rule out rent reductions larger than ~X% in the most exposed neighborhoods; smaller effects are indistinguishable from post-pandemic normalization"* is a contribution. Nobody credible has published a careful LL18 rent estimate yet (§5) — an honest bounded null with open code is a real calling card.

**What your plan missed** (beyond items already covered): the first stage (§2.4 — add it); anticipation handling (estimate a version dropping Jan 2022–Aug 2023 as a transition window, or use March 2023/registration as an alternative event date); dose-bin event studies (quartiles of intensity instead of a linear dose — nonparametric in the dose, easy, and directly shows whether the top quartile drives everything); the aggregate-plausibility check (§5); and the survivorship rebuild of the dose (§2.2 — the plan implicitly assumed the dose was fine).

---

## 4. The tooling decision: Python, plus one small R script

**My call: do not port the project to R. Do everything in Python except Honest DiD, for which you should write a single small R script calling the canonical CRAN `HonestDiD` package.** Reasoning:

- **Event studies, TWFE, clustering:** Python is fully mature. `pyfixest` (py-econometrics) replicates R's `fixest` — high-dimensional FE, cluster-robust and wild-bootstrap inference, event-study helpers. Your `statsmodels` + `C(zip)` approach works but is slow and verbose; migrating the specs to `pyfixest` is optional polish, not a requirement.
- **Wild cluster bootstrap:** `wildboottest` (py-econometrics, on PyPI; MacKinnon–Nielsen–Webb algorithms) is mature and integrates with `pyfixest`. No R needed.
- **Honest DiD:** the canonical implementation is the authors' R package (`HonestDiD`, CRAN v0.2.8). Python ports exist (e.g., `anzonyquispe/honestdid` on GitHub) but are unofficial, thinly used, and not something you want to be debugging or defending in an interview. The method's interface is tiny: it consumes your event-study coefficient vector β̂ and covariance matrix Σ̂. So: estimate in Python → export two CSVs → 30 lines of R → import the sensitivity results back for plotting in Python. This is the *lowest-risk* route, and "I ran the canonical package" is the answer you want to give when a pre-doc interviewer asks. Incidentally, demonstrating you can touch R is a small plus for RA applications (many labs are R/Stata shops), at near-zero cost here.
- **Synthetic DiD:** canonical package is R `synthdid` (synth-inference). If you do SDID, either use the R package in the same tiny-script pattern, or use the `d2cml-ai/synthdid.py` Python port (the most maintained of the ports — supports block designs, SEs) and validate it once against the R package's published example. For plain synthetic control with placebo-in-space inference, a manual implementation on an 82×83 panel is ~50 lines and arguably *better* for learning; that's a legitimate choice at your level if you show the placebo inference.
- **What not to do:** don't hand-roll Honest DiD (the confidence-set constructions are subtle: conditional/hybrid FLCIs, moment-inequality machinery — high effort, high silent-failure risk, zero credibility gain over the canonical package).

---

## 5. Benchmarking against the literature

**Your sign does not actually disagree with the academic literature — untangle this.** The literature says Airbnb *presence raises* rents; therefore *removing* it should lower rents relative to counterfactual. Your corrected model's negative sign is consistent with that. What disagrees is (a) your own baseline TWFE (a clean null), and (b) the NYC-specific post-LL18 empirical reporting, which shows rents in formerly high-Airbnb areas rising as fast or faster than elsewhere — note that the most-cited version of that claim comes from an Airbnb-commissioned HR&A Advisors report (and Airbnb's own follow-ups citing record Manhattan rents), so treat it as advocacy-grade evidence with a conflict of interest, but it is consistent with your raw event study.

Reference points (all verified against current sources):

| Study | Setting | Finding |
|---|---|---|
| Barron, Kung & Proserpio (2021, *Marketing Science*) | US zips | +1% listings → +0.018% rents (median owner-occupancy zip) |
| Garcia-López, Jofre-Monseny, Martínez-Mazza & Segú (2020, *J. Urban Econ.*) | Barcelona | Airbnb activity raised rents ~1.9% in the average neighborhood; up to ~7% in the highest-activity areas (accumulated over years of growth) |
| Koster, van Ommeren & Volkhausen (2021, *J. Urban Econ.*) | LA-county Home Sharing Ordinances | Ordinances cut listings ~50%; **rents and prices fell ~2%** in regulated cities — the closest design to yours, with a real regulatory shock |
| Duso, Michelsen, Schäfer & Tran (2024, *Reg. Sci. Urban Econ.*) | Berlin 2016/2018 regulations | Regulation reduced listings; nearby rent effects of Airbnb on the order of 1–3% cumulatively |
| Calder-Wang (working paper, Wharton #841) | NYC structural model | Airbnb cost the median NYC renter ≈ $125/year (~$10/month) in higher rent, concentrated in high-income, high-tourism neighborhoods |
| Jin, Wagman & Zhong (2024, NBER WP 32537) | Chicago middle-ground ordinance | Listings −16% vs. control cities; enforcement capacity (platform data feeds) is what made regulation bite |
| Wachsmuth et al. / UPGo (McGill, pre-enforcement report on NYC) | NYC projection | Applied Barron et al. elasticities to project modest rent-growth slowdowns under strict enforcement; explicitly cautioned those elasticities weren't estimated from sharp de-listing events |

Now your numbers. LL18 cut short-stay listings on the order of 80–90%. A crude Barron-et-al. extrapolation (−85% listings × 0.018) implies citywide-average rent effects around −1.5% — and your median-zip implied effect (−0.49% × 2.9 ≈ −1.4%) is *right in that range*, which is worth saying. The problem is the top of the dose distribution: Williamsburg at −6.3% within 27 months is roughly triple the largest credible regulation-driven estimates (Koster et al.'s −2% for whole treated cities; Garcia-López's +7% took years of accumulation in the most extreme areas), delivered as an instant level shift. Combined with the aggregate arithmetic — ~10–15k units potentially returned against a rental stock of ~2.3M (≈0.5%), in a market with ~1.4% vacancy — a 5–6% neighborhood-level rent reduction requires extreme localization of the supply effect. Possible, but extraordinary claims from a specification you already distrust.

**On an LL18-specific causal study:** as of this writing I could not find a peer-reviewed or credible working-paper DiD estimate of LL18's effect on rents. What exists: the Airbnb/HR&A advocacy analyses (rents rose faster in high-Airbnb areas); Airbnb's "20 months later" releases (record rents, hotel rates +, ~90% listing decline); the city's OSE two-year report (Sept 2025) claiming tens of thousands of illegal rentals eliminated; law-review treatments (e.g., Cornell JLPP 2025); and the McGill/UPGo pre-enforcement projections. NBER WP 32537 covers Chicago, not NYC. **This is good news for you: the question is genuinely open, and an honest, open-source zip-level analysis has a real audience.** (Policy status check for your intro: LL18 remains in force; a loosening bill, Intro 1107 of 2024, covering 1–2 family homes, was still being debated per the latest reporting I found — verify its status the week you finalize, since Airbnb's lobbying push has been active through 2025–26.)

---

## 6. Making it read as professional

**Deliverable format.** For resume/cold-email/pre-doc use, the notebook is the appendix, not the product. Produce:
1. A **6–10 page paper-style PDF** (you already have Quarto front matter — `format: pdf` is nearly free): Intro & policy background (with correct adoption/enforcement chronology) → Data (with a *data-vintage table*: source, snapshot date, what each vintage can and cannot see) → Empirical strategy → Results (event study centerpiece + Honest DiD sensitivity plot) → Robustness → Limitations → Conclusion.
2. The **repo** as the reproducibility artifact: `requirements.txt` (pin versions), a `data/README.md` with download URLs and snapshot dates (the data files are gitignored — right call given a 77MB CSV, but then the repo must tell a stranger how to rebuild them; right now it doesn't), delete `nyc_airbnb.db` (0 bytes) and the unused `sqlite3`/`sys`/`re` imports, and state the render command.
3. A **one-screen README**: question, one event-study figure, three-sentence honest answer, link to PDF. Your current README's "Key Findings" section must be rewritten around the honest framing — as written it asserts the −0.5%/p<0.001 result that this audit (and your own diagnosis) rejects. That's the single most dangerous artifact in the repo for cold-email purposes, because it's the first and possibly only thing an economist reads.

**Reporting standards to adopt throughout:** every headline number carries a 95% CI (dollar figures included, §2.7); every map with an estimate on it gets an uncertainty note in the caption; clustered SEs only (drop the unclustered column, or footnote it); placebo results described as "fail to reject" never "confirm"; the word "significant" always prefixed by "statistically" or replaced with magnitudes.

**Structural rewrite of the narrative arc** — this is your biggest presentational asset. The current arc is "null → diagnose → fix → big effect → victory lap." The credible arc is: *"Baseline DiD: null. Event study: the comparison was never valid — here's why (COVID + gentrification). A common 'fix' (group trends) manufactures a large effect — here's exactly how it fools you. Honest bounds: what the data can actually support. Conclusion: bounded, honest, and clear about what data would settle it (longer post-period, listing-level micro-data)."* That arc demonstrates *judgment*, which is the thing pre-doc screeners are actually screening for. The Williamsburg counterfactual plot can survive as an illustration of the trend-model's implied (implausible) counterfactual — relabeled as such, not as "Estimated Tenant Savings."

**Resume line once done** (something like): *"Evaluated NYC's Airbnb ban (Local Law 18) using a zip-month panel DiD with event-study and Rambachan–Roth sensitivity analysis; showed naive trend-corrected estimates are confounded by post-COVID rent dynamics and derived honest bounds on the policy effect."* Every phrase in that sentence is interview-defensible, which is the test.

---

## 7. Prioritized action list

**Essential (do these; ~2 focused weeks):**

| # | Task | Effort | Learning/hour |
|---|---|---|---|
| E1 | Rebuild dose from an archived pre-enforcement Inside Airbnb snapshot; move baseline year to 2019 (or justify 2022 explicitly); re-run everything | 3–5 h | High — data vintage & survivorship is a lesson that generalizes to every scraped-data project |
| E2 | Fix the event study: bin endpoints, full horizon, correct labels; re-examine with the new dose | 2–3 h | High |
| E3 | Confront COVID in text and design: plot raw rent paths by intensity quartile 2015–2025; add a 2015–2019 pre-trend check; robustness on a post-rebound window | 3–4 h | Very high — this is the core identification reasoning |
| E4 | First-stage event study (log review volume on intensity × event-time) | 2–3 h | High |
| E5 | Honest DiD on the fixed event study (Python export → R `HonestDiD` → plot); report breakdown points for smoothness and relative-magnitude classes | 4–6 h | Very high — the most valuable new tool per hour in the whole plan |
| E6 | Re-frame: demote trend model, rewrite README/conclusion/abstract around the honest arc; CIs on all dollar figures; fix all §2.11-style presentation items | 3–4 h | Medium, but highest reputational return |
| E7 | Repro hygiene: requirements.txt, data/README with URLs+dates, delete dead files/imports, wild-cluster-bootstrap p-value for the main spec | 2 h | Medium |

**Nice-to-have (pick at most two):**
- N1. Dose-quartile event study (nonparametric dose) — 1–2 h, high value per hour, honestly borderline-essential.
- N2. Synthetic control / SDID on high vs. low exposure with placebo-in-space inference — 4–8 h.
- N3. Out-of-city donor pool (other metros' high-Airbnb zips via national ZORI + Inside Airbnb archives) — 8 h+, the strongest design upgrade if you have appetite.
- N4. Spillover check (drop controls adjacent to high-dose zips) — 2 h.
- N5. Anticipation variants (drop Jan 2022–Aug 2023 window; alternative event dates) — 2 h.

**Skip (deliberately):** quadratic/cubic group trends (you already know why); implementing Callaway–Goodman-Bacon–Sant'Anna estimators (cite, don't build); spatial econometrics / Conley SEs (a paragraph on spillovers beats machinery here); any IV strategy for intensity (no credible instrument in sight, and a bad IV is worse than an honest OLS); porting the repo to R.

---

## Sources consulted (web)

- Rambachan & Roth (2023), "A More Credible Approach to Parallel Trends," *REStud*; `HonestDiD` R package (CRAN v0.2.8): https://cran.r-project.org/package=HonestDiD ; https://github.com/asheshrambachan/HonestDiD ; unofficial Python port: https://github.com/anzonyquispe/honestdid
- Arkhangelsky, Athey, Hirshberg, Imbens & Wager (2021), "Synthetic Difference-in-Differences," *AER*; R `synthdid`: https://synth-inference.github.io/synthdid ; Python port: https://github.com/d2cml-ai/synthdid.py
- Callaway, Goodman-Bacon & Sant'Anna, "Difference-in-Differences with a Continuous Treatment": https://psantanna.com/files/CGBS_v4.pdf ; NBER WP 32117
- Roth, "DiD Resources" (incl. Roth, Sant'Anna, Bilinski & Poe 2023 survey): https://jonathandroth.github.io/did-resources
- `wildboottest` (Python wild cluster bootstrap): https://github.com/py-econometrics/wildboottest ; `pyfixest`: https://pyfixest.org
- Barron, Kung & Proserpio (2021), *Marketing Science*: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3006832
- Garcia-López, Jofre-Monseny, Martínez-Mazza & Segú (2020), *J. Urban Economics*: https://www.sciencedirect.com/science/article/pii/S0094119020300498
- Koster, van Ommeren & Volkhausen (2021), *J. Urban Economics* (LA Home Sharing Ordinances): https://ideas.repec.org/a/eee/juecon/v124y2021ics0094119021000383.html
- Duso, Michelsen, Schäfer & Tran (2024), "Airbnb and rental markets: Evidence from Berlin," *Reg. Sci. Urban Econ.*: https://www.sciencedirect.com/science/article/pii/S0166046224000310
- Calder-Wang, "The Distributional Impact of the Sharing Economy on the Housing Market" (Wharton WP #841): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3908062
- Jin, Wagman & Zhong (2024), NBER WP 32537 (Chicago STR regulation): https://www.nber.org/system/files/working_papers/w32537/w32537.pdf
- Wachsmuth et al. / UPGo (McGill), "The Impact of New Short-term Rental Regulations on New York City": https://upgo.lab.mcgill.ca/publication/impact-of-new-regulations/impact-of-new-regulations.pdf
- NYC OSE, LL18 registration law & Sept 2025 two-year enforcement report: https://www.nyc.gov/site/specialenforcement/registration-law/registration.page ; https://www.nyc.gov/site/specialenforcement/news/new-report-sheds-fresh-light-on-how-local-law-18.page
- Airbnb/HR&A advocacy analyses of LL18 (conflict of interest noted): https://impact.airbnb.com/news/nyc-sees-record-rents-hotel-rates-as-short-term-rental-law-continues ; https://news.airbnb.com/new-report-finds-nycs-short-term-rental-law-takes-toll-on-outer-boroughs
- Intro 1107 reform debate: https://ace-usa.org/blog/research/research-housing-policy/understanding-the-intro-1107-legislation-debate-short-term-rental-regulations-in-nyc ; https://www.rentalscaleup.com/new-york-short-term-rental-regulations
- White & Thor (2025), *Cornell J. Law & Public Policy* (LL18 legal history): https://community.lawschool.cornell.edu/wp-content/uploads/2025/04/White-Thor-final.pdf

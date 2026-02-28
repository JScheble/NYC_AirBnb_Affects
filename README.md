# Does Restricting Airbnb Lower Rents? Estimating Effects from NYC's Local Law 18

## Project Summary

This project looks at whether New York City's Local Law 18, the September 2023 ban on most short-term Airbnb rentals, actually helped slow down rising residential rents. To figure this out, the analysis uses a difference-in-differences approach, combining Zillow rent data, Airbnb listing counts, and Census housing stats across 82 NYC zip codes from 2009 to 2025. The model measures how concentrated Airbnbs were in different neighborhoods and checks what happened to rents in those specific areas after the law kicked in. One major hurdle was that rents in heavy-Airbnb neighborhoods were already rising faster than in other areas before the ban even started. By controlling for these pre-existing trends, the model isolates the actual impact of the new law rather than just capturing normal market momentum.

## Research Question

Did Local Law 18's restrictions on short-term rentals reduce residential rents in NYC neighborhoods with high Airbnb activity, relative to low-activity neighborhoods?

## Key Findings

- Local Law 18 reduced rents by approximately **0.5% per unit of Airbnb intensity** (p < 0.001), after correcting for pre-existing differential rent trends.
- The median zip code saw an estimated monthly rent reduction of roughly **$50**; in Williamsburg (zip 11211, the highest-intensity area at 12.8 listings per 1,000 housing units), the cumulative effect reached approximately **$300/month** — a ~5% reduction.
- Geographic patterns confirm the largest effects in lower Manhattan and North Brooklyn, with near-zero effects in areas that had minimal Airbnb presence.
- Robustness checks — including placebo testing and outlier sensitivity analysis — support the stability of the estimated effect.

## Tools & Methods

**Language:** Python 3
**Libraries:** pandas, numpy, statsmodels, geopandas, matplotlib, sqlite3, stargazer
**Methods:** Two-way fixed effects (TWFE) regression, interaction modeling (`log(Rent) ~ Airbnb Intensity × Post-Law + Zip FE + Month FE`), clustered standard errors, event study analysis, group-specific linear time trends (parallel trends correction), placebo testing
**Data:** Zillow Rent Index, Airbnb listings/reviews data, American Community Survey (ACS) housing unit counts

## Rendered Report

The full analysis — including regression tables, choropleth maps, counterfactual rent trajectories, and event study plots — is best viewed in the rendered HTML report:

👉 **[Airbnb_Law_Effect.html](Airbnb_Law_Effect.html)**

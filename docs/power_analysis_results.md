# Power Analysis Results
## 20% First-Order Promo Discount A/B Test

**Phase:** 3 of 6  
**Author:** Akash Singh  
**Date:** June 2026  
**Input:** Phase 2 SQL outputs — 24,956 control / 25,044 treatment users  

---

## Summary

The experiment is **well-powered**. With approximately 25,000 users per group,
the test can reliably detect a true reorder rate lift as small as **0.88
percentage points** — far smaller than the 5pp business threshold defined in the
experiment design document. Any non-significant result from Phase 4 is a true
null finding, not an artifact of an underpowered experiment.

---

## Parameters

| Parameter | Value | Source |
|---|---|---|
| Baseline reorder rate (control) | 80.27% | Phase 2 SQL output |
| Target treatment rate | 85.27% | Baseline + 5pp MDE |
| Planned minimum detectable effect | 5.0 pp | Experiment design doc |
| Significance level (alpha) | 0.05 | Experiment design doc |
| Target power | 80% | Experiment design doc |
| Test direction | One-tailed (improvement only) | Experiment design doc |

---

## Results

| Metric | Value |
|---|---|
| Effect size (Cohen's h) | 0.1327 |
| Required users per group (5pp MDE) | 702 |
| Required total users | 1,404 |
| Actual control users | 24,956 |
| Actual treatment users | 25,044 |
| Achieved statistical power | 100% |
| Actual MDE at n=24,956 | **0.88 pp** |

---

## Interpretation

**The sample far exceeds the minimum required.** We needed only 702 users per
group to detect a 5pp lift at 80% power. We have 24,956 — approximately 35x
the minimum. This gives us 100% power for the 5pp planned effect, meaning
we will almost certainly detect it if it truly exists.

**The actual MDE is 0.88pp.** This means our sample can detect any true
improvement in reorder rate larger than 0.88 percentage points. This is well
below the 5pp business threshold, which confirms that if Phase 4 shows no
statistically significant difference, it is a genuine finding — the promo does
not meaningfully improve reorder behavior — not a limitation of sample size.

**Why this matters for the business decision:** An underpowered experiment that
returns a non-significant result leaves open the question of whether the effect
was real but undetectable. Our sample eliminates that ambiguity entirely. A
null result in Phase 4 is a confident null result.

---

## Multiple Metrics Testing Plan

| Metric | Alpha | Rationale |
|---|---|---|
| Primary — 30-day reorder rate | 0.05 | Decision driver — strict threshold |
| Secondary — 60-day reorder rate | 0.10 | Exploratory — relaxed threshold |
| Secondary — 90-day reorder rate | 0.10 | Exploratory — relaxed threshold |
| Secondary — average order value | 0.10 | Exploratory — relaxed threshold |
| Guardrail — net revenue 90 days | 0.05 | Must not degrade — strict threshold |
| Guardrail — refund rate | 0.05 | Must not degrade — strict threshold |

No Bonferroni correction is applied to secondary metrics because they are
exploratory and inform follow-up design, not the primary Go/No-Go call.

---

## Output Files

- `reports/power_analysis_curves.png` — power curve and MDE vs. sample size charts
- `reports/power_analysis_summary.csv` — all parameters and results in tabular form
- `src/03_power_analysis.py` — full reproducible Python script

---

## Next Step

Phase 4 — Statistical Testing. With the experiment confirmed as well-powered,
all test results can be interpreted with confidence.

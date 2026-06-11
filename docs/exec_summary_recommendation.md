# Executive Summary and Go/No-Go Recommendation
## 20% First-Order Promo Discount A/B Test

**Prepared by:** Akash Singh, Data Analyst  
**Date:** June 2026  
**Audience:** Product, Marketing, and Finance Leadership  
**Status:** Final — Ready for Decision  

---

## One-Line Answer

> **No-Go.** The 20% first-order discount generated no measurable
> improvement in customer reorder behavior and costs the platform
> $7.54 per acquired user in net destroyed margin. At 100,000 new
> users per month, that is **$9.05 million in annual losses** with
> zero incremental revenue to show for it.

---

## What We Tested

The marketing team proposed offering new users a 20% discount on
their first order to improve 90-day retention. Before committing
to a platform-wide rollout, we ran a controlled experiment:

- 25,044 new users received the 20% discount (treatment group)
- 24,956 new users received no discount (control group)
- We tracked reorder behavior, order values, and net revenue
  for 90 days after each user's first order

---

## What We Found

### The discount did not change behavior

Users who received the 20% discount reordered at exactly the same
rate as users who received no discount — 80.25% vs. 80.27% over
30 days. The difference of 0.02 percentage points is statistically
indistinguishable from zero (p = 0.52).

This finding held across every metric we tested:

| Metric | Control | Treatment | Difference | Significant? |
|---|---|---|---|---|
| 30-day reorder rate | 80.27% | 80.25% | -0.02pp | No (p=0.52) |
| Average reorder value | $35.00 | $34.99 | -$0.01 | No (p=0.88) |
| Loyal user share | 53.4% | 52.7% | -0.7pp | No (p=0.39) |
| Net revenue per user (90d) | $133.80 | $126.39 | **-$7.42** | **Yes (p<0.001)** |

The only statistically significant difference was the one we did
not want: treatment users generated $7.42 less net revenue per
user — almost exactly the $7.03 average discount cost — with no
behavioral change to justify it.

### The economics do not work at any realistic scenario

| Scenario | Assumption | Net value/user | At 100K users/mo |
|---|---|---|---|
| Observed | No behavioral change | -$7.54 | -$9.05M/year |
| Conservative | 2pp reorder lift | -$4.93 | -$5.92M/year |
| Optimistic | 5pp reorder lift | -$1.78 | -$2.14M/year |

Break-even requires a **6.70pp reorder rate lift**. Even the most
optimistic realistic scenario falls short of that threshold.

### The experiment was well-powered — this is a real finding

Before running the tests, we confirmed the experiment had
sufficient statistical power. With 25,000 users per group, we
can detect a true effect as small as 0.88 percentage points. The
null result is not a data limitation. It is a definitive answer.

---

## Why This Happens — The Business Explanation

The users the discount attracted were going to reorder anyway.
The 80%+ reorder rate in the control group shows these are
high-intent grocery shoppers with strong habitual behavior. The
discount did not create new reorder intent — it simply reduced
the price for users who were already committed to the platform.

This is the classic **deal-seeker trap**: a promotion that appears
to drive engagement because treated users look active, but the
activity would have occurred with or without the discount.

---

## Recommendation

### Primary recommendation: No-Go on the flat 20% discount

Do not roll out the flat 20% first-order discount at current terms.
The promotion destroys $7.54 per acquired user with no measurable
return on any behavioral metric.

### What to test instead — three alternative designs

**Option 1 — Raise the order value floor**
Apply the discount only on first orders above $50. This targets
higher-value customers, reduces the discount cost on low-basket
users, and improves net economics even if behavioral lift stays flat.
Estimated break-even with a $50 floor: requires a 4.0pp lift instead
of 6.70pp — a more achievable target.

**Option 2 — Loyalty-linked discount structure**
Replace the first-order discount with a "second order reward" — $7
credit applied automatically when the user places their second order
within 14 days. This only pays out when the desired behavior (repeat
ordering) actually occurs. Cost is zero for users who never reorder.
This directly addresses the deal-seeker problem.

**Option 3 — Segment-targeted promo**
The current experiment treated all new users identically. Re-run
the experiment targeted only at users in lower-frequency acquisition
channels (e.g., social media vs. organic search). Users arriving
from paid channels may have lower baseline intent and respond more
to discount incentives. Test this hypothesis before committing to
a broader rollout.

---

## Conditions That Would Change This Recommendation

This recommendation is based on the Instacart grocery delivery
dataset. The following conditions would warrant re-evaluation:

- Platform-specific data shows a materially different baseline
  reorder rate (below 50%), where the behavioral lift from a
  discount may be larger in percentage-point terms
- A redesigned experiment using Options 1, 2, or 3 above shows
  statistically significant improvement at lower cost per user
- Customer acquisition cost data shows the $7.03 discount is
  cheaper than alternative acquisition channels, making it
  valuable as an acquisition tool even without behavioral lift

---

## Limitations to Disclose

The Instacart dataset reflects grocery delivery behavior with an
80%+ reorder rate — materially higher than typical restaurant
delivery platforms (estimated 25-35%). The analytical methodology
is fully transferable to any platform. The specific break-even
numbers (6.70pp lift required) should be recalibrated using
platform-specific baseline reorder rates before making a final
production decision.

---

## Next Steps

| Action | Owner | Timeline |
|---|---|---|
| Share findings with marketing and product leads | Analytics | Week 1 |
| Design follow-up experiment using Option 2 (loyalty-linked) | Product + Analytics | Week 2-3 |
| Define platform-specific baseline reorder rate | Data Engineering | Week 2 |
| Run power analysis for redesigned experiment | Analytics | Week 3 |
| Launch follow-up experiment | Product | Week 4-6 |

---

## Supporting Documents

| Document | Location | Purpose |
|---|---|---|
| Experiment design document | `docs/experiment_design_document.md` | Full hypothesis and metric definitions |
| Power analysis results | `docs/power_analysis_results.md` | Sample size and MDE confirmation |
| SQL funnel build | `sql/02_funnel_build.sql` | Order funnel query with 5-stage CTEs |
| Group metrics | `sql/03_group_metrics.sql` | All aggregated test inputs |
| Statistical test results | `reports/statistical_test_results.csv` | All three test outputs |
| Dollar impact model | `reports/platform_impact_by_volume.csv` | Platform-level scenario table |
| Per-user economics | `reports/per_user_economics.csv` | Per-user ROI by scenario |

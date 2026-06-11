# Food Delivery Promo Discount A/B Test

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![DuckDB](https://img.shields.io/badge/DuckDB-0.10%2B-yellow?style=flat-square)
![scipy](https://img.shields.io/badge/scipy-1.11%2B-blue?style=flat-square)
![statsmodels](https://img.shields.io/badge/statsmodels-0.14%2B-blue?style=flat-square)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=flat-square)

A/B test analysis of a 20% first-order promo on 50K users. No significant reorder lift detected (p=0.52). Guardrail breached: $7.42 net revenue loss per user. Covers experiment design, power analysis, SQL funnel, 3 hypothesis tests, dollar impact model, and Go/No-Go recommendation. Python &bull; DuckDB &bull; scipy &bull; statsmodels.

---

## Business Problem

Food delivery platforms routinely offer first-order discounts to acquire new customers. A 20% discount on a $35 average order costs $7 per user in direct margin. The business question is whether that investment generates enough repeat order behavior to be profitable over a 90-day window.

This project answers that question end-to-end — from experiment design through statistical testing to a dollar-denominated Go/No-Go recommendation — using Instacart's public 3.4M order dataset.

---

## Key Finding

> The 20% first-order discount produced **no statistically significant improvement** on any behavioral metric. The guardrail was breached: treatment users generated **$7.42 less net revenue per user** over 90 days — driven entirely by the discount cost with zero offsetting behavioral change. At 100,000 new users per month, this represents a **$9.05M annual loss** with nothing to show for it.

| Metric | Control | Treatment | Difference | Significant? |
|---|---|---|---|---|
| 30-day reorder rate | 80.27% | 80.25% | -0.02pp | No (p=0.52) |
| Average reorder value | $35.00 | $34.99 | -$0.01 | No (p=0.88) |
| Loyal user share | 53.4% | 52.7% | -0.7pp | No (p=0.39) |
| Net revenue / user (90d) | $133.80 | $126.39 | **-$7.42** | **Yes (p&lt;0.001)** |

---

## Project Structure

```
food-delivery-promo-ab-test/
├── docs/
│   ├── experiment_design_document.md   # Phase 1 — BA artifact
│   ├── power_analysis_results.md       # Phase 3 — BA artifact
│   └── exec_summary_recommendation.md # Phase 6 — Go/No-Go decision
├── sql/
│   ├── 01_experiment_assignment.sql    # Load data, hash-based group assignment
│   ├── 02_funnel_build.sql             # 5-stage CTE funnel, window functions
│   └── 03_group_metrics.sql            # Group-level aggregations, all metrics
├── src/
│   ├── 03_power_analysis.py            # Sample size, MDE, power curves
│   ├── 04_statistical_testing.py       # Z-test, Mann-Whitney U, chi-square
│   ├── 05_dollar_impact_model.py       # 3-scenario ROI model, break-even
│   └── 06_exec_onepager.py             # Executive summary visualization
├── reports/
│   ├── power_analysis_curves.png
│   ├── statistical_test_results.png
│   ├── dollar_impact_model.png
│   ├── exec_onepager.png
│   ├── group_metrics_summary.csv
│   ├── statistical_test_results.csv
│   ├── per_user_economics.csv
│   └── platform_impact_by_volume.csv
├── requirements.txt
└── README.md
```

---

## Phase-by-Phase Overview

<table>
  <thead>
    <tr>
      <th>Phase</th>
      <th>Deliverable</th>
      <th>Type</th>
      <th>Key Output</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>1 &mdash; Experiment Design</strong></td>
      <td>experiment_design_document.md</td>
      <td>BA document</td>
      <td>Hypotheses, metric tiers, decision criteria — written before seeing any data</td>
    </tr>
    <tr>
      <td><strong>2 &mdash; SQL Funnel</strong></td>
      <td>01 / 02 / 03 .sql files</td>
      <td>DuckDB SQL</td>
      <td>Hash-based randomization, 5-stage CTE funnel, window functions, 6 aggregation queries across 50K users</td>
    </tr>
    <tr>
      <td><strong>3 &mdash; Power Analysis</strong></td>
      <td>03_power_analysis.py</td>
      <td>Python</td>
      <td>Required n=702 per group &mdash; actual n=24,956. Achieved power 100%. MDE 0.88pp. Null result is definitive.</td>
    </tr>
    <tr>
      <td><strong>4 &mdash; Statistical Testing</strong></td>
      <td>04_statistical_testing.py</td>
      <td>Python</td>
      <td>Two-proportion z-test (p=0.52), Mann-Whitney U (p=0.88), chi-square (p=0.39). Guardrail breached (p&lt;0.001).</td>
    </tr>
    <tr>
      <td><strong>5 &mdash; Dollar Impact Model</strong></td>
      <td>05_dollar_impact_model.py</td>
      <td>Python</td>
      <td>3 scenarios (observed / conservative / optimistic). Break-even requires 6.70pp lift. All scenarios net negative.</td>
    </tr>
    <tr>
      <td><strong>6 &mdash; Recommendation</strong></td>
      <td>exec_summary_recommendation.md</td>
      <td>BA document</td>
      <td>No-Go on flat 20% discount. 3 alternative promo designs proposed with rationale.</td>
    </tr>
  </tbody>
</table>

---

## Dollar Impact Model

| Scenario | Assumption | Net value/user | At 100K users/month |
|---|---|---|---|
| Observed | No behavioral change | -$7.54 | -$9.05M/year |
| Conservative | 2pp reorder lift | -$4.93 | -$5.92M/year |
| Optimistic | 5pp reorder lift | -$1.78 | -$2.14M/year |

Break-even requires a **6.70pp reorder rate lift.** Observed lift: **-0.01pp.**

---

## SQL Techniques Demonstrated

`02_funnel_build.sql` is the core analytical file. It demonstrates:

```sql
-- 5-stage CTE pipeline
WITH first_orders AS (...),
     subsequent_orders AS (...),
     user_reorder_flags AS (...),   -- MAX(CASE WHEN days <= 30 THEN 1 ELSE 0 END)
     user_lifetime_value AS (...),  -- net_order_net + reorder_revenue_90d
     user_order_frequency_tier AS (
         CASE
             WHEN reorders_in_90d = 0 THEN 'one_and_done'
             WHEN reorders_in_90d = 1 THEN 'occasional'
             WHEN reorders_in_90d = 2 THEN 'regular'
             WHEN reorders_in_90d >= 3 THEN 'loyal'
         END AS frequency_tier
     )
SELECT * FROM user_order_frequency_tier;
```

Full technique list: multi-step CTEs, `ROW_NUMBER` / `RANK` / `PERCENT_RANK` window functions, `PERCENTILE_CONT`, `NULLIF` for divide-by-zero protection, conditional aggregation with `CASE WHEN`, date arithmetic via `days_since_first_order`, hash-based deterministic randomization, `GROUPING SETS` rollups.

---

## Statistical Tests

| Test | Metric | Result | Decision |
|---|---|---|---|
| Two-proportion z-test | 30-day reorder rate | p = 0.5163 | Fail to reject H0 |
| Mann-Whitney U | Avg reorder order value | p = 0.8811 | Fail to reject H0 |
| Chi-square | Loyalty tier distribution | p = 0.3917 | Fail to reject H0 |
| Mann-Whitney U (guardrail) | Net revenue / user 90d | p &lt; 0.001 | **Guardrail breached** |

---

## Dataset

This project uses the **Instacart Market Basket Analysis** dataset (publicly available, no authentication required).

**Download:** [kaggle.com/competitions/instacart-market-basket-analysis/data](https://www.kaggle.com/competitions/instacart-market-basket-analysis/data)

**Files needed:** Download `orders.csv` and place it in a `data/` folder in the project root before running any scripts.

```
food-delivery-promo-ab-test/
└── data/
    └── orders.csv       # ~18MB — not included in repo
```

The dataset contains 3.4 million orders across 206,209 users. This project uses a preprocessed version with `order_value` added via simulation at a realistic $35 mean with $10 standard deviation, matching published food delivery average order value benchmarks.

**Dataset size:** 230,713 orders &bull; 50,000 users &bull; up to 15 orders per user &bull; up to 297 days tracked

---

## Setup and Usage

```bash
# Clone the repository
git clone https://github.com/aksingh-ops/food-delivery-promo-ab-test.git
cd food-delivery-promo-ab-test

# Install dependencies
pip install -r requirements.txt

# Add dataset (download from Kaggle link above)
mkdir data
# place orders.csv in data/

# Run phases in order
python src/03_power_analysis.py
python src/04_statistical_testing.py
python src/05_dollar_impact_model.py
python src/06_exec_onepager.py
```

SQL files are executed automatically by the Python scripts via DuckDB. No separate database setup required.

---

## Limitations

The Instacart dataset reflects grocery delivery with an 80%+ reorder rate — materially higher than restaurant delivery platforms (estimated 25-35%). The analytical methodology transfers directly to any platform. The specific break-even threshold (6.70pp) should be recalibrated against platform-specific baseline reorder rates before a production decision.

The discount is simulated on historical data, not a live randomized experiment. Results are directional estimates, not causal claims. This limitation is documented explicitly in the experiment design document.

---

## Requirements

```
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0
statsmodels>=0.14.0
duckdb>=0.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

## Industry Relevance

This project directly addresses analytical problems at companies including DoorDash, Instacart, Uber Eats, Grubhub, and any e-commerce or marketplace platform running customer acquisition experiments. The experiment design, SQL funnel structure, and Go/No-Go recommendation framework are transferable to any industry running controlled experiments on promotional spend.

---

## Author

**Akash Singh**  
M.S. Business Analytics &mdash; Iowa State University  
[github.com/aksingh-ops](https://github.com/aksingh-ops) &bull; [LinkedIn](https://www.linkedin.com/in/akash-bhupesh-singh/)

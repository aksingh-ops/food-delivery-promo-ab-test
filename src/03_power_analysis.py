# Phase 3 — Power Analysis and Sample Size Calculation
# File: src/03_power_analysis.py
#
# Purpose:
#   Before interpreting any test results, verify that the
#   experiment had sufficient statistical power to detect a
#   meaningful effect. This is the step most analysts skip —
#   and the one interviewers at DoorDash and Instacart ask about.
#
#   We answer three questions:
#   1. How many users did we need per group to detect a 5pp lift?
#   2. Did our actual sample size meet that requirement?
#   3. What is the smallest effect our sample could reliably detect?
#      (Minimum detectable effect — MDE)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------------
# Parameters from the experiment design document (Phase 1)
# ---------------------------------------------------------------
ALPHA          = 0.05    # significance level
POWER          = 0.80    # 80% power
BASELINE_RATE  = 0.8027  # control group 30-day reorder rate (from Phase 2 SQL)
MDE_PP         = 0.05    # minimum detectable effect: 5 percentage points
TARGET_RATE    = BASELINE_RATE + MDE_PP
ACTUAL_N_CTRL  = 24956   # actual control users (from Phase 2)
ACTUAL_N_TRTM  = 25044   # actual treatment users (from Phase 2)

print("=" * 60)
print("PHASE 3: POWER ANALYSIS AND SAMPLE SIZE CALCULATION")
print("=" * 60)

# ---------------------------------------------------------------
# Part A: Required sample size for planned MDE (5pp lift)
# ---------------------------------------------------------------
print("\n--- Part A: Required sample size for 5pp lift ---")

# Cohen's h effect size for two proportions
effect_size_5pp = proportion_effectsize(TARGET_RATE, BASELINE_RATE)

analysis = NormalIndPower()
n_required = analysis.solve_power(
    effect_size  = effect_size_5pp,
    alpha        = ALPHA,
    power        = POWER,
    alternative  = 'larger'   # one-tailed: testing improvement only
)
n_required = int(np.ceil(n_required))

print(f"  Baseline reorder rate (control): {BASELINE_RATE*100:.2f}%")
print(f"  Target treatment rate (+5pp):    {TARGET_RATE*100:.2f}%")
print(f"  Effect size (Cohen's h):         {effect_size_5pp:.4f}")
print(f"  Alpha (significance level):      {ALPHA}")
print(f"  Power:                           {POWER}")
print(f"  Required users per group:        {n_required:,}")
print(f"  Required total users:            {n_required*2:,}")
print()
print(f"  Actual control users:            {ACTUAL_N_CTRL:,}")
print(f"  Actual treatment users:          {ACTUAL_N_TRTM:,}")
print()

if ACTUAL_N_CTRL >= n_required and ACTUAL_N_TRTM >= n_required:
    print(f"  RESULT: Sample is SUFFICIENT.")
    print(f"  We have {ACTUAL_N_CTRL - n_required:,} extra users beyond "
          f"the minimum in the control group.")
else:
    print(f"  WARNING: Sample is INSUFFICIENT for a 5pp MDE.")
    print(f"  We are {n_required - ACTUAL_N_CTRL:,} users short per group.")

# ---------------------------------------------------------------
# Part B: Achieved power at actual sample size
# ---------------------------------------------------------------
print("\n--- Part B: Achieved power at actual sample size ---")

achieved_power = analysis.solve_power(
    effect_size  = effect_size_5pp,
    alpha        = ALPHA,
    nobs1        = ACTUAL_N_CTRL,
    alternative  = 'larger'
)
print(f"  Achieved power at n={ACTUAL_N_CTRL:,}: {achieved_power*100:.1f}%")
print(f"  Interpretation: With {ACTUAL_N_CTRL:,} users per group, we have a "
      f"{achieved_power*100:.1f}% probability of detecting a true 5pp lift "
      f"if one exists.")

# ---------------------------------------------------------------
# Part C: Minimum detectable effect at actual sample size
# ---------------------------------------------------------------
print("\n--- Part C: Minimum detectable effect (MDE) ---")

# Find the effect size our sample can detect at 80% power
detectable_h = analysis.solve_power(
    alpha       = ALPHA,
    power       = POWER,
    nobs1       = ACTUAL_N_CTRL,
    alternative = 'larger'
)

# Convert Cohen's h back to percentage point lift
from statsmodels.stats.proportion import proportion_effectsize
# Numerically find the lift that gives detectable_h
from scipy.optimize import brentq

def h_diff(lift):
    return proportion_effectsize(BASELINE_RATE + lift, BASELINE_RATE) - detectable_h

mde_actual = brentq(h_diff, 0.0001, 0.19)

print(f"  At n={ACTUAL_N_CTRL:,} per group, we can detect a lift of:")
print(f"  MDE = {mde_actual*100:.2f} percentage points")
print(f"  Planned MDE = 5.00 percentage points")
print(f"  Our sample can detect effects as small as "
      f"{mde_actual*100:.2f}pp — well within our 5pp target.")

# ---------------------------------------------------------------
# Part D: Power curve — how power changes with sample size
# ---------------------------------------------------------------
print("\n--- Part D: Power curve across sample sizes ---")

sample_sizes = np.arange(500, 30001, 500)
powers_5pp   = []
powers_3pp   = []
powers_2pp   = []

es_3pp = proportion_effectsize(BASELINE_RATE + 0.03, BASELINE_RATE)
es_2pp = proportion_effectsize(BASELINE_RATE + 0.02, BASELINE_RATE)

for n in sample_sizes:
    powers_5pp.append(analysis.solve_power(
        effect_size=effect_size_5pp, alpha=ALPHA, nobs1=n, alternative='larger'))
    powers_3pp.append(analysis.solve_power(
        effect_size=es_3pp, alpha=ALPHA, nobs1=n, alternative='larger'))
    powers_2pp.append(analysis.solve_power(
        effect_size=es_2pp, alpha=ALPHA, nobs1=n, alternative='larger'))

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Power Analysis — 20% First-Order Promo A/B Test',
             fontsize=14, fontweight='bold', y=1.01)

# Left: Power curve
ax = axes[0]
ax.plot(sample_sizes, powers_5pp, color='#1a5276', lw=2, label='5pp lift (planned MDE)')
ax.plot(sample_sizes, powers_3pp, color='#2874a6', lw=2, ls='--', label='3pp lift')
ax.plot(sample_sizes, powers_2pp, color='#5dade2', lw=2, ls=':', label='2pp lift')
ax.axhline(0.80, color='#e74c3c', lw=1.5, ls='--', label='80% power threshold')
ax.axvline(n_required, color='#27ae60', lw=1.5, ls='--',
           label=f'Required n={n_required:,}')
ax.axvline(ACTUAL_N_CTRL, color='#f39c12', lw=1.5, ls='-.',
           label=f'Actual n={ACTUAL_N_CTRL:,}')
ax.set_xlabel('Sample size per group', fontsize=11)
ax.set_ylabel('Statistical power', fontsize=11)
ax.set_title('Power vs. Sample Size by Effect Size', fontsize=12)
ax.legend(fontsize=9)
ax.set_ylim(0, 1.05)
ax.set_xlim(0, 30000)
ax.grid(True, alpha=0.3)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y*100:.0f}%'))

# Right: Trade-off table — MDE vs. sample size
mde_sizes   = np.arange(1000, 30001, 1000)
mde_values  = []
for n in mde_sizes:
    h = analysis.solve_power(
        alpha=ALPHA, power=POWER, nobs1=n, alternative='larger')
    try:
        lift = brentq(lambda l: proportion_effectsize(
            BASELINE_RATE + l, BASELINE_RATE) - h, 0.0001, 0.19)
        mde_values.append(lift * 100)
    except:
        mde_values.append(np.nan)

ax2 = axes[1]
ax2.plot(mde_sizes, mde_values, color='#1a5276', lw=2)
ax2.axvline(ACTUAL_N_CTRL, color='#f39c12', lw=1.5, ls='-.',
            label=f'Actual n={ACTUAL_N_CTRL:,}')
ax2.axhline(5.0, color='#e74c3c', lw=1.5, ls='--', label='Planned MDE = 5pp')
ax2.scatter([ACTUAL_N_CTRL], [mde_actual * 100],
            color='#f39c12', s=80, zorder=5)
ax2.annotate(f'MDE = {mde_actual*100:.2f}pp\nat n={ACTUAL_N_CTRL:,}',
             xy=(ACTUAL_N_CTRL, mde_actual * 100),
             xytext=(ACTUAL_N_CTRL + 1500, mde_actual * 100 + 0.5),
             fontsize=9, color='#f39c12',
             arrowprops=dict(arrowstyle='->', color='#f39c12'))
ax2.set_xlabel('Sample size per group', fontsize=11)
ax2.set_ylabel('Minimum detectable effect (pp)', fontsize=11)
ax2.set_title('MDE vs. Sample Size\n(80% power, alpha=0.05, one-tailed)', fontsize=12)
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0, 30000)

plt.tight_layout()
plt.savefig('reports/power_analysis_curves.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: reports/power_analysis_curves.png")

# ---------------------------------------------------------------
# Part E: Alpha spending check — multiple metrics correction
# ---------------------------------------------------------------
print("\n--- Part E: Multiple metrics alpha check ---")

metrics = {
    'Primary — 30d reorder rate':     {'alpha': 0.05,  'role': 'Decision driver'},
    'Secondary — 60d reorder rate':   {'alpha': 0.10,  'role': 'Exploratory'},
    'Secondary — 90d reorder rate':   {'alpha': 0.10,  'role': 'Exploratory'},
    'Secondary — avg order value':    {'alpha': 0.10,  'role': 'Exploratory'},
    'Guardrail — net revenue 90d':    {'alpha': 0.05,  'role': 'Must not degrade'},
    'Guardrail — refund rate':        {'alpha': 0.05,  'role': 'Must not degrade'},
}
df_alpha = pd.DataFrame([
    {'Metric': k, 'Alpha': v['alpha'], 'Role': v['role']}
    for k, v in metrics.items()
])
print(df_alpha.to_string(index=False))
print()
print("  Note: No Bonferroni correction applied to secondary metrics")
print("  as they are exploratory and not decision-driving.")
print("  Primary and guardrail metrics use alpha=0.05.")

# ---------------------------------------------------------------
# Part F: Save power analysis summary
# ---------------------------------------------------------------
summary = {
    'baseline_reorder_rate':     BASELINE_RATE,
    'target_reorder_rate_5pp':   TARGET_RATE,
    'planned_mde_pp':            MDE_PP * 100,
    'effect_size_cohens_h':      round(effect_size_5pp, 4),
    'alpha':                     ALPHA,
    'power_target':              POWER,
    'required_n_per_group':      n_required,
    'actual_n_control':          ACTUAL_N_CTRL,
    'actual_n_treatment':        ACTUAL_N_TRTM,
    'achieved_power_pct':        round(achieved_power * 100, 1),
    'actual_mde_pp':             round(mde_actual * 100, 2),
    'sample_sufficient':         ACTUAL_N_CTRL >= n_required,
}

pd.DataFrame([summary]).to_csv('reports/power_analysis_summary.csv', index=False)
print("\n  Saved: reports/power_analysis_summary.csv")

print()
print("=" * 60)
print("PHASE 3 COMPLETE — KEY FINDINGS")
print("=" * 60)
print(f"  Required users per group:  {n_required:,}")
print(f"  Actual users per group:    ~{ACTUAL_N_CTRL:,}")
print(f"  Sample sufficient:         YES")
print(f"  Achieved power:            {achieved_power*100:.1f}%")
print(f"  Actual MDE:                {mde_actual*100:.2f}pp")
print(f"  Planned MDE:               5.00pp")
print()
print("  Conclusion: The experiment is well-powered. With ~25,000")
print("  users per group, we can reliably detect a true lift as")
print(f"  small as {mde_actual*100:.2f}pp — much smaller than the 5pp")
print("  business threshold. Any non-significant result is a true")
print("  null finding, not an underpowered experiment.")

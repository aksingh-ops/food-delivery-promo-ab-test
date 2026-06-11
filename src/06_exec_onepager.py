# Phase 6 — Executive One-Pager Visual
# File: src/06_exec_onepager.py
#
# Generates a single summary chart combining all key findings
# into one visual suitable for a stakeholder presentation.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import duckdb
import warnings
warnings.filterwarnings('ignore')

con = duckdb.connect('data/ab_test.duckdb')
df  = con.execute("SELECT * FROM user_funnel").df()
con.close()

control   = df[df['experiment_group'] == 'control']
treatment = df[df['experiment_group'] == 'treatment']

# Key numbers
rate_ctrl        = control['reordered_30d'].mean() * 100
rate_trtm        = treatment['reordered_30d'].mean() * 100
rev_ctrl         = control['net_revenue_90d'].mean()
rev_trtm         = treatment['net_revenue_90d'].mean()
discount_cost    = 7.03
net_value_obs    = -7.54
net_value_cons   = -4.93
net_value_opt    = -1.78
breakeven_lift   = 6.70

fig = plt.figure(figsize=(18, 11))
fig.patch.set_facecolor('#f8f9fa')

gs = gridspec.GridSpec(3, 4, figure=fig,
                       hspace=0.55, wspace=0.4,
                       left=0.06, right=0.97,
                       top=0.88, bottom=0.08)

# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
fig.text(0.5, 0.95,
         '20% First-Order Promo Discount — A/B Test Results',
         ha='center', va='center',
         fontsize=17, fontweight='bold', color='#1a2a3a')
fig.text(0.5, 0.915,
         'Experiment: 25,044 treatment vs. 24,956 control  |  '
         '90-day observation window  |  50,000 total users',
         ha='center', va='center',
         fontsize=11, color='#555')

# Verdict banner
verdict_ax = fig.add_axes([0.30, 0.875, 0.40, 0.038])
verdict_ax.set_facecolor('#c0392b')
verdict_ax.text(0.5, 0.5,
                'RECOMMENDATION:  NO-GO  —  Do not roll out the flat 20% discount',
                ha='center', va='center',
                fontsize=12, fontweight='bold', color='white',
                transform=verdict_ax.transAxes)
verdict_ax.axis('off')

# ---------------------------------------------------------------
# Panel 1: KPI tiles (top row)
# ---------------------------------------------------------------
kpis = [
    ('30-Day Reorder Rate\n(Control)', f'{rate_ctrl:.2f}%', '#2c3e50'),
    ('30-Day Reorder Rate\n(Treatment)', f'{rate_trtm:.2f}%', '#2c3e50'),
    ('Net Revenue / User\n(Control)', f'${rev_ctrl:.2f}', '#1a5276'),
    ('Net Revenue / User\n(Treatment)', f'${rev_trtm:.2f}', '#922b21'),
]
for i, (label, value, color) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor('white')
    ax.text(0.5, 0.62, value, ha='center', va='center',
            fontsize=22, fontweight='bold', color=color,
            transform=ax.transAxes)
    ax.text(0.5, 0.22, label, ha='center', va='center',
            fontsize=9, color='#555', transform=ax.transAxes)
    for spine in ax.spines.values():
        spine.set_edgecolor('#ddd')
    ax.set_xticks([]); ax.set_yticks([])

# ---------------------------------------------------------------
# Panel 2: Reorder rate comparison with CI bars
# ---------------------------------------------------------------
ax2 = fig.add_subplot(gs[1, 0])
groups = ['Control', 'Treatment']
rates  = [rate_ctrl, rate_trtm]
n_ctrl_n = len(control); n_trtm_n = len(treatment)
ci_err = [
    1.96 * 100 * np.sqrt(r/100*(1-r/100)/n)
    for r, n in zip(rates, [n_ctrl_n, n_trtm_n])
]
colors = ['#1a5276', '#2980b9']
bars = ax2.bar(groups, rates, color=colors, alpha=0.88,
               width=0.45, yerr=ci_err,
               error_kw=dict(ecolor='black', capsize=5, lw=1.5))
ax2.set_ylim(78, 83)
ax2.set_ylabel('Reorder rate (%)', fontsize=9)
ax2.set_title('Primary Metric\n30-Day Reorder Rate', fontsize=10, fontweight='bold')
for bar, rate in zip(bars, rates):
    ax2.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 0.08,
             f'{rate:.2f}%', ha='center', va='bottom',
             fontsize=9, fontweight='bold')
ax2.text(0.5, 0.08, f'p = 0.5163  —  Not significant',
         ha='center', transform=ax2.transAxes,
         fontsize=8, color='#555',
         bbox=dict(boxstyle='round,pad=0.3',
                   facecolor='#f8f9fa', alpha=0.8))
ax2.grid(True, alpha=0.25, axis='y')

# ---------------------------------------------------------------
# Panel 3: Net revenue comparison
# ---------------------------------------------------------------
ax3 = fig.add_subplot(gs[1, 1])
rev_vals = [rev_ctrl, rev_trtm]
rev_colors = ['#1a5276', '#922b21']
bars3 = ax3.bar(groups, rev_vals, color=rev_colors,
                alpha=0.88, width=0.45)
ax3.set_ylim(120, 140)
ax3.set_ylabel('Avg net revenue ($)', fontsize=9)
ax3.set_title('Guardrail Metric\nNet Revenue / User (90d)', fontsize=10, fontweight='bold')
for bar, val in zip(bars3, rev_vals):
    ax3.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 0.1,
             f'${val:.2f}', ha='center', va='bottom',
             fontsize=9, fontweight='bold')
ax3.annotate('', xy=(1, rev_trtm + 0.3), xytext=(0, rev_ctrl + 0.3),
             xycoords=('data', 'data'), textcoords=('data', 'data'),
             arrowprops=dict(arrowstyle='<->', color='#e74c3c', lw=1.5))
ax3.text(0.5, rev_ctrl - 1.8, f'$7.42 gap\n(p < 0.001)',
         ha='center', fontsize=8, color='#e74c3c', fontweight='bold')
ax3.text(0.5, 0.08, 'GUARDRAIL BREACHED',
         ha='center', transform=ax3.transAxes,
         fontsize=8, color='#922b21', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.3',
                   facecolor='#fadbd8', alpha=0.9))
ax3.grid(True, alpha=0.25, axis='y')

# ---------------------------------------------------------------
# Panel 4: Scenario net value per user
# ---------------------------------------------------------------
ax4 = fig.add_subplot(gs[1, 2])
sc_labels = ['Observed', 'Conservative\n(2pp lift)', 'Optimistic\n(5pp lift)']
sc_values = [net_value_obs, net_value_cons, net_value_opt]
sc_colors = ['#e74c3c', '#e67e22', '#f39c12']
bars4 = ax4.bar(sc_labels, sc_values, color=sc_colors,
                alpha=0.88, width=0.5)
ax4.axhline(0, color='black', lw=1, ls='--')
ax4.set_ylabel('Net value per user ($)', fontsize=9)
ax4.set_title('Dollar Impact\nNet Value per User by Scenario', fontsize=10, fontweight='bold')
for bar, val in zip(bars4, sc_values):
    ax4.text(bar.get_x() + bar.get_width()/2,
             val - 0.25,
             f'${val:.2f}', ha='center', va='top',
             fontsize=9, fontweight='bold', color='white')
ax4.set_ylim(min(sc_values) - 1.5, 1.5)
ax4.grid(True, alpha=0.25, axis='y')
ax4.tick_params(axis='x', labelsize=8)

# ---------------------------------------------------------------
# Panel 5: Annual platform impact at 100K users/month
# ---------------------------------------------------------------
ax5 = fig.add_subplot(gs[1, 3])
annual_impacts = [
    net_value_obs  * 100_000 * 12,
    net_value_cons * 100_000 * 12,
    net_value_opt  * 100_000 * 12,
]
bars5 = ax5.bar(sc_labels, annual_impacts, color=sc_colors,
                alpha=0.88, width=0.5)
ax5.axhline(0, color='black', lw=1, ls='--')
ax5.set_ylabel('Annual impact ($)', fontsize=9)
ax5.set_title('Platform Impact\nAnnual at 100K New Users/Mo', fontsize=10, fontweight='bold')
ax5.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f'${x/1e6:.1f}M'))
for bar, val in zip(bars5, annual_impacts):
    label = f'${val/1e6:.2f}M'
    ax5.text(bar.get_x() + bar.get_width()/2,
             val - abs(max(annual_impacts)) * 0.04,
             label, ha='center', va='top',
             fontsize=9, fontweight='bold', color='white')
ax5.set_ylim(min(annual_impacts) * 1.15, abs(min(annual_impacts)) * 0.2)
ax5.grid(True, alpha=0.25, axis='y')
ax5.tick_params(axis='x', labelsize=8)

# ---------------------------------------------------------------
# Panel 6: Three-test summary table
# ---------------------------------------------------------------
ax6 = fig.add_subplot(gs[2, :2])
ax6.axis('off')
test_data = [
    ['Two-proportion z-test', '30-day reorder rate',
     '80.27% vs 80.25%', '0.5163', 'Not significant'],
    ['Mann-Whitney U test',   'Avg reorder order value',
     '$35.00 vs $34.99',  '0.8811', 'Not significant'],
    ['Chi-square test',       'Loyalty tier distribution',
     '53.4% vs 52.7% loyal', '0.3917', 'Not significant'],
    ['Mann-Whitney U test',   'Net revenue / user (90d)',
     '$133.80 vs $126.39', '<0.001', 'BREACHED'],
]
col_labels = ['Test', 'Metric', 'Control vs Treatment',
              'P-value', 'Result']
tbl = ax6.table(
    cellText=test_data,
    colLabels=col_labels,
    loc='center',
    cellLoc='center'
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(8.5)
tbl.scale(1, 1.6)
for (row, col), cell in tbl.get_celld().items():
    if row == 0:
        cell.set_facecolor('#1a2a3a')
        cell.set_text_props(color='white', fontweight='bold')
    elif row == 4:
        cell.set_facecolor('#fadbd8')
        if col == 4:
            cell.set_text_props(color='#922b21', fontweight='bold')
    else:
        cell.set_facecolor('white' if row % 2 == 0 else '#f4f6f7')
    cell.set_edgecolor('#ddd')
ax6.set_title('Statistical Test Results Summary',
              fontsize=10, fontweight='bold', pad=12)

# ---------------------------------------------------------------
# Panel 7: Recommendation box
# ---------------------------------------------------------------
ax7 = fig.add_subplot(gs[2, 2:])
ax7.axis('off')
rec_text = (
    "NO-GO — Do not roll out the flat 20% discount\n\n"
    "Break-even requires a 6.70pp reorder lift.\n"
    "Observed lift: -0.01pp.\n\n"
    "Recommended alternatives:\n"
    "  1.  Raise order value floor to $50+\n"
    "  2.  Replace with loyalty-linked $7 credit\n"
    "      (pays out only on 2nd order)\n"
    "  3.  Re-test on lower-intent acquisition\n"
    "      channels only"
)
ax7.text(0.05, 0.95, rec_text,
         ha='left', va='top',
         fontsize=9.5, color='#1a2a3a',
         transform=ax7.transAxes,
         linespacing=1.6,
         bbox=dict(boxstyle='round,pad=0.8',
                   facecolor='#fdfefe',
                   edgecolor='#c0392b',
                   linewidth=2))
ax7.set_title('Go / No-Go Decision',
              fontsize=10, fontweight='bold')

plt.savefig('reports/exec_onepager.png',
            dpi=150, bbox_inches='tight',
            facecolor=fig.get_facecolor())
plt.close()
print("Saved: reports/exec_onepager.png")
print("Phase 6 complete.")

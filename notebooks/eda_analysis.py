"""
eda_analysis.py
---------------
Exploratory Data Analysis (EDA) script for the Poll Results Visualizer.
Mirrors a Jupyter Notebook workflow -- run section by section.

Sections:
  0. Setup & data load
  1. Dataset shape, dtypes, missing values
  2. Univariate analysis
  3. Bivariate analysis
  4. Time-series EDA
  5. Demographic deep-dive
  6. Per-poll-type analysis
  7. Correlation & heatmap
  8. Summary table export

Run:
    python notebooks/eda_analysis.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Fix Unicode output on Windows terminal
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ─── Output dir ───────────────────────────────────────────────────
EDA_OUT = "outputs/charts/eda"
os.makedirs(EDA_OUT, exist_ok=True)

sns.set_theme(style="whitegrid", palette="deep", font_scale=1.1)
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False})

PALETTE = ["#4361EE", "#7209B7", "#F72585", "#4CC9F0", "#06D6A0", "#FFB703", "#FB8500"]


def sep(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print("="*60)


def save_fig(fig, name: str) -> None:
    p = os.path.join(EDA_OUT, name)
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> Saved: {p}")


# ══════════════════════════════════════════════════════════════════
# 0. Load data
# ══════════════════════════════════════════════════════════════════
sep("0. LOADING DATA")

CSV = "data/poll_data_cleaned.csv"
if not os.path.exists(CSV):
    print("Cleaned data not found. Running pipeline first...")
    from src.data_generator import generate_all_poll_data
    from src.data_cleaner import clean_pipeline
    generate_all_poll_data("data/poll_data.csv")
    clean_pipeline("data/poll_data.csv", CSV)

df = pd.read_csv(CSV, parse_dates=["date"])
print(f"  Loaded {len(df):,} rows x {df.shape[1]} columns")

# ══════════════════════════════════════════════════════════════════
# 1. Basic EDA
# ══════════════════════════════════════════════════════════════════
sep("1. DATASET OVERVIEW")

print("\n  Shape:", df.shape)
print("\n  Columns:")
for c in df.columns:
    print(f"    {c:<22} {df[c].dtype}")

print("\n  Missing values:")
miss = df.isnull().sum()
print(miss[miss > 0].to_string() if miss.sum() > 0 else "    None")

print("\n  Numeric summary:")
print(df[["confidence_score", "response_score"]].describe().round(3).to_string())

print("\n  Poll type counts:")
print(df["poll_type"].value_counts().to_string())

# ══════════════════════════════════════════════════════════════════
# 2. Univariate Analysis
# ══════════════════════════════════════════════════════════════════
sep("2. UNIVARIATE ANALYSIS")

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle("Univariate Analysis - Categorical Columns", fontsize=15, fontweight="bold")

for ax, col in zip(axes.flat, ["poll_type", "region", "age_group", "gender", "education", "response"]):
    counts = df[col].value_counts()
    ax.barh(counts.index, counts.values, color=PALETTE[:len(counts)])
    ax.set_title(col.replace("_", " ").title(), fontweight="bold")
    ax.set_xlabel("Count")
    for rect, v in zip(ax.patches, counts.values):
        ax.text(rect.get_width() + 50, rect.get_y() + rect.get_height()/2,
                f"{v:,}", va="center", fontsize=9)

fig.tight_layout()
save_fig(fig, "eda_01_univariate_categorical.png")

# Confidence score distribution
fig2, ax2 = plt.subplots(figsize=(10, 4))
sns.histplot(df["confidence_score"], bins=30, kde=True, color=PALETTE[0], ax=ax2)
ax2.set_title("Confidence Score Distribution", fontweight="bold")
ax2.set_xlabel("Confidence Score")
fig2.tight_layout()
save_fig(fig2, "eda_02_confidence_distribution.png")

# Response score distribution (only valid scores)
score_df = df[df["response_score"].notna()]
fig3, ax3 = plt.subplots(figsize=(10, 4))
sns.countplot(data=score_df, x="response_score", palette=PALETTE, ax=ax3)
ax3.set_title("Response Score Distribution (Likert-scale polls)", fontweight="bold")
ax3.set_xlabel("Response Score (1=Lowest, 5=Highest)")
for p in ax3.patches:
    ax3.annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width()/2, p.get_height()),
                 ha="center", va="bottom", fontsize=10)
fig3.tight_layout()
save_fig(fig3, "eda_03_response_score_dist.png")

# ══════════════════════════════════════════════════════════════════
# 3. Bivariate Analysis
# ══════════════════════════════════════════════════════════════════
sep("3. BIVARIATE ANALYSIS")

# Poll type × avg confidence
fig4, ax4 = plt.subplots(figsize=(12, 5))
pt_conf = df.groupby("poll_type")["confidence_score"].mean().sort_values(ascending=False)
ax4.bar(pt_conf.index, pt_conf.values, color=PALETTE[:len(pt_conf)])
ax4.set_title("Avg Confidence Score by Poll Type", fontweight="bold")
ax4.set_ylabel("Avg Confidence Score")
ax4.set_xticklabels(pt_conf.index, rotation=15, ha="right")
for i, v in enumerate(pt_conf.values):
    ax4.text(i, v + 0.003, f"{v:.3f}", ha="center", fontsize=10)
fig4.tight_layout()
save_fig(fig4, "eda_04_polltype_confidence.png")

# Region × response (cross-tab heatmap)
ct = pd.crosstab(df["region"], df["response"])
ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100

fig5, ax5 = plt.subplots(figsize=(14, 5))
sns.heatmap(ct_pct, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=0.5, ax=ax5)
ax5.set_title("Region × Response Cross-tab (%)", fontweight="bold")
ax5.set_xlabel("Response Option")
ax5.set_ylabel("Region")
ax5.set_xticklabels(ax5.get_xticklabels(), rotation=35, ha="right")
fig5.tight_layout()
save_fig(fig5, "eda_05_region_response_heatmap.png")

# ══════════════════════════════════════════════════════════════════
# 4. Time-series EDA
# ══════════════════════════════════════════════════════════════════
sep("4. TIME-SERIES EDA")

monthly = df.groupby("month").size().reset_index(name="count").sort_values("month")

fig6, ax6 = plt.subplots(figsize=(14, 5))
ax6.plot(monthly["month"], monthly["count"], marker="o",
         color=PALETTE[0], linewidth=2.0)
ax6.fill_between(monthly["month"], monthly["count"], alpha=0.12, color=PALETTE[0])
ax6.set_title("Monthly Response Volume", fontweight="bold")
ax6.set_xlabel("Month")
ax6.set_ylabel("Total Responses")
ax6.tick_params(axis="x", rotation=45)
fig6.tight_layout()
save_fig(fig6, "eda_06_monthly_volume.png")

# Monthly avg satisfaction score
score_monthly = (
    score_df.groupby("month")["response_score"]
    .mean().round(2).reset_index()
    .rename(columns={"response_score": "avg_score"})
    .sort_values("month")
)
fig7, ax7 = plt.subplots(figsize=(14, 5))
ax7.plot(score_monthly["month"], score_monthly["avg_score"],
         marker="s", color=PALETTE[2], linewidth=2.0)
ax7.axhline(3.0, color="gray", linestyle="--", linewidth=1.2, label="Neutral (3.0)")
ax7.set_title("Monthly Average Satisfaction Score (Likert Polls)", fontweight="bold")
ax7.set_xlabel("Month")
ax7.set_ylabel("Avg Score (1-5)")
ax7.set_ylim(1, 5.5)
ax7.tick_params(axis="x", rotation=45)
ax7.legend()
fig7.tight_layout()
save_fig(fig7, "eda_07_monthly_avg_score.png")

# ══════════════════════════════════════════════════════════════════
# 5. Demographic Deep-Dive
# ══════════════════════════════════════════════════════════════════
sep("5. DEMOGRAPHIC DEEP-DIVE")

for demo in ["age_group", "gender", "education"]:
    grp = df.groupby([demo, "response"]).size().reset_index(name="count")
    grp["pct"] = grp["count"] / grp.groupby(demo)["count"].transform("sum") * 100

    pivot = grp.pivot_table(index=demo, columns="response", values="pct", fill_value=0)
    fig_d, ax_d = plt.subplots(figsize=(13, 5))
    pivot.plot(kind="bar", stacked=True, ax=ax_d, color=PALETTE[:len(pivot.columns)],
               edgecolor="white", width=0.6)
    ax_d.set_title(f"Response Distribution by {demo.replace('_', ' ').title()}",
                   fontweight="bold")
    ax_d.set_xlabel(demo.replace("_", " ").title())
    ax_d.set_ylabel("Share (%)")
    ax_d.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax_d.set_xticklabels(ax_d.get_xticklabels(), rotation=15, ha="right")
    ax_d.legend(title="Response", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
    fig_d.tight_layout()
    save_fig(fig_d, f"eda_08_demo_{demo}.png")
    print(f"  {demo} breakdown:")
    print(pivot.round(1).to_string())

# ══════════════════════════════════════════════════════════════════
# 6. Per-Poll Summary Table
# ══════════════════════════════════════════════════════════════════
sep("6. PER-POLL SUMMARY TABLE")

summary_rows = []
for pt in df["poll_type"].unique():
    sub = df[df["poll_type"] == pt]
    winner = sub["response"].value_counts().idxmax()
    win_pct = sub["response"].value_counts(normalize=True).max() * 100
    avg_score = sub["response_score"].mean()
    summary_rows.append({
        "Poll Type":       pt,
        "Respondents":     sub["respondent_id"].nunique(),
        "Total Records":   len(sub),
        "Questions":       sub["question"].nunique(),
        "Leading Option":  winner,
        "Leading Share %": round(win_pct, 2),
        "Avg Score (1-5)": round(avg_score, 2) if not np.isnan(avg_score) else "N/A",
        "Avg Confidence":  round(sub["confidence_score"].mean(), 3),
    })

summary_df = pd.DataFrame(summary_rows)
print("\n  Per-Poll Summary:")
print(summary_df.to_string(index=False))

out_path = "outputs/reports/per_poll_summary.csv"
os.makedirs("outputs/reports", exist_ok=True)
summary_df.to_csv(out_path, index=False)
print(f"\n  Summary table saved -> {out_path}")

# ══════════════════════════════════════════════════════════════════
# 7. Correlation
# ══════════════════════════════════════════════════════════════════
sep("7. CORRELATION ANALYSIS")

num_cols = df[["confidence_score", "response_score", "week", "year"]].dropna()
fig8, ax8 = plt.subplots(figsize=(7, 5))
sns.heatmap(num_cols.corr(), annot=True, fmt=".2f", cmap="coolwarm",
            linewidths=0.5, ax=ax8, square=True)
ax8.set_title("Correlation Matrix (Numeric Features)", fontweight="bold")
fig8.tight_layout()
save_fig(fig8, "eda_09_correlation_matrix.png")

sep("EDA COMPLETE")
print(f"\n  All EDA charts saved to: {EDA_OUT}")
print(f"  Summary CSV saved to   : outputs/reports/per_poll_summary.csv")

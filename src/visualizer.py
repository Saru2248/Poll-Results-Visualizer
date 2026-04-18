"""
visualizer.py
-------------
All chart generation for the Poll Results Visualizer.

Charts produced:
  01 - Bar chart: Overall response share (per poll type)
  02 - Pie chart: Vote/response distribution
  03 - Stacked bar: Region-wise response breakdown
  04 - Grouped bar: Demographic (age/gender) comparison
  05 - Line chart: Monthly response trend
  06 - Heatmap: Region × response matrix
  07 - Box plot: Confidence score distribution
  08 - Multi-poll comparison bar chart

All charts saved to outputs/charts/
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")            # non-interactive backend (safe in all envs)
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

# ─────────────────────────────────────────────────────────────────
# Global style
# ─────────────────────────────────────────────────────────────────

PALETTE = [
    "#4361EE", "#3A0CA3", "#7209B7", "#F72585",
    "#4CC9F0", "#06D6A0", "#FFB703", "#FB8500",
]
CHART_DIR = "outputs/charts"
os.makedirs(CHART_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "figure.dpi":       120,
})


def _save(fig: plt.Figure, filename: str) -> str:
    path = os.path.join(CHART_DIR, filename)
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved → {path}")
    return path


# ─────────────────────────────────────────────────────────────────
# Chart 01 – Horizontal Bar: Overall Response Share
# ─────────────────────────────────────────────────────────────────

def plot_overall_share(share_df: pd.DataFrame, poll_type: str) -> str:
    """
    Horizontal bar chart of overall vote/response share.
    share_df cols: response, count, percentage
    """
    share_df = share_df.sort_values("percentage")

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(
        share_df["response"], share_df["percentage"],
        color=PALETTE[:len(share_df)], edgecolor="white", height=0.55,
    )
    ax.bar_label(bars, labels=[f"{v:.1f}%" for v in share_df["percentage"]],
                 padding=4, fontsize=11, fontweight="bold")

    ax.set_xlabel("Share (%)", fontsize=11)
    ax.set_title(f"Overall Response Share\n{poll_type}", fontsize=14, fontweight="bold", pad=12)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_xlim(0, share_df["percentage"].max() + 12)
    fig.tight_layout()

    fname = f"01_overall_share_{poll_type.replace(' ', '_').lower()}.png"
    return _save(fig, fname)


# ─────────────────────────────────────────────────────────────────
# Chart 02 – Donut / Pie: Response Distribution
# ─────────────────────────────────────────────────────────────────

def plot_pie_chart(share_df: pd.DataFrame, poll_type: str) -> str:
    """Donut chart of response distribution."""
    fig, ax = plt.subplots(figsize=(8, 8))

    wedges, texts, autotexts = ax.pie(
        share_df["percentage"],
        labels=share_df["response"],
        autopct="%1.1f%%",
        pctdistance=0.78,
        colors=PALETTE[:len(share_df)],
        startangle=140,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )

    # Donut hole
    centre_circle = plt.Circle((0, 0), 0.55, fc="white")
    ax.add_patch(centre_circle)

    for at in autotexts:
        at.set_fontsize(11)
        at.set_fontweight("bold")

    ax.set_title(f"Response Distribution\n{poll_type}", fontsize=14, fontweight="bold", pad=14)
    fig.tight_layout()

    fname = f"02_pie_chart_{poll_type.replace(' ', '_').lower()}.png"
    return _save(fig, fname)


# ─────────────────────────────────────────────────────────────────
# Chart 03 – Stacked Bar: Region-wise Breakdown
# ─────────────────────────────────────────────────────────────────

def plot_region_stacked_bar(region_pct_df: pd.DataFrame, poll_type: str) -> str:
    """
    Stacked bar chart: each bar = one region, segments = response %.
    region_pct_df: pivot table (index=region, columns=response, values=%)
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    region_pct_df.plot(
        kind="bar", stacked=True, ax=ax,
        color=PALETTE[:len(region_pct_df.columns)],
        edgecolor="white", width=0.6,
    )
    ax.set_xlabel("Region / Group", fontsize=11)
    ax.set_ylabel("Share (%)", fontsize=11)
    ax.set_title(f"Region-wise Response Breakdown\n{poll_type}", fontsize=14, fontweight="bold")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.legend(title="Response", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()

    fname = f"03_region_stacked_{poll_type.replace(' ', '_').lower()}.png"
    return _save(fig, fname)


# ─────────────────────────────────────────────────────────────────
# Chart 04 – Grouped Bar: Demographic Comparison
# ─────────────────────────────────────────────────────────────────

def plot_demographic_grouped_bar(
    demo_df: pd.DataFrame,
    demo_col: str,
    poll_type: str,
) -> str:
    """
    Grouped bar chart: x = demographic group, hue = response option.
    demo_df: long form with cols [demo_col, response, percentage]
    """
    n_responses = demo_df["response"].nunique()
    palette = PALETTE[:n_responses]
    fig, ax = plt.subplots(figsize=(13, 6))
    sns.barplot(
        data=demo_df, x=demo_col, y="percentage", hue="response",
        palette=palette, ax=ax, edgecolor="white",
    )
    ax.set_xlabel(demo_col.replace("_", " ").title(), fontsize=11)
    ax.set_ylabel("Share (%)", fontsize=11)
    ax.set_title(
        f"Demographic Comparison ({demo_col.replace('_', ' ').title()})\n{poll_type}",
        fontsize=14, fontweight="bold",
    )
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.xaxis.set_major_locator(plt.FixedLocator(range(demo_df[demo_col].nunique())))
    ax.set_xticklabels(sorted(demo_df[demo_col].unique()), rotation=20, ha="right")
    ax.legend(title="Response", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    fig.tight_layout()

    fname = f"04_demographic_{demo_col}_{poll_type.replace(' ', '_').lower()}.png"
    return _save(fig, fname)


# ─────────────────────────────────────────────────────────────────
# Chart 05 – Line: Monthly Response Trend
# ─────────────────────────────────────────────────────────────────

def plot_monthly_trend(trend_df: pd.DataFrame, poll_type: str) -> str:
    """
    Line chart of monthly percentage per response option.
    trend_df cols: month, response, count, percentage
    """
    fig, ax = plt.subplots(figsize=(13, 5))

    for idx, resp in enumerate(trend_df["response"].unique()):
        sub = trend_df[trend_df["response"] == resp].sort_values("month")
        ax.plot(
            sub["month"], sub["percentage"],
            marker="o", linewidth=2.2,
            color=PALETTE[idx % len(PALETTE)], label=resp,
        )
        ax.fill_between(sub["month"], sub["percentage"], alpha=0.08,
                        color=PALETTE[idx % len(PALETTE)])

    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Share (%)", fontsize=11)
    ax.set_title(f"Monthly Response Trend\n{poll_type}", fontsize=14, fontweight="bold")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.tick_params(axis="x", rotation=45)
    ax.legend(title="Response", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    fig.tight_layout()

    fname = f"05_monthly_trend_{poll_type.replace(' ', '_').lower()}.png"
    return _save(fig, fname)


# ─────────────────────────────────────────────────────────────────
# Chart 06 – Heatmap: Region × Response Matrix
# ─────────────────────────────────────────────────────────────────

def plot_heatmap(region_pct_df: pd.DataFrame, poll_type: str) -> str:
    """
    Heatmap of region × response percentages.
    """
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.heatmap(
        region_pct_df,
        annot=True, fmt=".1f", cmap="YlOrRd",
        linewidths=0.5, linecolor="white",
        ax=ax, cbar_kws={"label": "Share (%)"},
    )
    ax.set_title(f"Region × Response Heatmap\n{poll_type}", fontsize=14, fontweight="bold")
    ax.set_xlabel("Response Option", fontsize=11)
    ax.set_ylabel("Region", fontsize=11)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()

    fname = f"06_heatmap_{poll_type.replace(' ', '_').lower()}.png"
    return _save(fig, fname)


# ─────────────────────────────────────────────────────────────────
# Chart 07 – Box Plot: Confidence Score Distribution
# ─────────────────────────────────────────────────────────────────

def plot_confidence_boxplot(df: pd.DataFrame) -> str:
    """Box plot of confidence scores across all poll types."""
    fig, ax = plt.subplots(figsize=(11, 5))
    poll_order = df["poll_type"].unique().tolist()
    sns.boxplot(
        data=df, x="poll_type", y="confidence_score",
        palette=PALETTE, order=poll_order,
        width=0.5, linewidth=1.5, ax=ax,
        flierprops={"marker": "o", "markerfacecolor": "#F72585", "markersize": 4},
    )
    ax.set_xlabel("Poll Type", fontsize=11)
    ax.set_ylabel("Confidence Score", fontsize=11)
    ax.set_title("Confidence Score Distribution by Poll Type", fontsize=14, fontweight="bold")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout()

    fname = "07_confidence_boxplot.png"
    return _save(fig, fname)


# ─────────────────────────────────────────────────────────────────
# Chart 08 – Multi-Poll Comparison: Avg Response Score
# ─────────────────────────────────────────────────────────────────

def plot_avg_score_comparison(df: pd.DataFrame) -> str:
    """
    Bar chart comparing average response scores across poll types.
    Only includes polls with a numeric response_score.
    """
    score_df = (
        df[df["response_score"].notna()]
        .groupby("poll_type")["response_score"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"response_score": "avg_score"})
        .sort_values("avg_score", ascending=False)
    )

    if score_df.empty:
        print("  No numeric scores available for comparison chart. Skipping.")
        return ""

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(
        score_df["poll_type"], score_df["avg_score"],
        color=PALETTE[:len(score_df)], edgecolor="white", width=0.5,
    )
    ax.bar_label(bars, labels=[f"{v:.2f}" for v in score_df["avg_score"]],
                 padding=4, fontsize=12, fontweight="bold")
    ax.set_xlabel("Poll Type", fontsize=11)
    ax.set_ylabel("Avg Satisfaction Score (out of 5)", fontsize=11)
    ax.set_title("Average Satisfaction Score – Cross-Poll Comparison",
                 fontsize=14, fontweight="bold")
    ax.set_ylim(0, 5.5)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout()

    fname = "08_avg_score_comparison.png"
    return _save(fig, fname)


# ─────────────────────────────────────────────────────────────────
# Master runner
# ─────────────────────────────────────────────────────────────────

def generate_all_charts(df: pd.DataFrame) -> list:
    """
    Generate all charts for every poll type.
    Returns list of saved file paths.
    """
    from src.analyzer import (
        overall_response_share,
        region_wise_analysis,
        demographic_breakdown,
        monthly_trend,
    )

    saved = []
    poll_types = df["poll_type"].unique().tolist()

    print("\n=== Generating Charts ===")
    for pt in poll_types:
        print(f"\n  Poll type: {pt}")

        # 01 – Bar chart
        share = overall_response_share(df, pt)
        saved.append(plot_overall_share(share, pt))

        # 02 – Pie chart
        saved.append(plot_pie_chart(share, pt))

        # 03 – Region stacked bar
        rpct = region_wise_analysis(df, pt)
        saved.append(plot_region_stacked_bar(rpct, pt))

        # 04 – Age-group grouped bar
        age_demo = demographic_breakdown(df, "age_group", pt)
        saved.append(plot_demographic_grouped_bar(age_demo, "age_group", pt))

        # 04b – Gender grouped bar
        gen_demo = demographic_breakdown(df, "gender", pt)
        saved.append(plot_demographic_grouped_bar(gen_demo, "gender", pt))

        # 05 – Monthly trend
        trend = monthly_trend(df, pt)
        saved.append(plot_monthly_trend(trend, pt))

        # 06 – Heatmap
        saved.append(plot_heatmap(rpct, pt))

    # 07 – Confidence boxplot (all polls)
    saved.append(plot_confidence_boxplot(df))

    # 08 – Avg score comparison
    saved.append(plot_avg_score_comparison(df))

    saved = [s for s in saved if s]   # remove empty strings
    print(f"\n  Total charts generated: {len(saved)}")
    return saved


if __name__ == "__main__":
    df = pd.read_csv("data/poll_data_cleaned.csv", parse_dates=["date"])
    generate_all_charts(df)

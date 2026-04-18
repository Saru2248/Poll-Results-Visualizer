"""
analyzer.py
-----------
Core analysis engine for the Poll Results Visualizer.

Provides:
  - vote / response share calculations
  - region-wise breakdown
  - demographic (age, gender, education) analysis
  - trend analysis over time
  - leading option identification
  - summary insights generation
"""

import pandas as pd
import numpy as np


# ─────────────────────────────────────────────────────────────────
# Helper: percentage table
# ─────────────────────────────────────────────────────────────────

def pct_table(series: pd.Series, label: str = "response") -> pd.DataFrame:
    """Return value-count + percentage DataFrame for a series."""
    counts = series.value_counts().reset_index()
    counts.columns = [label, "count"]
    counts["percentage"] = (counts["count"] / counts["count"].sum() * 100).round(2)
    counts["share_label"] = counts["percentage"].astype(str) + "%"
    return counts


# ─────────────────────────────────────────────────────────────────
# 1. Overall Response Share
# ─────────────────────────────────────────────────────────────────

def overall_response_share(df: pd.DataFrame, poll_type: str = None) -> pd.DataFrame:
    """
    Calculate overall vote/response share for a poll type.
    If poll_type is None, uses the entire dataset.
    """
    if poll_type:
        df = df[df["poll_type"] == poll_type].copy()

    # If multiple questions exist, aggregate across all
    result = pct_table(df["response"])
    result = result.sort_values("percentage", ascending=False).reset_index(drop=True)
    return result


def per_question_share(df: pd.DataFrame, poll_type: str) -> dict:
    """
    For surveys with multiple questions, calculate share per question.
    Returns dict: {question_text: DataFrame}
    """
    subset = df[df["poll_type"] == poll_type]
    results = {}
    for q in subset["question"].unique():
        q_df = subset[subset["question"] == q]
        results[q] = pct_table(q_df["response"])
    return results


# ─────────────────────────────────────────────────────────────────
# 2. Region-wise Analysis
# ─────────────────────────────────────────────────────────────────

def region_wise_analysis(df: pd.DataFrame, poll_type: str = None) -> pd.DataFrame:
    """
    Cross-tabulate region vs response (counts).
    Returns a pivot table with percentage share per region.
    """
    if poll_type:
        df = df[df["poll_type"] == poll_type].copy()

    pivot = pd.crosstab(df["region"], df["response"])
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0).mul(100).round(2)
    return pivot_pct


def region_response_long(df: pd.DataFrame, poll_type: str = None) -> pd.DataFrame:
    """
    Long-form region × response DataFrame with percentage.
    Useful for grouped bar charts.
    """
    if poll_type:
        df = df[df["poll_type"] == poll_type].copy()

    grp = (
        df.groupby(["region", "response"])
        .size()
        .reset_index(name="count")
    )
    grp["total_region"] = grp.groupby("region")["count"].transform("sum")
    grp["percentage"] = (grp["count"] / grp["total_region"] * 100).round(2)
    return grp


# ─────────────────────────────────────────────────────────────────
# 3. Demographic Analysis
# ─────────────────────────────────────────────────────────────────

def demographic_breakdown(
    df: pd.DataFrame,
    demo_col: str = "age_group",
    poll_type: str = None,
) -> pd.DataFrame:
    """
    Breakdown of responses by a demographic column.
    demo_col: 'age_group', 'gender', or 'education'
    """
    if poll_type:
        df = df[df["poll_type"] == poll_type].copy()

    grp = (
        df.groupby([demo_col, "response"])
        .size()
        .reset_index(name="count")
    )
    grp["total_demo"] = grp.groupby(demo_col)["count"].transform("sum")
    grp["percentage"] = (grp["count"] / grp["total_demo"] * 100).round(2)
    return grp


# ─────────────────────────────────────────────────────────────────
# 4. Trend Analysis (Time Series)
# ─────────────────────────────────────────────────────────────────

def monthly_trend(df: pd.DataFrame, poll_type: str = None) -> pd.DataFrame:
    """
    Monthly response count trend.
    Returns DataFrame with columns: month, response, count, percentage.
    """
    if poll_type:
        df = df[df["poll_type"] == poll_type].copy()

    grp = (
        df.groupby(["month", "response"])
        .size()
        .reset_index(name="count")
    )
    grp["total_month"] = grp.groupby("month")["count"].transform("sum")
    grp["percentage"] = (grp["count"] / grp["total_month"] * 100).round(2)
    grp = grp.sort_values("month")
    return grp


def satisfaction_score_trend(df: pd.DataFrame, poll_type: str) -> pd.DataFrame:
    """
    For Likert-scale surveys: compute average response_score per month.
    """
    subset = df[(df["poll_type"] == poll_type) & (df["response_score"].notna())]
    trend = (
        subset.groupby("month")["response_score"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"response_score": "avg_score"})
    )
    return trend.sort_values("month")


# ─────────────────────────────────────────────────────────────────
# 5. Leading Option / Winner Detection
# ─────────────────────────────────────────────────────────────────

def get_winner(df: pd.DataFrame, poll_type: str = None) -> dict:
    """
    Identify the leading response option overall and per region.
    Returns a dict with:
      {
        'overall_winner': str,
        'overall_share': float,
        'regional_winners': DataFrame
      }
    """
    if poll_type:
        df = df[df["poll_type"] == poll_type].copy()

    overall = overall_response_share(df)
    winner = overall.iloc[0]["response"]
    winner_share = overall.iloc[0]["percentage"]

    # Regional winners
    region_pct = region_wise_analysis(df)
    regional_winners = region_pct.idxmax(axis=1).reset_index()
    regional_winners.columns = ["region", "leading_option"]
    regional_winners["leading_share_%"] = region_pct.max(axis=1).values

    return {
        "overall_winner": winner,
        "overall_share": winner_share,
        "regional_winners": regional_winners,
    }


# ─────────────────────────────────────────────────────────────────
# 6. Summary Statistics
# ─────────────────────────────────────────────────────────────────

def summary_statistics(df: pd.DataFrame, poll_type: str) -> dict:
    """
    Generate a dictionary of key summary statistics for a poll type.
    """
    subset = df[df["poll_type"] == poll_type]

    stats = {
        "poll_type":         poll_type,
        "total_respondents": subset["respondent_id"].nunique(),
        "total_responses":   len(subset),
        "questions_count":   subset["question"].nunique(),
        "date_range":        f"{subset['date'].min().date()} → {subset['date'].max().date()}",
        "regions":           subset["region"].nunique(),
        "response_options":  subset["response"].nunique(),
        "avg_confidence":    round(subset["confidence_score"].mean(), 3),
    }

    if subset["response_score"].notna().any():
        stats["avg_response_score"] = round(subset["response_score"].mean(), 2)

    winner_info = get_winner(df, poll_type)
    stats["overall_winner"]       = winner_info["overall_winner"]
    stats["winner_share_%"]       = winner_info["overall_share"]
    stats["regional_winners"]     = winner_info["regional_winners"]

    return stats


# ─────────────────────────────────────────────────────────────────
# 7. Insights Generator
# ─────────────────────────────────────────────────────────────────

def generate_insights(df: pd.DataFrame) -> list:
    """
    Produce a bullet-point list of automated insights across all poll types.
    Returns a list of strings.
    """
    insights = []
    poll_types = df["poll_type"].unique()

    for pt in poll_types:
        stats = summary_statistics(df, pt)
        w = stats["overall_winner"]
        ws = stats["winner_share_%"]
        insights.append(
            f"[{pt}]  Leading option: '{w}' with {ws}% share "
            f"across {stats['total_respondents']:,} respondents."
        )

        # Regional insight
        rw = stats["regional_winners"]
        dominant_regions = rw[rw["leading_option"] == w]["region"].tolist()
        if dominant_regions:
            insights.append(
                f"  → '{w}' leads in regions: {', '.join(dominant_regions)}."
            )

        # Satisfaction score insight
        if "avg_response_score" in stats:
            score = stats["avg_response_score"]
            label = (
                "High satisfaction" if score >= 3.5
                else "Moderate satisfaction" if score >= 2.5
                else "Low satisfaction"
            )
            insights.append(
                f"  → Average response score: {score}/5.0 ({label})."
            )

    # Cross-poll insight
    all_scores = df[df["response_score"].notna()].groupby("poll_type")["response_score"].mean()
    if not all_scores.empty:
        best_poll = all_scores.idxmax()
        best_score = round(all_scores.max(), 2)
        insights.append(
            f"\n[CROSS-POLL]  Highest avg satisfaction score: '{best_poll}' ({best_score}/5.0)."
        )

    return insights


if __name__ == "__main__":
    df = pd.read_csv("data/poll_data_cleaned.csv", parse_dates=["date"])

    print("\n=== OVERALL RESPONSE SHARE (Election Poll) ===")
    print(overall_response_share(df, "Election Preference"))

    print("\n=== REGIONAL WINNERS ===")
    result = get_winner(df, "Election Preference")
    print(result["regional_winners"])

    print("\n=== AUTOMATED INSIGHTS ===")
    insights = generate_insights(df)
    for ins in insights:
        print(ins)

"""
report_generator.py
-------------------
Generates a text-based summary report saved to outputs/reports/
covering:
  - Dataset overview
  - Per-poll type statistics
  - Regional winners
  - Key insights
"""

import os
import pandas as pd
from datetime import datetime
from src.analyzer import summary_statistics, generate_insights


REPORT_DIR = "outputs/reports"
os.makedirs(REPORT_DIR, exist_ok=True)


def _divider(char: str = "-", width: int = 60) -> str:
    return char * width


def generate_text_report(df: pd.DataFrame) -> str:
    """
    Build a full text report and save it.
    Returns the path to the saved file.
    """
    lines = []

    lines.append("=" * 60)
    lines.append("        POLL RESULTS VISUALIZER -- ANALYSIS REPORT")
    lines.append(f"        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)

    # -- Dataset Overview -----------------------------------------
    lines.append("\n1. DATASET OVERVIEW")
    lines.append(_divider())
    lines.append(f"   Total records          : {len(df):,}")
    lines.append(f"   Unique poll types      : {df['poll_type'].nunique()}")
    lines.append(f"   Unique respondents     : {df['respondent_id'].nunique():,}")
    lines.append(f"   Date range             : {df['date'].min().date()} → {df['date'].max().date()}")
    lines.append(f"   Columns                : {', '.join(df.columns.tolist())}")

    lines.append("\n   Poll Type Distribution:")
    pt_counts = df["poll_type"].value_counts()
    for pt, cnt in pt_counts.items():
        lines.append(f"     • {pt:<28} {cnt:>6,} records")

    # -- Per-Poll Analysis -----------------------------------------
    lines.append("\n\n2. PER-POLL TYPE ANALYSIS")
    lines.append(_divider())

    for pt in df["poll_type"].unique():
        stats = summary_statistics(df, pt)
        lines.append(f"\n   [{pt.upper()}]")
        lines.append(f"   Respondents     : {stats['total_respondents']:,}")
        lines.append(f"   Total responses : {stats['total_responses']:,}")
        lines.append(f"   Questions       : {stats['questions_count']}")
        lines.append(f"   Date range      : {stats['date_range']}")
        lines.append(f"   Regions/Groups  : {stats['regions']}")
        lines.append(f"   Avg confidence  : {stats['avg_confidence']}")
        lines.append(f"   Overall winner  : {stats['overall_winner']} ({stats['winner_share_%']}%)")

        if "avg_response_score" in stats:
            lines.append(f"   Avg score (1-5) : {stats['avg_response_score']}")

        lines.append("   Regional leaders:")
        rw = stats["regional_winners"]
        for _, row in rw.iterrows():
            lines.append(
                f"     {row['region']:<14} → {row['leading_option']:<22} "
                f"({row['leading_share_%']:.1f}%)"
            )

    # -- Automated Insights ----------------------------------------
    lines.append("\n\n3. KEY AUTOMATED INSIGHTS")
    lines.append(_divider())
    insights = generate_insights(df)
    for ins in insights:
        lines.append(f"   {ins}")

    # -- Recommendations -------------------------------------------
    lines.append("\n\n4. RECOMMENDATIONS FOR DECISION MAKERS")
    lines.append(_divider())
    lines.append("   • Focus campaign resources on regions showing lower leader share.")
    lines.append("   • Address dissatisfaction trends identified in monthly trend charts.")
    lines.append("   • Segment outreach by age group where preferences diverge significantly.")
    lines.append("   • Deploy follow-up surveys in regions with high 'Undecided' or 'Neutral'.")
    lines.append("   • Use demographic heatmaps to personalise product/service messaging.")

    lines.append("\n" + "=" * 60)
    lines.append("              END OF REPORT")
    lines.append("=" * 60 + "\n")

    report_text = "\n".join(lines)

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORT_DIR, f"poll_analysis_report_{ts}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"  Report saved → {path}")
    return path


if __name__ == "__main__":
    df = pd.read_csv("data/poll_data_cleaned.csv", parse_dates=["date"])
    path = generate_text_report(df)
    print(f"\nReport generated at: {path}")

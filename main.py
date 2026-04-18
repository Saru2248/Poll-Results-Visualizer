"""
main.py
-------
Poll Results Visualizer -- Master Entry Point

Orchestrates the full pipeline:
  Step 1 → Generate synthetic poll data
  Step 2 → Clean & preprocess the data
  Step 3 → Run analysis
  Step 4 → Generate all charts
  Step 5 → Generate text report
  Step 6 → Print summary insights to console

Run:
    python main.py
"""

import sys
import os
import time
import pandas as pd

# Fix Unicode output on Windows terminal
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─── Ensure project root is on the path ───────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def banner(title: str) -> None:
    width = 60
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def step(num: int, desc: str) -> None:
    print(f"\n[Step {num}] {desc}")
    print("-" * 50)


# ─────────────────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────────────────

def main():
    start_time = time.time()

    banner("POLL RESULTS VISUALIZER  |  Full Pipeline Run")
    print("  Author   : Data Science Portfolio Project")
    print("  Version  : 1.0.0")
    print("  Python   : " + sys.version.split(" ")[0])

    # ── Step 1: Generate data ─────────────────────────────────────
    step(1, "Generating Synthetic Poll Datasets")
    from src.data_generator import generate_all_poll_data
    raw_df = generate_all_poll_data(save_path="data/poll_data.csv")

    # ── Step 2: Clean data ────────────────────────────────────────
    step(2, "Cleaning & Preprocessing Data")
    from src.data_cleaner import clean_pipeline
    df = clean_pipeline(
        input_path="data/poll_data.csv",
        output_path="data/poll_data_cleaned.csv",
    )

    # ── Step 3: Analysis ──────────────────────────────────────────
    step(3, "Running Analysis")
    from src.analyzer import (
        overall_response_share,
        get_winner,
        summary_statistics,
        generate_insights,
    )

    print("\n  === Summary Statistics per Poll Type ===")
    for pt in df["poll_type"].unique():
        stats = summary_statistics(df, pt)
        print(f"\n  [{pt}]")
        print(f"    Respondents  : {stats['total_respondents']:,}")
        print(f"    Winner       : {stats['overall_winner']} ({stats['winner_share_%']}%)")
        if "avg_response_score" in stats:
            print(f"    Avg Score    : {stats['avg_response_score']} / 5.0")

    # ── Step 4: Charts ────────────────────────────────────────────
    step(4, "Generating Visualizations")
    from src.visualizer import generate_all_charts
    saved_charts = generate_all_charts(df)

    # ── Step 5: Report ────────────────────────────────────────────
    step(5, "Generating Text Report")
    from src.report_generator import generate_text_report
    report_path = generate_text_report(df)

    # ── Step 6: Print Insights ────────────────────────────────────
    step(6, "Key Automated Insights")
    insights = generate_insights(df)
    for ins in insights:
        print(f"  {ins}")

    # ── Final summary ─────────────────────────────────────────────
    elapsed = round(time.time() - start_time, 2)
    banner("PIPELINE COMPLETE")
    print(f"  Total records processed  : {len(df):,}")
    print(f"  Charts generated         : {len(saved_charts)}")
    print(f"  Report saved             : {report_path}")
    print(f"  Time elapsed             : {elapsed}s")
    print(f"\n  Charts directory  → outputs/charts/")
    print(f"  Reports directory → outputs/reports/")
    print("\n  Run the Streamlit dashboard:")
    print("    streamlit run dashboard.py")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

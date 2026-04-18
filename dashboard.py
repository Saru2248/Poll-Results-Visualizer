"""
dashboard.py
------------
Interactive Streamlit Dashboard for Poll Results Visualizer.

Features:
  - Sidebar poll type selector
  - KPI metric cards
  - Interactive Plotly charts (bar, pie, stacked, heatmap, line, scatter)
  - Region-wise & demographic drill-down
  - Raw data table with filters
  - Downloadable filtered CSV

Run:
    streamlit run dashboard.py
"""

import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────────────────────────
# Page config (MUST be first Streamlit call)
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Poll Results Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# Custom CSS — dark premium theme
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15, 12, 41, 0.85);
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 18px 20px;
    backdrop-filter: blur(10px);
}
[data-testid="stMetricValue"]  { font-size: 2rem !important; font-weight: 800; color: #7c3aed !important; }
[data-testid="stMetricLabel"]  { font-size: 0.82rem !important; color: #94a3b8 !important; }
[data-testid="stMetricDelta"]  { font-size: 0.80rem !important; }

/* Headings */
h1 { color: #a78bfa !important; font-weight: 800; letter-spacing: -0.5px; }
h2 { color: #c4b5fd !important; font-weight: 700; }
h3 { color: #ddd6fe !important; font-weight: 600; }

/* Divider */
hr { border-color: rgba(255,255,255,0.1); }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.05); border-radius: 10px; }
.stTabs [data-baseweb="tab"]      { color: #94a3b8; }
.stTabs [aria-selected="true"]    { color: #a78bfa !important; border-bottom-color: #a78bfa !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* Select boxes & widgets */
.stSelectbox label, .stMultiSelect label, .stSlider label { color: #c4b5fd !important; font-weight: 600; }

/* Buttons */
.stDownloadButton button {
    background: linear-gradient(90deg, #7c3aed, #4f46e5);
    color: white; border: none; border-radius: 8px;
    font-weight: 600; padding: 0.4rem 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# Plotly template (dark)
# ─────────────────────────────────────────────────────────────────
PLOTLY_TEMPLATE = "plotly_dark"
COLOR_SEQ = px.colors.qualitative.Vivid

# ─────────────────────────────────────────────────────────────────
# Data loader (cached)
# ─────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load cleaned poll data. Generate if not found."""
    path = "data/poll_data_cleaned.csv"
    if not os.path.exists(path):
        with st.spinner("Generating synthetic poll data for first run…"):
            from src.data_generator import generate_all_poll_data
            from src.data_cleaner import clean_pipeline
            generate_all_poll_data("data/poll_data.csv")
            clean_pipeline("data/poll_data.csv", path)
    df = pd.read_csv(path, parse_dates=["date"])
    df["month_label"] = df["date"].dt.strftime("%b %Y")
    df["month_sort"]  = df["date"].dt.to_period("M").astype(str)
    return df


# ─────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────
def render_header():
    col_icon, col_title = st.columns([0.07, 0.93])
    with col_icon:
        st.markdown("## 📊")
    with col_title:
        st.markdown("# Poll Results Visualizer")
        st.caption("Interactive analytics dashboard for survey & poll data · Data Science Portfolio Project")
    st.markdown("---")


# ─────────────────────────────────────────────────────────────────
# Sidebar filters
# ─────────────────────────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame):
    st.sidebar.markdown("## 🎛️ Filters")
    st.sidebar.markdown("---")

    poll_types = ["All"] + sorted(df["poll_type"].unique().tolist())
    selected_poll = st.sidebar.selectbox("📋 Poll Type", poll_types, index=0)

    regions = ["All"] + sorted(df["region"].unique().tolist())
    selected_regions = st.sidebar.multiselect("🌍 Region / Group", regions[1:],
                                               default=regions[1:])

    age_groups = sorted(df["age_group"].unique().tolist())
    selected_ages = st.sidebar.multiselect("👤 Age Group", age_groups, default=age_groups)

    genders = sorted(df["gender"].unique().tolist())
    selected_genders = st.sidebar.multiselect("⚧ Gender", genders, default=genders)

    date_min = df["date"].min().date()
    date_max = df["date"].max().date()
    date_range = st.sidebar.date_input(
        "📅 Date Range",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.info(
        "This dashboard visualizes synthetic poll data "
        "covering 5 real-world survey scenarios."
    )

    return {
        "poll_type": selected_poll,
        "regions":   selected_regions if selected_regions else df["region"].unique().tolist(),
        "ages":      selected_ages    if selected_ages    else age_groups,
        "genders":   selected_genders if selected_genders else genders,
        "date_range": date_range,
    }


# ─────────────────────────────────────────────────────────────────
# Apply filters
# ─────────────────────────────────────────────────────────────────
def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    fdf = df.copy()
    if filters["poll_type"] != "All":
        fdf = fdf[fdf["poll_type"] == filters["poll_type"]]
    fdf = fdf[fdf["region"].isin(filters["regions"])]
    fdf = fdf[fdf["age_group"].isin(filters["ages"])]
    fdf = fdf[fdf["gender"].isin(filters["genders"])]
    if len(filters["date_range"]) == 2:
        d0, d1 = filters["date_range"]
        fdf = fdf[(fdf["date"].dt.date >= d0) & (fdf["date"].dt.date <= d1)]
    return fdf


# ─────────────────────────────────────────────────────────────────
# KPI Cards
# ─────────────────────────────────────────────────────────────────
def render_kpis(df: pd.DataFrame, full_df: pd.DataFrame):
    total_resp = df["respondent_id"].nunique()
    total_rec  = len(df)
    poll_count = df["poll_type"].nunique()
    avg_conf   = df["confidence_score"].mean()

    # Overall winner
    top_resp = df["response"].value_counts().idxmax()
    top_pct  = df["response"].value_counts(normalize=True).max() * 100

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👥 Respondents",    f"{total_resp:,}",
              delta=f"{total_resp - full_df['respondent_id'].nunique():+,} vs total")
    c2.metric("📝 Total Responses", f"{total_rec:,}")
    c3.metric("📋 Poll Types",      str(poll_count))
    c4.metric("🏆 Leading Option",  top_resp, delta=f"{top_pct:.1f}% share")
    c5.metric("⭐ Avg Confidence",  f"{avg_conf:.2f}")


# ─────────────────────────────────────────────────────────────────
# TAB 1 — Overview
# ─────────────────────────────────────────────────────────────────
def tab_overview(df: pd.DataFrame):
    st.subheader("📊 Overall Response Distribution")

    col1, col2 = st.columns([1.1, 0.9])

    # Bar chart — overall share
    share = df["response"].value_counts(normalize=True).mul(100).round(2).reset_index()
    share.columns = ["response", "percentage"]
    share = share.sort_values("percentage", ascending=True)

    with col1:
        fig_bar = px.bar(
            share, x="percentage", y="response", orientation="h",
            color="response", color_discrete_sequence=COLOR_SEQ,
            text=share["percentage"].apply(lambda x: f"{x:.1f}%"),
            template=PLOTLY_TEMPLATE,
            title="Response Share (%)",
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(showlegend=False, height=400,
                              xaxis_title="Share (%)", yaxis_title="")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Donut pie
    with col2:
        fig_pie = px.pie(
            share, names="response", values="percentage",
            color_discrete_sequence=COLOR_SEQ,
            hole=0.5, template=PLOTLY_TEMPLATE,
            title="Response Distribution",
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(height=400, showlegend=True,
                              legend=dict(orientation="v", x=1.0, y=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Poll type distribution
    st.subheader("📋 Records by Poll Type")
    pt_counts = df["poll_type"].value_counts().reset_index()
    pt_counts.columns = ["poll_type", "count"]
    fig_pt = px.bar(
        pt_counts, x="poll_type", y="count",
        color="poll_type", color_discrete_sequence=COLOR_SEQ,
        text="count", template=PLOTLY_TEMPLATE,
        title="Total Responses per Poll Type",
    )
    fig_pt.update_traces(textposition="outside")
    fig_pt.update_layout(showlegend=False, height=380,
                         xaxis_title="Poll Type", yaxis_title="Responses")
    st.plotly_chart(fig_pt, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
# TAB 2 — Region Analysis
# ─────────────────────────────────────────────────────────────────
def tab_region(df: pd.DataFrame):
    st.subheader("🌍 Region-wise Response Analysis")

    # Stacked bar
    grp = (
        df.groupby(["region", "response"])
        .size()
        .reset_index(name="count")
    )
    grp["total"]  = grp.groupby("region")["count"].transform("sum")
    grp["pct"]    = (grp["count"] / grp["total"] * 100).round(2)

    fig_stack = px.bar(
        grp, x="region", y="pct", color="response",
        barmode="stack", color_discrete_sequence=COLOR_SEQ,
        template=PLOTLY_TEMPLATE,
        text=grp["pct"].apply(lambda x: f"{x:.0f}%" if x >= 6 else ""),
        title="Stacked Region-wise Response Share (%)",
    )
    fig_stack.update_layout(
        yaxis_title="Share (%)", xaxis_title="Region / Group",
        legend_title="Response", height=430,
    )
    st.plotly_chart(fig_stack, use_container_width=True)

    # Heatmap
    st.subheader("🔥 Region × Response Heatmap")
    pivot = grp.pivot_table(index="region", columns="response",
                             values="pct", fill_value=0)
    fig_heat = px.imshow(
        pivot, color_continuous_scale="Viridis",
        text_auto=".1f", template=PLOTLY_TEMPLATE,
        title="Response Percentage Heatmap (Region vs Option)",
    )
    fig_heat.update_layout(height=400, coloraxis_colorbar_title="Share (%)")
    st.plotly_chart(fig_heat, use_container_width=True)

    # Regional winner table
    st.subheader("🏆 Leading Option per Region")
    winners = (
        grp.loc[grp.groupby("region")["pct"].idxmax()]
        [["region", "response", "pct"]]
        .rename(columns={"pct": "Leading Share (%)", "response": "Leader"})
        .reset_index(drop=True)
        .sort_values("Leading Share (%)", ascending=False)
    )
    st.dataframe(
        winners.style.background_gradient(cmap="Purples", subset=["Leading Share (%)"]),
        use_container_width=True,
    )


# ─────────────────────────────────────────────────────────────────
# TAB 3 — Demographics
# ─────────────────────────────────────────────────────────────────
def tab_demographics(df: pd.DataFrame):
    st.subheader("👤 Demographic Analysis")

    demo_choice = st.radio(
        "Select demographic dimension:",
        ["Age Group", "Gender", "Education"],
        horizontal=True,
    )
    demo_col_map = {
        "Age Group":  "age_group",
        "Gender":     "gender",
        "Education":  "education",
    }
    demo_col = demo_col_map[demo_choice]

    grp = (
        df.groupby([demo_col, "response"])
        .size()
        .reset_index(name="count")
    )
    grp["total"] = grp.groupby(demo_col)["count"].transform("sum")
    grp["pct"]   = (grp["count"] / grp["total"] * 100).round(2)

    fig = px.bar(
        grp, x=demo_col, y="pct", color="response",
        barmode="group", color_discrete_sequence=COLOR_SEQ,
        text=grp["pct"].apply(lambda x: f"{x:.1f}%"),
        template=PLOTLY_TEMPLATE,
        title=f"Response Distribution by {demo_choice}",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        yaxis_title="Share (%)", xaxis_title=demo_choice,
        legend_title="Response", height=430,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Cross table
    st.subheader(f"📋 Crosstab: {demo_choice} × Response")
    pivot = grp.pivot_table(index=demo_col, columns="response",
                             values="pct", fill_value=0).round(2)
    st.dataframe(
        pivot.style.background_gradient(cmap="Blues", axis=1),
        use_container_width=True,
    )


# ─────────────────────────────────────────────────────────────────
# TAB 4 — Trend Analysis
# ─────────────────────────────────────────────────────────────────
def tab_trend(df: pd.DataFrame):
    st.subheader("📈 Monthly Response Trends")

    grp = (
        df.groupby(["month_sort", "month_label", "response"])
        .size()
        .reset_index(name="count")
    )
    grp["total"] = grp.groupby("month_sort")["count"].transform("sum")
    grp["pct"]   = (grp["count"] / grp["total"] * 100).round(2)
    grp = grp.sort_values("month_sort")

    fig_line = px.line(
        grp, x="month_label", y="pct", color="response",
        markers=True, color_discrete_sequence=COLOR_SEQ,
        template=PLOTLY_TEMPLATE,
        title="Monthly Response Share (%) Over Time",
    )
    fig_line.update_traces(line_width=2.5)
    fig_line.update_layout(
        xaxis_title="Month", yaxis_title="Share (%)",
        legend_title="Response", height=420,
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Satisfaction score trend
    score_df = df[df["response_score"].notna()]
    if not score_df.empty:
        st.subheader("⭐ Avg Satisfaction Score Trend")
        trend_score = (
            score_df.groupby(["month_sort", "month_label", "poll_type"])["response_score"]
            .mean()
            .round(2)
            .reset_index()
            .rename(columns={"response_score": "avg_score"})
            .sort_values("month_sort")
        )
        fig_score = px.line(
            trend_score, x="month_label", y="avg_score", color="poll_type",
            markers=True, color_discrete_sequence=COLOR_SEQ,
            template=PLOTLY_TEMPLATE,
            title="Monthly Average Satisfaction Score by Poll Type",
        )
        fig_score.add_hline(y=3.0, line_dash="dash", line_color="gray",
                             annotation_text="Neutral (3.0)")
        fig_score.update_layout(
            xaxis_title="Month", yaxis_title="Avg Score (1–5)",
            yaxis=dict(range=[1, 5.5]), height=400,
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig_score, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
# TAB 5 — Cross-Poll Comparison
# ─────────────────────────────────────────────────────────────────
def tab_comparison(df: pd.DataFrame):
    st.subheader("🔄 Cross-Poll Type Comparison")

    # Records per poll type
    col1, col2 = st.columns(2)
    with col1:
        pt_cnt = df["poll_type"].value_counts().reset_index()
        pt_cnt.columns = ["poll_type", "count"]
        fig = px.pie(
            pt_cnt, names="poll_type", values="count",
            hole=0.45, color_discrete_sequence=COLOR_SEQ,
            template=PLOTLY_TEMPLATE, title="Records Share by Poll Type",
        )
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True)

    # Avg confidence per poll type
    with col2:
        conf = df.groupby("poll_type")["confidence_score"].mean().round(3).reset_index()
        fig2 = px.bar(
            conf.sort_values("confidence_score"),
            x="confidence_score", y="poll_type", orientation="h",
            color="poll_type", color_discrete_sequence=COLOR_SEQ,
            template=PLOTLY_TEMPLATE,
            title="Avg Confidence Score per Poll Type",
            text=conf.sort_values("confidence_score")["confidence_score"],
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False, height=360,
                            xaxis_title="Avg Confidence Score", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    # Avg satisfaction score comparison
    score_df = df[df["response_score"].notna()]
    if not score_df.empty:
        st.subheader("⭐ Avg Satisfaction Score per Poll Type")
        score_comp = (
            score_df.groupby("poll_type")["response_score"]
            .mean().round(2).reset_index()
            .rename(columns={"response_score": "avg_score"})
            .sort_values("avg_score", ascending=False)
        )
        fig3 = px.bar(
            score_comp, x="poll_type", y="avg_score",
            color="poll_type", color_discrete_sequence=COLOR_SEQ,
            text="avg_score", template=PLOTLY_TEMPLATE,
            title="Avg Satisfaction Score Across Poll Types",
        )
        fig3.update_traces(textposition="outside")
        fig3.add_hline(y=3.0, line_dash="dash", line_color="gray",
                        annotation_text="Neutral (3.0)")
        fig3.update_layout(showlegend=False, yaxis=dict(range=[0, 5.5]),
                            xaxis_title="Poll Type", yaxis_title="Avg Score (1–5)",
                            height=390)
        st.plotly_chart(fig3, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
# TAB 6 — Raw Data
# ─────────────────────────────────────────────────────────────────
def tab_raw_data(df: pd.DataFrame):
    st.subheader("🗃️ Filtered Dataset")

    search_q = st.text_input("🔍 Search in Question / Response:", "")
    view_df = df.copy()
    if search_q:
        mask = (
            view_df["question"].str.contains(search_q, case=False, na=False) |
            view_df["response"].str.contains(search_q, case=False, na=False)
        )
        view_df = view_df[mask]

    st.caption(f"Showing {len(view_df):,} records")
    st.dataframe(
        view_df[[
            "respondent_id", "date", "poll_type", "question",
            "response", "region", "age_group", "gender",
            "education", "confidence_score", "response_score",
        ]].reset_index(drop=True),
        use_container_width=True,
        height=480,
    )

    # Download
    csv_bytes = view_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=csv_bytes,
        file_name="poll_data_filtered.csv",
        mime="text/csv",
    )


# ─────────────────────────────────────────────────────────────────
# TAB 7 — Insights
# ─────────────────────────────────────────────────────────────────
def tab_insights(df: pd.DataFrame):
    st.subheader("💡 Automated Insights")

    from src.analyzer import generate_insights
    insights = generate_insights(df)

    for ins in insights:
        if ins.startswith("\n"):
            st.markdown("---")
            ins = ins.strip()
        if ins.startswith("["):
            st.markdown(f"#### {ins}")
        else:
            st.markdown(f"&nbsp;&nbsp;{ins}")

    st.markdown("---")
    st.subheader("📋 Recommendations")
    recs = [
        "🎯 **Focus campaign resources** on regions showing lower leader share.",
        "📉 **Address dissatisfaction trends** identified in monthly trend charts.",
        "👥 **Segment outreach** by age group where preferences diverge significantly.",
        "🔁 **Deploy follow-up surveys** in regions with high 'Undecided' or 'Neutral' rates.",
        "📊 **Use demographic heatmaps** to personalise product/service messaging.",
        "🤖 **Integrate sentiment analysis** on open-ended responses for richer insights.",
    ]
    for r in recs:
        st.markdown(f"- {r}")


# ─────────────────────────────────────────────────────────────────
# Main app
# ─────────────────────────────────────────────────────────────────
def main():
    render_header()

    with st.spinner("Loading poll data…"):
        df = load_data()

    filters  = render_sidebar(df)
    fdf      = apply_filters(df, filters)

    if fdf.empty:
        st.warning("⚠️ No data matches the selected filters. Please adjust your selections.")
        return

    render_kpis(fdf, df)
    st.markdown("---")

    tabs = st.tabs([
        "📊 Overview",
        "🌍 Region",
        "👤 Demographics",
        "📈 Trends",
        "🔄 Comparison",
        "🗃️ Raw Data",
        "💡 Insights",
    ])

    with tabs[0]: tab_overview(fdf)
    with tabs[1]: tab_region(fdf)
    with tabs[2]: tab_demographics(fdf)
    with tabs[3]: tab_trend(fdf)
    with tabs[4]: tab_comparison(fdf)
    with tabs[5]: tab_raw_data(fdf)
    with tabs[6]: tab_insights(df)   # full df for cross-poll insights

    st.markdown(
        "<br><center style='color:#475569;font-size:0.8rem;'>"
        "Poll Results Visualizer · Data Science Portfolio Project · Built with Streamlit & Plotly"
        "</center>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

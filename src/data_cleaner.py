"""
data_cleaner.py
---------------
Cleans and preprocesses the raw poll dataset:
  - Handle missing values
  - Standardise text columns
  - Remove duplicates
  - Validate data types
  - Add derived columns (month, week, numeric score)
  - Save cleaned dataset
"""

import pandas as pd
import numpy as np
import os


# ─────────────────────────────────────────────────────────────────
# Response → Numeric score mappings
# ─────────────────────────────────────────────────────────────────

LIKERT_SCORE_MAP = {
    # Satisfaction scale
    "Very Satisfied":      5,
    "Satisfied":           4,
    "Neutral":             3,
    "Dissatisfied":        2,
    "Very Dissatisfied":   1,
    # Agreement scale
    "Strongly Agree":      5,
    "Agree":               4,
    "Disagree":            2,
    "Strongly Disagree":   1,
    # Event rating
    "Excellent":           4,
    "Good":                3,
    "Average":             2,
    "Poor":                1,
}


def load_raw_data(filepath: str = "data/poll_data.csv") -> pd.DataFrame:
    """Load the raw poll CSV into a DataFrame."""
    print(f"Loading raw data from: {filepath}")
    df = pd.read_csv(filepath, parse_dates=["date"])
    print(f"  Raw shape: {df.shape}")
    return df


def check_missing(df: pd.DataFrame) -> None:
    """Print a summary of missing values per column."""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    summary = pd.DataFrame({"Missing Count": missing, "Missing %": missing_pct})
    print("\nMissing Value Summary:")
    print(summary[summary["Missing Count"] > 0].to_string() or "  No missing values found.")


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and standardise case for object columns."""
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
    print("  Text columns cleaned (stripped whitespace).")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate rows."""
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    print(f"  Duplicates removed: {before - after} rows ({before} → {after})")
    return df


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values with sensible defaults:
    - Categorical columns → 'Unknown'
    - Numeric columns     → column median
    """
    # Categorical
    for col in ["region", "age_group", "gender", "education"]:
        if col in df.columns:
            df[col] = df[col].replace({"nan": np.nan}).fillna("Unknown")

    # Numeric
    if "confidence_score" in df.columns:
        df["confidence_score"] = df["confidence_score"].fillna(df["confidence_score"].median())

    print("  Missing values filled.")
    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add time-based and score-based derived columns."""
    # Time
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["week"]  = df["date"].dt.isocalendar().week.astype(int)
    df["year"]  = df["date"].dt.year

    # Numeric response score (for Likert / rating questions)
    df["response_score"] = df["response"].map(LIKERT_SCORE_MAP)
    # Candidates / non-scale options → NaN (expected)

    print("  Derived columns added: month, week, year, response_score.")
    return df


def validate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure required columns exist and have correct types."""
    required_cols = [
        "respondent_id", "date", "poll_type", "question",
        "response", "region", "age_group", "gender",
        "education", "confidence_score",
    ]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Required column missing: {col}")

    df["date"] = pd.to_datetime(df["date"])
    df["confidence_score"] = pd.to_numeric(df["confidence_score"], errors="coerce")
    print("  All required columns validated.")
    return df


def clean_pipeline(
    input_path: str  = "data/poll_data.csv",
    output_path: str = "data/poll_data_cleaned.csv",
) -> pd.DataFrame:
    """
    Full cleaning pipeline. Returns the cleaned DataFrame.
    """
    print("=" * 55)
    print("  POLL DATA CLEANING PIPELINE")
    print("=" * 55)

    df = load_raw_data(input_path)
    check_missing(df)

    df = clean_text_columns(df)
    df = remove_duplicates(df)
    df = fill_missing_values(df)
    df = validate_columns(df)
    df = add_derived_columns(df)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print("\nCleaned dataset saved -> " + output_path)
    print(f"Final shape: {df.shape}")
    print("=" * 55)
    return df


if __name__ == "__main__":
    cleaned_df = clean_pipeline()
    print("\nCleaned Dataset Sample:")
    print(cleaned_df.head(8).to_string(index=False))
    print("\nData Types:")
    print(cleaned_df.dtypes)

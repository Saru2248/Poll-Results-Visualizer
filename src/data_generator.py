"""
data_generator.py
-----------------
Generates realistic synthetic poll/survey datasets for:
  1. Election Preference Poll
  2. Customer Satisfaction Survey
  3. Employee Engagement Survey
  4. Product Preference Poll
  5. Classroom / Event Feedback Survey

Each row = one respondent's response to one question.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────────
# Seed for reproducibility
# ─────────────────────────────────────────────────────────────────
np.random.seed(42)

# ─────────────────────────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────────────────────────

REGIONS = ["North", "South", "East", "West", "Central"]
AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55+"]
GENDERS = ["Male", "Female", "Non-Binary"]
EDUCATION = ["High School", "Graduate", "Post-Graduate", "PhD"]


def random_dates(start: str, end: str, n: int) -> list:
    """Generate n random dates between start and end."""
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    delta = (end_dt - start_dt).days
    return [
        (start_dt + timedelta(days=int(np.random.randint(0, delta)))).strftime("%Y-%m-%d")
        for _ in range(n)
    ]


def weighted_choice(options: list, weights: list, n: int) -> np.ndarray:
    """Return n samples from options using given weights."""
    weights = np.array(weights, dtype=float)
    weights /= weights.sum()
    return np.random.choice(options, size=n, p=weights)


# ─────────────────────────────────────────────────────────────────
# 1. Election Preference Poll
# ─────────────────────────────────────────────────────────────────

def generate_election_poll(n: int = 1000) -> pd.DataFrame:
    """
    Simulates a state-level election preference poll.
    Candidates: Candidate A (ruling), Candidate B (opposition),
                Candidate C (regional), Undecided
    """
    candidates = ["Candidate A", "Candidate B", "Candidate C", "Undecided"]
    # Region-wise voting tendencies
    region_weights = {
        "North":   [0.40, 0.35, 0.15, 0.10],
        "South":   [0.25, 0.45, 0.20, 0.10],
        "East":    [0.35, 0.30, 0.25, 0.10],
        "West":    [0.45, 0.30, 0.15, 0.10],
        "Central": [0.30, 0.40, 0.20, 0.10],
    }

    regions = np.random.choice(REGIONS, size=n)
    age_groups = np.random.choice(AGE_GROUPS, size=n)
    genders = weighted_choice(GENDERS, [0.49, 0.49, 0.02], n)
    education = np.random.choice(EDUCATION, size=n)
    dates = random_dates("2024-01-01", "2024-03-31", n)

    votes = [
        weighted_choice(candidates, region_weights[r], 1)[0]
        for r in regions
    ]

    df = pd.DataFrame({
        "respondent_id": [f"EP{str(i+1).zfill(4)}" for i in range(n)],
        "date": dates,
        "poll_type": "Election Preference",
        "question": "Which candidate will you vote for in the upcoming state election?",
        "response": votes,
        "region": regions,
        "age_group": age_groups,
        "gender": genders,
        "education": education,
        "confidence_score": np.round(np.random.uniform(0.5, 1.0, n), 2),
    })
    return df


# ─────────────────────────────────────────────────────────────────
# 2. Customer Satisfaction Survey
# ─────────────────────────────────────────────────────────────────

def generate_customer_satisfaction(n: int = 800) -> pd.DataFrame:
    """
    Simulates a post-purchase customer satisfaction survey.
    Rating scale: Very Satisfied, Satisfied, Neutral, Dissatisfied, Very Dissatisfied
    """
    ratings = ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
    weights = [0.30, 0.35, 0.20, 0.10, 0.05]

    questions = [
        "Overall satisfaction with the product?",
        "Satisfaction with the delivery experience?",
        "Would you recommend us to a friend?",
        "Satisfaction with customer support?",
    ]

    rows = []
    for i in range(n):
        region = np.random.choice(REGIONS)
        age = np.random.choice(AGE_GROUPS)
        gender = weighted_choice(GENDERS, [0.49, 0.49, 0.02], 1)[0]
        date = random_dates("2024-04-01", "2024-06-30", 1)[0]
        for q in questions:
            rows.append({
                "respondent_id": f"CS{str(i+1).zfill(4)}",
                "date": date,
                "poll_type": "Customer Satisfaction",
                "question": q,
                "response": weighted_choice(ratings, weights, 1)[0],
                "region": region,
                "age_group": age,
                "gender": gender,
                "education": np.random.choice(EDUCATION),
                "confidence_score": np.round(np.random.uniform(0.6, 1.0), 2),
            })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────
# 3. Employee Engagement Survey
# ─────────────────────────────────────────────────────────────────

def generate_employee_survey(n: int = 500) -> pd.DataFrame:
    """
    Simulates an annual employee satisfaction & engagement survey.
    Scale: Strongly Agree, Agree, Neutral, Disagree, Strongly Disagree
    """
    responses = ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]

    questions = [
        "I feel valued at my workplace.",
        "My manager supports my career growth.",
        "I have the tools I need to do my job effectively.",
        "I would recommend this company as a great place to work.",
        "I am satisfied with my work-life balance.",
    ]

    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
    dept_weights = {
        "Engineering": [0.25, 0.35, 0.20, 0.15, 0.05],
        "Marketing":   [0.30, 0.30, 0.20, 0.15, 0.05],
        "Sales":       [0.20, 0.30, 0.25, 0.15, 0.10],
        "HR":          [0.35, 0.35, 0.15, 0.10, 0.05],
        "Finance":     [0.25, 0.30, 0.25, 0.15, 0.05],
        "Operations":  [0.20, 0.30, 0.20, 0.20, 0.10],
    }

    rows = []
    for i in range(n):
        dept = np.random.choice(departments)
        age = np.random.choice(AGE_GROUPS)
        gender = weighted_choice(GENDERS, [0.50, 0.48, 0.02], 1)[0]
        date = random_dates("2024-07-01", "2024-07-31", 1)[0]
        for q in questions:
            rows.append({
                "respondent_id": f"EE{str(i+1).zfill(4)}",
                "date": date,
                "poll_type": "Employee Engagement",
                "question": q,
                "response": weighted_choice(responses, dept_weights[dept], 1)[0],
                "region": dept,           # region col holds department for this poll
                "age_group": age,
                "gender": gender,
                "education": np.random.choice(EDUCATION),
                "confidence_score": np.round(np.random.uniform(0.55, 1.0), 2),
            })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────
# 4. Product Preference Poll
# ─────────────────────────────────────────────────────────────────

def generate_product_preference(n: int = 600) -> pd.DataFrame:
    """
    Simulates a product/brand preference survey among consumers.
    Products: Brand X, Brand Y, Brand Z, No Preference
    """
    products = ["Brand X", "Brand Y", "Brand Z", "No Preference"]
    age_weights = {
        "18-24": [0.40, 0.30, 0.20, 0.10],
        "25-34": [0.35, 0.35, 0.20, 0.10],
        "35-44": [0.30, 0.35, 0.25, 0.10],
        "45-54": [0.25, 0.30, 0.30, 0.15],
        "55+":   [0.20, 0.25, 0.35, 0.20],
    }

    questions = [
        "Which smartphone brand do you prefer?",
        "Which brand offers the best value for money?",
        "Which brand do you trust the most for after-sales service?",
    ]

    rows = []
    for i in range(n):
        age = np.random.choice(AGE_GROUPS)
        region = np.random.choice(REGIONS)
        gender = weighted_choice(GENDERS, [0.49, 0.49, 0.02], 1)[0]
        date = random_dates("2024-08-01", "2024-09-30", 1)[0]
        for q in questions:
            rows.append({
                "respondent_id": f"PP{str(i+1).zfill(4)}",
                "date": date,
                "poll_type": "Product Preference",
                "question": q,
                "response": weighted_choice(products, age_weights[age], 1)[0],
                "region": region,
                "age_group": age,
                "gender": gender,
                "education": np.random.choice(EDUCATION),
                "confidence_score": np.round(np.random.uniform(0.5, 1.0), 2),
            })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────
# 5. Classroom / Event Feedback
# ─────────────────────────────────────────────────────────────────

def generate_event_feedback(n: int = 400) -> pd.DataFrame:
    """
    Simulates a post-workshop/event feedback form.
    Rating: Excellent, Good, Average, Poor
    """
    ratings = ["Excellent", "Good", "Average", "Poor"]
    weights = [0.35, 0.40, 0.18, 0.07]

    questions = [
        "How would you rate the overall event?",
        "How would you rate the speaker / trainer?",
        "Was the content relevant to your needs?",
        "How would you rate the venue / online platform?",
    ]

    rows = []
    for i in range(n):
        region = np.random.choice(REGIONS)
        age = np.random.choice(["18-24", "25-34", "35-44"])
        gender = weighted_choice(GENDERS, [0.48, 0.50, 0.02], 1)[0]
        date = random_dates("2024-10-01", "2024-12-31", 1)[0]
        for q in questions:
            rows.append({
                "respondent_id": f"EF{str(i+1).zfill(4)}",
                "date": date,
                "poll_type": "Event Feedback",
                "question": q,
                "response": weighted_choice(ratings, weights, 1)[0],
                "region": region,
                "age_group": age,
                "gender": gender,
                "education": np.random.choice(EDUCATION),
                "confidence_score": np.round(np.random.uniform(0.6, 1.0), 2),
            })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────
# Master dataset builder
# ─────────────────────────────────────────────────────────────────

def generate_all_poll_data(save_path: str = "data/poll_data.csv") -> pd.DataFrame:
    """
    Combines all 5 poll datasets into one master CSV.
    Returns the combined DataFrame.
    """
    print("Generating poll datasets...")

    dfs = [
        generate_election_poll(1000),
        generate_customer_satisfaction(800),
        generate_employee_survey(500),
        generate_product_preference(600),
        generate_event_feedback(400),
    ]

    master_df = pd.concat(dfs, ignore_index=True)
    master_df["date"] = pd.to_datetime(master_df["date"])
    master_df.sort_values("date", inplace=True)
    master_df.reset_index(drop=True, inplace=True)

    # Save
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    master_df.to_csv(save_path, index=False)

    print(f"  Total records   : {len(master_df):,}")
    print(f"  Poll types      : {master_df['poll_type'].nunique()}")
    print(f"  Date range      : {master_df['date'].min().date()} → {master_df['date'].max().date()}")
    print(f"  Saved to        : {save_path}")

    return master_df


if __name__ == "__main__":
    df = generate_all_poll_data()
    print("\nSample rows:")
    print(df.head(10).to_string(index=False))

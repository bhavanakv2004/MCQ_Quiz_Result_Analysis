import pandas as pd
import numpy as np

# Load data
def load_data(data_file, answer_file):
    df = pd.read_csv(data_file)
    answer_df = pd.read_csv(answer_file)

    df.fillna("Not Answered", inplace=True)
    df.columns = df.columns.str.strip()
    answer_df.columns = answer_df.columns.str.strip()

    return df, answer_df


# ---------------- FILE VALIDATION ---------------- #
def validate_files(df, answer_df):
    # Check answer file format
    if "Question" not in answer_df.columns or "Answer" not in answer_df.columns:
        return False, "❌ Answer file format is incorrect"

    question_cols = answer_df["Question"].tolist()

    # Detect swapped files
    if "Q1" not in df.columns and "Q1" in answer_df.columns:
        return False, "❌ Files seem swapped! Please upload correctly."

    # Check student data
    for q in question_cols:
        if q not in df.columns:
            return False, f"❌ Missing column {q} in student data"

    return True, "✅ Files are valid"


# ---------------- SCORE ---------------- #
def calculate_score(df, answer_df):
    answer_key = dict(zip(answer_df["Question"], answer_df["Answer"]))

    def score_row(row):
        score = 0
        for q in answer_key:
            if row[q] == answer_key[q]:
                score += 1
        return score

    df["Score"] = df.apply(score_row, axis=1)
    return df


# ---------------- PERFORMANCE ---------------- #
def department_performance(df):
    return df.groupby("Department")["Score"].mean()


def college_performance(df):
    return df.groupby("College")["Score"].mean()


# ---------------- QUESTION ANALYSIS ---------------- #
def question_analysis(df, answer_df):
    answer_key = dict(zip(answer_df["Question"], answer_df["Answer"]))
    result = {}

    for q in answer_key:
        correct = (df[q] == answer_key[q]).sum()
        accuracy = correct / len(df)

        if accuracy > 0.8:
            difficulty = "Easy"
        elif accuracy >= 0.5:
            difficulty = "Medium"
        else:
            difficulty = "Difficult"

        result[q] = [accuracy, difficulty]

    return pd.DataFrame(result).T.reset_index().rename(
        columns={"index": "Question", 0: "Accuracy", 1: "Difficulty"}
    )


# ---------------- ATTEMPT RATE ---------------- #
def attempt_rate(df, answer_df):
    answer_key = dict(zip(answer_df["Question"], answer_df["Answer"]))
    result = {}

    for q in answer_key:
        rate = (df[q] != "Not Answered").mean()
        result[q] = rate

    return pd.DataFrame(result.items(), columns=["Question", "Attempt Rate"])


# ---------------- STATISTICS ---------------- #
def score_statistics(df):
    return {
        "Mean": df["Score"].mean(),
        "Median": df["Score"].median(),
        "Std Dev": df["Score"].std()
    }


# ---------------- HEATMAP ---------------- #
def heatmap_data(df):
    return df.pivot_table(values="Score", index="Department", columns="College")


# ---------------- LEADERBOARD ---------------- #
def leaderboard(df):
    return df.sort_values("Score", ascending=False)[["Name", "Score"]]

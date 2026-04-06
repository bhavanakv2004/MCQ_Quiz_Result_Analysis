import pandas as pd
import numpy as np

# Load data
def load_data(data_file, answer_file):
    df = pd.read_csv(data_file)
    answer_df = pd.read_csv(answer_file)

    df.fillna("Not Answered", inplace=True)
    df.columns = df.columns.str.strip()

    return df, answer_df


# Calculate score
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


# Department performance
def department_performance(df):
    return df.groupby("Department")["Score"].mean()


# College performance
def college_performance(df):
    return df.groupby("College")["Score"].mean()


# Question analysis + difficulty
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


# Attempt rate
def attempt_rate(df, answer_df):
    answer_key = dict(zip(answer_df["Question"], answer_df["Answer"]))
    result = {}

    for q in answer_key:
        rate = (df[q] != "Not Answered").mean()
        result[q] = rate

    return pd.DataFrame(result.items(), columns=["Question", "Attempt Rate"])


# Score statistics
def score_statistics(df):
    return {
        "Mean": df["Score"].mean(),
        "Median": df["Score"].median(),
        "Std Dev": df["Score"].std()
    }


# Heatmap data
def heatmap_data(df):
    pivot = df.pivot_table(values="Score", index="Department", columns="College")
    return pivot


# Leaderboard
def leaderboard(df):
    return df.sort_values("Score", ascending=False)[["Name", "Score"]]

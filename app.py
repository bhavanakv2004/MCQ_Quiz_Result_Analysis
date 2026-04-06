import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from analysis import *

st.set_page_config(page_title="MCQ Analytics", layout="wide")

st.title("📊 MCQ Quiz Analytics Dashboard")

# ---------------- FILE UPLOAD ---------------- #
data_file = st.file_uploader("Upload Student Data CSV", type=["csv"])
answer_file = st.file_uploader("Upload Answer Key CSV", type=["csv"])

if data_file and answer_file:
    df, answer_df = load_data(data_file, answer_file)

    # Validate files
    valid, message = validate_files(df, answer_df)
    if not valid:
        st.error(message)
        st.stop()

    df = calculate_score(df, answer_df)

    # ---------------- SIDEBAR FILTERS ---------------- #
    st.sidebar.header("🔍 Filters")

    colleges = st.sidebar.multiselect("Select College", df["College"].unique())
    departments = st.sidebar.multiselect("Select Department", df["Department"].unique())
    students = st.sidebar.multiselect("Select Student", df["Name"].unique())

    filtered_df = df.copy()

    if colleges:
        filtered_df = filtered_df[filtered_df["College"].isin(colleges)]
    if departments:
        filtered_df = filtered_df[filtered_df["Department"].isin(departments)]
    if students:
        filtered_df = filtered_df[filtered_df["Name"].isin(students)]

    # ---------------- SECTION 1: OVERALL ANALYTICS ---------------- #
    st.header("📊 Overall Analytics")

    col1, col2 = st.columns(2)

    # Score Distribution
    with col1:
        fig, ax = plt.subplots(figsize=(5, 3))
        sns.histplot(filtered_df["Score"], bins=10, ax=ax)
        ax.set_title("Score Distribution")
        st.pyplot(fig)

    # Score Stats
    with col2:
        stats = score_statistics(filtered_df)
        stats_df = pd.DataFrame({
            "Metric": ["Mean", "Median", "Std Dev"],
            "Value": [
                round(stats["Mean"], 2),
                stats["Median"],
                round(stats["Std Dev"], 2)
            ]
        })
        st.table(stats_df)

    # ---------------- SECTION 2: LEADERBOARD ---------------- #
    st.header("🏆 Student Leaderboard")

    leaderboard_df = leaderboard(filtered_df)
    st.dataframe(leaderboard_df.head(10))

    # ---------------- SECTION 3: DEPARTMENT PERFORMANCE ---------------- #
    st.header("🏢 Department Performance")

    col1, col2 = st.columns(2)

    with col1:
        dept = department_performance(filtered_df)
        fig, ax = plt.subplots(figsize=(5, 3))
        dept.plot(kind="bar", ax=ax)
        ax.set_title("Department Performance")
        st.pyplot(fig)

    with col2:
        pivot = heatmap_data(filtered_df)
        fig, ax = plt.subplots(figsize=(5, 3))
        sns.heatmap(pivot, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # ---------------- SECTION 4: COLLEGE PERFORMANCE ---------------- #
    st.header("🏫 College Ranking")

    college = college_performance(filtered_df)

    fig, ax = plt.subplots(figsize=(5, 3))
    college.sort_values().plot(kind="barh", ax=ax)
    ax.set_title("College Performance")
    st.pyplot(fig)

    # ---------------- SECTION 5: QUESTION ANALYSIS ---------------- #
    st.header("❓ Question Analysis")

    col1, col2 = st.columns(2)

    with col1:
        q_analysis = question_analysis(filtered_df, answer_df)
        st.dataframe(q_analysis)

    with col2:
        fig, ax = plt.subplots(figsize=(5, 3))
        sns.barplot(x="Question", y="Accuracy", data=q_analysis, ax=ax)
        ax.set_title("Question Accuracy")
        st.pyplot(fig)

    # ---------------- ATTEMPT RATE ---------------- #
    st.subheader("📌 Attempt Rate")

    attempt = attempt_rate(filtered_df, answer_df)

    fig, ax = plt.subplots(figsize=(5, 3))
    sns.barplot(x="Question", y="Attempt Rate", data=attempt, ax=ax)
    ax.set_title("Attempt Rate")
    st.pyplot(fig)

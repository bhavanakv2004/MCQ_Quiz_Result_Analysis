import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from analysis import *

st.set_page_config(page_title="MCQ Analytics", layout="wide")

st.title("📊 MCQ Quiz Analytics Dashboard")

# Upload files
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

    # ---------------- DATA ---------------- #
    st.subheader("📋 Data Preview")
    st.dataframe(df)

    # ---------------- SCORE DISTRIBUTION ---------------- #
    st.subheader("📊 Student Score Distribution")

    fig, ax = plt.subplots(figsize=(10,3))
    sns.histplot(df["Score"], bins=10, ax=ax)
    ax.set_title("Student Score Distribution")
    st.pyplot(fig)

    # ---------------- LEADERBOARD ---------------- #
    st.subheader("🏆 Leaderboard")
    st.dataframe(leaderboard(df).head(10))

    # ---------------- DEPARTMENT ---------------- #
    st.subheader("🏢 Department Performance")

    dept = department_performance(df)
    fig, ax = plt.subplots(figsize=(10,3))
    dept.plot(kind="bar", ax=ax)
    ax.set_title("Department Performance")
    st.pyplot(fig)

    # ---------------- COLLEGE ---------------- #
    st.subheader("🏫 College Performance")

    college = college_performance(df)
    fig, ax = plt.subplots(figsize=(10,3))
    college.sort_values().plot(kind="barh", ax=ax)
    ax.set_title("College Performance")
    st.pyplot(fig)

    # ---------------- QUESTION ANALYSIS ---------------- #
    st.subheader("❓ Question Analysis")

    q_analysis = question_analysis(df, answer_df)
    st.dataframe(q_analysis)

    fig, ax = plt.subplots(figsize=(10,3))
    sns.barplot(x="Question", y="Accuracy", data=q_analysis, ax=ax)
    ax.set_title("Question Accuracy")
    st.pyplot(fig)

    # ---------------- ATTEMPT RATE ---------------- #
    st.subheader("📌 Attempt Rate")

    attempt = attempt_rate(df, answer_df)
    st.dataframe(attempt)

    fig, ax = plt.subplots(figsize=(10,3))
    sns.barplot(x="Question", y="Attempt Rate", data=attempt, ax=ax)
    ax.set_title("Attempt Rate")
    st.pyplot(fig)

    # ---------------- HEATMAP ---------------- #
    st.subheader("🔥 Department vs College Heatmap")

    pivot = heatmap_data(df)
    fig, ax = plt.subplots(figsize=(10,3))
    sns.heatmap(pivot, annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    # ---------------- STATISTICS ---------------- #
    st.subheader("📈 Score Statistics")

    stats = score_statistics(df)

    stats_df = pd.DataFrame({
        "Metric": ["Mean", "Median", "Std Dev"],
        "Value": [
            round(stats["Mean"], 2),
            stats["Median"],
            round(stats["Std Dev"], 2)
        ]
    })

    st.table(stats_df)

    #---- Report -----#
    st.subheader("📄 Generate Analytics Report")

    student_report, dept_report, college_report, q_report = generate_report(df, answer_df)

    # Save to Excel
    file_name = "quiz_analysis.xlsx"
    
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        student_report.to_excel(writer, sheet_name="Student Report", index=False)
        dept_report.to_excel(writer, sheet_name="Department Report")
        college_report.to_excel(writer, sheet_name="College Report")
        q_report.to_excel(writer, sheet_name="Question Report", index=False)

    # Download button
    with open(file_name, "rb") as f:
        st.download_button(
            label="📥 Download Full Report",
            data=f,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

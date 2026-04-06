import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from analysis import *

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="MCQ Analytics", layout="wide")

st.title("📊 Smart MCQ Quiz Analytics Dashboard")
st.markdown("Analyze performance, identify weak areas, and rank students efficiently.")

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

    # ---------------- KPIs ---------------- #
    st.subheader("📌 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students", len(filtered_df))
    col2.metric("Average Score", round(filtered_df["Score"].mean(), 2))
    col3.metric("Highest Score", filtered_df["Score"].max())
    col4.metric("Lowest Score", filtered_df["Score"].min())

    # ---------------- OVERALL ANALYTICS ---------------- #
    st.header("📊 Overall Analytics")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        sns.histplot(filtered_df["Score"], bins=10, kde=True, ax=ax)
        ax.set_title("Score Distribution")
        st.pyplot(fig)

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

    # ---------------- BOX PLOT ---------------- #
    st.subheader("📦 Score Spread")
    fig, ax = plt.subplots()
    sns.boxplot(x=filtered_df["Score"], ax=ax)
    st.pyplot(fig)

    # ---------------- LEADERBOARD ---------------- #
    st.header("🏆 Student Leaderboard")

    leaderboard_df = leaderboard(filtered_df)
    leaderboard_df["Rank"] = leaderboard_df["Score"].rank(ascending=False, method="min")
    leaderboard_df = leaderboard_df.sort_values("Rank")

    st.dataframe(leaderboard_df.head(10))

    # ---------------- DEPARTMENT PERFORMANCE ---------------- #
    st.header("🏢 Department Performance")

    col1, col2 = st.columns(2)

    with col1:
        dept = department_performance(filtered_df)
        fig, ax = plt.subplots()
        dept.plot(kind="bar", ax=ax)
        ax.set_title("Department Performance")
        st.pyplot(fig)

    with col2:
        pivot = heatmap_data(filtered_df)
        fig, ax = plt.subplots()
        sns.heatmap(pivot, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # Department Insights Table
    st.subheader("📊 Department Insights")
    dept_df = filtered_df.groupby("Department")["Score"].agg(["mean", "count"])
    st.dataframe(dept_df)

    # ---------------- COLLEGE PERFORMANCE ---------------- #
    st.header("🏫 College Ranking")

    college_df = filtered_df.groupby("College")["Score"].mean().sort_values(ascending=False)

    fig, ax = plt.subplots()
    college_df.plot(kind="barh", ax=ax)
    ax.set_title("College Performance")
    st.pyplot(fig)

    # ---------------- QUESTION ANALYSIS ---------------- #
    st.header("❓ Question Analysis")

    col1, col2 = st.columns(2)

    with col1:
        q_analysis = question_analysis(filtered_df, answer_df)

        # Add Difficulty Level
        q_analysis["Difficulty"] = pd.cut(
            q_analysis["Accuracy"],
            bins=[0, 0.4, 0.7, 1],
            labels=["Hard", "Medium", "Easy"]
        )

        st.dataframe(q_analysis)

    with col2:
        fig, ax = plt.subplots()
        sns.barplot(x="Question", y="Accuracy", data=q_analysis, ax=ax)
        ax.set_title("Question Accuracy")
        st.pyplot(fig)

    # ---------------- ATTEMPT RATE ---------------- #
    st.subheader("📌 Attempt Rate")

    attempt = attempt_rate(filtered_df, answer_df)

    fig, ax = plt.subplots()
    sns.barplot(x="Question", y="Attempt Rate", data=attempt, ax=ax)
    ax.set_title("Attempt Rate")
    st.pyplot(fig)

    # ---------------- WEAK & STRONG QUESTIONS ---------------- #
    st.subheader("⚠️ Weak Questions")
    weak_q = q_analysis[q_analysis["Accuracy"] < 0.5]
    st.dataframe(weak_q)

    st.subheader("💪 Strong Questions")
    strong_q = q_analysis[q_analysis["Accuracy"] > 0.8]
    st.dataframe(strong_q)


    
    # ---------------- REPORT GENERATION ---------------- #
    st.header("📄 Generate Reports")

    report_type = st.selectbox(
        "Select Report Type",
        ["Student Report", "Department Report", "College Report", "Quiz Report"]
    )

    # -------- STUDENT REPORT -------- #
    if report_type == "Student Report":
        st.subheader("👤 Student Report")

        student_name = st.selectbox("Select Student", filtered_df["Name"].unique())
        student_df = filtered_df[filtered_df["Name"] == student_name]

        if not student_df.empty:
            score = student_df["Score"].values[0]
            rank = leaderboard_df[leaderboard_df["Name"] == student_name]["Rank"].values[0]

            weak_topics = q_analysis[q_analysis["Accuracy"] < 0.5]["Question"].tolist()

            report = pd.DataFrame({
                "Metric": ["Score", "Rank", "Weak Questions"],
                "Value": [score, rank, ", ".join(map(str, weak_topics))]
            })

            st.table(report)

     # -------- DEPARTMENT REPORT -------- #
    elif report_type == "Department Report":
        st.subheader("🏢 Department Report")

        dept = filtered_df.groupby("Department")["Score"].agg(["mean", "count"])
        top_students = leaderboard_df.head(5)

        st.write("### Average Scores")
        st.dataframe(dept)

        st.write("### Top Students")
        st.dataframe(top_students)

    # -------- COLLEGE REPORT -------- #
    elif report_type == "College Report":
        st.subheader("🏫 College Report")

        college_df = filtered_df.groupby("College")["Score"].mean().sort_values(ascending=False)

        st.write("### College Ranking")
        st.dataframe(college_df)

    # -------- QUIZ REPORT -------- #
    elif report_type == "Quiz Report":
        st.subheader("📝 Quiz Report")

        attempt = attempt_rate(filtered_df, answer_df)

        report = q_analysis.merge(attempt, on="Question")

        st.dataframe(report)

    # ---------------- DOWNLOAD ---------------- #
       
    st.subheader("📥 Download Report")
    
    download_df = None
    
    # Select correct report data
    if report_type == "Student Report" and 'report' in locals():
        download_df = report
    
    elif report_type == "Department Report":
        download_df = dept.reset_index()
    
    elif report_type == "College Report":
        download_df = college_df.reset_index()
    
    elif report_type == "Quiz Report":
        download_df = report
    
    # Download button
    if download_df is not None:
        st.download_button(
            label="Download Selected Report",
            data=download_df.to_csv(index=False),
            file_name=f"{report_type.replace(' ', '_').lower()}.csv",
            mime="text/csv"
        )
    else:
        st.info("Generate a report first to download.")

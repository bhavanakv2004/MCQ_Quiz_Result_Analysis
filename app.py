import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="Quiz Analytics", layout="wide")

# ---------------- LOGIN USERS ---------------- #
users = {
    "admin": "1234",
    "student": "abcd"
}

# ---------------- SESSION ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN FUNCTION ---------------- #
def login():
    st.title("🔐 Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Username or Password ❌")

# ---------------- MAIN APP ---------------- #
def main_app():

    st.title("📊 Smart Quiz Analytics Dashboard")

    # Logout
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Upload
    file = st.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])

    if file:
        # Read file
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        df.columns = df.columns.str.strip()

        st.success("File uploaded successfully")

        # Detect questions
        question_cols = [col for col in df.columns if col.startswith("Q")]
        st.write("Detected Questions:", question_cols)

        # Sidebar Answer Key
        st.sidebar.header("Answer Key")
        answer_key = {}
        for q in question_cols:
            answer_key[q] = st.sidebar.selectbox(q, ["A", "B", "C", "D"])

        # Score calculation
        def calc_score(row):
            score = 0
            for q in answer_key:
                if row[q] == answer_key[q]:
                    score += 1
            return score

        df["Score"] = df.apply(calc_score, axis=1)
        df["Rank"] = df["Score"].rank(ascending=False)

        # KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Students", len(df))
        col2.metric("Average Score", round(df["Score"].mean(), 2))
        col3.metric("Top Score", df["Score"].max())

        # Leaderboard
        st.subheader("🏆 Top Students")
        st.dataframe(df.sort_values("Score", ascending=False).head(10))

        # Charts
        col1, col2 = st.columns(2)

        # Score Distribution
        with col1:
            st.subheader("📈 Score Distribution")
            fig, ax = plt.subplots()
            ax.hist(df["Score"], bins=5)
            st.pyplot(fig)

            #  Save chart (IMPORTANT FIX)
            chart_path = "score_chart.png"
            fig.savefig(chart_path)

        # Department Performance
        with col2:
            if "Department" in df.columns:
                st.subheader(" Department Performance")
                st.bar_chart(df.groupby("Department")["Score"].mean())

        # College Performance
        if "College" in df.columns:
            st.subheader(" College Performance")
            st.bar_chart(df.groupby("College")["Score"].mean())

        # Question Analysis
        st.subheader(" Question Difficulty")

        acc = {}
        for q in question_cols:
            acc[q] = (df[q] == answer_key[q]).mean()

        q_df = pd.DataFrame.from_dict(acc, orient="index", columns=["Accuracy"])
        st.bar_chart(q_df)

        # CSV Download
        st.download_button(
            "⬇️ Download CSV",
            df.to_csv(index=False),
            "quiz_report.csv"
        )
    else:
        st.info("Upload a dataset to begin")

# ---------------- RUN ---------------- #
if not st.session_state.logged_in:
    login()
else:
    main_app()

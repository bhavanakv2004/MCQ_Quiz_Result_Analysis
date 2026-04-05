import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Quiz Analytics", layout="wide")

st.title("📊 Smart Quiz Analytics Dashboard")
# --Upload-- #
file = st.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])

if file:
    # Read file
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.str.strip()

    st.success("File uploaded successfully")

   # ---Detect questions ---- #
    question_cols = [col for col in df.columns if col.startswith("Q")]

    st.write("Detected Questions:", question_cols)

    # ---Sidebar answer key --- #
    st.sidebar.header("Answer Key")
    answer_key = {}
    for q in question_cols:
        answer_key[q] = st.sidebar.selectbox(q, ["A", "B", "C", "D"])

    # ---Score calculation --- #
    def calc_score(row):
        score = 0
        for q in answer_key:
            if row[q] == answer_key[q]:
                score += 1
        return score

    df["Score"] = df.apply(calc_score, axis=1)
    df["Rank"] = df["Score"].rank(ascending=False)


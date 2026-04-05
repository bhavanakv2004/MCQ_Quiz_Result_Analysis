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

   

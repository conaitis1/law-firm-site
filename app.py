import streamlit as st
import pandas as pd

# Load data
@st.cache_data

def load_data():
    df = pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")
    df = df.dropna(axis=1, how='all')  # Drop columns with all NaN values
    return df

df = load_data()

# Title
st.title("Law Firm Case Explorer")
st.write("Filter and explore legal cases based on law firms, outcomes, and financials.")

# Sidebar filters
with st.sidebar:
    st.header("Filter Options")

    firm1 = st.text_input("Search Plaintiff Firm")
    firm2 = st.text_input("Search Defendant Firm")

    status = st.selectbox("Case Status", ["All"] + sorted(df["CaseStatus"].dropna().unique()))
    court = st.selectbox("Federal Court", ["All"] + sorted(df["FederalCourt"].dropna().unique()))
    judge = st.selectbox("Federal Judge", ["All"] + sorted(df["FederalJudge"].dropna().unique()))
    sec_action = st.selectbox("SEC Action", ["All"] + sorted(df["SECActionYN"].dropna().unique()))
    bankruptcy = st.selectbox("Bankruptcy Case", ["All"] + sorted(df["BankruptcyCaseYN"].dropna().unique()))

# Filtering logic
filtered_df = df.copy()

if firm1:
    filtered_df = filtered_df[filtered_df['Plaintiff Firms'].str.contains(firm1, case=False, na=False)]

if firm2:
    filtered_df = filtered_df[filtered_df['Defendant Firms'].str.contains(firm2, case=False, na=False)]

if status != "All":
    filtered_df = filtered_df[filtered_df["CaseStatus"] == status]

if court != "All":
    filtered_df = filtered_df[filtered_df["FederalCourt"] == court]

if judge != "All":
    filtered_df = filtered_df[filtered_df["FederalJudge"] == judge]

if sec_action != "All":
    filtered_df = filtered_df[filtered_df["SECActionYN"] == sec_action]

if bankruptcy != "All":
    filtered_df = filtered_df[filtered_df["BankruptcyCaseYN"] == bankruptcy]

# Display filtered results
st.write(f"### Showing {len(filtered_df)} Matching Cases")
st.dataframe(filtered_df)

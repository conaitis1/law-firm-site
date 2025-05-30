import streamlit as st
import pandas as pd

st.set_page_config(page_title="Law Firm Case Explorer", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")

df = load_data()

st.title("📊 Law Firm Case Explorer")
st.write("Filter and explore legal cases based on law firms, outcomes, and financials.")

# Filters
firm1 = st.text_input("🔍 Plaintiff Firm 1")
firm2 = st.text_input("🔍 Plaintiff Firm 2")
firm3 = st.text_input("🔍 Defendant Firm 1")
firm4 = st.text_input("🔍 Defendant Firm 2")

status = st.selectbox("📂 Case Status", ["All"] + sorted(df["CaseStatus"].dropna().unique()))
po = st.selectbox("📈 PO YN", ["All"] + sorted(df["PO YN"].dropna().unique()))
ipo = st.selectbox("💹 IPO YN", ["All"] + sorted(df["IPO YN"].dropna().unique()))
gaap = st.selectbox("📊 GAAP YN", ["All"] + sorted(df["GAAP YN"].dropna().unique()))
sec11 = st.selectbox("📑 SEC 11 YN", ["All"] + sorted(df["SEC 11 YN"].dropna().unique()))

# Filtering logic
filtered_df = df.copy()

if firm1:
    filtered_df = filtered_df[filtered_df["Plaintiff Firms"].str.contains(firm1, case=False, na=False)]
if firm2:
    filtered_df = filtered_df[filtered_df["Plaintiff Firms"].str.contains(firm2, case=False, na=False)]
if firm3:
    filtered_df = filtered_df[filtered_df["Defendant Firms"].str.contains(firm3, case=False, na=False)]
if firm4:
    filtered_df = filtered_df[filtered_df["Defendant Firms"].str.contains(firm4, case=False, na=False)]

if status != "All":
    filtered_df = filtered_df[filtered_df["CaseStatus"] == status]
if po != "All":
    filtered_df = filtered_df[filtered_df["PO YN"] == po]
if ipo != "All":
    filtered_df = filtered_df[filtered_df["IPO YN"] == ipo]
if gaap != "All":
    filtered_df = filtered_df[filtered_df["GAAP YN"] == gaap]
if sec11 != "All":
    filtered_df = filtered_df[filtered_df["SEC 11 YN"] == sec11]

# Display final filtered data
st.dataframe(filtered_df[[
    "CaseID", "CaseStatus", "CaseName", "SICCode", "ClassStartDate", "ClassEndDate",
    "FederalFilingDate", "PO YN", "IPO YN", "LadderingYN", "TransactionalYN", "IT YN",
    "GAAP YN", "RestatedFinancialsYN", "10B 5 YN", "SEC 11 YN", "SECActionYN",
    "CaseLawFirmRole", "CashAmount", "TotalAmount"
]])

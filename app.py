import streamlit as st
import pandas as pd

st.set_page_config(page_title="Law Firm Case Explorer", layout="wide")
st.title("📊 Law Firm Case Explorer")
st.markdown("Filter and explore legal cases based on law firms, outcomes, and financials.")

@st.cache_data
def load_data():
    df = pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")
    df = df.dropna(axis=1, how='all')
    return df

df = load_data()

with st.sidebar:
    firm1 = st.text_input("🔍 Plaintiff Firm Name")
    firm2 = st.text_input("🔍 Defendant Firm Name")
    status = st.selectbox("Case Status", ["All"] + sorted(df["CaseStatus"].dropna().unique()))
    po = st.selectbox("📈 PO YN", ["All"] + sorted(df["PO YN"].dropna().unique()))
    ipo = st.selectbox("📉 IPO YN", ["All"] + sorted(df["IPO YN"].dropna().unique()))
    ladder = st.selectbox("📊 Laddering YN", ["All"] + sorted(df["LadderingYN"].dropna().unique()))
    transactional = st.selectbox("💼 Transactional YN", ["All"] + sorted(df["TransactionalYN"].dropna().unique()))
    it = st.selectbox("💻 IT YN", ["All"] + sorted(df["IT_YN"].dropna().unique()))
    gaap = st.selectbox("📚 GAAP YN", ["All"] + sorted(df["GAAP_YN"].dropna().unique()))
    restated = st.selectbox("📑 Restated Financials YN", ["All"] + sorted(df["RestatedFinancialsYN"].dropna().unique()))
    sec11 = st.selectbox("📕 SEC 11 YN", ["All"] + sorted(df["SEC_11_YN"].dropna().unique()))
    secaction = st.selectbox("⚖️ SEC Action YN", ["All"] + sorted(df["SECActionYN"].dropna().unique()))
    tenb5 = st.selectbox("🔐 10B 5 YN", ["All"] + sorted(df["10B 5 YN"].dropna().unique()))

filtered_df = df.copy()

if firm1:
    filtered_df = filtered_df[filtered_df['Plaintiff Firms'].str.contains(firm1, case=False, na=False)]

if firm2:
    filtered_df = filtered_df[filtered_df['Defendant Firms'].str.contains(firm2, case=False, na=False)]

if status != "All":
    filtered_df = filtered_df[filtered_df["CaseStatus"] == status]

if po != "All":
    filtered_df = filtered_df[filtered_df["PO YN"] == po]

if ipo != "All":
    filtered_df = filtered_df[filtered_df["IPO YN"] == ipo]

if ladder != "All":
    filtered_df = filtered_df[filtered_df["LadderingYN"] == ladder]

if transactional != "All":
    filtered_df = filtered_df[filtered_df["TransactionalYN"] == transactional]

if it != "All":
    filtered_df = filtered_df[filtered_df["IT YN"] == it]

if gaap != "All":
    filtered_df = filtered_df[filtered_df["GAAP YN"] == gaap]

if restated != "All":
    filtered_df = filtered_df[filtered_df["RestatedFinancialsYN"] == restated]

if sec11 != "All":
    filtered_df = filtered_df[filtered_df["SEC 11 YN"] == sec11]

if secaction != "All":
    filtered_df = filtered_df[filtered_df["SECActionYN"] == secaction]

if tenb5 != "All":
    filtered_df = filtered_df[filtered_df["10B 5 YN"] == tenb5]

st.dataframe(filtered_df[[
    "CaseID", "CaseStatus", "CaseName", "SICCode", "ClassStartDate", "ClassEndDate", "FederalFilingDate",
    "PO YN", "IPO YN", "LadderingYN", "TransactionalYN", "IT_YN", "GAAP_YN", "RestatedFinancialsYN",
    "10B 5 YN", "SEC_11_YN", "SECActionYN", "CaseLawFirmRole", "Plaintiff Firms", "Defendant Firms",
    "CashAmount", "TotalAmount"
]])

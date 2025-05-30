import streamlit as st
import pandas as pd

st.set_page_config(page_title="Law Firm Case Explorer", layout="wide")

@st.cache_data

def load_data():
    df = pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")
    df = df.dropna(axis=1, how='all')  # Drop columns with all NaN values
    return df

df = load_data()

st.title("📊 Law Firm Case Explorer")
st.markdown("""
Filter and explore legal cases based on law firms, outcomes, and financials.
""")

# --- Filters ---
plaintiff_firm1 = st.text_input("🔎 Plaintiff Firm 1 (contains):")
plaintiff_firm2 = st.text_input("🔎 Plaintiff Firm 2 (contains):")
defendant_firm1 = st.text_input("🔍 Defendant Firm 1 (contains):")
defendant_firm2 = st.text_input("🔍 Defendant Firm 2 (contains):")

status = st.selectbox("📂 Case Status", ["All"] + sorted(df["CaseStatus"].dropna().unique()))
sic = st.selectbox("🏷️ SIC Code", ["All"] + sorted(df["SICCode"].dropna().unique()))
po = st.selectbox("📈 PO_YN", ["All"] + sorted(df["PO_YN"].dropna().unique()))
ipo = st.selectbox("🚀 IPO_YN", ["All"] + sorted(df["IPO_YN"].dropna().unique()))
laddering = st.selectbox("📉 LadderingYN", ["All"] + sorted(df["LadderingYN"].dropna().unique()))
transactional = st.selectbox("📃 TransactionalYN", ["All"] + sorted(df["TransactionalYN"].dropna().unique()))
it_yn = st.selectbox("💻 IT_YN", ["All"] + sorted(df["IT_YN"].dropna().unique()))
gaap = st.selectbox("📚 GAAP_YN", ["All"] + sorted(df["GAAP_YN"].dropna().unique()))
restated = st.selectbox("🧾 RestatedFinancialsYN", ["All"] + sorted(df["RestatedFinancialsYN"].dropna().unique()))
sec10b = st.selectbox("📑 10B_5_YN", ["All"] + sorted(df["10B_5_YN"].dropna().unique()))
sec11 = st.selectbox("📑 SEC_11_YN", ["All"] + sorted(df["SEC_11_YN"].dropna().unique()))
secaction = st.selectbox("⚖️ SECActionYN", ["All"] + sorted(df["SECActionYN"].dropna().unique()))

# --- Apply Filters ---
filtered_df = df.copy()

if plaintiff_firm1:
    filtered_df = filtered_df[filtered_df["Plaintiff Firms"].str.contains(plaintiff_firm1, case=False, na=False)]
if plaintiff_firm2:
    filtered_df = filtered_df[filtered_df["Plaintiff Firms"].str.contains(plaintiff_firm2, case=False, na=False)]
if defendant_firm1:
    filtered_df = filtered_df[filtered_df["Defendant Firms"].str.contains(defendant_firm1, case=False, na=False)]
if defendant_firm2:
    filtered_df = filtered_df[filtered_df["Defendant Firms"].str.contains(defendant_firm2, case=False, na=False)]

if status != "All":
    filtered_df = filtered_df[filtered_df["CaseStatus"] == status]
if sic != "All":
    filtered_df = filtered_df[filtered_df["SICCode"] == sic]
if po != "All":
    filtered_df = filtered_df[filtered_df["PO_YN"] == po]
if ipo != "All":
    filtered_df = filtered_df[filtered_df["IPO_YN"] == ipo]
if laddering != "All":
    filtered_df = filtered_df[filtered_df["LadderingYN"] == laddering]
if transactional != "All":
    filtered_df = filtered_df[filtered_df["TransactionalYN"] == transactional]
if it_yn != "All":
    filtered_df = filtered_df[filtered_df["IT_YN"] == it_yn]
if gaap != "All":
    filtered_df = filtered_df[filtered_df["GAAP_YN"] == gaap]
if restated != "All":
    filtered_df = filtered_df[filtered_df["RestatedFinancialsYN"] == restated]
if sec10b != "All":
    filtered_df = filtered_df[filtered_df["10B_5_YN"] == sec10b]
if sec11 != "All":
    filtered_df = filtered_df[filtered_df["SEC_11_YN"] == sec11]
if secaction != "All":
    filtered_df = filtered_df[filtered_df["SECActionYN"] == secaction]

# --- Display Table ---
st.subheader("📁 Filtered Case Results")
st.dataframe(filtered_df[[
    "CaseID", "CaseStatus", "CaseName", "SICCode", "ClassStartDate", "ClassEndDate",
    "FederalFilingDate", "PO_YN", "IPO_YN", "LadderingYN", "TransactionalYN", "IT_YN",
    "GAAP_YN", "RestatedFinancialsYN", "10B_5_YN", "SEC_11_YN", "SECActionYN",
    "CaseLawFirm(Role)", "CashAmount", "TotalAmount"
]])
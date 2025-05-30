import streamlit as st
import pandas as pd

st.set_page_config(page_title="Law Firm Case Explorer", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")

df = load_data()

st.sidebar.title("🔍 Filter Cases")

# Filters
case_status = st.sidebar.selectbox("📂 Case Status", ["All"] + sorted(df["CaseStatus"].dropna().unique()))
plaintiff_firm_1 = st.sidebar.text_input("👨‍⚖️ Plaintiff Firm 1")
plaintiff_firm_2 = st.sidebar.text_input("👨‍⚖️ Plaintiff Firm 2")
defendant_firm_1 = st.sidebar.text_input("🏛 Defendant Firm 1")
defendant_firm_2 = st.sidebar.text_input("🏛 Defendant Firm 2")
po = st.sidebar.selectbox("📈 PO YN", ["All"] + sorted(df["PO YN"].dropna().unique()))
ipo = st.sidebar.selectbox("💹 IPO YN", ["All"] + sorted(df["IPO YN"].dropna().unique()))
laddering = st.sidebar.selectbox("🪜 Laddering YN", ["All"] + sorted(df["LadderingYN"].dropna().unique()))
transactional = st.sidebar.selectbox("🔁 Transactional YN", ["All"] + sorted(df["TransactionalYN"].dropna().unique()))
it = st.sidebar.selectbox("💻 IT YN", ["All"] + sorted(df["IT YN"].dropna().unique()))
gaap = st.sidebar.selectbox("📊 GAAP YN", ["All"] + sorted(df["GAAP YN"].dropna().unique()))
restated = st.sidebar.selectbox("🔄 Restated Financials YN", ["All"] + sorted(df["RestatedFinancialsYN"].dropna().unique()))
sec_10b5 = st.sidebar.selectbox("📑 10B 5 YN", ["All"] + sorted(df["10B 5 YN"].dropna().unique()))
sec_11 = st.sidebar.selectbox("📜 SEC 11 YN", ["All"] + sorted(df["SEC 11 YN"].dropna().unique()))
sec_action = st.sidebar.selectbox("⚖️ SEC Action YN", ["All"] + sorted(df["SECActionYN"].dropna().unique()))

# Filtering logic
filtered_df = df.copy()

if case_status != "All":
    filtered_df = filtered_df[filtered_df["CaseStatus"] == case_status]
if po != "All":
    filtered_df = filtered_df[filtered_df["PO YN"] == po]
if ipo != "All":
    filtered_df = filtered_df[filtered_df["IPO YN"] == ipo]
if laddering != "All":
    filtered_df = filtered_df[filtered_df["LadderingYN"] == laddering]
if transactional != "All":
    filtered_df = filtered_df[filtered_df["TransactionalYN"] == transactional]
if it != "All":
    filtered_df = filtered_df[filtered_df["IT YN"] == it]
if gaap != "All":
    filtered_df = filtered_df[filtered_df["GAAP YN"] == gaap]
if restated != "All":
    filtered_df = filtered_df[filtered_df["RestatedFinancialsYN"] == restated]
if sec_10b5 != "All":
    filtered_df = filtered_df[filtered_df["10B 5 YN"] == sec_10b5]
if sec_11 != "All":
    filtered_df = filtered_df[filtered_df["SEC 11 YN"] == sec_11]
if sec_action != "All":
    filtered_df = filtered_df[filtered_df["SECActionYN"] == sec_action]

# Plaintiff and Defendant firm filters (2 each)
if plaintiff_firm_1:
    filtered_df = filtered_df[filtered_df['Plaintiff Firms'].str.contains(plaintiff_firm_1, case=False, na=False)]
if plaintiff_firm_2:
    filtered_df = filtered_df[filtered_df['Plaintiff Firms'].str.contains(plaintiff_firm_2, case=False, na=False)]
if defendant_firm_1:
    filtered_df = filtered_df[filtered_df['Defendant Firms'].str.contains(defendant_firm_1, case=False, na=False)]
if defendant_firm_2:
    filtered_df = filtered_df[filtered_df['Defendant Firms'].str.contains(defendant_firm_2, case=False, na=False)]

# Display
st.title("📊 Law Firm Case Explorer")
st.markdown("Filter and explore legal cases based on law firms, outcomes, and financials.")

columns_to_display = [
    "CaseID", "CaseStatus", "CaseName", "SICCode", "ClassStartDate", "ClassEndDate",
    "FederalFilingDate", "PO YN", "IPO YN", "LadderingYN", "TransactionalYN",
    "IT YN", "GAAP YN", "RestatedFinancialsYN", "10B 5 YN", "SEC 11 YN", "SECActionYN",
    "CaseLawFirmRole", "CashAmount", "TotalAmount"
]

available_columns = [col for col in columns_to_display if col in filtered_df.columns]

st.dataframe(filtered_df[available_columns], use_container_width=True)

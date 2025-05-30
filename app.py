import streamlit as st
import pandas as pd

@st.cache_data

def load_data():
    df = pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")
    df = df.dropna(axis=1, how='all')  # Drop columns with all NaN values
    df["FederalCaseNumber"] = df["FederalCaseNumber"].astype(str)
    return df

df = load_data()

st.set_page_config(page_title="Law Firm Case Explorer", layout="wide")
st.title("📊 Law Firm Case Explorer")
st.markdown("Filter and explore legal cases based on key legal case attributes.")

# Sidebar filters with selected fields only
with st.sidebar:
    st.header("🔍 Filters")
    case_id = st.text_input("Case ID")
    status = st.selectbox("Case Status", ["All"] + sorted(df["CaseStatus"].dropna().unique()))
    casename = st.text_input("Case Name")
    sic_code = st.text_input("SIC Code")
    class_start = st.date_input("Class Start Date", value=None)
    class_end = st.date_input("Class End Date", value=None)
    filing_date = st.date_input("Federal Filing Date", value=None)

    # Binary flag fields
    flags = ["PO_YN", "IPO_YN", "LadderingYN", "TransactionalYN", "IT_YN", "GAAP_YN",
             "RestatedFinancialsYN", "10B_5_YN", "SEC_11_YN", "SECActionYN"]
    flag_filters = {}
    for flag in flags:
        if flag in df.columns:
            flag_filters[flag] = st.selectbox(f"{flag}", ["All", "Yes", "No"])

# Apply filters
filtered_df = df.copy()

if case_id:
    filtered_df = filtered_df[filtered_df["CaseID"].astype(str).str.contains(case_id, case=False, na=False)]

if status != "All":
    filtered_df = filtered_df[filtered_df["CaseStatus"] == status]

if casename:
    filtered_df = filtered_df[filtered_df["CaseName"].str.contains(casename, case=False, na=False)]

if sic_code:
    filtered_df = filtered_df[filtered_df["SICCode"].astype(str).str.contains(sic_code, na=False)]

if class_start:
    filtered_df = filtered_df[pd.to_datetime(filtered_df["ClassStartDate"], errors='coerce') >= pd.to_datetime(class_start)]

if class_end:
    filtered_df = filtered_df[pd.to_datetime(filtered_df["ClassEndDate"], errors='coerce') <= pd.to_datetime(class_end)]

if filing_date:
    filtered_df = filtered_df[pd.to_datetime(filtered_df["FederalFilingDate"], errors='coerce') >= pd.to_datetime(filing_date)]

for flag, value in flag_filters.items():
    if value != "All":
        filtered_df = filtered_df[filtered_df[flag] == value]

# Display final result
st.write(f"### {len(filtered_df)} Matching Cases")
st.dataframe(filtered_df[[
    "CaseID", "CaseStatus", "CaseName", "SICCode", "ClassStartDate", "ClassEndDate",
    "FederalFilingDate", "PO_YN", "IPO_YN", "LadderingYN", "TransactionalYN", "IT_YN",
    "GAAP_YN", "RestatedFinancialsYN", "10B_5_YN", "SEC_11_YN", "SECActionYN",
    "CaseLawFirm(Role)", "CashAmount", "TotalAmount"
]])

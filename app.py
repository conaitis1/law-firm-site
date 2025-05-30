import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")

df = load_data()

st.set_page_config(page_title="📊 Law Firm Case Explorer", layout="wide")
st.title("📊 Law Firm Case Explorer")
st.markdown("Filter and explore legal cases based on law firms, outcomes, and financials.")

# Sidebar Filters
with st.sidebar:
    st.header("🔍 Filter Cases")

    firm1 = st.text_input("Plaintiff Firm")
    firm2 = st.text_input("Defendant Firm")

    status = st.selectbox("Case Status", ["All"] + sorted(df["CaseStatus"].dropna().unique()))
    casename = st.text_input("Case Name")
    sic_code = st.text_input("SIC Code")

    class_start = st.date_input("Class Start Date", value=None)
    class_end = st.date_input("Class End Date", value=None)

    # Optional flag-based filters
    flags = ["Alleged GAAP Violations", "Restatement of Financials", "Insider Trading",
             "SEC Investigation", "Criminal Charges", "DOJ Investigation"]
    flag_filters = {}
    for flag in flags:
        flag_filters[flag] = st.checkbox(flag)

# Filter logic
filtered = df.copy()

if firm1:
    filtered = filtered[filtered["PlaintiffFirm"].str.contains(firm1, case=False, na=False)]
if firm2:
    filtered = filtered[filtered["DefendantFirm"].str.contains(firm2, case=False, na=False)]
if status != "All":
    filtered = filtered[filtered["CaseStatus"] == status]
if casename:
    filtered = filtered[filtered["CaseName"].str.contains(casename, case=False, na=False)]
if sic_code:
    filtered = filtered[filtered["SICCode"].astype(str).str.contains(sic_code, na=False)]

for flag, active in flag_filters.items():
    if active and flag in filtered.columns:
        filtered = filtered[filtered[flag] == "Yes"]

st.markdown(f"### 📁 {len(filtered)} Matching Cases")
st.dataframe(filtered, use_container_width=True)

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Law Firm Case Explorer", layout="wide")

@st.cache_data

def load_data():
    df = pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")
    df = df.dropna(axis=1, how='all')
    return df

df = load_data()
st.title("📊 Law Firm Case Explorer")
st.markdown("Filter and explore legal cases based on law firms, outcomes, and financials.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    firm1 = st.text_input("🔍 Plaintiff Firm Name 1")
with col2:
    firm2 = st.text_input("🔍 Plaintiff Firm Name 2")
with col3:
    firm3 = st.text_input("⚖️ Defendant Firm Name 1")
with col4:
    firm4 = st.text_input("⚖️ Defendant Firm Name 2")

col5, col6, col7, col8 = st.columns(4)
with col5:
    status = st.selectbox("📌 Case Status", ["All"] + sorted(df["CaseStatus"].dropna().unique()))
with col6:
    sic = st.selectbox("🏷️ SIC Code", ["All"] + sorted(df["SICCode"].dropna().astype(str).unique()))
with col7:
    po = st.selectbox("📈 PO_YN", ["All"] + sorted(df["PO_YN"].dropna().astype(str).unique()))
with col8:
    ipo = st.selectbox("📉 IPO_YN", ["All"] + sorted(df["IPO_YN"].dropna().astype(str).unique()))

col9, col10, col11, col12 = st.columns(4)
with col9:
    laddering = st.selectbox("📊 LadderingYN", ["All"] + sorted(df["LadderingYN"].dropna().astype(str).unique()))
with col10:
    transactional = st.selectbox("📃 TransactionalYN", ["All"] + sorted(df["TransactionalYN"].dropna().astype(str).unique()))
with col11:
    it = st.selectbox("💻 IT_YN", ["All"] + sorted(df["IT_YN"].dropna().astype(str).unique()))
with col12:
    gaap = st.selectbox("📚 GAAP_YN", ["All"] + sorted(df["GAAP_YN"].dropna().astype(str).unique()))

col13, col14, col15, col16 = st.columns(4)
with col13:
    restated = st.selectbox("📝 RestatedFinancialsYN", ["All"] + sorted(df["RestatedFinancialsYN"].dropna().astype(str).unique()))
with col14:
    sec_10b5 = st.selectbox("🧾 10B_5_YN", ["All"] + sorted(df["10B_5_YN"].dropna().astype(str).unique()))
with col15:
    sec_11 = st.selectbox("📄 SEC_11_YN", ["All"] + sorted(df["SEC_11_YN"].dropna().astype(str).unique()))
with col16:
    sec_action = st.selectbox("⚖️ SECActionYN", ["All"] + sorted(df["SECActionYN"].dropna().astype(str).unique()))

filtered_df = df.copy()

if firm1:
    filtered_df = filtered_df[filtered_df['CaseLawFirm(Role)'].str.contains(firm1, case=False, na=False)]
if firm2:
    filtered_df = filtered_df[filtered_df['CaseLawFirm(Role)'].str.contains(firm2, case=False, na=False)]
if firm3:
    filtered_df = filtered_df[filtered_df['CaseLawFirm(Role)'].str.contains(firm3, case=False, na=False)]
if firm4:
    filtered_df = filtered_df[filtered_df['CaseLawFirm(Role)'].str.contains(firm4, case=False, na=False)]

if status != "All":
    filtered_df = filtered_df[filtered_df["CaseStatus"] == status]
if sic != "All":
    filtered_df = filtered_df[filtered_df["SICCode"].astype(str) == sic]
if po != "All":
    filtered_df = filtered_df[filtered_df["PO_YN"].astype(str) == po]
if ipo != "All":
    filtered_df = filtered_df[filtered_df["IPO_YN"].astype(str) == ipo]
if laddering != "All":
    filtered_df = filtered_df[filtered_df["LadderingYN"].astype(str) == laddering]
if transactional != "All":
    filtered_df = filtered_df[filtered_df["TransactionalYN"].astype(str) == transactional]
if it != "All":
    filtered_df = filtered_df[filtered_df["IT_YN"].astype(str) == it]
if gaap != "All":
    filtered_df = filtered_df[filtered_df["GAAP_YN"].astype(str) == gaap]
if restated != "All":
    filtered_df = filtered_df[filtered_df["RestatedFinancialsYN"].astype(str) == restated]
if sec_10b5 != "All":
    filtered_df = filtered_df[filtered_df["10B_5_YN"].astype(str) == sec_10b5]
if sec_11 != "All":
    filtered_df = filtered_df[filtered_df["SEC_11_YN"].astype(str) == sec_11]
if sec_action != "All":
    filtered_df = filtered_df[filtered_df["SECActionYN"].astype(str) == sec_action]

st.dataframe(filtered_df[[
    "CaseID", "CaseStatus", "CaseName", "SICCode", "ClassStartDate", "ClassEndDate",
    "FederalFilingDate", "PO_YN", "IPO_YN", "LadderingYN", "TransactionalYN",
    "IT_YN", "GAAP_YN", "RestatedFinancialsYN", "10B_5_YN", "SEC_11_YN", "SECActionYN",
    "CaseLawFirm(Role)", "CashAmount", "TotalAmount"
]])

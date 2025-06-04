import streamlit as st
import pandas as pd

st.set_page_config(page_title="Law Firm Case Explorer", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")

df = load_data()

# Format date columns
for col in ['ClassStartDate', 'ClassEndDate', 'FederalFilingDate']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# Sidebar filters
st.sidebar.title("🔍 Filter Cases")

case_status = st.sidebar.selectbox("📂 Case Status", ["All"] + sorted(df["CaseStatus"].dropna().unique()))
plaintiff_firm = st.sidebar.selectbox("👨‍⚖️ Plaintiff Firm", ["All"] + sorted(df["Plaintiff Firms"].dropna().unique()))
defendant_firm = st.sidebar.selectbox("🏛 Defendant Firm", ["All"] + sorted(df["Defendant Firms"].dropna().unique()))
firm_counts = df.groupby(['Plaintiff Firms', 'Defendant Firms']).size().reset_index(name='Count')
max_cases = firm_counts['Count'].max()
min_case_filter_enabled = st.sidebar.checkbox("✅ Apply Minimum Case Count Filter", value=True)
min_case_count = st.sidebar.slider("🔢 Minimum Cases Between Firms", 1, int(max_cases), 5)

year_range = st.sidebar.slider("📅 Class Start Year Range", 2000, 2025, (2010, 2025))

# Additional filters with updated column names
po = st.sidebar.selectbox("📈 PO YN", ["All"] + sorted(df["PO YN"].dropna().unique()))
ipo = st.sidebar.selectbox("💹 IPO YN", ["All"] + sorted(df["IPO YN"].dropna().unique()))
laddering = st.sidebar.selectbox("🪜 Laddering YN", ["All"] + sorted(df["Laddering YN"].dropna().unique()))
transactional = st.sidebar.selectbox("🔁 Transactional YN", ["All"] + sorted(df["TransactionalYN"].dropna().unique()))
it = st.sidebar.selectbox("💻 IT YN", ["All"] + sorted(df["IT YN"].dropna().unique()))
gaap = st.sidebar.selectbox("📊 GAAP YN", ["All"] + sorted(df["GAAP YN"].dropna().unique()))
restated = st.sidebar.selectbox("🔄 Restated Financials YN", ["All"] + sorted(df["RestatedFinancialsYN"].dropna().unique()))
sec_10b5 = st.sidebar.selectbox("📑 10B 5 YN", ["All"] + sorted(df["10B 5 YN"].dropna().unique()))
sec_11 = st.sidebar.selectbox("📜 SEC 11 YN", ["All"] + sorted(df["SEC 11 YN"].dropna().unique()))
sec_action = st.sidebar.selectbox("⚖️ SEC Action YN", ["All"] + sorted(df["SECActionYN"].dropna().unique()))

# === Filtering logic ===
filtered_df = df.copy()

if case_status != "All":
    filtered_df = filtered_df[filtered_df["CaseStatus"] == case_status]
if plaintiff_firm != "All":
    filtered_df = filtered_df[filtered_df["Plaintiff Firms"] == plaintiff_firm]
if defendant_firm != "All":
    filtered_df = filtered_df[filtered_df["Defendant Firms"] == defendant_firm]
if po != "All":
    filtered_df = filtered_df[filtered_df["PO YN"] == po]
if ipo != "All":
    filtered_df = filtered_df[filtered_df["IPO YN"] == ipo]
if laddering != "All":
    filtered_df = filtered_df[filtered_df["Laddering YN"] == laddering]
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

# Year range filter
filtered_df = filtered_df[
    filtered_df['ClassStartDate'].notna() &
    (filtered_df['ClassStartDate'].dt.year >= year_range[0]) &
    (filtered_df['ClassStartDate'].dt.year <= year_range[1])
]

# Case count filter (if checkbox enabled)
if min_case_filter_enabled:
    filtered_df = filtered_df.merge(firm_counts, on=['Plaintiff Firms', 'Defendant Firms'])
    filtered_df = filtered_df[filtered_df['Count'] >= min_case_count]

# Format all datetime columns to just date (no time)
for col in filtered_df.columns:
    if pd.api.types.is_datetime64_any_dtype(filtered_df[col]):
        filtered_df[col] = filtered_df[col].dt.date

# Format currency columns
for col in ["CashAmount", "TotalAmount"]:
    if col in filtered_df.columns:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors="coerce")
        filtered_df[col] = filtered_df[col].map(lambda x: f"$ {x:,.2f}" if pd.notnull(x) else "")

# Display title and description
st.title("📊 Law Firm Case Explorer")
st.markdown("Filter and explore legal cases based on law firms, outcomes, and financials.")

# Show full table with centered cell style
st.dataframe(
    filtered_df.style
    .set_properties(**{"text-align": "center"})
    .set_table_styles([
        {"selector": "th", "props": [("text-align", "center")]},
        {"selector": "td", "props": [("text-align", "center")]}
    ]),
    use_container_width=True,
    height=800
)

st.markdown(f"### Total Cases Displayed: {len(filtered_df)}")


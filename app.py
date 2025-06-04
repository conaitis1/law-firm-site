import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="Law Firm Case Explorer", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")

df = load_data()

# Convert datetime columns to just dates
for col in df.columns:
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.date

# Sidebar filters
st.sidebar.title("🔍 Filter Cases")

case_status = st.sidebar.selectbox("📂 Case Status", ["All"] + sorted(df["CaseStatus"].dropna().unique()))
plaintiff_firm = st.sidebar.selectbox("👨‍⚖️ Plaintiff Firm", ["All"] + sorted(df["Plaintiff Firms"].dropna().unique()))
defendant_firm = st.sidebar.selectbox("🏛 Defendant Firm", ["All"] + sorted(df["Defendant Firms"].dropna().unique()))
firm_pair_counts = df.groupby(['Plaintiff Firms', 'Defendant Firms']).size().reset_index(name='Count')
max_case_count = firm_pair_counts['Count'].max()
use_case_count_filter = st.sidebar.checkbox("🔢 Use Minimum Case Filter", value=False)
min_case_count = st.sidebar.slider("Minimum Cases Between Firms", 1, int(max_case_count), 1)
year_range = st.sidebar.slider("📅 Class Start Year Range", 2000, 2025, (2010, 2025))

# Other filters
filters = {
    "PO_YN": "📈 PO YN",
    "IPO_YN": "💹 IPO YN",
    "LadderingYN": "🪜 Laddering YN",
    "TransactionalYN": "🔁 Transactional YN",
    "IT_YN": "💻 IT YN",
    "GAAP_YN": "📊 GAAP YN",
    "RestatedFinancialsYN": "🔄 Restated Financials YN",
    "10B_5_YN": "📑 10B 5 YN",
    "SEC_11_YN": "📜 SEC 11 YN",
    "SECActionYN": "⚖️ SEC Action YN"
}

for col, label in filters.items():
    options = ["All"] + sorted(df[col].dropna().unique())
    selected = st.sidebar.selectbox(label, options)
    if selected != "All":
        df = df[df[col] == selected]

# Apply other filters
if case_status != "All":
    df = df[df["CaseStatus"] == case_status]
if plaintiff_firm != "All":
    df = df[df["Plaintiff Firms"] == plaintiff_firm]
if defendant_firm != "All":
    df = df[df["Defendant Firms"] == defendant_firm]
df = df[
    df["ClassStartDate"].notna() &
    (pd.to_datetime(df["ClassStartDate"]).dt.year >= year_range[0]) &
    (pd.to_datetime(df["ClassStartDate"]).dt.year <= year_range[1])
]
if use_case_count_filter:
    df = df.merge(firm_pair_counts, on=['Plaintiff Firms', 'Defendant Firms'])
    df = df[df['Count'] >= min_case_count]

# Format cash columns
for col in ["CashAmount", "TotalAmount"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Ag-Grid display with formatting
gb = GridOptionsBuilder.from_dataframe(df)
currency_formatter = JsCode('''function(params) {
    if (params.value === undefined || params.value === null || params.value === "") {
        return "";
    }
    return "$" + Number(params.value).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
}''')

for col in df.columns:
    gb.configure_column(col, cellStyle={'textAlign': 'center'})
for money_col in ["CashAmount", "TotalAmount"]:
    if money_col in df.columns:
        gb.configure_column(money_col, type=["numericColumn", "customNumericFormat"], valueFormatter=currency_formatter)

gridOptions = gb.build()

st.title("📊 Law Firm Case Explorer")
st.markdown("Filter and explore legal cases based on law firms, outcomes, and financials.")
AgGrid(df, gridOptions=gridOptions, height=800, fit_columns_on_grid_load=True)

st.markdown(f"### Total Cases Displayed: {len(df)}")

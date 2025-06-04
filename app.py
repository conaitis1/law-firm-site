import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="Law Firm Case Explorer", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")

df = load_data()

# Convert datetime columns to date (no time)
for col in df.columns:
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.date

# Sidebar filters
st.sidebar.title("🔍 Filter Cases")

def safe_unique(colname):
    return sorted(df[colname].dropna().unique()) if colname in df.columns else []

case_status = st.sidebar.selectbox("📂 Case Status", ["All"] + safe_unique("CaseStatus"))
plaintiff_firm = st.sidebar.selectbox("👨‍⚖️ Plaintiff Firm", ["All"] + safe_unique("Plaintiff Firms"))
defendant_firm = st.sidebar.selectbox("🏛 Defendant Firm", ["All"] + safe_unique("Defendant Firms"))
year_range = st.sidebar.slider("📅 Class Start Year Range", 2000, 2025, (2010, 2025))

# Feature filters
filters = {
    "PO YN": "📈 PO YN",
    "IPO YN": "💹 IPO YN",
    "LadderingYN": "🪜 Laddering YN",
    "TransactionalYN": "🔁 Transactional YN",
    "IT YN": "💻 IT YN",
    "GAAP YN": "📊 GAAP YN",
    "RestatedFinancialsYN": "🔄 Restated Financials YN",
    "10B 5 YN": "📑 10B 5 YN",
    "SEC 11 YN": "📜 SEC 11 YN",
    "SECActionYN": "⚖️ SEC Action YN"
}

filter_values = {}
for col, label in filters.items():
    options = ["All"] + safe_unique(col)
    filter_values[col] = st.sidebar.selectbox(label, options)

# Min cases toggle + slider
use_min_case_filter = st.sidebar.checkbox("🔢 Enable Minimum Case Count Filter", value=True)
max_case_count = df.groupby(['Plaintiff Firms', 'Defendant Firms']).size().max()
min_case_count = st.sidebar.slider("Minimum Cases Between Firms", 1, int(max_case_count), 5)

# Apply filters
filtered_df = df.copy()

if case_status != "All":
    filtered_df = filtered_df[filtered_df["CaseStatus"] == case_status]
if plaintiff_firm != "All":
    filtered_df = filtered_df[filtered_df["Plaintiff Firms"] == plaintiff_firm]
if defendant_firm != "All":
    filtered_df = filtered_df[filtered_df["Defendant Firms"] == defendant_firm]
for col, val in filter_values.items():
    if val != "All":
        filtered_df = filtered_df[filtered_df[col] == val]
if "ClassStartDate" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df['ClassStartDate'].notna() &
        (pd.to_datetime(filtered_df['ClassStartDate']).dt.year >= year_range[0]) &
        (pd.to_datetime(filtered_df['ClassStartDate']).dt.year <= year_range[1])
    ]

# Filter by case count between firm pairs
if use_min_case_filter:
    pair_counts = df.groupby(['Plaintiff Firms', 'Defendant Firms']).size().reset_index(name='Count')
    filtered_df = filtered_df.merge(pair_counts, on=['Plaintiff Firms', 'Defendant Firms'], how='left')
    filtered_df = filtered_df[filtered_df['Count'] >= min_case_count]
    filtered_df.drop(columns=['Count'], inplace=True, errors='ignore')

# Convert monetary columns to numeric
for col in ["CashAmount", "TotalAmount"]:
    if col in filtered_df.columns:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')

# === Display with AgGrid ===
st.title("📊 Law Firm Case Explorer")

gb = GridOptionsBuilder.from_dataframe(filtered_df)

# Format currency columns
currency_format = JsCode("""
function(params) {
    if (params.value === null || params.value === undefined || params.value === "") {
        return '';
    }
    return '$' + Number(params.value).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
}
""")

for col in ["CashAmount", "TotalAmount"]:
    if col in filtered_df.columns:
        gb.configure_column(col, type=["numericColumn"], cellRenderer=currency_format)

# Center all columns
for col in filtered_df.columns:
    gb.configure_column(col, cellStyle={"textAlign": "center"})

grid_options = gb.build()

AgGrid(
    filtered_df,
    gridOptions=grid_options,
    enable_enterprise_modules=False,
    use_checkbox=False,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    height=800
)

st.markdown(f"### Total Cases Displayed: {len(filtered_df)}")

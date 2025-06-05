import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="Law Firm Case Explorer", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")

df = load_data()

# Clean and convert datetime columns
for col in df.columns:
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.date

# Ensure monetary columns are numeric
for col in ["CashAmount", "TotalAmount"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# === Sidebar Filters ===
st.sidebar.title("🔍 Filter Cases")

def safe_unique(colname):
    return sorted(df[colname].dropna().unique()) if colname in df.columns else []

case_status = st.sidebar.selectbox("📂 Case Status", ["All"] + safe_unique("CaseStatus"))
plaintiff_firm = st.sidebar.selectbox("👨‍⚖️ Plaintiff Firm", ["All"] + safe_unique("Plaintiff Firms"))
defendant_firm = st.sidebar.selectbox("🏛 Defendant Firm", ["All"] + safe_unique("Defendant Firms"))
year_range = st.sidebar.slider("📅 Class Start Year Range", 2000, 2025, (2010, 2025))

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

use_case_filter = st.sidebar.checkbox("🔢 Enable Minimum Case Filter", value=True)
max_case_count = df.groupby(['Plaintiff Firms', 'Defendant Firms']).size().max()
min_case_count = st.sidebar.slider("Minimum Cases Between Firms", 1, int(max_case_count), 5)

# === Filtering Logic ===
filtered_df = df.copy()

if case_status != "All":
    filtered_df = filtered_df[filtered_df["CaseStatus"] == case_status]
if plaintiff_firm != "All":
    filtered_df = filtered_df[filtered_df["Plaintiff Firms"] == plaintiff_firm]
if defendant_firm != "All":
    filtered_df = filtered_df[filtered_df["Defendant Firms"] == defendant_firm]
for col, val in filter_values.items():
    if val != "All" and col in filtered_df.columns:
        filtered_df = filtered_df[filtered_df[col] == val]
if "ClassStartDate" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["ClassStartDate"].notna() &
        (pd.to_datetime(filtered_df["ClassStartDate"]).dt.year >= year_range[0]) &
        (pd.to_datetime(filtered_df["ClassStartDate"]).dt.year <= year_range[1])
    ]

if use_case_filter:
    pair_counts = df.groupby(['Plaintiff Firms', 'Defendant Firms']).size().reset_index(name='Count')
    filtered_df = filtered_df.merge(pair_counts, on=['Plaintiff Firms', 'Defendant Firms'], how='left')
    filtered_df = filtered_df[filtered_df['Count'] >= min_case_count]
    filtered_df.drop(columns=['Count'], inplace=True, errors='ignore')

# === AgGrid Config ===
gb = GridOptionsBuilder.from_dataframe(filtered_df)

# Global defaults: compact, non-wrapping
gb.configure_default_column(
    resizable=True,
    autoHeight=False,
    wrapText=False,
    cellStyle={
        "whiteSpace": "nowrap",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
        "textAlign": "center"
    }
)

# JS for dollar formatting
currency_format = JsCode("""
function(params) {
    if (params.value === null || params.value === undefined || isNaN(params.value)) {
        return '';
    }
    return '$' + Number(params.value).toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}
""")

for col in ["CashAmount", "TotalAmount"]:
    if col in filtered_df.columns:
        gb.configure_column(col, valueFormatter=currency_format)

# Scrollable long columns
long_columns = ["SettlementDesc", "SettlingDefendants", "PlaintiffLegalFeesDesc", "Allegations", "CaseLawFirmRole"]
for col in long_columns:
    if col in filtered_df.columns:
        gb.configure_column(
            col,
            cellStyle={
                "textAlign": "left",
                "overflow": "auto",
                "whiteSpace": "nowrap",
                "maxWidth": "300px"
            },
            autoHeight=False,
            wrapText=False
        )

grid_options = gb.build()
grid_options["suppressSizeToFit"] = True  # <- critical to prevent global auto-stretch

# === Display ===
st.title("📊 Law Firm Case Explorer")
# Convert datetime columns to formatted strings so AgGrid doesn't parse them as dates
date_columns = ["ClassStartDate", "ClassEndDate", "FederalFilingDate", "FinalSettlementDate", "TentativeSettlementDate", "ObjectionDeadline", "ClaimDeadline", "LeadPlaintiffDeadline", "Updated_On_Date"]

for col in date_columns:
    if col in filtered_df.columns:
        filtered_df[col] = pd.to_datetime(filtered_df[col], errors="coerce").apply(
            lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else ""
        )

AgGrid(
    filtered_df,
    gridOptions=grid_options,
    enable_enterprise_modules=False,
    use_checkbox=False,
    fit_columns_on_grid_load=False,
    allow_unsafe_jscode=True,
    height=800
)

st.markdown(f"### Total Cases Displayed: {len(filtered_df)}")

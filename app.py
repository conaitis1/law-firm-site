import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

@st.cache_resource
def load_model():
    return joblib.load("rf_model.joblib")

st.set_page_config(page_title="Law Firm Case Explorer", layout="wide")
st.markdown("""
    <style>
    .stSelectbox div[role="option"]:first-child {
        color: gray;
    }
    </style>
""", unsafe_allow_html=True)

from PIL import Image
import streamlit as st

# Load and display the image in top-right corner
image = Image.open("logo.png")

# Set up fixed-position logo in top-right corner using HTML
st.markdown(
    """
    <style>
    .top-right-logo {
        position: absolute;
        top: 35px;
        right: 60px;
        z-index: 10000;
    </style>
    <div class="top-right-logo">
        <img src="https://raw.githubusercontent.com/conaitis1/law-firm-site/main/logo.png" width="120">
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    return pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")

df = load_data()

# Normalize all YN filter columns to proper "Yes"/"No"
yn_columns = ["PO", "IPO", "Laddering", "Transactional", "IT", "GAAP", "RestatedFinancials", "10B 5", "SEC 11", "SECAction"]
for col in yn_columns:
    if col in df.columns:
        df[col] = df[col].map({1: "Yes", 0: "No", "Yes": "Yes", "No": "No"})  # handles both numeric and string

# Convert datetime columns to 'YYYY-MM-DD' strings
date_columns = [
    "ClassStartDate", "ClassEndDate", "FederalFilingDate", "FinalSettlementDate",
    "TentativeSettlementDate", "ObjectionDeadline", "ClaimDeadline",
    "LeadPlaintiffDeadline", "Updated_On_Date", "DismissalDate"
]
for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')

# Ensure monetary columns are numeric (needed for formatting to work)
monetary_columns = ["CashAmount", "TotalAmount", "NonCashAmount"]
for col in monetary_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# === Sidebar Filters ===
st.sidebar.title("🔍 Filter Cases")

def safe_unique(colname):
    return sorted(df[colname].dropna().unique()) if colname in df.columns else []

case_status = st.sidebar.selectbox("Case Status", ["All"] + safe_unique("CaseStatus"))
year_range = st.sidebar.slider("Class Start Year Range", 2000, 2025, (2010, 2025))
# Only keep values that can be safely cast to integers
valid_siccodes = pd.to_numeric(df["SICCode"], errors="coerce").dropna().astype(int).astype(str).unique()
siccode_options = ["Select..."] + sorted(valid_siccodes)
siccode_input = st.sidebar.text_input("Filter by SICCode", placeholder="Enter SICCode...")




def extract_individual_firms(column):
    all_firms = df[column].dropna().astype(str).str.split(";")
    flat_firms = sorted(set(firm.strip() for sublist in all_firms for firm in sublist if firm.strip()))
    return flat_firms

# Plaintiff Firm
plaintiff_firm_options = ["All"] + extract_individual_firms("Plaintiff Firms")
plaintiff_firm = st.sidebar.selectbox(
    "Plaintiff Firm", 
    plaintiff_firm_options, 
    index=None,  # 👈 makes it look empty until user clicks
    placeholder="Select firm..."
)

# Defendant Firm
defendant_firm_options = ["All"] + extract_individual_firms("Defendant Firms")
defendant_firm = st.sidebar.selectbox(
    "Defendant Firm", 
    defendant_firm_options, 
    index=None,
    placeholder="Select firm..."
)

filters = {
    "PO": "PO",
    "IPO": "IPO",
    "Laddering": "Laddering",
    "Transactional": "Transactional",
    "IT": "IT",
    "GAAP": "GAAP",
    "RestatedFinancials": "Restated Financials",
    "10B 5": "10B 5",
    "SEC 11": "SEC 11",
    "SECAction": "SEC Action"
}

filter_values = {}
for col, label in filters.items():
    options = ["Select..."] + [val for val in ["Yes", "No"] if col in df.columns and val in df[col].unique()]
    filter_values[col] = st.sidebar.selectbox(label, options, index=0)



use_case_filter = st.sidebar.checkbox("Enable Minimum Case Filter", value=False)
max_case_count = df.groupby(['Plaintiff Firms', 'Defendant Firms']).size().max()
min_case_count = st.sidebar.slider("Minimum Cases Between Firms", 1, int(max_case_count), 5)

# === Filtering Logic ===
filtered_df = df.copy()
currency_formatter = JsCode("""
(params) => params.value != null ? '$' + Math.round(params.value).toLocaleString() : ''
""")
gb = GridOptionsBuilder.from_dataframe(filtered_df)

for col in monetary_columns:
    if col in filtered_df.columns:
        gb.configure_column(
            col,
            type=["numericColumn"],
            valueFormatter=currency_formatter,
            headerClass="centered-header"
        )

if case_status != "All":
    filtered_df = filtered_df[filtered_df["CaseStatus"] == case_status]
if plaintiff_firm and plaintiff_firm != "All":
    filtered_df = filtered_df[filtered_df["Plaintiff Firms"].astype(str).str.contains(plaintiff_firm)]

if defendant_firm and defendant_firm != "All":
    filtered_df = filtered_df[filtered_df["Defendant Firms"].astype(str).str.contains(defendant_firm)]
try:
    siccode_num = float(siccode_input.strip())
    filtered_df = filtered_df[filtered_df["SICCode"] == siccode_num]
except ValueError:
    pass






for col, val in filter_values.items():
    if val != "Select..." and col in filtered_df.columns:
        filtered_df = filtered_df[filtered_df[col] == val]


if "ClassStartDate" in filtered_df.columns:
    class_start = pd.to_datetime(filtered_df["ClassStartDate"], errors="coerce")
    filtered_df = filtered_df[class_start.dt.year.between(year_range[0], year_range[1])]

if use_case_filter:
    pair_counts = df.groupby(['Plaintiff Firms', 'Defendant Firms']).size().reset_index(name='Count')
    filtered_df = filtered_df.merge(pair_counts, on=['Plaintiff Firms', 'Defendant Firms'], how='left')
    filtered_df = filtered_df[filtered_df['Count'] >= min_case_count]
    filtered_df.drop(columns=['Count'], inplace=True, errors='ignore')

# === Exact Date Filter ===
from datetime import date

exact_class_end_date = st.sidebar.date_input(
    "Filter by Exact Class End Date (optional)",
    value=None,
    min_value=date(2000, 1, 1),
    max_value=date(2030, 12, 31)
)

if exact_class_end_date:
    filtered_df = filtered_df[
        pd.to_datetime(filtered_df["ClassEndDate"], errors='coerce') == pd.to_datetime(exact_class_end_date)
    ]

# === AgGrid Config ===
# Define a custom CSS class for centered headers
gb.configure_default_column(
    resizable=True,
    autoHeight=False,
    wrapText=False,
    headerClass="center-header",  # <-- This line is key
    cellStyle={
        "whiteSpace": "nowrap",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
        "textAlign": "center"
    }
)



# ✅ Dollar formatting via valueFormatter
currency_formatter = JsCode("""
(params) => params.value != null ? '$' + Math.round(params.value).toLocaleString() : ''
""")


for col in monetary_columns:
    if col in filtered_df.columns:
        gb.configure_column(
            col,
            type=["numericColumn"],
            valueFormatter=currency_formatter,
            headerClass="centered-header"
        )


# Horizontally scrollable long-text columns
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

if "CaseName" in filtered_df.columns:
    gb.configure_column(
        "CaseName",
        cellStyle={
            "textAlign": "left",
            "whiteSpace": "nowrap",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
            "maxWidth": "300px"
        },
        autoHeight=False,
        wrapText=False
    )
# 👇 Manually list the renamed YN-style columns
tight_columns = [
    "PO", "IPO", "Laddering", "Transactional", "IT", "GAAP",
    "RestatedFinancials", "10B 5", "SEC 11", "SECAction"
]

for col in tight_columns:
    if col in filtered_df.columns:
        gb.configure_column(
            col,
            width=80,
            cellStyle={
                "textAlign": "center"
            }
        )


grid_options = gb.build()
grid_options["suppressSizeToFit"] = True  # Prevents all columns from stretching out

# === Display ===
st.markdown("""
    <div style='display: flex; justify-content: center; align-items: center;'>
        <h1 style='text-align: center; margin-bottom: 0;'>Law Firm Case Explorer</h1>
    </div>
""", unsafe_allow_html=True)


st.markdown("""
    <style>
    .ag-header-cell-label {
        justify-content: center !important;
    }
    .centered-header .ag-header-cell-label {
        justify-content: center !important;
    }
    </style>
""", unsafe_allow_html=True)

custom_css = {
    ".left-align-header .ag-header-cell-label": {
        "justify-content": "flex-start"
    }
}

AgGrid(
    filtered_df,
    gridOptions=grid_options,
    enable_enterprise_modules=False,
    use_checkbox=False,
    fit_columns_on_grid_load=False,
    allow_unsafe_jscode=True,
    height=800,
    custom_css=custom_css  # ← ADD THIS
)


st.markdown(f"### Total Cases Displayed: {len(filtered_df)}")

import matplotlib.pyplot as plt

# Load firm matchup sheet (Sheet2) once
@st.cache_data
def load_matchup_data():
    return pd.read_excel("firm_vs_firm_2sheet.xlsx", sheet_name="Sheet2", engine="openpyxl")

matchup_df = load_matchup_data()

# Only show pie chart and summary table if there's data
if not filtered_df.empty:
    st.subheader("📊 Outcome Distribution and Settlement Amount Summary")

    # Split layout into two columns
    col1, col2 = st.columns([1, 1])

    # === PIE CHART (left column) ===
    with col1:
        pie_df = filtered_df[filtered_df["CaseStatus"].str.strip().str.lower() != "active"]
        outcome_mapped = pie_df["CaseStatus"].apply(
            lambda x: x if x in ["Settled", "Dismissed"] else "Other"
        )
        outcome_counts = outcome_mapped.value_counts()

        if not outcome_counts.empty:
            fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
            ax.pie(
                outcome_counts.values,
                labels=outcome_counts.index,
                autopct="%1.1f%%",
                startangle=90,
                textprops={"fontsize": 8},
            )
            ax.axis("equal")
            st.pyplot(fig, use_container_width=False, clear_figure=True)
        else:
            st.info("Not enough outcome data to plot.")

    # === TOTAL AMOUNT SUMMARY TABLE (right column) ===
    # === TOTAL AMOUNT SUMMARY TABLE (right column) ===
   # === TOTAL AMOUNT SUMMARY TABLE (right column) ===
    with col2:
        total_amounts = filtered_df["TotalAmount"].fillna(0)
        total_cases = len(total_amounts)

    # Define shared thresholds
        thresholds = [
            1_000_000, 5_000_000, 10_000_000, 15_000_000,
            20_000_000, 25_000_000, 30_000_000,
            40_000_000, 50_000_000, 100_000_000
        ]

    # Compute average and median
        avg = total_amounts.mean() if total_cases > 0 else 0
        median = total_amounts.median() if total_cases > 0 else 0

        value_col = [f"${avg:,.0f}", f"${median:,.0f}"]
        range_labels = ["Average", "Median"]

    # Cumulative Under
        for t in thresholds:
            pct = (total_amounts <= t).sum() / total_cases * 100 if total_cases > 0 else 0
            range_labels.append(f"Under ${t // 1_000_000}M")
            value_col.append(f"{pct:.1f}%")

    # Cumulative Over
        for t in thresholds:
            pct = (total_amounts > t).sum() / total_cases * 100 if total_cases > 0 else 0
            range_labels.append(f"Over ${t // 1_000_000}M")
            value_col.append(f"{pct:.1f}%")

    # Build and display
        table_data = pd.DataFrame({
            "Range": range_labels,
            "Value": value_col
        })

        st.table(table_data)

import joblib
import numpy as np
import matplotlib.pyplot as plt

st.subheader("📈 Predict Case Outcome Based on Inputs")

model = load_model()

# Load merged data to access all model inputs
@st.cache_data
def load_model_input_data():
    xls_path = "THE BIG ANSWER SEPT.23.xlsx"
    legal = pd.read_excel(xls_path, sheet_name="LEGAL", engine="openpyxl")
    financial = pd.read_excel(xls_path, sheet_name="FINANCIAL", engine="openpyxl")
    legal["CaseID_clean"] = legal["CaseID"].astype(str).str.strip()
    financial["CaseID_clean"] = financial["CaseID"].astype(str).str.strip()
    return pd.merge(legal, financial, on="CaseID_clean", suffixes=("_legal", "_fin"))

df_for_inputs = load_model_input_data()
input_dict = {}
model_features = model.feature_names_in_

# Helper: choose smart filter UI
def add_filter(colname, df):
    options = sorted(df[colname].dropna().astype(str).unique())
    options = ["Select..."] + options

    if "YN" in colname:
        val = st.selectbox(colname, ["Select...", "Yes", "No"], index=0)
        input_dict[colname] = (
            1 if val == "Yes" else 0 if val == "No" else None
        )

    elif df[colname].dtype in ["float64", "int64"] and df[colname].nunique() > 20:
        # Let user skip by typing nothing — handled naturally
        val = st.text_input(f"{colname} (Leave blank to skip)", value="")
        input_dict[colname] = float(val) if val.strip() != "" else None

    else:
        val = st.selectbox(colname, options, index=0)
        input_dict[colname] = val if val != "Select..." else None

# Generate filters
for feature in model_features:
    if feature in df_for_inputs.columns:
        add_filter(feature, df_for_inputs)

# === Prediction ===
input_df = pd.DataFrame([input_dict])

# Encode categoricals
for col in input_df.select_dtypes(include="object").columns:
    input_df[col] = input_df[col].astype("category").cat.codes

input_df = input_df.reindex(columns=model_features, fill_value=0)

probs = model.predict_proba(input_df)[0]
labels = model.classes_

# Pie chart
fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
ax.pie(probs, labels=labels, autopct="%1.1f%%", startangle=90,
       textprops={'fontsize': 10},  # readable but clean
       colors=["skyblue", "orange", "lightgreen"])
ax.set_title("Predicted Case Outcome Probabilities", fontsize=12)
plt.tight_layout(pad=0.5)
st.pyplot(fig, clear_figure=True)


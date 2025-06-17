import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="Law Firm Case Explorer", layout="wide")

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
siccode_options = ["Select..."] + sorted(df["SICCode"].dropna().unique().astype(int).astype(str).tolist())
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
    "PO YN": "PO YN",
    "IPO YN": "IPO YN",
    "Laddering YN": "Laddering YN",
    "Transactional YN": "Transactional YN",
    "IT YN": "IT YN",
    "GAAP YN": "GAAP YN",
    "RestatedFinancialsYN": "Restated Financials YN",
    "10B 5 YN": "10B 5 YN",
    "SEC 11 YN": "SEC 11 YN",
    "SECActionYN": "SEC Action YN"
}

filter_values = {}
for col, label in filters.items():
    options = ["Select..."] + safe_unique(col)
    filter_values[col] = st.sidebar.selectbox(label, options, index=0)



use_case_filter = st.sidebar.checkbox("Enable Minimum Case Filter", value=False)
max_case_count = df.groupby(['Plaintiff Firms', 'Defendant Firms']).size().max()
min_case_count = st.sidebar.slider("Minimum Cases Between Firms", 1, int(max_case_count), 5)

# === Filtering Logic ===
filtered_df = df.copy()

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
gb = GridOptionsBuilder.from_dataframe(filtered_df)
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
            "textAlign": "left"
        }
    )


grid_options = gb.build()
grid_options["suppressSizeToFit"] = True  # Prevents all columns from stretching out

# === Display ===
st.title("Law Firm Case Explorer")
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
    with col2:
    # Always create a table — treat blanks as 0
        total_amounts = filtered_df["TotalAmount"].fillna(0)

    # Define bins and labels
        bins = [0, 1_000_000, 5_000_000, 10_000_000, 15_000_000, 20_000_000, 25_000_000,
                30_000_000, 40_000_000, 50_000_000, 100_000_000, float("inf")]
        labels = [
            "Under $1M", "Under $5M", "Under $10M", "Under $15M", "Under $20M",
            "Under $25M", "Under $30M", "Under $40M", "Under $50M",
            "Over $50M", "Over $100M"
        ]

    # Default values
        avg = total_amounts.mean() if not total_amounts.empty else 0
        median = total_amounts.median() if not total_amounts.empty else 0

        if not total_amounts.empty:
            binned = pd.cut(total_amounts, bins=bins, labels=labels, right=True)
            percentages = binned.value_counts(normalize=True).reindex(labels).fillna(0) * 100
            percent_vals = [f"{val:.1f}%" for val in percentages.tolist()]
        else:
            percent_vals = ["0.0%" for _ in labels]

    # Build table
        value_col = [f"${avg:,.0f}", f"${median:,.0f}"] + percent_vals
        table_data = pd.DataFrame({
            "Range": ["Average", "Median"] + labels,
            "Value": value_col
        })

        st.dataframe(
            table_data.reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            height=500
        )

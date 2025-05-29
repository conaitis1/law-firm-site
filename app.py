import streamlit as st
import pandas as pd

# === Custom CSS Styling ===
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    h1, h2, h3 { color: #1E88E5; }
    .stDataFrame { font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# === Load Dataset ===
@st.cache_data
def load_data():
    df = pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")

    # Drop fully empty columns
    df.dropna(axis=1, how='all', inplace=True)

    # Clean law firm list columns into readable strings
    if 'PlaintiffFirms' in df.columns:
        df['Plaintiff Firms'] = df['PlaintiffFirms'].apply(lambda x: '; '.join(eval(x)) if pd.notnull(x) else '')
        df.drop(columns=['PlaintiffFirms'], inplace=True)
    if 'DefendantFirms' in df.columns:
        df['Defendant Firms'] = df['DefendantFirms'].apply(lambda x: '; '.join(eval(x)) if pd.notnull(x) else '')
        df.drop(columns=['DefendantFirms'], inplace=True)

    # Optional: Rename key columns for clarity
    df.rename(columns=lambda col: col.replace("_", " ").title(), inplace=True)

    return df

df = load_data()

# === Title & Sidebar ===
st.title("📊 Law Firm Case Explorer")
st.markdown("Filter and explore legal cases based on law firms, outcomes, and financials.")

with st.sidebar:
    st.header("🔍 Filters")
    firm1 = st.text_input("First Law Firm")
    firm2 = st.text_input("Second Law Firm")
    status = st.selectbox("Case Status", ["All"] + sorted(df["Case Status"].dropna().unique()))
    casename = st.text_input("Case Name Search")

# === Filter Logic ===
filtered = df.copy()

def firm_match(row, f1, f2):
    return all(f in (row.get("Plaintiff Firms", "") + row.get("Defendant Firms", "")) for f in [f1, f2])

if firm1 and firm2:
    filtered = filtered[filtered.apply(lambda r: firm_match(r, firm1, firm2), axis=1)]
if status != "All":
    filtered = filtered[filtered["Case Status"] == status]
if casename:
    filtered = filtered[filtered["Case Name"].str.contains(casename, case=False, na=False)]

st.markdown(f"### Results: {len(filtered)} Matching Cases")
st.dataframe(filtered, use_container_width=True)

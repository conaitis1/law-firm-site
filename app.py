import streamlit as st
import pandas as pd

st.set_page_config(page_title="Law Firm Case Explorer - DEBUG MODE", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")

df = load_data()

# Fix datetime formatting but keep datetime (not just date)
for col in ['ClassStartDate', 'ClassEndDate', 'FederalFilingDate']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

st.sidebar.title("Debug Filters")
year_range = st.sidebar.slider("Class Start Year Range", 2000, 2025, (2010, 2025))

# Debug info
st.subheader("🧪 Debug Info")
st.write("Total Rows:", len(df))
st.write("Sample ClassStartDate values:", df["ClassStartDate"].dropna().dt.year.unique())

# Show raw data
st.subheader("📋 Raw Data Preview")
st.dataframe(df.head(50))
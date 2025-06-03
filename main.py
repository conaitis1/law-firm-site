import pandas as pd

# Load original Excel
df = pd.read_excel("copy LAW FIRM DATA-4.3.25 (1).xlsx", sheet_name="LAW FIRM DATA-4.3.25")

yn_columns = [
    "POYN", "IPOYN", "LadderingYN", "TransactionalYN",
    "ITYN", "GAAPYN", "RestatedFinancialsYN", "10B5YN",
    "SEC11YN", "SECActionYN"
]

rename_map = {
    "POYN": "PO YN", "IPOYN": "IPO YN", "LadderingYN": "Laddering YN",
    "TransactionalYN": "Transactional YN", "ITYN": "IT YN", "GAAPYN": "GAAP YN",
    "RestatedFinancialsYN": "RestatedFinancialsYN", "10B5YN": "10B 5 YN",
    "SEC11YN": "SEC 11 YN", "SECActionYN": "SECActionYN"
}

for col in yn_columns:
    if col in df.columns:
        df[rename_map[col]] = df[col].map({1: "Yes", 0: "No"})
        
# Flatten law firm names
def extract_firms_by_role(cell_value, role_keyword):
    if pd.isna(cell_value):
        return []
    return [entry.split('(')[0].strip() for entry in cell_value.split(';') if role_keyword in entry]

df["Plaintiff Firms"] = df["CaseLawFirm(Role)"].apply(lambda x: '; '.join(extract_firms_by_role(x, "Plaintiff law firm")))
df["Defendant Firms"] = df["CaseLawFirm(Role)"].apply(lambda x: '; '.join(extract_firms_by_role(x, "Defendant law firm")))

# Clean column names
# df.columns = df.columns.str.replace("_", " ").str.replace("(", "").str.replace(")", "").str.strip()

# Convert binary columns to Yes/No
for col in df.columns:
    if df[col].dropna().isin([0, 1]).all():
        df[col] = df[col].map({1: "Yes", 0: "No"})

# Fix date columns
date_cols = ['ClassStartDate', 'ClassEndDate', 'FederalFilingDate']
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')
    # Remove 1900s and far future placeholders
    df[col] = df[col].mask(df[col].dt.year == 1900)
    df[col] = df[col].mask(df[col].dt.year > 2025)

# Keep only rows with at least one date >= 2010
# Keep rows where ClassStartDate is in or after 2010
# df = df[df['ClassStartDate'].notna() & (df['ClassStartDate'].dt.year >= 2010)]


# Save output
df.to_excel("modified_law_firm_data.xlsx", index=False)

print(f"✅ Final cleaned file saved with correct date filtering: {len(df)} rows.")

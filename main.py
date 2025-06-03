import pandas as pd

# Load original Excel
df = pd.read_excel("copy LAW FIRM DATA-4.3.25 (1).xlsx", sheet_name="LAW FIRM DATA-4.3.25")

# Flatten law firm roles
def extract_firms_by_role(cell_value, role_keyword):
    if pd.isna(cell_value):
        return []
    return [entry.split('(')[0].strip() for entry in cell_value.split(';') if role_keyword in entry]

df["Plaintiff Firms"] = df["CaseLawFirm(Role)"].apply(lambda x: '; '.join(extract_firms_by_role(x, "Plaintiff law firm")))
df["Defendant Firms"] = df["CaseLawFirm(Role)"].apply(lambda x: '; '.join(extract_firms_by_role(x, "Defendant law firm")))

# Rename and convert YN columns to Yes/No
yn_columns = {
    "PO_YN": "PO YN", "IPO_YN": "IPO YN", "LadderingYN": "Laddering YN",
    "TransactionalYN": "Transactional YN", "IT_YN": "IT YN", "GAAP_YN": "GAAP YN",
    "RestatedFinancialsYN": "RestatedFinancialsYN", "10B_5_YN": "10B 5 YN",
    "SEC_11_YN": "SEC 11 YN", "SECActionYN": "SECActionYN"
}

for old, new in yn_columns.items():
    if old in df.columns:
        df[new] = df[old].map({1: "Yes", 0: "No"})

# Clean date columns and fix bad years
date_cols = ['ClassStartDate', 'ClassEndDate', 'FederalFilingDate']
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')
    df[col] = df[col].mask(df[col].dt.year == 1900)
    df[col] = df[col].mask(df[col].dt.year > 2025)

# Save cleaned dataset
df.to_excel("modified_law_firm_data.xlsx", index=False)
print(f"✅ Saved cleaned file with {len(df)} rows.")

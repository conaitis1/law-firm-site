import pandas as pd

# Load the raw data
df = pd.read_excel("copy LAW FIRM DATA-4.3.25 (1).xlsx", sheet_name='LAW FIRM DATA-4.3.25')

# Helper: extract law firms by role
def extract_firms_by_role(cell_value, role_keyword):
    if pd.isna(cell_value):
        return []
    return [entry.split('(')[0].strip() for entry in cell_value.split(';') if role_keyword in entry]

# Flattened columns for plaintiff and defendant firms
df['Plaintiff Firms'] = df['CaseLawFirm(Role)'].apply(lambda x: '; '.join(extract_firms_by_role(x, 'Plaintiff law firm')))
df['Defendant Firms'] = df['CaseLawFirm(Role)'].apply(lambda x: '; '.join(extract_firms_by_role(x, 'Defendant law firm')))

# Drop if old exists
if 'PlaintiffFirms' in df.columns:
    df.drop(columns=['PlaintiffFirms'], inplace=True)

# Clean column names
df.columns = df.columns.str.replace('_', ' ').str.replace('(', '').str.replace(')', '')
df.columns = df.columns.str.replace('  ', ' ').str.strip()

# Convert 0/1 to Yes/No for boolean-style cols
for col in df.columns:
    if df[col].dropna().isin([0, 1]).all():
        df[col] = df[col].map({1: "Yes", 0: "No"})

# Standardize date columns
date_cols = ['ClassStartDate', 'ClassEndDate', 'FederalFilingDate']
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# Remove rows where all dates are either null or pre-2010
df = df[
    df[date_cols]
    .apply(lambda row: any((pd.notna(d) and d.year >= 2010) for d in row), axis=1)
]

# Drop columns with all missing values
df.dropna(axis=1, how='all', inplace=True)

# Save cleaned result
df.to_excel("modified_law_firm_data.xlsx", index=False)

print(f"✅ Cleaned file saved: {len(df)} rows, {len(df.columns)} columns.")

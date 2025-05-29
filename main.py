import pandas as pd

# Load the raw data
df = pd.read_excel("copy LAW FIRM DATA-4.3.25 (1).xlsx", sheet_name='LAW FIRM DATA-4.3.25')

# Helper function: extract law firms by role
def extract_firms_by_role(cell_value, role_keyword):
    if pd.isna(cell_value):
        return []
    return [entry.split('(')[0].strip() for entry in cell_value.split(';') if role_keyword in entry]

# Create new flattened string columns for plaintiff and defendant firms
df['Plaintiff Firms'] = df['CaseLawFirm(Role)'].apply(
    lambda x: '; '.join(extract_firms_by_role(x, 'Plaintiff law firm'))
)

df['Defendant Firms'] = df['CaseLawFirm(Role)'].apply(
    lambda x: '; '.join(extract_firms_by_role(x, 'Defendant law firm'))
)

# Drop the original list-format PlaintiffFirms column if it exists
if 'PlaintiffFirms' in df.columns:
    df.drop(columns=['PlaintiffFirms'], inplace=True)

# Clean column names (prettier)
df.columns = df.columns.str.replace('_', ' ').str.replace('(', '').str.replace(')', '')
df.columns = df.columns.str.replace('  ', ' ').str.strip()

# Convert 1/0 to Yes/No where applicable
for col in df.columns:
    if df[col].dropna().isin([0, 1]).all():
        df[col] = df[col].map({1: "Yes", 0: "No"})

# Convert date columns and filter out pre-2010 rows
for col in ['ClassStartDate', 'ClassEndDate']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

df = df[
    (df['ClassStartDate'].dt.year >= 2010) |
    (df['ClassEndDate'].dt.year >= 2010)
]

# Drop all-null columns
df.dropna(axis=1, how='all', inplace=True)

# Save cleaned dataset
df.to_excel("modified_law_firm_data.xlsx", index=False)

print(f"✅ Final file saved. Rows: {len(df)} | Columns: {len(df.columns)}")

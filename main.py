import pandas as pd

# Load original and modified data
original_df = pd.read_excel("copy LAW FIRM DATA-4.3.25 (1).xlsx", sheet_name='LAW FIRM DATA-4.3.25')
df = original_df.copy()  # Work from original to avoid any corruption

# Extract law firms by role
def extract_firms_by_role(cell_value, role_keyword):
    if pd.isna(cell_value):
        return []
    return [entry.split('(')[0].strip() for entry in cell_value.split(';') if role_keyword in entry]

# Add flattened law firm columns
df['Plaintiff Firms'] = df['CaseLawFirm(Role)'].apply(lambda x: '; '.join(extract_firms_by_role(x, 'Plaintiff law firm')))
df['Defendant Firms'] = df['CaseLawFirm(Role)'].apply(lambda x: '; '.join(extract_firms_by_role(x, 'Defendant law firm')))

# Drop legacy column if present
if 'PlaintiffFirms' in df.columns:
    df.drop(columns=['PlaintiffFirms'], inplace=True)

# Clean up column names
df.columns = df.columns.str.replace('_', ' ').str.replace('(', '').str.replace(')', '')
df.columns = df.columns.str.replace('  ', ' ').str.strip()

# Convert 0/1 columns to Yes/No
for col in df.columns:
    if df[col].dropna().isin([0, 1]).all():
        df[col] = df[col].map({1: "Yes", 0: "No"})

# Just preserve original date values — no formatting, no coercion
# (We already loaded from original file, so nothing else to change)

# Save to Excel WITHOUT formatting
df.to_excel("modified_law_firm_data.xlsx", index=False)

print(f"✅ Final cleaned file saved with all rows and correct dates: {len(df)} rows, {len(df.columns)} columns.")

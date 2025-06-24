import matplotlib.pyplot as plt
plt.ion()  # Enable interactive plotting in VS Code

import pandas as pd

# Load the Excel data
df = pd.read_excel("modified_law_firm_data.xlsx")

# Encode CaseStatus: Dismissed=0, Settled=1, Other=2
df['CaseStatus'] = df['CaseStatus'].map({'Dismissed': 0, 'Settled': 1}).fillna(2).astype(int)

# Convert Y/N columns to 1/0
yn_columns = ['PO', 'IPO', 'Laddering', 'Transactional', 'IT', 'GAAP', '10B 5', 'SEC 11', 'SECAction', 'RestatedFinancialsYN']
for col in yn_columns:
    if col in df.columns:
        df[col] = df[col].map({'Yes': 1, 'No': 0}).fillna(0)

# Convert money columns to numeric
money_cols = ['CashAmount', 'TotalAmount', 'NonCashAmount']
for col in money_cols:
    df[col] = pd.to_numeric(df[col].replace('[\$,]', '', regex=True), errors='coerce').fillna(0)

# Convert dates to datetime and create duration feature
df['FederalFilingDate'] = pd.to_datetime(df['FederalFilingDate'], errors='coerce')
df['FinalSettlementDate'] = pd.to_datetime(df['FinalSettlementDate'], errors='coerce')
df['CaseDurationDays'] = (df['FinalSettlementDate'] - df['FederalFilingDate']).dt.days.fillna(-1)

# Encode categorical text columns
from sklearn.preprocessing import LabelEncoder
cat_cols = ['FederalCourt', 'FederalJudge', 'Plaintiff Firms', 'Defendant Firms', 'SICCode']
for col in cat_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).fillna('Unknown')
        df[col] = LabelEncoder().fit_transform(df[col])

# Drop problematic, unstructured, or leakage-prone columns
df = df.drop(columns=[
    'CaseID', 'CaseName', 'Updated_On_Date', 'SettlementID',
    'FederalFilingDate', 'FinalSettlementDate',
    'ClassStartDate', 'ClassEndDate', 'DismissalDate',
    'NamedDefendants', 'IndividualLeadPlaintiff', 'CaseLawFirm(Role)', 'ClassDefinition'
], errors='ignore')

# Drop rows with missing values in key fields
df = df.dropna(subset=['CaseStatus', 'Plaintiff Firms', 'Defendant Firms', 'FederalCourt', 'FederalJudge'])

# Define features and target
X = df.drop(columns='CaseStatus')
y = df['CaseStatus']

# Debug: check for non-numeric columns
non_numeric_cols = X.select_dtypes(exclude=['number']).columns.tolist()
if non_numeric_cols:
    print("⚠️ Non-numeric columns in X:", non_numeric_cols)

# Train/test split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

# Train model
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict and evaluate
from sklearn.metrics import classification_report
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Feature importance plot
importances = model.feature_importances_
feat_importances = pd.Series(importances, index=X.columns).sort_values(ascending=False)

# Save feature importance chart
plt.figure(figsize=(10, 6))
feat_importances.head(15).plot(kind='bar', title="Top Predictive Features for CaseStatus")
plt.ylabel("Importance")
plt.tight_layout()
plt.savefig("feature_importances.png", dpi=300, bbox_inches='tight')
print("✅ Saved feature_importances.png to your current folder.")
import joblib

# Save the trained model to a file
joblib.dump(model, "rf_model.joblib")
print("✅ Saved model as rf_model.joblib")

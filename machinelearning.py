import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# === Load and merge data ===
xls_path = "THE BIG ANSWER SEPT.23.xlsx"  # <-- converted .xlsx version
legal_df = pd.read_excel(xls_path, sheet_name="LEGAL", engine="openpyxl")
financial_df = pd.read_excel(xls_path, sheet_name="FINANCIAL", engine="openpyxl")

legal_df["CaseID_clean"] = legal_df["CaseID"].astype(str).str.strip()
financial_df["CaseID_clean"] = financial_df["CaseID"].astype(str).str.strip()
df = pd.merge(legal_df, financial_df, on="CaseID_clean", suffixes=("_legal", "_fin"))

# === Clean target labels ===
df = df[~df["CaseStatus_legal"].isin(["Active"])]
df["TargetStatus"] = df["CaseStatus_legal"].apply(lambda x: x if x in ["Settled", "Dismissed"] else "Other")
print("✅ Class breakdown:\n", df["TargetStatus"].value_counts())

# === Define usable features (NO leakage) ===
features = [
    "FederalJudge_legal",
    "FederalCourt_legal",
    "SICCode_legal",
    "CashAmount",
    "TotalAmount",
    "Current Ratio",
    # Add any Violation/Tag columns here
    "ViolationType_legal",
    "Tag_Insider",
    "Tag_FinancialFraud",
    "Tag_Accounting",
    "Tag_Bribes",
    "Tag_Whistleblower"
]


features = [f for f in features if f in df.columns]

X = df[features].copy()
y = df["TargetStatus"]

# Map Y/N to binary
for col in X.columns:
    if "YN" in col:
        X[col] = X[col].map({"Yes": 1, "No": 0, 1: 1, 0: 0})

# Encode object fields
for col in X.select_dtypes(include="object").columns:
    X[col] = X[col].astype("category").cat.codes

X = X.fillna(0)

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=42)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, "rf_model.joblib")
print("✅ Model saved with features:", model.feature_names_in_)

# Plot importances
importances = model.feature_importances_
feat_df = pd.DataFrame({"Feature": X.columns, "Importance": importances}).sort_values("Importance", ascending=False)

plt.figure(figsize=(12, 6))
plt.bar(feat_df["Feature"], feat_df["Importance"])
plt.xticks(rotation=75)
plt.title("Feature Importances (No Duration Leakage)")
plt.tight_layout()
plt.savefig("feature_importances.png")
plt.show()
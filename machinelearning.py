import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# === Load and merge sheets ===
xls_path = "THE BIG ANSWER SEPT.23.xlsb"
legal_df = pd.read_excel(xls_path, sheet_name="LEGAL", engine="pyxlsb")
financial_df = pd.read_excel(xls_path, sheet_name="FINANCIAL", engine="pyxlsb")

# Clean and merge on CaseID
legal_df["CaseID_clean"] = legal_df["CaseID"].astype(str).str.strip()
financial_df["CaseID_clean"] = financial_df["CaseID"].astype(str).str.strip()
df = pd.merge(legal_df, financial_df, on="CaseID_clean", suffixes=("_legal", "_fin"))

# Keep valid case statuses only
df = df[df["CaseStatus_legal"].isin(["Settled", "Dismissed", "Other"])].copy()

# === Feature columns ===
features = [
    "Days Until Settlement",       # proxy for CaseDurationDays
    "CashAmount",                  # monetary strength
    "TotalAmount",                 # total settlement
    "Current Ratio",               # company financial metric
    "FederalJudge_legal",         # contextual legal
    "FederalCourt_legal",
    "SICCode_legal"
]

X = df[features].copy()
y = df["CaseStatus_legal"]

# Encode any categorical/object columns
for col in X.select_dtypes(include="object").columns:
    X[col] = X[col].astype("category").cat.codes

# Handle missing values
X = X.fillna(0)

# === Train model ===
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "rf_model.joblib")
print("✅ Model trained and saved as rf_model.joblib")

# === Plot feature importances ===
importances = model.feature_importances_
feature_names = X.columns
feat_imp_df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
feat_imp_df = feat_imp_df.sort_values("Importance", ascending=False)

plt.figure(figsize=(10, 6))
plt.bar(feat_imp_df["Feature"], feat_imp_df["Importance"])
plt.title("Top Predictive Features for CaseStatus")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("feature_importances.png")
plt.show()

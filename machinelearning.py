import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# === Load and merge ===
xls_path = "THE BIG ANSWER SEPT.23.xlsb"
legal_df = pd.read_excel(xls_path, sheet_name="LEGAL", engine="pyxlsb")
financial_df = pd.read_excel(xls_path, sheet_name="FINANCIAL", engine="pyxlsb")
legal_df["CaseID_clean"] = legal_df["CaseID"].astype(str).str.strip()
financial_df["CaseID_clean"] = financial_df["CaseID"].astype(str).str.strip()
df = pd.merge(legal_df, financial_df, on="CaseID_clean", suffixes=("_legal", "_fin"))

# === Clean up CaseStatus ===
df = df[~df["CaseStatus_legal"].isin(["Active"])]  # ❌ Remove active
df["TargetStatus"] = df["CaseStatus_legal"].apply(lambda x: x if x in ["Dismissed", "Settled"] else "Other")
print("✅ Class breakdown:\n", df["TargetStatus"].value_counts())

# === Define features ===
features = [
    "Days Until Settlement", "CashAmount", "TotalAmount", "Current Ratio",
    "FederalJudge_legal", "FederalCourt_legal", "SICCode_legal",
    "GAAP_YN", "IPO_YN", "TransactionalYN", "PO_YN", "10B_5_YN",
    "SEC_11_YN", "SECActionYN", "RestatedFinancialsYN", "IT_YN", "LadderingYN"
]

features = [f for f in features if f in df.columns]  # drop any missing

X = df[features].copy()
y = df["TargetStatus"]

# Map Yes/No flags
for col in X.columns:
    if "YN" in col:
        X[col] = X[col].map({"Yes": 1, "No": 0, 1: 1, 0: 0})

# Label encode object fields
for col in X.select_dtypes(include="object").columns:
    X[col] = X[col].astype("category").cat.codes

X = X.fillna(0)

# === Train and save model ===
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=42)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, "rf_model.joblib")
print("✅ Model trained with 3-class target and saved.")

# === Plot feature importances ===
importances = model.feature_importances_
feat_df = pd.DataFrame({"Feature": X.columns, "Importance": importances})
feat_df = feat_df.sort_values("Importance", ascending=False)

plt.figure(figsize=(12, 6))
plt.bar(feat_df["Feature"], feat_df["Importance"])
plt.title("Feature Importances - 3-Class Model")
plt.xticks(rotation=75)
plt.tight_layout()
plt.savefig("feature_importances.png")
plt.show()

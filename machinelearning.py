import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# === Load and merge data ===
xls_path = "THE BIG ANSWER SEPT.23.xlsx"
legal_df = pd.read_excel(xls_path, sheet_name="LEGAL", engine="openpyxl")
financial_df = pd.read_excel(xls_path, sheet_name="FINANCIAL", engine="openpyxl")

legal_df["CaseID_clean"] = legal_df["CaseID"].astype(str).str.strip()
financial_df["CaseID_clean"] = financial_df["CaseID"].astype(str).str.strip()
df = pd.merge(legal_df, financial_df, on="CaseID_clean", suffixes=("_legal", "_fin"))

# === Clean target labels ===
df = df[~df["CaseStatus_legal"].isin(["Active"])]
df["TargetStatus"] = df["CaseStatus_legal"].apply(lambda x: x if x in ["Settled", "Dismissed"] else "Other")
print("✅ Class breakdown:\n", df["TargetStatus"].value_counts())

# === Features ===
features = [
    "FederalJudge_legal",
    "FederalCourt_legal",
    "PlaintiffFirm_legal",
    "DefendantFirm_legal",
    "SICCode_legal",
    "ViolationType_legal",
    "Tag_Insider",
    "Tag_FinancialFraud",
    "Tag_Accounting",
    "Tag_Bribes",
    "Tag_Whistleblower",
    "Current Ratio",
    "Market Cap High_fin",
    "Market Cap Low_fin",
    "Market Cap Drop",
    "Filing Date Market Cap",
    "Insider Ownership",
    "Institutional Ownership",
    "Prior Year Revenue (TTM)",
    "WHY SUED CATEGORY",     # single-label
    "Short %",               # single numeric
]

features = [f for f in features if f in df.columns]
X = df[features].copy()
y = df["TargetStatus"]

# === Reduce cardinality + encode
high_card_cols = ["FederalJudge_legal", "FederalCourt_legal", "PlaintiffFirm_legal", "DefendantFirm_legal", "SICCode_legal"]
for col in high_card_cols:
    if col in X.columns:
        top_vals = X[col].value_counts().head(20).index
        X[col] = X[col].where(X[col].isin(top_vals), "Other")
        X[col] = LabelEncoder().fit_transform(X[col].astype(str))

# === Encode "WHY SUED CATEGORY" as single-label (not one-hot)
if "WHY SUED CATEGORY" in X.columns:
    X["WHY SUED CATEGORY"] = LabelEncoder().fit_transform(X["WHY SUED CATEGORY"].astype(str))

# === Force numeric
for col in ["Prior Year Revenue (TTM)", "Current Ratio", "Short %", "Market Cap Drop"]:
    if col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")

# === One-hot encode low-card categorical features (EXCLUDING label-encoded ones)
label_encoded = set(high_card_cols + ["WHY SUED CATEGORY"])
onehot_cols = [col for col in X.select_dtypes(include="object").columns if col not in label_encoded]
X = pd.get_dummies(X, columns=onehot_cols, drop_first=True)

# === Final cleanup
X = X.fillna(0)

# === Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=42)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)
joblib.dump(model, "rf_model.joblib")
print("✅ Model saved with features:", model.feature_names_in_)

# === Plot importances
importances = model.feature_importances_
feat_df = pd.DataFrame({"Feature": X.columns, "Importance": importances}).sort_values("Importance", ascending=False)
top_feats = feat_df.head(25)

plt.figure(figsize=(12, 6))
plt.bar(top_feats["Feature"], top_feats["Importance"])
plt.xticks(rotation=45, ha="right")
plt.title("Top 25 Feature Importances")
plt.tight_layout()
plt.savefig("feature_importances.png")
plt.show()

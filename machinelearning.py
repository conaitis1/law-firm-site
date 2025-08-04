import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
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
    "Current Ratio",
    "ViolationType_legal",
    "Tag_Insider",
    "Tag_FinancialFraud",
    "Tag_Accounting",
    "Tag_Bribes",
    "Tag_Whistleblower",
    "Market Cap High_fin",
    "Market Cap Low_fin",
    "Filing Date Market Cap",
    "Free Float Amount",
    "Insider Ownership",
    "Institutional Ownership",
    "Prior Year Revenue (TTM)"
]

features = [f for f in features if f in df.columns]
X = df[features].copy()
y = df["TargetStatus"]

from sklearn.preprocessing import LabelEncoder

# === Step 1: Reduce cardinality
def reduce_cardinality(df, col, top_n=20):
    top_vals = df[col].value_counts().head(top_n).index
    df[col] = df[col].where(df[col].isin(top_vals), "Other")
    return df

high_card_cols = [
    "FederalJudge_legal",
    "FederalCourt_legal",
    "PlaintiffFirm_legal",
    "DefendantFirm_legal",
    "SICCode_legal"
]

for col in high_card_cols:
    if col in X.columns:
        X = reduce_cardinality(X, col, top_n=20)
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))

# === Step 2: Encode remaining categoricals using one-hot
low_card_cols = X.select_dtypes(include=["object", "category"]).columns
X = pd.get_dummies(X, columns=low_card_cols, drop_first=True)

# === Step 3: Fill missing + sort columns
X = X.fillna(0)


# === Train model ===
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=42)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)
joblib.dump(model, "rf_model.joblib")
print("✅ Model saved with features:", model.feature_names_in_)

# === Plot importances (top 25 only)
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

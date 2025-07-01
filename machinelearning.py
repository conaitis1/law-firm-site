import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# === Load dataset ===
df = pd.read_excel("answerdata.xlsx", engine="openpyxl")

# Filter valid target rows
df = df[df["CaseStatus"].isin(["Settled", "Dismissed", "Other"])].copy()

# Calculate case duration
df["ClassStartDate"] = pd.to_datetime(df["ClassStartDate"], errors="coerce")
df["ClassEndDate"] = pd.to_datetime(df["ClassEndDate"], errors="coerce")
df["CaseDurationDays"] = (df["ClassEndDate"] - df["ClassStartDate"]).dt.days

# === Feature selection ===
candidate_features = [
    "TotalAmount", "CashAmount", "CaseDurationDays", "FederalJudge", "FederalCourt",
    "SICCode", "Plaintiff Firms", "Defendant Firms",
    "GAAP", "IT", "IPO", "10B 5", "SEC 11", "Transactional", "RestatedFinancials"
]

X = df[candidate_features].copy()
y = df["CaseStatus"]

# Convert Yes/No to binary
for col in X.columns:
    if X[col].isin(["Yes", "No"]).all():
        X[col] = X[col].map({"Yes": 1, "No": 0})

# Label encode categorical features
for col in X.select_dtypes(include="object").columns:
    X[col] = X[col].astype("category").cat.codes

# Fill missing values
X = X.fillna(0)

# === Train model ===
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "rf_model.joblib")
print("✅ Model trained and saved.")

# === Plot feature importances ===
importances = model.feature_importances_
feature_names = X.columns
feat_imp_df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
feat_imp_df = feat_imp_df.sort_values("Importance", ascending=False)

# Plot
plt.figure(figsize=(10, 6))
plt.bar(feat_imp_df["Feature"], feat_imp_df["Importance"])
plt.xticks(rotation=75)
plt.title("Top Predictive Features for CaseStatus")
plt.ylabel("Importance")
plt.tight_layout()
plt.savefig("feature_importances.png")
plt.show()

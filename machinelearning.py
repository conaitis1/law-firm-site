import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load dataset
df = pd.read_excel("modified_law_firm_data.xlsx", engine="openpyxl")

# Drop rows with missing target
df = df[df["CaseStatus"].isin(["Settled", "Dismissed", "Other"])]

# Create CaseDurationDays if not already present
if "CaseDurationDays" not in df.columns:
    df["ClassStartDate"] = pd.to_datetime(df["ClassStartDate"], errors="coerce")
    df["ClassEndDate"] = pd.to_datetime(df["ClassEndDate"], errors="coerce")
    df["CaseDurationDays"] = (df["ClassEndDate"] - df["ClassStartDate"]).dt.days

# Select features
features = ["FederalJudge", "FederalCourt", "CaseDurationDays", "SICCode"] + [
    col for col in df.columns if col in [
        "PO", "IPO", "Laddering", "Transactional", "IT", "GAAP",
        "RestatedFinancials", "10B 5", "SEC 11", "SECAction"
    ]
]

X = df[features].copy()
y = df["CaseStatus"]

# Convert Yes/No to binary
for col in X.columns:
    if X[col].isin(["Yes", "No"]).all():
        X[col] = X[col].map({"Yes": 1, "No": 0})

# Label encode categorical features
for col in X.select_dtypes(include="object").columns:
    X[col] = X[col].astype("category").cat.codes

# Handle missing values
X = X.fillna(0)

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "rf_model.joblib")
print("✅ Model trained and saved.")

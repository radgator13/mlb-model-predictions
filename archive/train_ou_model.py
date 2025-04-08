import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Load comparison.csv
df = pd.read_csv("comparison.csv")

# Filter for valid labels
df = df[(df["OverHit"] | df["UnderHit"])].copy()

# Create binary target: 1 if over hit, 0 if under hit
df["Target"] = df["OverHit"].astype(int)

features = [
    "OpeningOverUnder",
    "OpeningPointSpread",
    "OpeningHomeMoneyLine",
    "OpeningAwayMoneyLine"
]

X = df[features]
y = df["Target"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression()
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Over/Under model accuracy: {acc:.1%}")

# Save
joblib.dump(model, "ou_model.pkl")
print("✅ Saved as ou_model.pkl")

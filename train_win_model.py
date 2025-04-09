import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Load training data
df = pd.read_csv("comparison.csv")

# Binary target: 1 = Home win, 0 = Away win
df = df[df["Winner"].isin(["Home", "Away"])].copy()
df["Target"] = df["Winner"].map({"Home": 1, "Away": 0})

# Features
features = [
    "OpeningHomeMoneyLine",
    "OpeningAwayMoneyLine",
    "OpeningPointSpread",
    "OpeningOverUnder"
]

X = df[features]
y = df["Target"]

# Split + train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LogisticRegression()
model.fit(X_train, y_train)

# Accuracy
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Win Prediction Accuracy: {acc:.1%}")

# Save model
joblib.dump(model, "win_model.pkl")
print("✅ Model saved to win_model.pkl")

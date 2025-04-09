import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load the data
df = pd.read_csv("comparison.csv")

# Target: who won
df["Target"] = df["Winner"].map({"Home": 1, "Away": 0})

# Select features
features = [
    "OpeningHomeMoneyLine",
    "OpeningAwayMoneyLine",
    "OpeningPointSpread",
    "OpeningOverUnder"
]

X = df[features]
y = df["Target"]

# Split for testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train logistic regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Win Prediction Accuracy: {acc:.1%}")

# Save model
import joblib
joblib.dump(model, "win_model.pkl")

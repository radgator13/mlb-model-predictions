import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# === Load your historical training data ===
# This should match your modeling structure
df = pd.read_csv("comparison.csv")

# === Build margin column (target) ===
# Positive = home team won by that many runs
df["margin"] = df["HomeScore"] - df["AwayScore"]

# === Features: replicate what's used in your current classifier ===
features = pd.DataFrame()
features["OpeningPointSpread"] = df["OpeningPointSpread"]
features["OpeningOverUnder"] = df["OpeningOverUnder"]
features["OpeningHomeMoneyLine"] = df["OpeningHomeMoneyLine"]
features["OpeningAwayMoneyLine"] = df["OpeningAwayMoneyLine"]

# === Clean rows with missing values ===
features = features.dropna()
df = df.loc[features.index]  # sync target

# === Target
target = df["margin"]

# === Split for validation (optional)
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# === Train model
model = LinearRegression()
model.fit(X_train, y_train)

# === Evaluate (optional)
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = mse ** 0.5
print(f"✅ Spread Margin Model Trained — RMSE: {rmse:.3f}")


# === Save model
joblib.dump(model, "win_model.pkl")
print("📁 Saved regression model to: win_model.pkl")

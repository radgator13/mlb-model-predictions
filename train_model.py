import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import cross_val_score

# === Load base game data ===
df = pd.read_csv("archive/comparison.csv")

# === Normalize team names ===
df["HomeTeam"] = df["HomeTeam"].str.upper().str.strip()
df["AwayTeam"] = df["AwayTeam"].str.upper().str.strip()

# === Load ESPN team stats ===
offense = pd.read_csv("espn_team_offense.csv")
defense = pd.read_csv("espn_team_defense.csv")
fielding = pd.read_csv("espn_team_fielding.csv")

for stats, label in [(offense, "O"), (defense, "D"), (fielding, "F")]:
    stats["TEAM"] = stats["TEAM"].str.upper().str.strip()
    df = df.merge(stats.add_prefix("HOME_" + label + "_"), left_on="HomeTeam", right_on="HOME_" + label + "_TEAM", how="left")
    df = df.merge(stats.add_prefix("AWAY_" + label + "_"), left_on="AwayTeam", right_on="AWAY_" + label + "_TEAM", how="left")

# === Create model targets ===

# For O/U model (classification)
df["total_runs"] = df["HomeScore"] + df["AwayScore"]
df["over_under_result"] = (df["total_runs"] > df["OpeningOverUnder"]).astype(int)  # 1 = Over, 0 = Under

# For spread model (regression)
df["spread_margin"] = df["HomeScore"] - df["AwayScore"]

# === Select features ===
feature_cols = [
    "OpeningOverUnder", "OpeningPointSpread",
    "HOME_O_AVG", "AWAY_O_AVG",
    "HOME_O_OBP", "AWAY_O_OBP",
    "HOME_O_OPS", "AWAY_O_OPS",
    "HOME_D_ERA", "AWAY_D_ERA",
    "HOME_D_WHIP", "AWAY_D_WHIP",
    "HOME_F_FP", "AWAY_F_FP"
]

# === Drop rows with missing feature data ===
df = df.dropna(subset=feature_cols + ["over_under_result", "spread_margin"])
X = df[feature_cols]

# Targets
y_ou = df["over_under_result"]
y_spread = df["spread_margin"]

# === Train Over/Under classifier ===
ou_model = LogisticRegression(max_iter=1000)
ou_model.fit(X, y_ou)
joblib.dump(ou_model, "ou_model.pkl")

# === Train Spread regression model ===
spread_model = LinearRegression()
spread_model.fit(X, y_spread)
joblib.dump(spread_model, "win_model.pkl")

# === Validation output (optional) ===
ou_acc = cross_val_score(ou_model, X, y_ou, cv=5).mean()
spread_rmse = ((spread_model.predict(X) - y_spread) ** 2).mean() ** 0.5

print("✅ Model training complete.")
print(f"🔵 Over/Under Model Accuracy (CV): {ou_acc:.3f}")
print(f"🟢 Spread Model RMSE: {spread_rmse:.3f}")

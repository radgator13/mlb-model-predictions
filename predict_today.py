import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime

def load_latest_clean_lines():
    files = sorted(Path().glob("mlb_clean_games_*.csv"), reverse=True)
    if not files:
        raise FileNotFoundError("No mlb_clean_games_*.csv found.")
    print(f"📂 Using: {files[0].name}")
    return pd.read_csv(files[0])

def build_features(df, model):
    features = pd.DataFrame()
    features["OpeningPointSpread"] = df["spread_line"]
    features["OpeningOverUnder"] = df["total_line"]
    features["OpeningHomeMoneyLine"] = -130
    features["OpeningAwayMoneyLine"] = 110
    return features[model.feature_names_in_]

# 🔥 Fireball scale for spread edge
def fireball_from_edge(edge):
    if edge >= 2.75: return "🔥🔥🔥🔥🔥"
    elif edge >= 2.65: return "🔥🔥🔥🔥"
    elif edge >= 2.55: return "🔥🔥🔥"
    elif edge >= 2.45: return "🔥🔥"
    elif edge >= 2.35: return "🔥"
    else: return "No Edge"

# 🔥 Fireball scale for probability
def fireball_from_prob(prob):
    if prob >= 0.70: return "🔥🔥🔥🔥🔥"
    elif prob >= 0.65: return "🔥🔥🔥🔥"
    elif prob >= 0.60: return "🔥🔥🔥"
    elif prob >= 0.55: return "🔥🔥"
    elif prob >= 0.50: return "🔥"
    else: return "No Edge"

def run_predictions():
    df = load_latest_clean_lines()

    # ✅ Load models first
    win_model = joblib.load("win_model.pkl")
    ou_model = joblib.load("ou_model.pkl")

    # ✅ Build features
    features_win = build_features(df, win_model)
    features_ou = build_features(df, ou_model)

    # === SPREAD predictions (regression)
    spread_pred = win_model.predict(features_win)
    spread_edge = abs(spread_pred - df["spread_line"])

    df["model_spread_pick"] = [
        f"{df.loc[i, 'team1']} {margin:+.1f} (vs {vegas:+.1f})" if margin < vegas
        else f"{df.loc[i, 'team2']} {margin:+.1f} (vs {vegas:+.1f})"
        for i, (margin, vegas) in enumerate(zip(spread_pred, df["spread_line"]))
    ]
    df["model_spread_conf"] = [fireball_from_edge(e) for e in spread_edge]
    df["spread_edge"] = spread_edge  # Optional for filtering/sorting

    # === TOTAL predictions (classification)
    total_class = ou_model.predict(features_ou)
    total_conf = ou_model.predict_proba(features_ou).max(axis=1)

    df["model_total_pick"] = [
        f"Over (vs {line:.1f})" if c == 1 else f"Under (vs {line:.1f})"
        for c, line in zip(total_class, df["total_line"])
    ]
    df["model_total_conf"] = [fireball_from_prob(p) for p in total_conf]

    # === Final formatting
    df["home_team"] = df["team1"]
    df["away_team"] = df["team2"]

    df_out = df[[
        "timestamp", "home_team", "away_team",
        "spread_line", "model_spread_pick", "model_spread_conf",
        "spread_edge",  # Optional for review
        "total_line", "model_total_pick", "model_total_conf"
    ]]

    # === Export
    today = datetime.now().strftime("%Y%m%d")
    out_file = f"mlb_predictions_{today}.csv"
    df_out.to_csv(out_file, index=False)

    print(f"\n✅ Predictions saved to: {out_file}")
    print("📊 Includes picks, edges, fireball confidence, and clean labeling.")

if __name__ == "__main__":
    run_predictions()

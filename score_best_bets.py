import pandas as pd
from pathlib import Path

log_file = Path("best_bets_log.csv")
scores_file = Path("espn_scores.csv")

if not log_file.exists() or not scores_file.exists():
    print("❌ Required files not found.")
    exit()

log_df = pd.read_csv(log_file)
scores_df = pd.read_csv(scores_file)

# === Normalize column formats ===
log_df["date"] = pd.to_datetime(log_df["date"]).dt.date
scores_df["GameDate"] = pd.to_datetime(scores_df["Date"]).dt.date

scores_df["HomeTeam"] = scores_df["Home Team"].str.upper().str.strip()
scores_df["AwayTeam"] = scores_df["Away Team"].str.upper().str.strip()

def determine_result(row):
    log_date = row["date"]
    home = row["home_team"].upper().strip()
    away = row["away_team"].upper().strip()
    line = row["line"]
    pick = row["model_pick"]
    ptype = row["type"]

    # Find matching game
    game = scores_df[
        (scores_df["GameDate"] == log_date) &
        (scores_df["HomeTeam"] == home) &
        (scores_df["AwayTeam"] == away)
    ]

    if game.empty or pd.isna(line):
        return pd.Series(["Pending", ""])

    hs = game.iloc[0]["Home Score"]
    as_ = game.iloc[0]["Away Score"]

    try:
        line = float(line)
    except:
        return pd.Series(["Pending", ""])

    if ptype == "spread":
        margin = hs - as_
        is_home_pick = home in pick
        covered = margin > line if is_home_pick else -margin > line
        return pd.Series(["Win" if covered else "Loss", 1 if covered else 0])

    elif ptype == "total":
        total_score = hs + as_
        if "Over" in pick:
            win = total_score > line
        elif "Under" in pick:
            win = total_score < line
        else:
            return pd.Series(["Unknown", ""])
        return pd.Series(["Win" if win else "Loss", 1 if win else 0])

    return pd.Series(["Unknown", ""])

# === Apply scoring logic
log_df[["result", "correct"]] = log_df.apply(determine_result, axis=1)

# === Save updated log
log_df.to_csv("best_bets_log.csv", index=False)
print("✅ Updated best_bets_log.csv with results.")

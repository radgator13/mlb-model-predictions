import pandas as pd

# === LOAD CLEANED SPORTS DATA ===
odds_df = pd.read_csv("mlb_opening_lines_clean.csv")
scores_df = pd.read_csv("espn_scores.csv")

# Normalize team and date
def normalize_team(name):
    return name.strip().upper() if pd.notnull(name) else name

odds_df["GameDate"] = pd.to_datetime(odds_df["GameDate"]).dt.date
odds_df["HomeTeam"] = odds_df["HomeTeam"].apply(normalize_team)
odds_df["AwayTeam"] = odds_df["AwayTeam"].apply(normalize_team)

scores_df["GameDate"] = pd.to_datetime(scores_df["Date"]).dt.date
scores_df["HomeTeam"] = scores_df["Home Team"].apply(normalize_team)
scores_df["AwayTeam"] = scores_df["Away Team"].apply(normalize_team)
scores_df["HomeScore"] = scores_df["Home Score"]
scores_df["AwayScore"] = scores_df["Away Score"]
scores_df = scores_df[["GameDate", "HomeTeam", "AwayTeam", "HomeScore", "AwayScore"]]

# === MERGE SCORES + ODDS ===
merged = pd.merge(
    odds_df,
    scores_df,
    on=["GameDate", "HomeTeam", "AwayTeam"],
    how="inner"
)

# === LOAD AND MERGE ESPN ODDS (IF AVAILABLE) ===
try:
    espn_odds = pd.read_csv("espn_odds.csv")
    espn_odds["GameDate"] = pd.to_datetime(espn_odds["GameDate"]).dt.date
    espn_odds["HomeTeam"] = espn_odds["HomeTeam"].apply(normalize_team)
    espn_odds["AwayTeam"] = espn_odds["AwayTeam"].apply(normalize_team)

    merged = pd.merge(
        merged,
        espn_odds[["GameDate", "HomeTeam", "AwayTeam", "Spread", "Total"]],
        on=["GameDate", "HomeTeam", "AwayTeam"],
        how="left",
        suffixes=("", "_ESPN")
    )

    # Use ESPN odds when available
    merged["OpeningPointSpread"] = merged["Spread"].combine_first(merged["OpeningPointSpread"])
    merged["OpeningOverUnder"] = merged["Total"].combine_first(merged["OpeningOverUnder"])

except Exception as e:
    print("⚠️ ESPN odds not merged:", e)

# === SANITY CHECK / CLAMP ===
merged["OpeningPointSpread"] = merged["OpeningPointSpread"].clip(-2.0, 2.0)
merged["OpeningOverUnder"] = merged["OpeningOverUnder"].clip(6.0, 11.0)

# === DROP DUPLICATES ===
merged.drop_duplicates(subset=["GameId"], inplace=True)

# === CALCULATE OUTCOMES ===
merged["Winner"] = merged.apply(
    lambda r: "Home" if r["HomeScore"] > r["AwayScore"]
    else "Away" if r["AwayScore"] > r["HomeScore"]
    else "Push",
    axis=1
)

merged["Favorite"] = merged.apply(
    lambda r: "Home" if r["OpeningHomeMoneyLine"] < r["OpeningAwayMoneyLine"]
    else "Away",
    axis=1
)

merged["CorrectSide"] = merged["Winner"] == merged["Favorite"]
merged["TotalRuns"] = merged["HomeScore"] + merged["AwayScore"]
merged["OverHit"] = merged["TotalRuns"] > merged["OpeningOverUnder"]
merged["UnderHit"] = merged["TotalRuns"] < merged["OpeningOverUnder"]
merged["PushTotal"] = merged["TotalRuns"] == merged["OpeningOverUnder"]

# === EXPORT ===
merged.to_csv("comparison.csv", index=False)

# === SUMMARY ===
print("\n===== LINE ACCURACY SUMMARY =====")
print(f"Games matched:            {len(merged)}")
print(f"Correct moneyline picks:  {merged['CorrectSide'].sum()} ({merged['CorrectSide'].mean():.1%})")
print(f"Games Over:               {merged['OverHit'].sum()}")
print(f"Games Under:              {merged['UnderHit'].sum()}")
print(f"Pushes on total:          {merged['PushTotal'].sum()}")
print("==================================\n")
print("✅ Full comparison saved to 'comparison.csv'")

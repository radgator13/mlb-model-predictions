import pandas as pd

# Load odds and scores
odds_df = pd.read_csv("mlb_opening_lines_clean.csv")
scores_df = pd.read_csv("espn_scores.csv")

# Normalize column cases and team names
def normalize_team(name):
    return name.strip().upper() if pd.notnull(name) else name

# ✅ Apply changes directly to each DataFrame
odds_df["GameDate"] = pd.to_datetime(odds_df["GameDate"]).dt.date
odds_df["HomeTeam"] = odds_df["HomeTeam"].apply(normalize_team)
odds_df["AwayTeam"] = odds_df["AwayTeam"].apply(normalize_team)

scores_df["GameDate"] = pd.to_datetime(scores_df["Date"]).dt.date  # 🛠 handle ESPN's "Date" column
scores_df["HomeTeam"] = scores_df["Home Team"].apply(normalize_team)
scores_df["AwayTeam"] = scores_df["Away Team"].apply(normalize_team)
scores_df["HomeScore"] = scores_df["Home Score"]
scores_df["AwayScore"] = scores_df["Away Score"]

# Only keep what we need from scores
scores_df = scores_df[["GameDate", "HomeTeam", "AwayTeam", "HomeScore", "AwayScore"]]

# Merge datasets
merged = pd.merge(
    odds_df,
    scores_df,
    on=["GameDate", "HomeTeam", "AwayTeam"],
    how="inner"
)

# Drop duplicate games by GameId
merged.drop_duplicates(subset=["GameId"], inplace=True)

# Determine outcome
merged["Winner"] = merged.apply(
    lambda r: "Home" if r["HomeScore"] > r["AwayScore"]
    else "Away" if r["AwayScore"] > r["HomeScore"]
    else "Push",
    axis=1
)

# Favorite by moneyline
merged["Favorite"] = merged.apply(
    lambda r: "Home" if r["OpeningHomeMoneyLine"] < r["OpeningAwayMoneyLine"]
    else "Away",
    axis=1
)

# Accuracy
merged["CorrectSide"] = merged["Winner"] == merged["Favorite"]
merged["TotalRuns"] = merged["HomeScore"] + merged["AwayScore"]
merged["OverHit"] = merged["TotalRuns"] > merged["OpeningOverUnder"]
merged["UnderHit"] = merged["TotalRuns"] < merged["OpeningOverUnder"]
merged["PushTotal"] = merged["TotalRuns"] == merged["OpeningOverUnder"]

# Save to CSV
merged.to_csv("comparison.csv", index=False)

# Summary
print("\n===== LINE ACCURACY SUMMARY =====")
print(f"Games matched:            {len(merged)}")
print(f"Correct moneyline picks:  {merged['CorrectSide'].sum()} ({merged['CorrectSide'].mean():.1%})")
print(f"Games Over:               {merged['OverHit'].sum()}")
print(f"Games Under:              {merged['UnderHit'].sum()}")
print(f"Pushes on total:          {merged['PushTotal'].sum()}")
print("==================================\n")
print("✅ Full comparison saved to 'comparison.csv'")

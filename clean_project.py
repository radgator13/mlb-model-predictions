import os
from pathlib import Path

# === Anchor to the directory where this script lives
BASE_DIR = Path(__file__).resolve().parent

FILES_TO_DELETE = [
    "check_model_type.py",
    "train_win_model.py",
    "train_ou_model.py",
    "train_win_regression_model.py",
    "predict_win.py",
    "comparison.csv",
    "espn_scrape.py",
    "espn_scores.csv",
    "espn_odds_scraper.py",
    "espn_odds_scraper_selenium.py",
    "ESPN_Scraper.py",
    "draftkings_debug_dump.html",
    "mlb_dk_full_lines.csv",
    "mlb_dk_full_odds.csv",
    "mlb_dk_moneyline.csv",
    "mlb_dk_odds_20250408_094504.csv",
    "mlb_dk_teams.csv",
    "mlb_opening_lines.csv",
    "mlb_opening_lines_clean.csv"
]

deleted = 0
skipped = 0

for filename in FILES_TO_DELETE:
    file_path = BASE_DIR / filename
    if file_path.exists():
        file_path.unlink()
        print(f"🗑️ Deleted: {filename}")
        deleted += 1
    else:
        print(f"⏭️ Skipped (not found): {filename}")
        skipped += 1

print(f"\n✅ Project cleanup complete. {deleted} file(s) deleted, {skipped} skipped.")

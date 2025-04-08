import requests
import csv
from datetime import datetime, timedelta
import time

print("All .py files in script dir:")
for f in SCRIPT_DIR.glob("*.py"):
    print("-", f.name)
# === CONFIG ===
START_DATE = datetime(2025, 3, 27)
END_DATE = datetime.today()  # ✅ Includes today
OUTPUT_FILE = "espn_scores.csv"

# === Fetch JSON from ESPN API ===
def fetch_espn_json(date_str):
    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={date_str}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Failed to fetch {date_str}: {e}")
        return {}

# === Parse JSON only for completed (final) games ===
def parse_espn_json(data, game_date):
    rows = []

    for event in data.get("events", []):
        try:
            comp = event["competitions"][0]
            status = comp["status"]["type"]["name"]

            if status != "STATUS_FINAL":
                print(f"⏭️ Skipping incomplete game on {game_date}: {status}")
                continue

            competitors = comp["competitors"]
            if len(competitors) != 2:
                continue

            away = next(c for c in competitors if c["homeAway"] == "away")
            home = next(c for c in competitors if c["homeAway"] == "home")

            away_team = away["team"]["abbreviation"]
            home_team = home["team"]["abbreviation"]
            away_score = int(away["score"])
            home_score = int(home["score"])
            total = away_score + home_score

            print(f"✅ {away_team} @ {home_team} — {away_score}-{home_score} → Total: {total}")
            rows.append({
                "Date": game_date,
                "Away Team": away_team,
                "Home Team": home_team,
                "Away Score": away_score,
                "Home Score": home_score,
                "Total": total
            })
        except Exception as e:
            print(f"❌ Error parsing game on {game_date}: {e}")
            continue

    return rows

# === Run the scraper ===
def run_scraper():
    current = START_DATE
    all_rows = []

    while current <= END_DATE:
        date_str = current.strftime("%Y%m%d")
        print(f"\n🔄 Fetching {date_str}...")
        json_data = fetch_espn_json(date_str)

        print(f"📅 {date_str} | Games found: {len(json_data.get('events', []))}")

        daily_rows = parse_espn_json(json_data, current.date())
        all_rows.extend(daily_rows)

        time.sleep(1)  # ⏳ Polite scraping delay
        current += timedelta(days=1)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Away Team", "Home Team", "Away Score", "Home Score", "Total"])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n✅ Done! {len(all_rows)} games written to {OUTPUT_FILE}")

# === Optional: Run just for today
def test_today_only():
    today_str = datetime.today().strftime("%Y%m%d")
    print(f"\n🔍 TESTING: Fetching games for today ({today_str}) only")
    json_data = fetch_espn_json(today_str)
    rows = parse_espn_json(json_data, datetime.today().date())
    print(f"✅ Parsed {len(rows)} completed games today")

# === MAIN ===
if __name__ == "__main__":
    run_scraper()
    # test_today_only()  # ← Uncomment to debug just today
    #
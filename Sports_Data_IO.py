import requests
import csv
import os
from datetime import datetime, timedelta

API_KEY = "7141524afacb4ab5a9ee8418096bfcd3"
BASE_URL = "https://api.sportsdata.io/v3/mlb/odds/json/GameOddsByDate/{date}?key={api_key}"
CSV_FILE = "mlb_opening_lines_clean.csv"

START_DATE = datetime(2025, 3, 27)
TODAY = datetime.today()

def fetch_data(date_str):
    url = BASE_URL.format(date=date_str, api_key=API_KEY)
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Error fetching {date_str}: {r.status_code}")
        return []
    return r.json()

def save_to_csv(data, is_new_file=False):
    fieldnames = [
        'GameDate', 'GameId', 'HomeTeam', 'AwayTeam',
        'OpeningHomeMoneyLine', 'OpeningAwayMoneyLine',
        'OpeningPointSpread', 'OpeningHomeSpreadOdds', 'OpeningAwaySpreadOdds',
        'OpeningOverUnder', 'OpeningOverOdds', 'OpeningUnderOdds'
    ]
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if is_new_file:
            writer.writeheader()
        writer.writerows(data)

def extract_valid_games(games, date_str):
    seen_game_ids = set()
    rows = []

    for game in games:
        gid = game.get("GameId")
        home = game.get("HomeTeamName") or game.get("HomeTeam")
        away = game.get("AwayTeamName") or game.get("AwayTeam")
        odds_list = game.get("PregameOdds")

        # Must have unique GameId and full data
        if not (gid and home and away and odds_list):
            continue
        if gid in seen_game_ids:
            continue

        # First entry = opening line
        opening = odds_list[0]
        fields = [
            opening.get("HomeMoneyLine"),
            opening.get("AwayMoneyLine"),
            opening.get("HomePointSpread"),
            opening.get("HomePointSpreadPayout"),
            opening.get("AwayPointSpreadPayout"),
            opening.get("OverUnder"),
            opening.get("OverPayout"),
            opening.get("UnderPayout")
        ]

        if any(v is None for v in fields):
            continue  # skip incomplete odds

        row = {
            "GameDate": date_str,
            "GameId": gid,
            "HomeTeam": home,
            "AwayTeam": away,
            "OpeningHomeMoneyLine": opening["HomeMoneyLine"],
            "OpeningAwayMoneyLine": opening["AwayMoneyLine"],
            "OpeningPointSpread": opening["HomePointSpread"],
            "OpeningHomeSpreadOdds": opening["HomePointSpreadPayout"],
            "OpeningAwaySpreadOdds": opening["AwayPointSpreadPayout"],
            "OpeningOverUnder": opening["OverUnder"],
            "OpeningOverOdds": opening["OverPayout"],
            "OpeningUnderOdds": opening["UnderPayout"]
        }

        rows.append(row)
        seen_game_ids.add(gid)

    return rows

def main():
    is_new_file = not os.path.exists(CSV_FILE)
    current_date = START_DATE
    while current_date <= TODAY:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"Processing {date_str}...")
        games = fetch_data(date_str)
        clean_rows = extract_valid_games(games, date_str)

        if clean_rows:
            save_to_csv(clean_rows, is_new_file)
            is_new_file = False

        current_date += timedelta(days=1)

if __name__ == "__main__":
    main()

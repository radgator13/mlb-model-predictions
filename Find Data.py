import requests
import json

API_KEY = "7141524afacb4ab5a9ee8418096bfcd3"
DATE = "2025-03-27"
URL = f"https://api.sportsdata.io/v3/mlb/odds/json/GameOddsByDate/{DATE}?key={API_KEY}"

def fetch_and_inspect():
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return

    games = response.json()

    print(f"\n🔍 Total games found: {len(games)}\n")
    
    for i, game in enumerate(games):
        print(f"--- Game {i + 1} ---")
        print(json.dumps(game, indent=2))  # Full structure

        home = game.get("HomeTeam")
        away = game.get("AwayTeam")

        print(f"> HomeTeam: {home}")
        print(f"> AwayTeam: {away}")
        print("------\n")

if __name__ == "__main__":
    fetch_and_inspect()

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def normalize_team(name):
    """Standardize team abbreviations for matching."""
    name = name.strip().upper()
    replacements = {
        "LA DODGERS": "LAD",
        "LA ANGELS": "LAA",
        "NY YANKEES": "NYY",
        "NY METS": "NYM",
        "WASHINGTON": "WAS"
    }
    for k, v in replacements.items():
        if k in name:
            return v
    return name.split()[-1][:3].upper()

def parse_money(value):
    try:
        return int(value.replace("+", "").replace("−", "-"))
    except:
        return None

def parse_total(val):
    val = val.replace("O ", "").replace("U ", "")
    try:
        return float(val)
    except:
        return None

def fetch_espn_odds(date=None):
    if date is None:
        date = datetime.today().strftime("%Y%m%d")
    url = f"https://www.espn.com/mlb/odds/_/date/{date}"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Failed to fetch ESPN odds for {date}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "html.parser")
    matchups = soup.select("section.odds__matchup")

    rows = []
    for matchup in matchups:
        try:
            teams = matchup.select(".team-name")
            if len(teams) != 2:
                continue
            away_team = normalize_team(teams[0].get_text())
            home_team = normalize_team(teams[1].get_text())

            # Caesars row is usually first
            caesars_row = matchup.select_one("table tbody tr")
            if not caesars_row:
                continue

            cells = caesars_row.find_all("td")
            if len(cells) < 6:
                continue

            # Parse values
            away_spread = cells[0].text.strip()
            away_money = parse_money(cells[1].text.strip())
            total = parse_total(cells[2].text.strip())

            home_spread = cells[3].text.strip()
            home_money = parse_money(cells[4].text.strip())

            rows.append({
                "GameDate": datetime.strptime(date, "%Y%m%d").date(),
                "HomeTeam": home_team,
                "AwayTeam": away_team,
                "OpeningHomeMoneyLine": home_money,
                "OpeningAwayMoneyLine": away_money,
                "OpeningPointSpread": float(home_spread.replace("+", "")) if home_spread else None,
                "OpeningOverUnder": total
            })

        except Exception as e:
            print("⚠️ Parsing error:", e)
            continue

    return pd.DataFrame(rows)

if __name__ == "__main__":
    date = input("Enter date (YYYYMMDD) or leave blank for today: ") or None
    df = fetch_espn_odds(date)
    if not df.empty:
        df.to_csv("espn_odds_scraped.csv", index=False)
        print(f"✅ Saved {len(df)} rows to espn_odds_scraped.csv")
    else:
        print("❌ No odds scraped")

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
import time

uc.Chrome.__del__ = lambda self: None

def normalize_team(name):
    return name.upper().replace(" ", "").replace("D-BACKS", "DIAMONDBACKS")

def convert_ml_to_prob(ml):
    try:
        ml = float(ml)
        if ml > 0:
            return round(100 / (ml + 100) * 100, 2)
        else:
            return round(-ml / (-ml + 100) * 100, 2)
    except:
        return None

def parse_total(val):
    if isinstance(val, str) and len(val) >= 2:
        side = val[0].upper()
        try:
            value = float(val[1:])
            return side, value
        except:
            return "", ""
    return "", ""

def extract_outcomes_by_role(cells):
    spread = ""
    ml = ""
    total = ""
    for cell in cells:
        try:
            label = cell.find_element(By.CSS_SELECTOR, "span.sportsbook-outcome-cell__label").text.strip()
        except:
            label = ""
        try:
            value = cell.find_element(By.CSS_SELECTOR, "span.sportsbook-outcome-cell__line").text.strip()
        except:
            value = ""

        # Moneyline: no label, integer value
        if not label and value and "." not in value:
            ml = value
        # Spread: no label, value has decimal (e.g., -1.5)
        elif not label and "." in value:
            spread = value
        # Total: has label O/U
        elif label in ("O", "U"):
            total = f"{label}{value}"

    return spread, ml, total

def fetch_dk_game_data():
    driver = uc.Chrome(headless=False)
    try:
        driver.get("https://sportsbook.draftkings.com/leagues/baseball/mlb")
        time.sleep(8)

        teams = driver.find_elements(By.CSS_SELECTOR, "div.event-cell__name-text")
        cells = driver.find_elements(By.CSS_SELECTOR, "div.sportsbook-outcome-cell")

        print(f"🧪 Found {len(teams)} teams")
        print(f"🧪 Found {len(cells)} outcome cells")

        if len(teams) % 2 != 0:
            print("⚠️ Unexpected number of teams.")
            return pd.DataFrame()

        # Build odds blocks: each team should have 3 outcome cells
        team_odds = []
        for i in range(0, len(cells), 3):
            chunk = cells[i:i+3]
            spread, ml, total = extract_outcomes_by_role(chunk)
            team_odds.append((spread, ml, total))

        if len(team_odds) != len(teams):
            print("❌ Team and odds count mismatch.")
            return pd.DataFrame()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        games = []

        for i in range(0, len(teams), 2):
            team1 = teams[i].text.strip()
            team2 = teams[i+1].text.strip()
            spread1, ml1, total1 = team_odds[i]
            spread2, ml2, total2 = team_odds[i+1]

            # Determine favorite by spread
            try:
                s1 = float(spread1)
            except:
                s1 = 0
            try:
                s2 = float(spread2)
            except:
                s2 = 0

            if s1 < s2:
                favorite = team1
                spread_line = s1
                ml_fav = ml1
            else:
                favorite = team2
                spread_line = s2
                ml_fav = ml2

            # Parse total from team1 side
            total_side, total_value = parse_total(total1)

            games.append({
                "timestamp": timestamp,
                "team1": team1,
                "team2": team2,
                "favorite_team": favorite,
                "spread_line": spread_line,
                "total_line": total_value,
                "total_side": total_side,
                "moneyline_fav": ml_fav
            })

        return pd.DataFrame(games)

    finally:
        try:
            driver.quit()
        except:
            pass
        del driver

if __name__ == "__main__":
    df = fetch_dk_game_data()

    if not df.empty:
        filename = f"mlb_clean_games_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"\n✅ DONE. Cleaned games saved to: {filename}")
    else:
        print("⚠️ No data extracted.")

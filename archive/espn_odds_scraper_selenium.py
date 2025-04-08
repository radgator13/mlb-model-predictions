import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


def normalize_team_name(name):
    return name.strip().upper().replace("LA ", "LAD").replace("NY ", "NY").replace("WSH", "WAS")


def fetch_espn_odds(date=None):
    if date is None:
        date = datetime.today().strftime("%Y%m%d")

    url = f"https://www.espn.com/mlb/odds/_/date/{date}"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".Odds__Table"))
        )

        teams = driver.find_elements(By.CSS_SELECTOR, ".team-name")
        team_names = [normalize_team_name(t.text) for t in teams if t.text.strip()]
        matchups = [(team_names[i], team_names[i+1]) for i in range(0, len(team_names), 2)]

        odds_rows = driver.find_elements(By.CSS_SELECTOR, ".Odds__Table table tbody tr")

        rows = []
        for i, row in enumerate(odds_rows[:len(matchups)]):
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 5:
                    continue

                away_spread = cells[0].text.strip()
                away_moneyline = cells[1].text.strip()
                total = cells[2].text.strip().replace("O ", "").replace("u", "").replace("o", "")
                home_spread = cells[3].text.strip()
                home_moneyline = cells[4].text.strip()

                away, home = matchups[i]
                game_date = datetime.today().date() if not date else datetime.strptime(date, "%Y%m%d").date()

                rows.append({
                    "GameDate": game_date,
                    "HomeTeam": home,
                    "AwayTeam": away,
                    "HomeMoneyLine_ESPN": home_moneyline,
                    "AwayMoneyLine_ESPN": away_moneyline,
                    "Spread_ESPN": home_spread,
                    "Total_ESPN": total
                })
            except Exception as e:
                print(f"⚠️ Parsing issue for row {i}: {e}")
                continue

        driver.quit()
        return pd.DataFrame(rows)

    except Exception as e:
        driver.quit()
        print("❌ Error during scraping:", e)
        return pd.DataFrame()


if __name__ == "__main__":
    date = input("Enter date (YYYYMMDD) or leave blank for today: ") or None
    odds_df = fetch_espn_odds(date)
    if not odds_df.empty:
        odds_df.to_csv("espn_odds_scraped.csv", index=False)
        print(f"✅ Saved {len(odds_df)} matchups to espn_odds_scraped.csv")
    else:
        print("❌ No odds found or failed to parse.")

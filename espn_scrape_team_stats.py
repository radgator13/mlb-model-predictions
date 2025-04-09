from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_page_html(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    driver.quit()
    return html

def extract_espn_stats(html):
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if not table:
        print("❌ No table found.")
        return pd.DataFrame()

    headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
    headers.insert(0, "TEAM")

    rows = []
    for row in table.find("tbody").find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        # ESPN: team name is in the second <td>
        team_name = cols[1].get_text(strip=True).upper()
        stats = [col.get_text(strip=True) for col in cols[2:]]
        full_row = [team_name] + stats

        if len(full_row) == len(headers):
            rows.append(full_row)

    df = pd.DataFrame(rows, columns=headers)
    return df

def fetch_and_save_stats(url, label, filename):
    print(f"🌐 Fetching {label} from {url}")
    html = get_page_html(url)
    df = extract_espn_stats(html)
    if not df.empty:
        df.to_csv(filename, index=False)
        print(f"✅ {label.capitalize()} saved to {filename}")
    else:
        print(f"❌ Failed to extract {label}")

# ESPN URLs
offense_url = "https://www.espn.com/mlb/stats/team/_/season/2025/seasontype/2"
defense_url = "https://www.espn.com/mlb/stats/team/_/season/2025/seasontype/2/stat/pitching"

fetch_and_save_stats(offense_url, "team offense", "espn_team_offense.csv")
fetch_and_save_stats(defense_url, "team defense", "espn_team_defense.csv")

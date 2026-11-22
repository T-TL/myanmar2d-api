
import requests
from bs4 import BeautifulSoup

URL = (
    "https://www.set.or.th/en/market/"
    "product/stock/overview?market=SET"
)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}

response = requests.get(URL, headers=headers, timeout=30)

print("HTTP:", response.status_code)

if response.status_code != 200:
    raise SystemExit("SET website request failed")

soup = BeautifulSoup(response.text, "html.parser")

print("\n========== MARKET TABLES ==========")

for table_number, table in enumerate(soup.find_all("table")):

    rows = table.find_all("tr")

    if not rows:
        continue

    print(f"\nTABLE NUMBER: {table_number}")

    for row in rows[:15]:
        cells = row.find_all(["th", "td"])

        values = [
            cell.get_text(" ", strip=True)
            for cell in cells
        ]

        if values:
            print(values)

        if values and values[0].strip().upper() == "SET":
            print(">>> POSSIBLE SET DATA ROW FOUND")

print("\n========== LAST UPDATE ==========")

page_text = soup.get_text(" ", strip=True)

position = page_text.find("Last Update")

if position >= 0:
    print(page_text[position:position + 250])
else:
    print("Last Update not found")

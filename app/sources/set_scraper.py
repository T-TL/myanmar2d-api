
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone


URL = (
    "https://www.set.or.th/en/market/"
    "product/stock/overview?market=SET"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}


def fetch_set_data():

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    for table in soup.find_all("table"):

        rows = table.find_all("tr")

        for row in rows:

            cells = row.find_all(["th", "td"])

            values = [
                cell.get_text(" ", strip=True)
                for cell in cells
            ]

            if len(values) < 8:
                continue

            if values[0].strip().upper() != "SET":
                continue

            try:
                set_index = float(
                    values[1].replace(",", "")
                )

                market_value = float(
                    values[7].replace(",", "")
                )

            except ValueError:
                continue

            return {
                "set_index": set_index,
                "market_value": market_value,
                "source": "SET_OFFICIAL",
                "fetched_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "is_live": False,
            }

    raise ValueError(
        "SET market data row not found"
    )


if __name__ == "__main__":

    try:
        data = fetch_set_data()

        print("SCRAPER SUCCESS")
        print(data)

    except Exception as error:
        print("SCRAPER ERROR:", str(error))
        raise

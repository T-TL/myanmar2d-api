
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

    print("HTTP STATUS:", response.status_code)

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    tables = soup.find_all("table")

    print("TABLE COUNT:", len(tables))

    for table_number, table in enumerate(tables):

        rows = table.find_all("tr")

        for row_number, row in enumerate(rows):

            # Use the same method as the successful parser
            cells = row.find_all(["th", "td"])

            values = [
                cell.get_text(" ", strip=True)
                for cell in cells
            ]

            if not values:
                continue

            normalized = [
                value.strip().replace("\xa0", " ")
                for value in values
            ]

            if (
                normalized[0].replace(" ", "").upper()
                == "SET"
            ):

                print("SET ROW FOUND")
                print("TABLE:", table_number)
                print("ROW:", row_number)
                print("VALUES:", normalized)

                if len(normalized) < 8:
                    raise ValueError(
                        "SET row has fewer than 8 columns"
                    )

                set_index = float(
                    normalized[1].replace(",", "")
                )

                market_value = float(
                    normalized[7].replace(",", "")
                )

                return {
                    "set_index": set_index,
                    "market_value": market_value,
                    "source": "SET_OFFICIAL",
                    "fetched_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "is_live": False,
                }

    print("No SET row found.")

    raise ValueError(
        "SET market data row not found"
    )


if __name__ == "__main__":

    data = fetch_set_data()

    print("\nSCRAPER SUCCESS")
    print(data)


def extract_last_update(soup):

    text = soup.get_text(" ", strip=True)

    import re

    match = re.search(
        r"Last Update\s*-\s*Market Status\s*:\s*"
        r"(.*?)\s*(?:Index\s+Last|Market Summary)",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None

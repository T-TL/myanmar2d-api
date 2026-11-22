
import requests
import re
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



def extract_last_update(soup):

    text = soup.get_text(" ", strip=True)

    import re

    patterns = [
        r"Last Update\s*:?\s*(\d{1,2}\s+\w+\s+\d{4}\s+\d{2}:\d{2}:\d{2})",
        r"Last Update.*?(\d{1,2}\s+\w+\s+\d{4}\s+\d{2}:\d{2}:\d{2})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None


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

    last_update = extract_last_update(soup)

    print("SOURCE LAST UPDATE:", last_update)

    for table_number, table in enumerate(tables):

        rows = table.find_all("tr")

        for row_number, row in enumerate(rows):

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

            if normalized[0].replace(" ", "").upper() == "SET":

                if len(normalized) < 8:
                    continue

                set_index = float(
                    normalized[1].replace(",", "")
                )

                market_value = float(
                    normalized[7].replace(",", "")
                )

                data = {
                    "set_index": set_index,
                    "market_value": market_value,
                    "source": "SET_OFFICIAL",
                    "source_last_update": last_update,
                    "fetched_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "is_live": False,
                }

                print("SET ROW FOUND")
                print("TABLE:", table_number)
                print("ROW:", row_number)

                return data

    raise ValueError(
        "SET market data row not found"
    )


if __name__ == "__main__":

    data = fetch_set_data()

    print("\nSCRAPER SUCCESS")

    for key, value in data.items():
        print(f"{key}: {value}")

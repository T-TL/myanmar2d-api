
import requests
from bs4 import BeautifulSoup
import re

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

response = requests.get(
    URL,
    headers=headers,
    timeout=30
)

print("HTTP:", response.status_code)
print("HTML SIZE:", len(response.text))

soup = BeautifulSoup(response.text, "html.parser")

text = soup.get_text(" ", strip=True)

keywords = [
    "SET Index",
    "Market Value",
    "Index",
    "Value",
    "Last Update",
    "Market Status",
]

for keyword in keywords:
    print("\nKEYWORD:", keyword)

    matches = list(
        re.finditer(
            re.escape(keyword),
            text,
            re.IGNORECASE
        )
    )

    print("FOUND:", len(matches))

    for match in matches[:3]:
        start = max(0, match.start() - 150)
        end = min(len(text), match.end() + 250)
        print(text[start:end])

print("\nPAGE TITLE:")
print(soup.title.get_text(strip=True) if soup.title else "No title")

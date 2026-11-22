
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

SOURCES = {
    "SET_OFFICIAL": (
        "https://www.set.or.th/en/market/"
        "product/stock/overview?market=SET"
    ),
    "SETLIVE_REFERENCE": (
        "https://setlive.myanmarnode.com/en"
    ),
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )
}

PATTERNS = [
    "set index",
    "market value",
    "total value",
    "index",
    "value",
    "market summary",
    "last update",
    "market status",
    "2d",
    "updated",
]


def inspect_source(name, url):
    print("\n" + "=" * 60)
    print("SOURCE:", name)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=25
        )

        print("HTTP:", response.status_code)
        print("HTML SIZE:", len(response.text))

        if response.status_code != 200:
            print("ACCESS FAILED")
            return

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        print("\nPAGE TITLE:")
        print(
            soup.title.get_text(strip=True)
            if soup.title else "No title"
        )

        print("\nSCRIPT FILES:")

        for script in soup.find_all("script", src=True):
            src = urljoin(url, script["src"])

            if src.startswith(("https://", "http://")):
                print(src[:300])

        print("\nEMBEDDED DATA:")

        for script in soup.find_all("script"):
            content = script.string or script.get_text()

            if not content:
                continue

            script_type = script.get("type", "")

            if script_type == "application/ld+json":
                print("JSON-LD FOUND")
                print(content[:1000])

            for pattern in PATTERNS:
                if pattern in content.lower():
                    print(
                        f"KEYWORD: {pattern} "
                        f"| LENGTH: {len(content)}"
                    )

                    match = re.search(
                        re.escape(pattern),
                        content,
                        re.IGNORECASE
                    )

                    if match:
                        start = max(0, match.start() - 180)
                        end = min(
                            len(content),
                            match.end() + 350
                        )
                        print(content[start:end][:550])
                    break

        print("\nPAGE DATA MARKERS:")

        markers = [
            "__NEXT_DATA__",
            "__NUXT__",
            "__APOLLO_STATE__",
            "application/json",
        ]

        for marker in markers:
            print(
                marker,
                "FOUND" if marker in response.text
                else "NOT FOUND"
            )

    except requests.RequestException as error:
        print("REQUEST ERROR:", error)


if __name__ == "__main__":
    for name, url in SOURCES.items():
        inspect_source(name, url)

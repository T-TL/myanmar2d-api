
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from html import unescape

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

KEYWORDS = [
    "setindex",
    "set_index",
    "marketvalue",
    "market_value",
    "totalvalue",
    "total_value",
    "marketdata",
    "market_data",
    "stockquote",
    "quote",
    "api/",
    "/api",
]


def inspect_source(name, page_url):
    print("\n" + "=" * 65)
    print("SOURCE:", name)

    try:
        response = requests.get(
            page_url,
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        scripts = soup.find_all("script", src=True)

        print("PAGE STATUS:", response.status_code)
        print("SCRIPT COUNT:", len(scripts))

        candidates = set()

        # Inspect JavaScript files linked by the page
        for script in scripts:
            js_url = urljoin(page_url, script["src"])

            if not js_url.startswith(("http://", "https://")):
                continue

            try:
                js_response = requests.get(
                    js_url,
                    headers=HEADERS,
                    timeout=25
                )

                if js_response.status_code != 200:
                    continue

                js = unescape(js_response.text)
                print("\nJS FILE:", js_url)
                print("JS SIZE:", len(js))

                # Find relevant API paths and URL strings
                patterns = [
                    r"""["']([^"' ]{1,250})["']"""
                ]

                for pattern in patterns:
                    for match in re.findall(pattern, js):
                        lower = match.lower()

                        if any(k in lower for k in KEYWORDS):
                            candidates.add(match)

                # Find relevant keywords with nearby code
                for keyword in KEYWORDS:
                    for match in re.finditer(
                        re.escape(keyword), js, re.IGNORECASE
                    ):
                        start = max(0, match.start() - 150)
                        end = min(len(js), match.end() + 250)

                        print(
                            "\nMATCH:",
                            keyword,
                            "\n",
                            js[start:end][:400]
                        )

            except requests.RequestException as error:
                print("JS DOWNLOAD ERROR:", error)

        print("\n--- POSSIBLE DATA URLS / PATHS ---")

        for item in sorted(candidates):
            print(item[:300])

        # Check Nuxt state in original HTML
        print("\n--- NUXT STATE CHECK ---")

        for marker in ["__NUXT__", "__NUXT_DATA__"]:
            print(
                marker,
                "FOUND" if marker in response.text else "NOT FOUND"
            )

    except requests.RequestException as error:
        print("PAGE ERROR:", error)


if __name__ == "__main__":
    for name, url in SOURCES.items():
        inspect_source(name, url)

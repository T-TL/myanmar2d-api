
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from html import unescape

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )
}

SET_URL = (
    "https://www.set.or.th/en/market/"
    "product/stock/overview?market=SET"
)

SET_TERMS = [
    "getStockIndexSet",
    "getStockOverview",
    "getStockIndexChart",
    "setIndexInfo",
    "setMarketIndexQuote",
    "axios",
    "baseURL",
    "fetch("
]

SETLIVE_URL = "https://setlive.myanmarnode.com/en"

SETLIVE_TERMS = [
    "fetch(",
    "axios",
    "baseURL",
    "market",
    "set_index",
    "market_value",
    "api/",
    "endpoint",
    "live"
]


def download(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()
    return unescape(response.text)


def show_matches(label, content, terms):
    print("\n---", label, "---")

    found = 0

    for term in terms:
        matches = list(
            re.finditer(re.escape(term), content, re.I)
        )

        for match in matches[:3]:
            start = max(0, match.start() - 250)
            end = min(len(content), match.end() + 450)

            print("\nTERM:", term)
            print(content[start:end][:700])
            found += 1

    if found == 0:
        print("No matching code found.")


def inspect_set():
    print("\n" + "=" * 65)
    print("SET OFFICIAL TARGETED INSPECTION")

    try:
        html = download(SET_URL)
        soup = BeautifulSoup(html, "html.parser")

        for script in soup.find_all("script", src=True):
            js_url = urljoin(SET_URL, script["src"])

            if "/_nuxt/" not in js_url:
                continue

            try:
                js = download(js_url)

                relevant = any(
                    term.lower() in js.lower()
                    for term in SET_TERMS
                )

                if relevant:
                    print("\nJS FILE:", js_url)
                    show_matches(
                        "SET JAVASCRIPT",
                        js,
                        SET_TERMS
                    )

            except Exception as error:
                print("JS ERROR:", error)

    except Exception as error:
        print("SET ERROR:", error)


def inspect_setlive():
    print("\n" + "=" * 65)
    print("SETLIVE TARGETED INSPECTION")

    try:
        html = download(SETLIVE_URL)
        soup = BeautifulSoup(html, "html.parser")

        app_scripts = []

        for script in soup.find_all("script", src=True):
            url = urljoin(SETLIVE_URL, script["src"])

            if "/build/assets/" in url and url.endswith(".js"):
                app_scripts.append(url)

        discovered = set()

        for url in app_scripts:
            try:
                js = download(url)

                print("\nMAIN JS:", url)

                # Find referenced JavaScript chunks
                chunks = re.findall(
                    r"""["']([^"']+\.js)["']""",
                    js
                )

                for chunk in chunks:
                    if any(
                        word in chunk.lower()
                        for word in [
                            "api-docs",
                            "quote-card",
                            "live-snippet",
                            "index-"
                        ]
                    ):
                        discovered.add(
                            urljoin(url, chunk)
                        )

                show_matches(
                    "SETLIVE MAIN JS",
                    js,
                    SETLIVE_TERMS
                )

            except Exception as error:
                print("MAIN JS ERROR:", error)

        print("\n--- DISCOVERED CHUNKS ---")

        for chunk_url in sorted(discovered):
            print(chunk_url)

            try:
                chunk_js = download(chunk_url)

                show_matches(
                    "SETLIVE CHUNK",
                    chunk_js,
                    SETLIVE_TERMS
                )

            except Exception as error:
                print("CHUNK ERROR:", error)

    except Exception as error:
        print("SETLIVE ERROR:", error)


if __name__ == "__main__":
    inspect_set()
    inspect_setlive()
